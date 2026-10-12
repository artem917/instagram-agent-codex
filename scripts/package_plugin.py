"""Build a deterministic portable plugin ZIP from reviewed files; stdlib only."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile

from validate import ROOT, SKILLS, validate

NAME = "instagram-agent-codex"
MARKETPLACE = "instagram-codex-local"
ROOT_FILES = ("plugin.json", "mcp.json", ".codex-plugin/plugin.json", "LICENSE", "UPSTREAM.md", "UPSTREAM.json")
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def path_inside(root, value):
    if not isinstance(value, str) or not value.startswith("./") or "\\" in value:
        raise ValueError(f"Plugin path must be ./-relative: {value}")
    if ".." in PurePosixPath(value).parts or PurePosixPath(value).is_absolute():
        raise ValueError(f"Unsafe plugin path: {value}")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Plugin path resolves outside its root")
    return path


def validate_plugin(root=ROOT):
    root = Path(root)
    manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    if manifest.get("$schema") != SCHEMA or manifest.get("name") != NAME:
        raise ValueError("Wrong portable schema or plugin identity")
    if set(manifest) - {"$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"}:
        raise ValueError("Unsupported portable manifest field")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")) or manifest.get("license") != "MIT":
        raise ValueError("Plugin version/license invalid")
    overlay = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    for key in ("name", "version", "description", "license"):
        if overlay.get(key) != manifest.get(key):
            raise ValueError(f"Compatibility view drift: {key}")
    ext = manifest["extensions"]["com.openai"]
    if overlay.get("interface") != ext["interface"] or overlay.get("skills") != "./skills/":
        raise ValueError("Compatibility interface/components drift")
    onboarding = path_inside(root, ext["onboardingSkill"])
    if onboarding != (root / "skills/ig-plan/SKILL.md").resolve() or not onboarding.is_file():
        raise ValueError("Onboarding must reference included ig-plan skill")
    if overlay["extensions"]["com.openai"]["onboardingSkill"] != ext["onboardingSkill"]:
        raise ValueError("Onboarding overlay drift")
    if not ext["publication"]["translations"]["ru-RU"]["description"]:
        raise ValueError("Russian description missing")
    mcp = json.loads((root / "mcp.json").read_text(encoding="utf-8"))
    if mcp != {"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "mcpServers": {}}:
        raise ValueError("V0 must contain no registered MCP server or endpoint")
    if set(p.name for p in (root / "skills").iterdir() if p.is_dir()) != set(SKILLS):
        raise ValueError("Plugin must retain exactly the original 13 skills")
    for name in SKILLS:
        folder = root / "skills" / name
        if not (folder / "SKILL.md").is_file() or (folder / "LICENSE").read_bytes().replace(b"\r\n", b"\n") != (root / "LICENSE").read_bytes().replace(b"\r\n", b"\n"):
            raise ValueError(f"Missing skill/license: {name}")
    return manifest


def catalog(plugin_path="./"):
    return {"name": MARKETPLACE, "interface": {"displayName": "Instagram Codex — Local"},
            "plugins": [{"name": NAME, "source": {"source": "local", "path": plugin_path},
                         "policy": {"installation": "AVAILABLE", "authentication": "ON_USE"}, "category": "Productivity"}]}


def records(root=ROOT):
    root = Path(root)
    validate(root)
    manifest = validate_plugin(root)
    result = {}
    for rel in ROOT_FILES:
        path = root / rel
        if path.is_symlink():
            raise ValueError(f"Symlink forbidden in package: {rel}")
        result[rel] = path.read_bytes().replace(b"\r\n", b"\n")
    for name in SKILLS:
        for path in sorted((root / "skills" / name).rglob("*")):
            if path.is_symlink():
                raise ValueError("Symlink forbidden in skill resources")
            if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path.suffix not in (".md", ".py", ".json", ".yaml") and path.name != "LICENSE":
                raise ValueError(f"Unreviewed skill resource: {path.name}")
            result[path.relative_to(root).as_posix()] = path.read_bytes().replace(b"\r\n", b"\n")
    result[".agents/plugins/marketplace.json"] = (json.dumps(catalog(), indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    readme = root / "PLUGIN.md"
    result["README.md"] = readme.read_bytes().replace(b"\r\n", b"\n") if readme.exists() else b"Instagram drafting for Codex. Run ig-plan onboarding.\n"
    inventory = {rel: hashlib.sha256(data).hexdigest() for rel, data in sorted(result.items())}
    result["PACKAGE.json"] = (json.dumps({"plugin": NAME, "version": manifest["version"], "files_sha256": inventory}, indent=2) + "\n").encode()
    return result


def write_directory(target, root=ROOT):
    target = Path(target)
    data = records(root)
    if target.exists():
        existing = {p.relative_to(target).as_posix(): p.read_bytes() for p in target.rglob("*") if p.is_file()}
        if existing != data:
            raise ValueError("Different plugin already exists; choose a fresh directory or reconcile it")
        return target
    for rel, content in data.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return target


def build_zip(destination, root=ROOT):
    destination = Path(destination)
    data = records(root)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel, content in sorted(data.items()):
            info = zipfile.ZipInfo(f"{NAME}/{rel}", date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    verify_zip(destination)
    return destination


def verify_zip(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(set(names)) != len(names) or archive.testzip() is not None:
            raise ValueError("Duplicate or corrupt ZIP entry")
        data = {}
        for name in names:
            parts = PurePosixPath(name).parts
            if not parts or parts[0] != NAME or ".." in parts or "\\" in name or PurePosixPath(name).is_absolute():
                raise ValueError("Unsafe ZIP path")
            if any(p in (".git", ".test-work", "__pycache__", ".instagram-agent") for p in parts) or name.endswith((".pyc", ".log", ".jsonl")) or any(p.startswith(".env") for p in parts):
                raise ValueError("Private/runtime file in ZIP")
            data["/".join(parts[1:])] = archive.read(name)
        package = json.loads(data.pop("PACKAGE.json"))
        actual = {rel: hashlib.sha256(raw).hexdigest() for rel, raw in sorted(data.items())}
        if actual != package["files_sha256"]:
            raise ValueError("Package inventory/hash mismatch")
        if sum(rel.endswith("/SKILL.md") for rel in data) != 13:
            raise ValueError("ZIP must contain all 13 skills exactly once")
    return {"plugin": NAME, "files": len(data) + 1, "skills": 13,
            "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="outputs/instagram-agent-codex-0.1.0.zip")
    parser.add_argument("--directory", help="also prepare a clean plugin directory")
    args = parser.parse_args()
    build_zip(args.out)
    if args.directory:
        write_directory(args.directory)
    print(json.dumps(verify_zip(args.out), indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)

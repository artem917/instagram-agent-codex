"""Validate this pack's deliberately restricted, valid YAML subset and resources.

No third-party YAML dependency is needed: authored string scalars use JSON
quoting, which is a YAML-compatible subset. This is not a general YAML parser.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "ig-audit", "ig-caption", "ig-carousel", "ig-comment", "ig-dm", "ig-human",
    "ig-plan", "ig-profile", "ig-reel", "ig-reply", "ig-repurpose", "ig-story", "ig-viral",
)
TOOLS = (
    "ig-caption/caption.py", "ig-human/detect.py", "ig-human/humanize.py",
    "ig-reel/beats.py", "ig-reel/hookscore.py", "ig-viral/swipe.py",
)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    header, body = text[4:].split("\n---\n", 1)
    fields = {}
    for line in header.splitlines():
        key, value = line.split(": ", 1)
        if key in fields:
            raise ValueError(f"{path}: duplicate field {key}")
        fields[key] = json.loads(value) if value.startswith('"') else value
    allowed = {"name", "description", "license"}
    if set(fields) - allowed:
        raise ValueError(f"{path}: unsupported frontmatter in this pack")
    name, description = fields.get("name"), fields.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError(f"{path}: invalid name")
    if name != path.parent.name or name not in SKILLS:
        raise ValueError(f"{path}: name/folder mismatch")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        raise ValueError(f"{path}: invalid description")
    if fields.get("license") != "MIT":
        raise ValueError(f"{path}: invalid license")
    if not body.strip():
        raise ValueError(f"{path}: empty instructions")
    return fields, body


def validate(root=ROOT):
    root = Path(root)
    found = tuple(sorted(p.name for p in (root / "skills").iterdir() if p.is_dir()))
    if found != SKILLS:
        raise ValueError(f"Expected all 13 skills, found {found}")
    license_bytes = (root / "LICENSE").read_bytes().replace(b"\r\n", b"\n")
    if b"Copyright (c) 2026 Jake Schincariol" not in license_bytes:
        raise ValueError("Original copyright notice missing")
    for name in SKILLS:
        folder = root / "skills" / name
        _, body = frontmatter(folder / "SKILL.md")
        for required in ("references/codex.md", "agents/openai.yaml", "LICENSE", "NOTICE.md"):
            if not (folder / required).is_file():
                raise ValueError(f"{name}: missing {required}")
        if (folder / "LICENSE").read_bytes().replace(b"\r\n", b"\n") != license_bytes:
            raise ValueError(f"{name}: license differs")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", body):
            if not re.match(r"https?://", link) and not (folder / link).is_file():
                raise ValueError(f"{name}: broken reference {link}")
        for sibling in re.findall(r"\$ig-([a-z]+)", body):
            if "ig-" + sibling not in SKILLS:
                raise ValueError(f"{name}: unknown sibling {sibling}")
        for script in re.findall(r"<skill_dir>/([a-z_]+\.py)", body):
            if not (folder / script).is_file():
                raise ValueError(f"{name}: missing script {script}")
        for resource in re.findall(r"`((?:\.\./)?ig-[a-z]+/[a-z]+\.json|[a-z]+\.json)`", body):
            if not (folder / resource).is_file():
                raise ValueError(f"{name}: missing resource {resource}")
        active = body + (folder / "references/codex.md").read_text(encoding="utf-8")
        if re.search(r"\.claude[/\\]|/plugin\s|(?<![.\w])/ig-[a-z]+", active):
            raise ValueError(f"{name}: active Claude-specific invocation or path")
        ui = (folder / "agents/openai.yaml").read_text(encoding="utf-8").splitlines()
        if ui[0] != "interface:" or len(ui) != 4:
            raise ValueError(f"{name}: unexpected UI metadata")
        values = {line.strip().split(": ", 1)[0]: json.loads(line.strip().split(": ", 1)[1]) for line in ui[1:]}
        if not 25 <= len(values["short_description"]) <= 64 or "$" + name not in values["default_prompt"]:
            raise ValueError(f"{name}: invalid UI metadata")
    for rel in TOOLS:
        path = root / "skills" / rel
        if not path.is_file() or not (path.parent / "ig_io.py").is_file():
            raise ValueError(f"Missing executable or I/O helper: {rel}")
    for path in root.rglob("*.py"):
        if any(part in (".git", ".agents", ".test-work", ".venv") for part in path.relative_to(root).parts):
            continue
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in (root / "skills").rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    hooks = json.loads((root / "skills/ig-reel/hooks.json").read_text(encoding="utf-8"))
    ids = [h["id"] for h in hooks["hooks"]]
    if len(ids) != 26 or len(set(ids)) != 26 or set(hooks["classify_order"]) != set(ids):
        raise ValueError("Hook formula inventory/order mismatch")
    for hook in hooks["hooks"]:
        re.compile(hook["match"], re.IGNORECASE)
    lex = json.loads((root / "skills/ig-human/slop.json").read_text(encoding="utf-8"))
    for item in lex["structures"]:
        re.compile(item["regex"], re.MULTILINE)
    rubric = json.loads((root / "skills/ig-profile/rubric.json").read_text(encoding="utf-8"))
    if len(rubric["items"]) != 12 or sum(i["points"] for i in rubric["items"]) != 100 or rubric["total"] != 100:
        raise ValueError("Profile rubric mismatch")
    template = root / "templates/voice.md"
    if template.read_bytes() != (root / "skills/ig-reel/assets/voice.md").read_bytes():
        raise ValueError("Installed voice template differs from source")
    provenance = json.loads((root / "UPSTREAM.json").read_text(encoding="utf-8"))
    for rel, digest in provenance["preserved_sha256_lf"].items():
        actual = hashlib.sha256((root / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if actual != digest:
            raise ValueError(f"Preserved upstream resource changed: {rel}")
    return {"skills": 13, "cli_tools": 6, "hooks": 26, "rubric_points": 100}


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    try:
        print(json.dumps({"status": "PASS", **validate()}, indent=2))
    except (OSError, ValueError, KeyError, SyntaxError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)

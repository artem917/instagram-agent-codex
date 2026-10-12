"""Copy the complete pack to a chosen project's .agents/skills. Never global."""
import argparse
import os
from pathlib import Path
import shutil
import sys

from validate import ROOT, SKILLS, validate


def contents(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def install(project, dry_run=False):
    validate()
    project = Path(os.path.expandvars(os.path.expanduser(str(project)))).resolve()
    if not project.is_dir():
        raise ValueError("--project must be an existing project directory")
    target = (project / ".agents/skills").resolve()
    if not target.is_relative_to(project):
        raise ValueError(".agents/skills resolves outside the selected project")
    pending = []
    # Preflight every folder before copying any. Never replace existing skills.
    for name in SKILLS:
        source, dest = ROOT / "skills" / name, target / name
        if dest.is_symlink():
            raise ValueError(f"Refusing an existing symlink: {dest}")
        if dest.exists():
            if not dest.is_dir() or contents(dest) != contents(source):
                raise ValueError(f"Different skill already exists at {dest}; choose another project or reconcile it manually")
        else:
            pending.append((source, dest))
    if not dry_run:
        for source, dest in pending:
            shutil.copytree(source, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return target, len(pending)


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="existing project directory")
    parser.add_argument("--dry-run", action="store_true", help="validate and show the target without copying")
    args = parser.parse_args()
    target, count = install(args.project, args.dry_run)
    print(f"{'Would install' if args.dry_run else 'Installed'} {count} new folders; 13 skills available at {target}")
    print("Open Codex in the chosen project and use $ig-reel (or /skills to inspect discovery).")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, SyntaxError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)

"""UTF-8 CLI I/O shared by the tools in this skill (standard library only)."""
import os
from pathlib import Path
import sys


def resolve_path(value):
    return Path(os.path.expandvars(os.path.expanduser(str(value))))


def configure_stdio():
    for name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, name)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="strict")


def read_text(value):
    if str(value) == "-":
        return sys.stdin.read().removeprefix("\ufeff")
    return resolve_path(value).read_text(encoding="utf-8-sig")


def write_text(value, text):
    path = resolve_path(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def cli(main):
    configure_stdio()
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from None

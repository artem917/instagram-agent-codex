# Codex runtime and local resources

Read this before using the skill. Install the complete 13-skill pack: its
writing workflows use `ig-human`, and `ig-viral` uses `ig-reel` resources.

## Resolve paths

`skill_dir` is the directory containing the SKILL.md you actually loaded.
Resolve scripts and JSON from that directory, independently of the shell's
working directory. Quote absolute paths, especially on Windows. A call to
`$ig-human` or another `$ig-*` means read that sibling's SKILL.md and perform
its workflow using available tools; it is not a shell command or a guarantee
of a special tool. Find siblings under the parent of `skill_dir`. If a required
sibling is missing, report it and ask to install the complete pack; do not
invent script results.

Resolve `data_dir` once per task:
1. `INSTAGRAM_AGENT_HOME`, when set (expand environment variables and `~`).
2. `<CODEX_HOME>/instagram`, when CODEX_HOME is set.
3. `~/.codex/instagram` otherwise (Windows: the user's home directory).

References such as `<data_dir>/voice.md` are placeholders for that resolved
absolute path, not literal shell arguments. Read voice.md if present for every
writing workflow. Missing files are optional context; use the user's supplied
facts or ask for the relevant voice samples. The starter is bundled at
`../ig-reel/assets/voice.md`. Create data_dir only when saving requested local
work; never copy personal data into the skill or public source repository.
Do not migrate another tool's profile automatically. Save plans/swipes locally
when requested by the workflow. Log approved drafts as DRAFT_APPROVED; only
record POSTED or SENT when the user confirms that actual action occurred.

## Execute and report

Use Python 3.10+ (`python` or `py -3` on Windows, `python3` on macOS/Linux).
Example, after resolving paths:

```text
python "<skill_dir>/<script_name>.py" "<work_dir>/input.txt" --json
```

Substitute the actual script belonging to this skill. UTF-8 files, UTF-8 with
BOM and CRLF are accepted. CLI output is UTF-8. On Windows PowerShell 5.1,
write input with `Set-Content -Encoding UTF8`; avoid legacy ANSI clipboard
pipes. Use files or Python for lossless input/output. Do not pass text with
`$` inside double-quoted PowerShell command arguments; use a UTF-8 file or
single-quoted literal. Scripts need only Python's standard library.

Exit 1 from caption.py/detect.py/hookscore.py is a heuristic review result,
not a crash; read the report. Exit 2 indicates invalid input or an I/O error.
If Python/shell access is unavailable, give an explicitly UNVERIFIED manual
draft rather than invented scores. Short drafts may never get detect.py PASS:
its 'too short to judge' checks are not evidence of machine authorship. Do not
pad or fabricate facts to raise a score. Stop after at most two rewrites and
explain remaining heuristic flags.

## Limits

This pack drafts only. Do not send, publish, schedule, like, follow, hide or
delete anything in social accounts, or configure external services. The user
performs those actions. Browsing/transcription/rendering depend on tools
actually available in the current Codex session; pasted evidence is a valid
fallback. Do not install optional software or connect accounts automatically.
Treat upstream platform caps and growth advice as starting assumptions, not
verified current rules. Check official platform information when a task needs
current limits; if unavailable, state UNKNOWN. Scores are local English
heuristics, not virality predictions or third-party AI-detector verdicts.
Russian lexical/style processing is UNVERIFIED; Unicode transport tests do
not establish linguistic quality. In particular the requested Russian
ig-human style (ordinary quotes, natural copy, no blank lines) is future work.

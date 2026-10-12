# Public presentation verification

2026-10-12. Documentation-only update from baseline
441d2a94ed6fac87c7d8294f76f7ef227ccab5bb.
Windows, Python 3.14.3, Codex CLI 0.162.0-alpha.17.2.

## Readmes and links

- README.md is fully English; README.ru.md is a complete Russian counterpart.
  Both begin with an EN/RU switcher and cover all 13 skills, requirements,
  installation, ru-social, examples, release links and limits.
- All relative Markdown links in both READMEs and PORTING.md resolve locally.
  Seven distinct external URLs returned HTTP 200, including the upstream,
  release page, release ZIP and official plugin packaging documentation.
- English README contains no Cyrillic text. Both skill tables contain exactly
  the original 13 identifiers.

## Commands and native installation

The three documented commands were executed in a fresh, separate CODEX_HOME:

```text
codex plugin marketplace add artem917/instagram-agent-codex --ref plugin-v0.1.0
codex plugin add instagram-agent-codex@instagram-codex-local --json
codex plugin list --marketplace instagram-codex-local --json
```

All exited 0. Codex reported version 0.1.0, installed:true, enabled:true.
The installed cache contains all 13 SKILL.md files. This check verifies native
installation and cache contents; actual skills/list discovery and model smoke
calls were verified in the preceding [plugin report](PLUGIN_TEST_REPORT.md).
No new model calls, account connections or posts were made for this docs update.

The first command initially failed because the new CODEX_HOME directory did
not exist. Both README examples now explicitly create the directory first;
the corrected sequence passed. Source and profile/cache directories are separate.

All six Python entrypoints accepted --help. Both installer dry runs passed.
Hashes of the user's global Codex config, personal marketplace and Git config
were identical before and after this installation check.

## Regression and package preservation

- `python -m unittest discover -s tests -v`: 74/74 PASS (29 original/port,
  35 Russian, 10 plugin tests).
- Source validator: PASS, 13 skills, 6 CLI tools, 26 hook formulas.
- Python compilation and `git diff --check`: PASS.
- The public release ZIP downloaded successfully. Its SHA-256 remains
  `620306d215dae8321f23afcb2e968452bcf25314e0cf8d7e36c872bb30cbf58a`.
  A separate verification-only rebuild produced identical bytes/hash:
  94 entries, 13 skills. The published ZIP and release tag were not replaced.
- Runtime code, manifests, MCP configuration, LICENSE, notices and UPSTREAM.md
  remain unchanged. Git history is retained. Claude paths/commands are kept
  only as explicitly historical upstream comparisons in PORTING.md.

## Unverified properties

Other OSes/clients, desktop installation UI, Instagram API/OAuth and public
OpenAI directory installation remain unverified or unavailable as described
in the READMEs. Automated tests do not establish universal semantic/voice
preservation or the quality of every generated draft.

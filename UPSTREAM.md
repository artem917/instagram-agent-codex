# Upstream and attribution

This repository adapts Jake Schincariol's Claude Code Instagram Agent Skill
pack for OpenAI Codex. The original creative workflows, hook formulas,
lexicon, profile rubric and core scoring algorithms remain credited to Jake.

- Upstream: https://github.com/Jakeschincariol/instagram-agent-skill
- Pinned commit: `d03c56bb598be770c60b201f94237e5d1a4268a6`
- Inspected/ported: 2026-10-12
- Original notice: `Copyright (c) 2026 Jake Schincariol`
- License: MIT; the complete original LICENSE is retained unchanged.
- Codex adaptation and new validation/installation code: artem917 (2026), MIT.

The original history is retained in this repository. All 13 skill names and
their creative workflows remain. The three JSON resources are unchanged;
UPSTREAM.json records the pinned source and SHA-256 values normalized to LF.
LICENSE and NOTICE.md travel inside every installable skill directory, so
copying the pack retains the original copyright and MIT terms.

Substantial adaptations:

1. Codex discovery/install into a selected project's `.agents/skills`, `$ig-*`
   invocation, optional `agents/openai.yaml` UI metadata and relative resource
   resolution rather than Claude command/plugin assumptions.
2. Explicit configurable local data directory and a bundled voice template;
   approved drafts are distinguished from confirmed published/sent material.
3. Portable UTF-8 CLI streams, BOM/CRLF and quoted paths; output directory and
   relative output handling; clear invalid input errors.
4. Consistent text/JSON review exit codes; input validation for beat timing and
   exact TSV counts; zero-view rows retained and mixed baselines labelled.
5. Actual local regressions and Codex smoke evidence, with external browser,
   transcription, image-export and Russian-language limitations stated.

Claude marketplace/plugin manifests are removed from the active port. No
OpenAI marketplace submission, social account integration, API keys or automatic
publishing is included. Upstream historical benchmark claims are attributed
to upstream, not new independently reproduced findings.

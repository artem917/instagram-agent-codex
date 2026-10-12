# INSTAGRAM_CODEX_PLUGIN_V0 — observed results

2026-10-12. Baseline 8548381e87b85666281bf3edd3470e84d4ac3044.
Runtime: Windows, Python 3.14.3, Codex CLI 0.162.0-alpha.17.2.

## Package and installation

Portable Agent Plugins 1.0 root manifest and empty MCP component passed the
official schemas fetched from agent-plugins.org (test-only jsonschema validator,
outside runtime dependencies). A supported Codex compatibility overlay is
included; a separate native installation **without** that overlay also passed.
English metadata and Russian translation/description copy are prepared.

Native marketplace add, plugin add and plugin list completed with exit 0 in
separate CODEX_HOME directories. list reports installed:true, enabled:true,
version 0.1.0. Native Codex app-server skills/list reports all 13 skills enabled,
each with pluginId instagram-agent-codex@instagram-codex-local and a path in
the installed cache, using names instagram-agent-codex:ig-*.
This is actual runtime discovery, not merely counting source folders.

The final scripts/install_plugin.py helper was also executed, and native Codex
confirmed its isolated-profile installation. It never copies authentication or
changes the user's global home. The existing scripts/install.py is unchanged.
No individual skill folders are manually installed for these tests.

## Automated checks

- All 64 previous tests pass, including English/Russian preservation/regression.
- Ten plugin tests pass: deterministic ZIP bytes, all 13 skills/resources and
  MIT notices, inventory hashes, corrupt/traversal/runtime-file rejection,
  manifest/path/empty-MCP checks, clean-snapshot conflicts, dry run, global-home
  refusal and refusal of source/cache overlap. Combined: **74/74 PASS**.
- Source validation, Python compilation and whitespace checks pass.
- ZIP uses one top-level plugin folder, includes all 13 skills exactly once,
  has per-file SHA-256 inventory and is reproducible in the tested runtime.
  No .git, test-home/auth, profiles, logs, caches or private output are included.
- Portable root and compatibility identity/interface/onboarding are consistent.
  All Python helpers remain standard-library-only; schemas are validation-only.

## Real skill calls through the installed plugin

The model was explicitly gpt-6.1-sol/high. The workspace was outside the source
repository, with no .agents/skills copy or ancestor repo marketplace. Only the
isolated profile's enabled plugin was used. Cached scripts and actual JSON
outputs were inspected. Global config hashes before/after all runs match.

| Call | Actual result |
| --- | --- |
| instagram-agent-codex:ig-human, ru-social | Source REVIEW; final CLEAN/exit 0. Protected-data comparison passed, including names, articles, numbers, negation, URL and family ZWJ emoji. |
| instagram-agent-codex:ig-caption | English Job A caption: READY/exit 0, 107 visible characters, one ask, no hashtags. ig-human REVIEW for short text was retained honestly. |
| instagram-agent-codex:ig-reel | Three actual hook scores 62.6/50.6/34.2; final four-beat script 9.09s at 165 wpm. Timing/cleanup execute; English detector FLAGGED 48.4/exit 1, so editorial review remains necessary. No quality PASS is asserted. |
| instagram-agent-codex:ig-plan onboarding | Saved a synthetic voice profile in the selected data/onboarding folder, preserved the existing voice profile, ran six actual ru-social checks with CLEAN/exit 0, and created no weekly schedule/account connection. |

All four Codex processes completed with exit 0. Nested heuristic exit 1 is
not an execution failure. The caption run initially combined humanize --json
with --out, which leaves stdout-only JSON and no text file; the agent saved
the returned text and successfully reran detection. That recovery is retained
in local evidence rather than hidden.

Sanitized evidence is in tests/fixtures/plugin-smoke.json. Raw events, private
paths and the private test authentication copy stay outside the published tree.

## Failed attempts and limits

The first local-source test put its cache inside the source root; native copying
timed out after 90s. Subsequent sources are clean snapshots and caches are
separate; the installer now refuses overlap. A policy-blocked cleanup left that
failed temporary directory ignored/excluded. It is not shipped in the ZIP/Git.

A project marketplace plus project enabled setting did not yield automatic
discovery in the tested client (0 plugin skills). That unverified activation
path was removed from the additional installer/documented promises; native add
in an explicit profile is the verified method. Repo catalogs remain valid
discovery inputs, not universal activation guarantees.

Native macOS/Linux, other Codex versions, desktop Setup-button rendering,
locale-specific card presentation and reinstall/update behavior in other
clients remain UNVERIFIED. The CLI onboarding workflow and metadata path were
tested; no desktop screenshot or click is fabricated.

Instagram OAuth, token exchange, account/API eligibility, App Review, exact
current quotas/formats, live publishing and current owner-specific regional
acceptance are not tested. MCP server count is zero. The proposal/research in
docs/INSTAGRAM_MCP_PLAN.md distinguishes confirmed sources, expectations and
unavailable Meta documentation. No account was connected, post sent, paid
server deployed or OpenAI moderation/submission initiated.

MIT and Jake Schincariol attribution are unchanged. The native plugin release
does not establish the quality of every generated draft or future API access.

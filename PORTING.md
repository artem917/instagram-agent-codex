# Compatibility review

**Historical initial-port report, not current installation instructions.**
The standalone baseline described here predates the V0.1.0 Codex plugin and
the Russian editor. For current installation and capabilities, see
[README.md](README.md), [README.ru.md](README.ru.md) and
[PLUGIN_TEST_REPORT.md](PLUGIN_TEST_REPORT.md). Claude commands/paths in the
comparison below describe the original upstream, not commands to run in Codex.

Initial port review at baseline 3f83e07. IG_HUMAN_RU_V1 subsequently adds
shared ru/ru-social editing and an emoji preservation fix; see
[RU_TEST_REPORT.md](RU_TEST_REPORT.md) and [RU workflow](skills/ig-human/references/ru.md).
Russian UNVERIFIED statements below describe that initial port. General
semantic/voice quality still requires contextual review.

Source reviewed: the README, all 13 SKILL.md files, all six Python tools,
hooks.json, slop.json, rubric.json, voice.md, .gitignore, MIT LICENSE and both
Claude plugin manifests at the commit in UPSTREAM.md. No requirements file,
package installer or non-stdlib Python imports existed upstream. The README's
"five tools" section actually includes six executable Python entry points.

Codex/Agent Skills requirements checked on 2026-10-12:
[official Codex Skills](https://learn.chatgpt.com/docs/build-skills) and
[Agent Skills specification](https://agentskills.io/specification).
Each skill keeps name/description frontmatter, a matching folder name, short
entrypoint instructions and bundled relative resources. Names meet the
lowercase/hyphen rules; descriptions stay below 1024 characters. Requirements
stay in the runtime reference rather than the optional `compatibility` field:
Agent Skills permits it, but the installed Codex quick validator rejected it.
The final manifests pass that stricter validator as well. No
Claude-specific allowed-tools permission syntax or hidden system instruction
was found in the source. The workflows themselves are Markdown instructions.

## Dependencies and behavior changes

| Historical Claude/upstream dependency | Initial standalone port at 3f83e07 |
| --- | --- |
| `~/.claude/skills`, project `.claude/skills` | Installer copies to the chosen project's `.agents/skills`; no global install is performed. |
| `/ig-*` Claude slash commands | `$ig-*` Codex skill mentions; sibling calls mean load SKILL.md and execute its workflow. |
| `.claude-plugin/{marketplace,plugin}.json`, `/plugin` | Removed in the initial standalone port. V0.1.0 subsequently adds native Codex plugin packaging; OpenAI catalog publication remains outside this release. |
| `~/.claude/instagram/{voice,swipe,plan,log}.md` | INSTAGRAM_AGENT_HOME, then CODEX_HOME/instagram, then ~/.codex/instagram. No automatic migration. |
| `python3`, `cp -r`, shell line continuations, `pbpaste` | Python project installer and quoted absolute script paths; Windows uses python/py. Mac clipboard examples are marked optional. |
| `hookscore.py`, `beats.py`, etc. as cwd-relative commands | Instructions resolve from the loaded skill's path. JSON resources still resolve from `__file__`. |
| `ig-viral` imports sibling hookscore and reads hooks.json | Retained and tested after installation. Full pack required; standalone missing dependencies produce explicit notes, not invented scores. |
| `ig-human` is used by writing workflows | Retained; sibling instructions loaded directly when no special invocation tool exists. |
| Windows default stdin/stdout encoding, UTF-8 BOM | Explicit UTF-8 CLI streams, utf-8-sig file input, universal newline handling. Invalid encodings fail clearly. |
| Relative `swipe.py --out swipe.md` crashes on empty dirname | Output Path parent creation now handles both relative files and nested directories. |
| detect/hookscore JSON returned success despite review | JSON and text now use the same documented verdict exit codes. hookscore success requires an actual STRONG verdict. |
| TSV `1.2M` silently becomes `12`, zero views skipped | Exact non-negative integer counts required; shorthand errors clearly. Zero views are retained. Mixed/follower/unknown baselines are labelled. |
| Non-positive/NaN timing inputs | Rejected by CLI before calculation. Caption truncation must be positive. |
| `ig-carousel` suggests print-to-PDF as image export | HTML stays supported; PDF is only a review artifact. PNG/JPEG requires a real image renderer and dimension/visual checks. |
| Local draft approvals treated as post/comment log | DRAFT_APPROVED and confirmed POSTED/SENT are distinct. |
| `ig-human` score loops on short drafts | REVIEW may be correct; stop after at most two rewrites and never invent facts to raise scores. |

Original scoring functions are unchanged. A fixed synthetic fixture was
generated from the pinned original source; tests compare the complete result
structures for hookscore, beats, caption, humanize and detect. swipe ranking
has the deliberately documented input/baseline corrections above. The I/O
helper is repeated in the four tool-bearing folders so scripts are usable
after copying the pack without repository-level imports.

## Per-skill review

| Skill | Preserved resources/workflow | Session-dependent capability |
| --- | --- | --- |
| ig-reel | 26 hooks, hookscore.py, beats.py, voice template, humanization | Footage/transcription supplied by user or available tool; final text is retimed. |
| ig-viral | swipe.py, sibling formula classifier/scorer | Manual/pasted research; browser optional; yt-dlp example optional and UNVERIFIED. |
| ig-caption | caption.py, preview, single ask, keywords | Current platform constraints must be verified separately. |
| ig-carousel | Slide copy, HTML sizing, caption/humanization | PNG/JPEG export UNVERIFIED without a supplied renderer. |
| ig-story | Frame sequence, sticker guidance, reply drafts | User applies stickers/sends replies manually. |
| ig-profile | Original 12-item/100-point rubric | Supplied screenshots/text; proposed rescore labelled hypothetical. |
| ig-plan | Weekly formats/angles, voice, swipe/log, local plan | No scheduler/account actions. |
| ig-human | humanize.py, detect.py, original lexicon | English heuristics; Russian language processing UNVERIFIED. |
| ig-comment | Nine comment types, batch drafts | Supplied post evidence; user sends manually. |
| ig-reply | Six-bucket triage and reply/Reel handoff | Supplied comments; no scraping/moderation actions. |
| ig-dm | Delivery/warm/collab drafts and two follow-ups | No sending, automation configuration or external partner connection. |
| ig-repurpose | Extraction and one-at-a-time drafting | Text supplied; transcription/editing optional and UNVERIFIED. |
| ig-audit | Outlier/hold/sends/follows calculations and handoffs | User-supplied Insights; no live account analytics connection. |

## Verification boundaries at the initial baseline

The following paragraph records the original 3f83e07 limitations. The later
Russian adaptation and emoji-preservation fix are tested in
[RU_TEST_REPORT.md](RU_TEST_REPORT.md); current plugin boundaries are recorded
in [PLUGIN_TEST_REPORT.md](PLUGIN_TEST_REPORT.md).

The pack is usable with a local Codex shell and supplied text without external
services. Browsing, transcription, actual editing, image export, platform
behavior and third-party detector results are not established by local tests.
Unicode character cleaning can alter emoji joiners and non-English formatting;
review outputs. Russian ig-human adaptation (ordinary quotation marks, natural
publication style and no blank lines) remains a separate future task. Tests
do not certify that adaptation or every possible content-generation behavior.

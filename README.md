**[EN](README.md) | [RU](README.ru.md)**

# Instagram Agent for Codex

13 content creation skills in one locally installable Codex plugin. Turn your facts, drafts and supplied metrics into Reel scripts, captions, carousels, Stories, plans and replies. Includes local Python tools and English/Russian text editing, with a shared `ru-social` mode for social networks.

Independent MIT adaptation of [Instagram Agent Skill](https://github.com/Jakeschincariol/instagram-agent-skill) by **Jake Schincariol**. Maintained for Codex by [artem917](https://github.com/artem917). This is a drafting toolkit: you review and publish the results yourself.

**Current release: [plugin-v0.1.0](https://github.com/artem917/instagram-agent-codex/releases/tag/plugin-v0.1.0) (GitHub prerelease).** [Download the plugin ZIP](https://github.com/artem917/instagram-agent-codex/releases/download/plugin-v0.1.0/instagram-agent-codex-0.1.0.zip). It has not been submitted to or published in OpenAI's public plugin directory. No Instagram account connection, OAuth, API integration or automatic posting is included.

## Install the whole plugin

Requirements:

- A Codex client with native plugin support and a configured sign-in/model for interactive use.
- Python 3 for the bundled tools; they use only the standard library. Tested with Python 3.14.3 on Windows.
- Git and network access for the GitHub marketplace installation. Instagram credentials are unnecessary.

The commands below were tested with **Codex CLI 0.162.0-alpha.17.2**. Other versions may expose a different installation interface. See the [official OpenAI plugin packaging guide](https://developers.openai.com/plugins/build/plugins) for the current marketplace format.

Run in your terminal to install all 13 skills at the fixed V0.1.0 tag:

```text
codex plugin marketplace add artem917/instagram-agent-codex --ref plugin-v0.1.0
codex plugin add instagram-agent-codex@instagram-codex-local --json
codex plugin list --marketplace instagram-codex-local --json
```

The list should report the plugin as installed and enabled, version `0.1.0`. These commands use the current Codex profile. Start a new Codex session after installation. Individual skill folders do not need to be copied.

### Use a separate Codex profile

To keep installation settings separate, set `CODEX_HOME` for the current terminal **before** running the three installation commands above. Choose a fresh directory outside the plugin source tree.

PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path 'C:\codex-profiles\instagram-test' | Out-Null
$env:CODEX_HOME = 'C:\codex-profiles\instagram-test'
```

macOS/Linux shell:

```sh
mkdir -p "$HOME/codex-profiles/instagram-test"
export CODEX_HOME="$HOME/codex-profiles/instagram-test"
```

Launch `codex` from that same terminal and sign in normally if the separate profile needs authentication. Keep using that `CODEX_HOME` in future sessions for this installation. These examples set a process environment variable, not a permanent system setting. Native installation has been verified on Windows; macOS/Linux installation remains unverified.

Alternatively, from a source checkout, the helper creates a clean package and runs native installation into an explicitly separate profile:

```text
python scripts/install_plugin.py --codex-home /path/to/isolated-profile --dry-run
python scripts/install_plugin.py --codex-home /path/to/isolated-profile
```

Replace the path with your actual directory. The helper refuses the default global Codex home and overlapping source/cache directories. It does not copy authentication. Use the same `CODEX_HOME` when launching Codex afterward. Details: [plugin installation guide](PLUGIN.md).

For an installation from the release ZIP, extract it and pass the full path of its `instagram-agent-codex` directory to `codex plugin marketplace add`, then run the same `plugin add` and `plugin list` commands. Keep the extracted source outside the profile/cache directory.

## First run and examples

Enter these as **messages in Codex**, not shell commands. Installed plugin skill names use the `instagram-agent-codex:` prefix.

```text
$instagram-agent-codex:ig-plan Help me get started. Use English. Ask for my topic and voice examples, then draft one caption from facts I supply.

$instagram-agent-codex:ig-caption Draft a caption for this photo from the supplied facts. Give me two opening options and explain the preview.

$instagram-agent-codex:ig-reel Turn these notes into a 20-second Reel. Give me three hooks, run the hook scorer and time the final script.

$instagram-agent-codex:ig-human Edit the text below in ru-social mode. Preserve facts, names, numbers, negations, links and emoji. Do not add a CTA, question or hashtags.
```

Supply the actual text, notes or metrics with your request. Onboarding uses `ig-plan`; there is no additional fourteenth skill. It helps choose a language and local data folder, can save a voice profile when requested, and runs a small first task. It does not connect an account or schedule posts.

## The 13 skills

Each short name below refers to an installed `$instagram-agent-codex:ig-*` skill.

| Skill | What it helps you produce |
| --- | --- |
| [ig-reel](skills/ig-reel/SKILL.md) | Reel scripts, three hook options from 26 formulas, local hook scoring and beat timing. |
| [ig-viral](skills/ig-viral/SKILL.md) | A swipe file from supplied Reel data, with account-median outlier ranking and hook analysis. |
| [ig-caption](skills/ig-caption/SKILL.md) | Caption drafts, opening alternatives, an approximate 125-character preview and lint checks. |
| [ig-carousel](skills/ig-carousel/SKILL.md) | Slide copy and HTML layouts for carousels; image export needs a separate renderer. |
| [ig-story](skills/ig-story/SKILL.md) | Story sequences, sticker suggestions and reply drafts. |
| [ig-profile](skills/ig-profile/SKILL.md) | A profile review using a 12-part, 100-point rubric on supplied material. |
| [ig-plan](skills/ig-plan/SKILL.md) | First-run onboarding and weekly content planning from your goals and facts. |
| [ig-human](skills/ig-human/SKILL.md) | English/Russian normalization, style analysis and contextual rewrite recommendations. |
| [ig-comment](skills/ig-comment/SKILL.md) | Comment drafts for posts you provide. |
| [ig-reply](skills/ig-reply/SKILL.md) | Triage of supplied comments and suggested replies. |
| [ig-dm](skills/ig-dm/SKILL.md) | DM and collaboration drafts, with up to two follow-up drafts. |
| [ig-repurpose](skills/ig-repurpose/SKILL.md) | New content angles and drafts from a supplied longer text. |
| [ig-audit](skills/ig-audit/SKILL.md) | Content-performance analysis from metrics you provide. |

Comments, replies and DMs are drafts; the plugin does not send them. Research and audits use supplied evidence. Browsing and transcription depend on tools actually available in your session.

## English and Russian editing

`ig-human` offers three modes through one shared Russian engine:

| Mode | Behavior |
| --- | --- |
| `en` | Default English workflow with regression coverage against the pinned upstream baseline. |
| `ru` | Natural grammatical Russian; literary typography is allowed. |
| `ru-social` | Conversational Russian for Instagram, VK, Telegram, Threads and other social networks. Straight double quotes, no em dash, no blank separator lines, natural paragraphs and varied rhythm. |

Russian workflows avoid formulaic introductions, empty conclusions, bureaucratic language and forced politeness. They do not require an ending question, CTA or hashtags, invent personal experience, or imitate spelling mistakes. Platform length/hashtag limits are optional settings, not separate language engines.

Character normalization, style detection and semantic recommendations are separate. Automatic wording changes are deliberately conservative. Ambiguous punctuation or a protected-data conflict returns `NEEDS_REWRITE` rather than silently changing the meaning. The tools check recognized names, identifiers, numbers, URLs, negations and emoji sequences, including ZWJ; full meaning and author voice still need contextual review. Use `--preserve` for additional exact literals.

See the [Russian workflow](skills/ig-human/references/ru.md) and [Russian test report](RU_TEST_REPORT.md), including false positives and unverified properties. These are editorial heuristics, not proof of AI authorship or a watermark-removal service.

## Local Python commands

From a **source checkout**, use the following commands with your own UTF-8 input files. For an installed plugin, Codex resolves scripts from the loaded skill's cache path; do not assume that the checkout or `.agents/skills` exists there.

```text
python skills/ig-human/humanize.py draft.txt --mode ru-social --report
python skills/ig-human/detect.py draft.txt --mode ru-social --json
python skills/ig-reel/hookscore.py hooks.txt --json
python skills/ig-reel/beats.py script.txt --target 20 --json
python skills/ig-caption/caption.py caption.txt --json
python skills/ig-viral/swipe.py reels.tsv --out swipe.md --json
```

The six tools accept files or stdin (`-`), and `--help` describes their options. UTF-8 BOM, CRLF and paths with spaces/Cyrillic are covered by tests. Quote file paths containing spaces. `swipe.py` expects TSV data; see the [research workflow](skills/ig-viral/SKILL.md) for its fields.

Russian normalization exits `0` for `CLEAN`, `1` for `REVIEW` and `3` for `NEEDS_REWRITE`; invalid CLI arguments exit `2`. For `NEEDS_REWRITE`, JSON contains `text: null` and a review candidate; no cleaned text file is written. With `--json`, normalization returns JSON on stdout rather than writing `--out`. Read each tool's verdict: a successful execution does not certify editorial quality. Original English hook/caption scores and thresholds are not Russian quality metrics.

## Local data and existing installations

Optional voice profiles, swipe files and plans use this directory order: `INSTAGRAM_AGENT_HOME`, then `CODEX_HOME/instagram`, then `~/.codex/instagram`. Choose a project-local directory during onboarding if preferred. A [voice.md template](templates/voice.md) is available for your own facts and writing samples. Keep personal data out of the installed plugin cache. Local Python tools do not send drafts to a service; Codex requests use your configured model/service.

The earlier project-scoped skill installer remains supported. From a source checkout:

```text
python scripts/install.py --project /path/to/existing-project --dry-run
python scripts/install.py --project /path/to/existing-project
```

It installs all 13 folders into the selected project's `.agents/skills`, uses unprefixed mentions such as `$ig-reel`, and does not alter global settings. It refuses to overwrite differing existing files. Choose either plugin or standalone installation to avoid duplicate skill entries; both preserve the same workflows.

## What changed from the Claude original?

The original creative methods and 13 skill identities are retained. This port adds native Codex plugin packaging, namespaced invocation, onboarding, a project-scoped legacy installer, Windows/UTF-8 CLI fixes, explicit review verdicts, and a shared Russian editor with a lexicon and preservation tests. It uses portable Agent Plugins 1.0 plus a Codex compatibility manifest; V0 registers zero MCP servers.

[UPSTREAM.md](UPSTREAM.md) records the original commit, authorship and changes. [PORTING.md](PORTING.md) is the historical initial-port review; it is not the current installation guide.

## Tests and release evidence

From the source checkout:

```text
python scripts/validate.py
python -m unittest discover -s tests -v
python -m compileall -q skills scripts tests
git diff --check
```

The existing suite has **74 tests**: 29 original regression/port tests, 35 Russian tests and 10 plugin tests. The Russian corpus contains 64 labelled examples. [Plugin verification](PLUGIN_TEST_REPORT.md) records actual isolated Codex discovery of all 13 skills, calls to `ig-human` (`ru-social`), `ig-caption`, `ig-reel` and onboarding, and honest heuristic review results. [Initial port tests](TEST_REPORT.md) and [Russian tests](RU_TEST_REPORT.md) document their respective boundaries.

[Public presentation verification](PRESENTATION_TEST_REPORT.md) records the latest documentation checks, installation from the release tag in a fresh profile, passing regression suite and unchanged release hash.

The V0.1.0 release ZIP includes all skills, Python resources and MIT notices. Its SHA-256 is `620306d215dae8321f23afcb2e968452bcf25314e0cf8d7e36c872bb30cbf58a`. The published ZIP remains the original V0.1.0 artifact; its bundled guide is [PLUGIN.md](PLUGIN.md). These public READMEs can evolve without changing that release.

## Real limitations

- No Instagram API, OAuth, connected accounts, live Insights, automatic posting, message delivery or scheduler. [Future Instagram MCP research](docs/INSTAGRAM_MCP_PLAN.md) is a proposal, not a working integration.
- No OpenAI directory publication, submission or endorsement. Installation is through this repository/local marketplace.
- Scores are heuristics; short texts, humor and unusual structures can need review. No promise of virality, AI-authorship detection, watermark removal or universal grammar/meaning preservation.
- Carousel PNG/JPEG export needs a real renderer and visual checks. Footage editing, transcription and browsing are optional external capabilities, not bundled services.
- Native installation on other OSes/clients, desktop setup UI and future platform limits are unverified. Codex access and model usage follow your own account configuration.

## License and attribution

[MIT License](LICENSE), copyright **2026 Jake Schincariol**. Upstream attribution and per-skill license/notices are retained. This independent Codex adaptation does not imply endorsement by the upstream author, OpenAI or Meta. See [UPSTREAM.md](UPSTREAM.md) for provenance.

# First-version test report

Date: 2026-10-12. All content inputs are synthetic. No Instagram account was
connected, modified or contacted. No social actions or external integrations
were tested or performed.

## Local checks: PASS

Environment: Windows, Python 3.14.3, PowerShell, Codex CLI
`0.162.0-alpha.17.2`. Lower Python versions and native macOS/Linux runs are
UNVERIFIED; code uses standard-library APIs available from Python 3.10.

| Check | Observed result |
| --- | --- |
| Pack validator | PASS: 13 skills, 6 CLI tools, 26 hook formulas, 12-item/100-point profile rubric. |
| Bundled Codex skill-creator quick_validate.py | 13/13 valid. PyYAML used only in an ignored, project-local validator directory; no runtime dependency added. |
| UI YAML parsing | 13/13 agents/openai.yaml files parsed with PyYAML. |
| Syntax compilation | `python -m compileall -q skills scripts tests`: exit 0. |
| Regression suite | `python -m unittest discover -s tests -v`: **29 tests passed**. |
| Source whitespace | `git diff --check`: no findings. |
| Original resource preservation | LICENSE and three JSON resources match recorded upstream SHA-256 values after LF normalization. |

The regressions cover complete installation in a directory with spaces and
Cyrillic, all sibling files/JSON/templates/license notices, installed swipe
classification/scoring, idempotence, conflict preflight, dry run, missing
project, and UTF-8 installer stdout. All six tools were executed on small
examples and stdin, with JSON parsing and actual exit-code checks.

I/O cases include UTF-8 BOM, CRLF, Cyrillic filenames/text transport, a forced
legacy stdout setting, environment/tilde expansion, relative swipe output,
nested output directory creation, custom lexicon input, missing files,
malformed JSON, empty input and invalid numeric options. Scoring/algorithm
tests include exact beat timing, caption truncation/length/hashtag/keyword
checks, typography/invisible cleanup with URL preservation, short-text REVIEW,
swipe ranking with zero views, mixed baselines and rejected abbreviated counts.

A fixed fixture in tests/fixtures/upstream-results.json was generated from
the pinned upstream source using the synthetic examples. Complete outputs
match the port's hookscore, beats, caption, humanize and detect functions.
This checks preservation, not real-world predictive power. Upstream's
historical 74-hook benchmark and third-party detector results were not rerun.

## Real Codex smoke runs

Installed all 13 skills through scripts/install.py into an isolated local
project. Ran Codex CLI with `gpt-6.1-sol`, high reasoning and synthetic local
voice/data. Skills were discovered at `.agents/skills`, their SKILL.md/runtime
references were read, and bundled scripts were executed through resolved paths.
Actual text and CLI JSON reports were saved and inspected locally.
Sanitized observed artifacts are included in
[tests/fixtures/codex-smoke.json](tests/fixtures/codex-smoke.json); private
absolute paths and raw event logs are not included.

| Case | Actual scripts | Observed result |
| --- | --- | --- |
| ig-caption + ig-human | caption.py, humanize.py, detect.py | 106-character Job A caption; caption READY/exit 0. Humanizer had no cleanup flags. Detector REVIEW 62.0/exit 1, with short-text checks inconclusive. Stopped after two rewrites. |
| ig-viral | swipe.py with sibling ig-reel formulas and scorer | 3 synthetic accounts/rows ordered 60.0x, 40.0x, 0.0x. Formula IDs 9, 3, null; hook scores 57.2, 87.0, 9.6. CLI exit 0, Markdown and JSON files exist. No real niche inference claimed. |
| ig-reel + ig-human | hookscore.py, beats.py, humanize.py, detect.py | Three actual hook scores: 80.8 STRONG, 62.6 OK, 77.8 STRONG. Final script 21 words / 7.64s at 165 wpm, retimed after cleanup. Under the 15s target, delivered short using only supplied facts. Detector REVIEW 62.0, reported honestly. |

The first workspace-write caption attempt was blocked by the local CLI's
execution policy, including reads. It produced no script results and was
UNVERIFIED. Subsequent bounded synthetic runs used a CLI session mode that
allowed local tool execution; the user's global settings were not changed.
Raw session events, private absolute paths and temporary output logs are kept
only under ignored `.test-work/`, outside the published tree.

These are three workflow smoke tests, exercising four named skills and all
six original Python entry points across the combined tests. The other nine
skills were inspected and statically validated, with resources preserved;
their end-to-end content workflows were not individually executed.

## UNVERIFIED and out of scope

- Live Instagram browsing, authenticated analytics, current platform caps and
  niche research conclusions.
- YouTube yt-dlp examples, media transcription, video cutting and real media
  quality; none of those optional tools was installed for this pack.
- Carousel PNG/JPEG export, renderer availability and visual quality. HTML
  instructions are preserved; a PDF is not claimed as an image upload.
- Russian lexical/style handling, Russian caption CTA/hashtags/tokenization,
  and the requested ordinary-quotes/no-blank-lines ig-human adaptation.
- Virality predictions, third-party AI-detector verdicts, cryptographic
  watermark claims, and automatic posting/commenting/DMs/scheduling.

## Release hygiene

Before publication, the staged tree and retained upstream history are scanned
for common GitHub/OpenAI/AWS credentials, private-key blocks, credential
literals and credential-bearing URLs; matched secret content is never printed.
Only reviewed source, synthetic fixtures and documentation are included.
Local profiles, filled voice files, auth material, validator packages,
temporary logs, compiled caches and smoke outputs are excluded. Pattern scans
are a bounded check, not a mathematical proof that no arbitrary secret exists.
The release scan covered 98 staged files and 29 retained upstream blobs:
zero credential-pattern findings and zero unwanted/private output paths.

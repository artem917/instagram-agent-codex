# IG_HUMAN_RU_V1

Date: 2026-10-12. Baseline: `3f83e0790432f2379543d03d57e1c2cbb1d8c86e`.
Implemented modes: en (default), ru, ru-social. A single RU engine and lexicon
serve both Russian modes. Platform limits are optional local JSON settings,
without default platform caps, account connections, truncation or social actions.

## Observed automated results

Environment: Windows, Python 3.14.3, Codex CLI 0.162.0-alpha.17.2.

| Check | Result |
| --- | --- |
| Original test_pack.py suite | 29/29 PASS, including complete pinned upstream scoring/transform result fixtures. |
| New test_ru.py suite | 35/35 PASS. |
| Combined suite | 64/64 PASS. |
| Labelled corpus | 64 examples: 20 ordinary human-style, 20 template-style, 24 edge cases; both ru modes tested. |
| Protected-data inventories | 64/64 preserved in each Russian mode. |
| Repeated processing | 64/64 idempotent in each Russian mode. |
| Mixed formatting | 120 deterministic layouts × 2 modes preserved data and remained idempotent. |
| English compatibility | Default/explicit en outputs match; original functions/results and slop.json preserved. |
| Emoji correction | EN and RU retain ZWJ, modifiers, selectors and tag sequences. |
| Python compilation / pack validation | PASS. |
| Installed skill-creator quick_validate.py | PASS with per-process `python -X utf8`, avoiding that validator's Windows ANSI default. |

The corpus is synthetic and labelled by its author for editorial regression,
not collected from actual humans/LLM systems. Development/holdout labels
are synthetic partitions; neither is an independent human evaluation. The
ordinary human-style label describes writing style, never verified authorship.
No accuracy, AI probability or detector benchmark is claimed.

Machine-readable cases/results:
[ru-corpus.json](tests/fixtures/ru-corpus.json),
[ru-evaluation.json](tests/fixtures/ru-evaluation.json).
Reproduce with:

```text
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/evaluate_ru.py --out outputs/ru-evaluation.json
python -m compileall -q skills scripts tests
```

Tests exercise Cyrillic/ё, quotes, dates/decimals/names/articles, URL/email,
negations, typography, multi-sentence paragraphs, useful lists, humor,
short/long posts, exact and near repeated phrases, rhythm, UTF-8/BOM/CRLF,
Cyrillic Windows paths, forced legacy stdout settings, stdin, before/after
reports, custom analysis lexicons and optional platform limits. No mandatory
CTA/question/hashtags are introduced. Invalid input/configuration fails clearly.
Unsafe custom semantic replacements are refused; digit joining through U+200B
rolls back instead of changing 12 + 34 into 1234. Unsafe social output never
overwrites an existing result file.

## Corpus findings and false positives

All 20 template-style examples produced at least one style warning in both
RU modes. No ordinary human-style example produced a style warning. Edge e07
did: `В современном мире ... в XIX веке` is a legitimate historical comparison,
so the generic opening rule is a documented false positive. This is one known
edge-case false positive, not an estimate of a real-world error rate.

Notes appear on legitimate «Безусловно», agreement, practical invitations,
«не только ... но и», and a six-step instruction. Those notes are contextual
review cues, not automatic deletion or authorship judgments.

Three social cases deliberately return NEEDS_REWRITE: e16/e17 ambiguous dash
syntax and e18 a verbatim quotation containing an em dash. They preserve
source/data as review candidates and return no finished text. For the other
61 social cases, finished normalization satisfies the social typography/no-
blank-line contract. ru permits the original literary typography in all 64.
These refusal cases are tested safety behavior, not hidden successful rewrites.

## Actual Codex forward tests

Installed the complete pack into an isolated local project and invoked
ig-human with gpt-6.1-sol/high. Two synthetic tasks were given without intended
answers. Codex read the updated skill/runtime/RU references, selected modes,
ran humanize.py and detect.py, wrote outputs/JSON and checked protected data.

- A Telegram post selected ru-social, removed the empty preamble, simplified
  temporal wording and normalized quotes/parenthetical punctuation/paragraphs.
  The final post has no em dash or blank lines, with multi-sentence paragraphs.
  Five actual CLI checks returned REVIEW/exit 1. An ironic «ключевой аспект»
  was retained as author humor, with its warning explicitly acknowledged.
- A Russian literary note selected ru, retained literary quotes/em dash and
  paragraphs, plus the meaningful historical comparison. Five actual CLI
  checks returned REVIEW/exit 1. «В современном мире» was accepted as a
  contextual false positive; «Безусловно» remained an ordinary author word.

Both before/after data guards returned passed:true / changed:[]. Negations,
numbers, names and URLs remain. Codex checked claims against the supplied text;
this is contextual machine review, not independent human certification of
semantics or author voice. Semantic equivalence remains explicitly UNVERIFIED,
rhythm is INCONCLUSIVE for these short samples, authorship is NOT_ASSESSED.
Codex processes completed with exit 0; nested CLI exit 1 is a style REVIEW.
An initial auxiliary shell encoding error was recovered using UTF-8; final
reports are actual CLI output. No network tools or social actions were used.

Sanitized evidence: [ru-codex-smoke.json](tests/fixtures/ru-codex-smoke.json).
Raw logs, private absolute paths and temporary profiles stay under ignored
.test-work and are excluded from publication.

## Practical limitations

Automatic cleanup is deliberately conservative. It doesn't rewrite arbitrary
grammar, generate missing facts, prove meaning, identify every name/brand, or
judge all humor/irony/negation scopes. Complex phrases are edited by Codex using
the specific recommendations and original facts, then rechecked. Lexical overlap
misses some semantic repetition and can overflag purposeful rhetoric. Quoted
sources/titles are shielded and may hide style patterns. Use --preserve for
ambiguous literals. Poetry, dialogue, tables and unusual structures need review.

The code preserves joiners/selectors/tags rather than implementing every Unicode
grapheme/emoji validity rule. The inventory is approximate. Native macOS/Linux
and lower Python versions remain UNVERIFIED; code uses Python 3.10+ APIs.
The other twelve skills/scorers are unchanged and retain their original English
limitations. No AI-authorship detection or watermark-removal capability is claimed.

MIT and Jake Schincariol's original copyright remain unchanged. Authored RU
code, dictionary and examples are credited as Codex adaptation work by artem917.

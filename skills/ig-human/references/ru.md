# RU engine and editorial review

ru and ru-social share one tokenizer, dictionary, analyzer, normalizer and
data guard. There are no platform language engines or dictionary copies.
The CLI defaults to en; choose Russian explicitly with --mode.

## Separate layers

1. Normalization: UTF-8/BOM/CRLF, U+200B artifacts outside protected spans,
   three reviewed equivalents for «сейчас», complete empty meta sentences,
   social quotes/paragraph flow and narrow punctuation rules. ru keeps literary
   typography. Unknown format characters are preserved.
2. Style: editable ru_lexicon.json, fragments/offsets, filler words/fraction,
   stock constructions, bureaucratic phrasing, reflex politeness, CTA/motivation,
   near lexical repetition, repeated openings, lists and formatting.
3. Semantic recommendations: explain what Codex should inspect/change,
   without deleting facts or rewriting complex sentence shapes by regex.

The dictionary's patterns accept IDs, categories, regex, severity and
recommendations. Invalid schemas/regex/thresholds fail clearly. Automatic
wording replacements and empty-sentence deletions are restricted to reviewed
sets in code. New semantic rewrites need code review and preservation tests.

## Russian checks

Tokens handle Cyrillic including ё, compounds and apostrophes. The sentence
splitter shields URLs/code, decimals, initials and common abbreviations; it
is not a complete Russian grammar or morphology parser.

Rhythm is numerical only with >=80 prose words and >=6 meaningful sentences.
A warning needs CV <0.18 and length range <=3 words. Shorter samples are
INCONCLUSIVE, with no penalty. Three repeated two-word openings produce a
contextual warning; intentional anaphora may remain. Near repetition uses
>=5 words and lexical-set overlap >=0.82, with matching numeric/negation
signatures. Six list items produce a note, not deletion of instructions.
Filler density uses a union of marked word spans; a warning needs >=25 words,
>=3 spans and fraction >=0.30. These engineering thresholds are checked on
synthetic examples, not population calibration or copied English thresholds.

## Punctuation and layout

Social quote delimiters become ordinary double quotes. Quoted content is not
lexically rewritten. Apostrophes within O’Connor aren't quote marks. Quoted
sources/titles, URL/code and explicit literals are shielded from lexical edits;
a whole-draft quote wrapper is still analyzed for style.

Dash conversions are limited to numeric ranges (en dash), commas before а/но,
exact introductory labels (colon) and a short list of parenthetical markers.
There is no blanket em-dash-to-hyphen conversion. For example,
`Не умеешь — не берись` needs contextual editing. Verbatim URL/code typography
can conflict with social rules: the result is blocked rather than corrupted.

Flow merges wrapped/single-sentence prose, removes empty separator lines,
and preserves lists and multi-sentence paragraphs. Tested processing is
idempotent. Poems, dialogue, tables and unusual formats need contextual review.

## Data and limits

The guard compares URLs/email, recognized names/IDs, numeric literals,
negation counts, approximate emoji spans, code and --preserve literals.
It is not complete named-entity NLP. For ambiguous brands/articles use a
repeatable `--preserve "exact value"`. Data changes roll back normalization
and return NEEDS_REWRITE. This does not prove that numbers still refer to the
same events or that negation scope/voice stayed unchanged. Meaning is
UNVERIFIED until contextual review.

Joiners, selectors, modifiers and tags are retained, including sequences
beyond the approximate inventory. See [Unicode Emoji / UTS #51](https://www.unicode.org/reports/tr51/).
Full Unicode grapheme/emoji validation is not claimed. Typography is not
authorship or watermark evidence. Legitimate epoch comparisons, honest
agreement, ordinary «безусловно», anaphora and practical lists may trigger
findings. Quoted material can hide styles. Inspect evidence instead of blindly
deleting. Lexical overlap cannot detect all semantic repetition.

## CLI

```text
python "<skill_dir>/humanize.py" post.txt --mode ru-social --json
python "<skill_dir>/humanize.py" post.txt --mode ru --preserve "Exact Brand" --report
python "<skill_dir>/detect.py" original.txt edited.txt --mode ru-social --json
python "<skill_dir>/detect.py" post.txt --mode ru-social --platform-settings settings.json --json
```

RU normalizer JSON separates text/candidate, normalization, analysis,
preservation and unresolved problems. For NEEDS_REWRITE text is null;
candidate is review material. Non-JSON calls do not write/overwrite a finished
output in that state. REVIEW candidates aren't advertised as finished copy.

| Exit | Russian-mode meaning |
| --- | --- |
| 0 | CLEAN or CLEAN_WITH_NOTES; inspect contextual notes. |
| 1 | REVIEW style/format/operator-limit findings. |
| 2 | Invalid input/configuration or I/O error. |
| 3 | Normalizer NEEDS_REWRITE: unsafe punctuation/data conflict; no finished output. |

detect.py before/after adds comparison to the second RU report. It checks
protected data, not meaning. English JSON and exit behavior remain compatible.
--json remains stdout-only as in the legacy CLI; --out writes non-JSON text.

Optional platform JSON permits name, max_chars and max_hashtags:

```json
{"name": "My network settings", "max_chars": 1200, "max_hashtags": 0}
```

These are operator-chosen constraints, not claims about current platform caps.
The engine reports excesses without truncating or adding CTA/hashtags. The
same options work for VK, Instagram, Telegram, Threads and other networks.

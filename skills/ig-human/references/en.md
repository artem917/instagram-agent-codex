# English workflow (default)

Existing calls, slop.json, transformation/report data and the five English
heuristic computations remain compatible with baseline 3f83e07. One bug fix
preserves U+200D and emoji tag characters; these are no longer removed or
counted as suspicious merely because their Unicode category is Cf.

```text
python "<skill_dir>/humanize.py" draft.txt -o clean.txt --report
python "<skill_dir>/detect.py" draft.txt clean.txt --json
```

The existing lexicon handles stock English words/phrases, typography and known
invisible artifacts. URLs are protected. Structural patterns are reported for
contextual rewriting. Rewrite flagged sentences yourself, preserving meaning
and voice, and rerun both tools. Short texts may correctly stay REVIEW:
do not pad, invent facts or iterate until a heuristic says PASS.

The retained checks are BURSTINESS, SPECIFICITY, SLOP DENSITY, FINGERPRINT and
VOICE. Overall remains 60% mean plus 40% minimum. Existing JSON keys
human_score and PASS/REVIEW/FLAGGED are historical style labels retained for
compatibility, not authorship evidence, AI probability or third-party verdicts.

English lexical replacements are the original heuristic behavior, not a
general semantic guarantee. Review the result. Russian data checks and
recommendations are used only with an explicit Russian mode. No social actions.

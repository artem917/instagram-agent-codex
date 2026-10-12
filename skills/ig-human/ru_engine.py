"""One Russian normalizer/analyzer for ru and ru-social. Standard library only."""
import json
import math
from pathlib import Path
import re
import statistics

from content_guard import NUMBER_RE, mask, overlaps, preservation, sentence_spans, spans, words
from ig_io import read_text

RULES = Path(__file__).with_name("ru_lexicon.json")
MODES = ("en", "ru", "ru-social")
SOCIAL_QUOTES = {'«': '"', '»': '"', '“': '"', '”': '"', '„': '"', '‟': '"', '‘': '"', '’': '"'}
LIST_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")
STOP = set("а без бы был была были быть в во вот все всё где да даже для до же за и из или как ко к ли на над но о об он она они от по под при про с со так то только у уже что это я мы вы ты не ни нет".split())
SAFE_EQUIVALENTS = {"на данный момент": "сейчас", "в настоящее время": "сейчас", "в настоящий момент": "сейчас"}
EMPTY_META = {"Давайте разберёмся", "Давайте разберемся", "Подводя итог", "Подводя итоги"}


def social_violations(text):
    for match in re.finditer(r'[—«»“”„‟‘’]|\n[ \t]*\n', text):
        # A typographic apostrophe inside O’Connor isn't a quotation mark.
        if (match.group() == '’' and match.start() and match.end() < len(text)
                and text[match.start() - 1].isalnum() and text[match.end()].isalnum()):
            continue
        yield match


def load_rules(path=RULES):
    data = json.loads(read_text(path))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("RU lexicon must be an object with version 1")
    for key in ("patterns", "safe_replacements", "empty_sentences", "thresholds"):
        if key not in data:
            raise ValueError(f"RU lexicon missing {key}")
    for key in ("patterns", "safe_replacements", "empty_sentences"):
        if not isinstance(data[key], list):
            raise ValueError(f"RU {key} must be a list")
    if not isinstance(data["thresholds"], dict):
        raise ValueError("RU thresholds must be an object")
    ids = set()
    for rule in data["patterns"]:
        if not isinstance(rule, dict) or not all(isinstance(rule.get(k), str) for k in
                ("id", "category", "regex", "recommendation", "severity")):
            raise ValueError("Invalid RU pattern entry")
        if rule["id"] in ids or rule["severity"] not in ("note", "warning"):
            raise ValueError("Duplicate rule ID or invalid severity")
        ids.add(rule["id"])
        try:
            re.compile(rule["regex"], re.IGNORECASE)
        except re.error as exc:
            raise ValueError(f"Invalid regex for {rule['id']}: {exc}") from None
    for rule in data["safe_replacements"]:
        if not isinstance(rule, dict) or not all(isinstance(rule.get(k), str) and rule[k] for k in ("find", "replace")):
            raise ValueError("Invalid safe replacement")
        if SAFE_EQUIVALENTS.get(rule["find"]) != rule["replace"]:
            raise ValueError("New automatic wording changes need code review and semantic regression tests; extend analysis patterns instead")
    if not all(isinstance(s, str) and s for s in data["empty_sentences"]):
        raise ValueError("Invalid empty sentence list")
    if set(data["empty_sentences"]) - EMPTY_META:
        raise ValueError("Only the reviewed content-free meta sentences may be automatically removed")
    defaults = {"rhythm_min_words": 80, "rhythm_min_sentences": 6, "rhythm_cv": 0.18,
                "repeat_min_words": 5, "repeat_overlap": 0.82, "list_min_items": 6}
    if set(data["thresholds"]) != set(defaults):
        raise ValueError("RU thresholds must contain the documented keys")
    for key, value in data["thresholds"].items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"Invalid RU threshold {key}")
        if key in ("rhythm_cv", "repeat_overlap") and value > 1:
            raise ValueError(f"Threshold {key} must be at most 1")
        if key not in ("rhythm_cv", "repeat_overlap") and type(value) is not int:
            raise ValueError(f"Threshold {key} must be an integer")
    return data


def platform_settings(path=None):
    if path is None:
        return {}
    data = json.loads(read_text(path))
    if not isinstance(data, dict) or set(data) - {"name", "max_chars", "max_hashtags"}:
        raise ValueError("Platform settings allow only name, max_chars, max_hashtags")
    if "name" in data and not isinstance(data["name"], str):
        raise ValueError("Platform name must be text")
    for key in ("max_chars", "max_hashtags"):
        if key in data and (type(data[key]) is not int or data[key] < (1 if key == "max_chars" else 0)):
            raise ValueError(f"Invalid platform setting {key}")
    return data


def finding(identifier, category, start, end, text, recommendation, severity="warning"):
    return {"id": identifier, "category": category, "start": start, "end": end,
            "evidence": text[start:end], "recommendation": recommendation, "severity": severity}


def analyze(text, mode="ru", rules=None, preserve=(), settings=None):
    if mode not in ("ru", "ru-social"):
        raise ValueError("RU engine mode must be ru or ru-social")
    rules = rules or load_rules()
    settings = settings or {}
    protected = spans(text, preserve)
    # Whole-post quotation wrappers are common in pasted drafts. Analyze their
    # contents; keep attributed fragments/quoted names protected elsewhere.
    protected = [(a, b, kind) for a, b, kind in protected if not (
        kind == "quote" and not text[:a].strip() and not text[b:].strip())]
    prose = mask(text, protected)
    found = []
    for rule in rules["patterns"]:
        for match in re.finditer(rule["regex"], prose, re.IGNORECASE):
            found.append(finding(rule["id"], rule["category"], *match.span(), text,
                                 rule["recommendation"], rule["severity"]))
    sentence_rows = sentence_spans(prose)
    lengths = [len(words(row)) for _, _, row in sentence_rows if len(words(row)) >= 3]
    n_words = len(words(prose))
    thresholds = rules["thresholds"]
    rhythm = {"status": "INCONCLUSIVE", "sentence_words": lengths, "coefficient_of_variation": None}
    if len(lengths) >= thresholds["rhythm_min_sentences"] and n_words >= thresholds["rhythm_min_words"]:
        cv = statistics.pstdev(lengths) / statistics.mean(lengths)
        rhythm.update(status="MEASURED", coefficient_of_variation=round(cv, 3))
        if cv < thresholds["rhythm_cv"] and max(lengths) - min(lengths) <= 3:
            found.append(finding("uniform-rhythm", "rhythm", 0, len(text), text,
                "Проверьте ритм: соседние фразы почти равны по длине. Не добавляйте случайные обрывки или ошибки ради вариации."))
    # Repeated syntax: initial two content words; never change their order automatically.
    starts = [(a, b, words(row)[:2]) for a, b, row in sentence_rows if len(words(row)) >= 4]
    for i in range(len(starts) - 2):
        prefix = [w.casefold() for w in starts[i][2]]
        if prefix == [w.casefold() for w in starts[i + 1][2]] == [w.casefold() for w in starts[i + 2][2]]:
            found.append(finding("repeated-openers", "rhythm", starts[i][0], starts[i + 2][1], text,
                "Три фразы начинаются одинаково. Проверьте, не намеренная ли это анафора; сохраняйте авторский приём."))
            break
    repetitions = []
    meaningful = []
    for a, b, row in sentence_rows:
        tokens = [w.casefold() for w in words(row)]
        if len(tokens) < thresholds["repeat_min_words"]:
            continue
        content = {w for w in tokens if w not in STOP}
        negations = [w for w in tokens if w in {"не", "нет", "ни", "нельзя", "никогда"}]
        nums = NUMBER_RE.findall(row)
        for old_a, old_b, old_content, old_neg, old_nums in meaningful:
            if negations != old_neg or nums != old_nums or not content or not old_content:
                continue
            overlap = len(content & old_content) / len(content | old_content)
            if overlap >= thresholds["repeat_overlap"]:
                repetitions.append({"first": [old_a, old_b], "second": [a, b], "lexical_overlap": round(overlap, 3)})
                found.append(finding("repeated-thought", "repetition", a, b, text,
                    "Лексически похожая мысль уже встречалась. Сопоставьте факты, контраст и шутку перед сокращением."))
                break
        meaningful.append((a, b, content, negations, nums))
    lines = text.splitlines()
    list_items = [line for line in lines if LIST_RE.match(line)]
    if len(list_items) >= thresholds["list_min_items"]:
        found.append(finding("list-density", "lists", 0, len(text), text,
            "Длинный список: проверьте, полезен ли каждый пункт. Инструкцию, меню или спецификацию не превращайте в прозу автоматически.", "note"))
    if mode == "ru-social":
        literal = spans(text, preserve, include_quotes=False)
        for match in social_violations(text):
            if not overlaps(*match.span(), literal):
                found.append(finding("social-format", "formatting", *match.span(), text,
                    "В ru-social нужны обычные двойные кавычки, отсутствие длинного тире и пустых строк."))
        prose_lines = [line for line in lines if line.strip() and not LIST_RE.match(line)]
        if len(prose_lines) >= 3 and all(len(sentence_spans(line)) == 1 for line in prose_lines):
            found.append(finding("sentence-per-line", "formatting", 0, len(text), text,
                "Не дробите обычный пост на строку для каждого предложения. Сохраните осмысленные абзацы; стихи требуют отдельной проверки."))
    if settings.get("max_chars") is not None and len(text.rstrip("\n")) > settings["max_chars"]:
        found.append(finding("platform-length", "platform", 0, len(text), text,
            f"Длина превышает заданные {settings['max_chars']} символов. Сократите вручную без потери данных."))
    tags = re.findall(r"(?<!\w)#[А-Яа-яЁёA-Za-z0-9_]+", prose)
    if "max_hashtags" in settings and len(tags) > settings["max_hashtags"]:
        found.append(finding("platform-hashtags", "platform", 0, len(text), text,
            f"Хештегов больше заданных {settings['max_hashtags']}. Выберите вручную, какие оставить."))
    style_ranges = [(f["start"], f["end"]) for f in found if f["category"] in ("filler", "bureaucratic", "politeness")]
    filler_words = sum(1 for match in re.finditer(r"[А-Яа-яЁёA-Za-z]+", prose)
                       if any(match.start() < end and match.end() > start for start, end in style_ranges))
    if n_words >= 25 and len(style_ranges) >= 3 and filler_words / n_words >= 0.30:
        found.append(finding("filler-density", "wateriness", 0, len(text), text,
            "Много вводных и общих оборотов. Проверьте, какие фразы сообщают новое; не придумывайте конкретику ради цифр."))
    return {"mode": mode, "verdict": "REVIEW" if any(f["severity"] == "warning" for f in found) else (
                "CLEAN_WITH_NOTES" if found else "CLEAN"),
            "findings": found, "metrics": {"prose_words": n_words, "rhythm": rhythm,
                "filler_spans": len(style_ranges), "filler_words": filler_words,
                "filler_fraction": round(filler_words / max(n_words, 1), 3),
                "list_items": len(list_items), "repetitions": repetitions},
            "platform_settings": settings, "authorship": "NOT_ASSESSED",
            "semantic_equivalence": "UNVERIFIED"}


def _case(source, replacement):
    if not replacement:
        return ""
    if source.isupper():
        return replacement.upper()
    return replacement[0].upper() + replacement[1:] if source[0].isupper() else replacement


def _replace(text, pattern, replacement, preserve, changes, identifier):
    protected = spans(text, preserve)
    edits = []
    for match in re.finditer(pattern, text, re.IGNORECASE):
        if overlaps(*match.span(), protected):
            continue
        new = replacement(match) if callable(replacement) else _case(match.group(), replacement)
        edits.append((*match.span(), new))
        changes.append({"id": identifier, "before": match.group(), "after": new})
    for a, b, new in reversed(edits):
        text = text[:a] + new + text[b:]
    return text


def _flow(text, preserve=()):
    """Keep lists and multi-sentence paragraphs; merge runs of one-line prose."""
    protected = spans(text, preserve, include_quotes=False)
    if any(kind in ("code", "explicit") and "\n" in text[a:b] for a, b, kind in protected):
        # Don't corrupt whitespace in code/explicit literal; caller checks compliance.
        return text
    blocks = re.split(r"\n[ \t]*\n+", text.strip())
    result = []
    short = []
    def flush():
        if short:
            result.append(" ".join(short))
            short.clear()
    for block in blocks:
        plain = []
        for line in block.splitlines():
            if LIST_RE.match(line):
                if plain:
                    short.append(" ".join(plain)); plain.clear()
                flush()
                result.append(line.strip())
            elif line.strip():
                if len(sentence_spans(line)) >= 2:
                    if plain:
                        short.append(" ".join(plain)); plain.clear()
                    flush()
                    result.append(line.strip())
                else:
                    plain.append(line.strip())
        if plain:
            paragraph = " ".join(plain)
            if len(sentence_spans(paragraph)) <= 1:
                short.append(paragraph)
            else:
                flush()
                result.append(paragraph)
    flush()
    return "\n".join(result)


def normalize(text, mode="ru", rules=None, preserve=(), settings=None):
    if mode not in ("ru", "ru-social"):
        raise ValueError("RU engine mode must be ru or ru-social")
    rules = rules or load_rules()
    original = text
    changes = []
    text = text.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    # Joiners, selectors, tags, bidi controls and other unknown format chars are
    # preserved. Only known U+200B artifacts outside immutable spans are removed.
    text = _replace(text, "\u200b", "", preserve, changes, "zero-width-space")
    for rule in rules["safe_replacements"]:
        pattern = r"(?<!\w)" + re.escape(rule["find"]).replace(r"\ ", r"[ \t]+") + r"(?!\w)"
        text = _replace(text, pattern, rule["replace"], preserve, changes, "plain-wording")
    for empty in rules["empty_sentences"]:
        # Only complete, content-free sentences. No clause removal or negation editing.
        pattern = r"(?m)(?:^|(?<=[.!?]))[ \t]*" + re.escape(empty) + r"[.!][ \t]*(?=\s|$)"
        text = _replace(text, pattern, "", preserve, changes, "empty-intro")
    if mode == "ru-social":
        immutable = spans(text, preserve, include_quotes=False)
        chars = list(text)
        for i, char in enumerate(chars):
            if char == '’' and i and i + 1 < len(chars) and chars[i - 1].isalnum() and chars[i + 1].isalnum():
                continue
            if char in SOCIAL_QUOTES and not overlaps(i, i + 1, immutable):
                chars[i] = SOCIAL_QUOTES[char]
        text = "".join(chars)
        # Grammatically bounded punctuation rules, not a blanket dash replacement.
        text = _replace(text, r"(?<=\d)[ \t]*—[ \t]*(?=\d)", "–", preserve, changes, "numeric-range")
        text = _replace(text, r"[ \t]*—[ \t]*(?=(?:а|но)\b)", ", ", preserve, changes, "before-conjunction")
        text = _replace(text, r"(?m)^([ \t]*(?:Мой план|Наш план|План|Итог|Результат|Главное|Причина))[ \t]+—[ \t]+",
                        lambda m: m.group(1) + ": ", preserve, changes, "label-colon")
        text = _replace(text, r"[ \t]+—[ \t]+(честно|кстати|например|если честно)[ \t]+—[ \t]+",
                        lambda m: ", " + m.group(1) + ", ", preserve, changes, "parenthetical")
        flowed = _flow(text, preserve)
        if flowed != text:
            changes.append({"id": "paragraph-flow", "before": text, "after": flowed})
        text = flowed
    # Keep punctuation and internal spaces in preserved strings verbatim.
    text = text.strip() + "\n" if text.strip() else ""
    guard = preservation(original, text, preserve)
    if not guard["passed"]:
        text = original
    analysis = analyze(text, mode, rules, preserve, settings)
    unresolved = []
    if mode == "ru-social":
        # Immutable content may conflict with social formatting; don't conceal it.
        for match in social_violations(text):
            unresolved.append(finding("unsafe-social-rewrite", "formatting", *match.span(), text,
                "Для этой пунктуации или защищённого фрагмента нужна смысловая правка Codex. Не заменяйте тире дефисом вслепую."))
    report = {"mode": mode, "normalization": changes if guard["passed"] else [],
              "analysis": analysis, "preservation": guard, "unresolved": unresolved,
              "status": "NEEDS_REWRITE" if unresolved or not guard["passed"] else analysis["verdict"]}
    # No copy-ready text is returned when a social contract cannot be fulfilled safely.
    return {"text": None if report["status"] == "NEEDS_REWRITE" else text,
            "candidate": text if report["status"] == "NEEDS_REWRITE" else None, "report": report}


def render_analysis(analysis, out):
    print(f"RU STYLE REVIEW ({analysis['mode']}): {analysis['verdict']}", file=out)
    print("Стиль, не определение авторства. Смысловая эквивалентность: UNVERIFIED.", file=out)
    for item in analysis["findings"]:
        print(f"[{item['severity']}] {item['id']}: {item['evidence'][:140]!r}", file=out)
        print("  " + item["recommendation"], file=out)
    if analysis["metrics"]["rhythm"]["status"] == "INCONCLUSIVE":
        print("Ритм: мало материала для численной оценки; штрафа за короткий текст нет.", file=out)

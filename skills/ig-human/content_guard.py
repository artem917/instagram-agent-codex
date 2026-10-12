"""Conservative content inventories and Unicode spans; no linguistic rewriting.

ZWJ, variation selectors, emoji modifiers and tag characters are preserved,
including sequences newer than this heuristic recognises. These routines do
not claim to implement full Unicode grapheme segmentation or named-entity NLP.
"""
from collections import Counter
import re

WORD_RE = re.compile(r"[А-Яа-яЁёA-Za-z]+(?:[-'’][А-Яа-яЁёA-Za-z]+)*")
NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)*")
URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>]+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
CODE_RE = re.compile(r"```[\s\S]*?```|`[^`\n]+`")
ID_RE = re.compile(r"(?<!\w)[A-Za-zА-ЯЁ]{1,12}[-_/][A-Za-zА-ЯЁ0-9][A-Za-zА-Яа-яЁё0-9/_-]*|\b[A-ZА-ЯЁ]{2,}\d[\w/-]*")
NAME_RE = re.compile(r"\b[A-ZА-ЯЁ][a-zа-яё]+(?:[ \t]+[A-ZА-ЯЁ][a-zа-яё]+){1,2}\b")
EMOJI_BASE = r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2300-\u23FF\u2B00-\u2BFF©®™‼⁉]"
EMOJI_TAIL = r"[\ufe0e\ufe0f\U0001F3FB-\U0001F3FF\U000E0020-\U000E007F]*"
EMOJI_RE = re.compile(EMOJI_BASE + EMOJI_TAIL + r"(?:\u200d" + EMOJI_BASE + EMOJI_TAIL + r")*|[0-9#*]\ufe0f?\u20e3")
NEGATIONS = {"не", "нет", "ни", "нельзя", "никогда", "ничего", "никто", "нигде", "никак"}


def words(text):
    return WORD_RE.findall(text)


def quote_spans(text):
    """Quoted content is evidence, not automatically editable prose."""
    spans = []
    pairs = {'«': '»', '“': '”', '„': '“', '"': '"', '‘': '’'}
    i = 0
    while i < len(text):
        end = pairs.get(text[i])
        if end:
            j = text.find(end, i + 1)
            if j >= 0:
                spans.append((i, j + 1, "quote"))
                i = j + 1
                continue
        i += 1
    return spans


def spans(text, preserve=(), include_quotes=True):
    found = []
    for kind, pattern in (("url", URL_RE), ("code", CODE_RE), ("identifier", ID_RE), ("name", NAME_RE)):
        for match in pattern.finditer(text):
            start, end = match.span()
            if kind == "url":
                # Treat sentence punctuation as prose; closing quotes are not URL data.
                while end > start and text[end - 1] in '.,!?;:»”"':
                    end -= 1
            found.append((start, end, kind))
    for value in preserve:
        if not isinstance(value, str) or not value:
            raise ValueError("--preserve values must be non-empty strings")
        found.extend((m.start(), m.end(), "explicit") for m in re.finditer(re.escape(value), text))
    if include_quotes:
        found.extend(quote_spans(text))
    return sorted(found)


def overlaps(start, end, protected):
    return any(start < right and end > left for left, right, _ in protected)


def mask(text, protected):
    chars = list(text)
    for left, right, _ in protected:
        for i in range(left, right):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def inventory(text, preserve=()):
    protected = spans(text, preserve, include_quotes=False)
    return {
        "urls": [text[a:b] for a, b, kind in protected if kind == "url"],
        "identifiers": [text[a:b] for a, b, kind in protected if kind == "identifier"],
        "names": [text[a:b] for a, b, kind in protected if kind == "name"],
        "numbers": NUMBER_RE.findall(text),
        "negations": dict(Counter(w.casefold() for w in words(text) if w.casefold() in NEGATIONS)),
        "emoji": EMOJI_RE.findall(text),
        "explicit": {value: text.count(value) for value in preserve},
        "code": [value.replace("\r\n", "\n").replace("\r", "\n") for value in CODE_RE.findall(text)],
    }


def preservation(before, after, preserve=()):
    old, new = inventory(before, preserve), inventory(after, preserve)
    changed = [key for key in old if old[key] != new[key]]
    return {"passed": not changed, "changed": changed,
            "checked": list(old), "semantic_equivalence": "UNVERIFIED"}


def sentence_spans(text):
    """RU-aware punctuation boundaries, decimals and common abbreviations.

    This is a sentence splitter, not a grammar parser. Initials, common
    abbreviations and URLs/code are masked without shifting character offsets.
    """
    safe = mask(text, spans(text, include_quotes=False))
    chars = list(safe)
    for pattern in (r"(?<=\d)[.,](?=\d)", r"\b[А-ЯЁA-Z]\.(?=\s*[А-ЯЁA-Zа-яё])",
                    r"(?i)\b(?:т\.\s*е\.|т\.\s*д\.|т\.\s*п\.|руб\.|коп\.|г\.|ул\.|им\.|стр\.|арт\.)"):
        for match in re.finditer(pattern, safe):
            for i in range(match.start(), match.end()):
                if chars[i] == ".":
                    chars[i] = "·"
    safe = "".join(chars)
    start = 0
    result = []
    for match in re.finditer(r"[.!?…]+(?=\s|$)|\n", safe):
        end = match.end()
        if text[start:end].strip():
            result.append((start, end, text[start:end].strip()))
        start = end
    if text[start:].strip():
        result.append((start, len(text), text[start:].strip()))
    return result

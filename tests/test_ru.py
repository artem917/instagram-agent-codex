"""Russian editorial review tests on labelled synthetic examples; all offline."""
import importlib.util
import json
import os
import random
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "skills/ig-human"
sys.path.insert(0, str(HUMAN))
from content_guard import inventory, sentence_spans, words
from ru_engine import analyze, load_rules, normalize, platform_settings, social_violations

RULES = load_rules()
CORPUS = json.loads((ROOT / "tests/fixtures/ru-corpus.json").read_text(encoding="utf-8"))["cases"]


class RussianCorpusTests(unittest.TestCase):
    def test_labelled_inventory(self):
        self.assertGreaterEqual(len(CORPUS), 40)
        self.assertEqual(len({case["id"] for case in CORPUS}), len(CORPUS))
        self.assertEqual({case["label"] for case in CORPUS}, {"human", "template", "edge"})
        self.assertTrue(any(case["split"] == "holdout" for case in CORPUS))

    def test_annotated_findings(self):
        for case in CORPUS:
            for mode in ("ru", "ru-social"):
                with self.subTest(case=case["id"], mode=mode):
                    report = analyze(case["text"], mode, RULES)
                    actual = {f["id"] for f in report["findings"]}
                    self.assertTrue(set(case["expected_ids"]) <= actual, (case["expected_ids"], actual))
                    if mode == "ru":
                        self.assertEqual(report["verdict"] == "REVIEW", case["expected_review"])

    def test_content_and_social_contract(self):
        for case in CORPUS:
            for mode in ("ru", "ru-social"):
                with self.subTest(case=case["id"], mode=mode):
                    result = normalize(case["text"], mode, RULES)
                    self.assertTrue(result["report"]["preservation"]["passed"], result)
                    if mode in case["blocked_modes"]:
                        self.assertIsNone(result["text"])
                        self.assertEqual(result["report"]["status"], "NEEDS_REWRITE")
                        candidate = result["candidate"]
                    else:
                        self.assertIsNotNone(result["text"], result)
                        candidate = result["text"]
                        if mode == "ru-social":
                            self.assertFalse(list(social_violations(candidate)))
                            self.assertTrue(all(line.strip() for line in candidate.splitlines()))
                    self.assertEqual(inventory(case["text"]), inventory(candidate))
                    # Neither branch can add made-up experiences, metrics or a CTA.
                    self.assertEqual(candidate.count("http"), case["text"].count("http"))

    def test_idempotence_every_case(self):
        for case in CORPUS:
            for mode in ("ru", "ru-social"):
                with self.subTest(case=case["id"], mode=mode):
                    first = normalize(case["text"], mode, RULES)
                    candidate = first["text"] if first["text"] is not None else first["candidate"]
                    second = normalize(candidate, mode, RULES)
                    self.assertEqual(first["text"], second["text"])
                    self.assertEqual(first["candidate"], second["candidate"])
                    self.assertEqual(first["report"]["status"], second["report"]["status"])


class RussianBehaviorTests(unittest.TestCase):
    def test_cyrillic_yo_hyphens_and_apostrophe_tokens(self):
        self.assertEqual(words("Ёжик, ёлка, чуть-чуть и O’Connor."), ["Ёжик", "ёлка", "чуть-чуть", "и", "O’Connor"])

    def test_decimals_initials_and_abbreviations(self):
        rows = sentence_spans("И. И. Иванов живёт на ул. Ленина. Цена 8,50 руб. за штуку. Т. е. скидки нет.")
        self.assertEqual(len(rows), 3, rows)

    def test_safe_edits_and_voice(self):
        value = "На данный момент я не купил велосипед. Шутка: бюджет купил меня."
        result = normalize(value, "ru-social")
        self.assertEqual(result["text"], "Сейчас я не купил велосипед. Шутка: бюджет купил меня.\n")

    def test_no_new_question_cta_hashtags(self):
        value = "Ничего не купил. Денег не было, и это не новая история успеха."
        self.assertEqual(normalize(value, "ru-social")["text"], value + "\n")

    def test_literary_ru_typography_is_permitted(self):
        value = '«Ёлка» — название рассказа.\n\nВторая часть завтра.'
        self.assertEqual(normalize(value, "ru")["text"], value + "\n")

    def test_social_quotes_and_no_sentence_per_line(self):
        value = 'Купил «ёлку».\nОна “красивая”.\n\nКот сказал ‘мяу’.'
        self.assertEqual(normalize(value, "ru-social")["text"], 'Купил "ёлку". Она "красивая".\nКот сказал "мяу".\n')

    def test_multi_sentence_paragraphs_keep_structure(self):
        value = "Сварил чай. Убрал чашку.\n\nПошёл гулять. Забыл ключи."
        self.assertEqual(normalize(value, "ru-social")["text"], "Сварил чай. Убрал чашку.\nПошёл гулять. Забыл ключи.\n")

    def test_lists_keep_useful_items(self):
        value = "Список:\n\n1. Взять ключи.\n2. Закрыть дверь.\n\nВернуться вовремя."
        result = normalize(value, "ru-social")
        self.assertEqual(result["text"], "Список:\n1. Взять ключи.\n2. Закрыть дверь.\nВернуться вовремя.\n")

    def test_contextual_dash_punctuation(self):
        cases = [("Мой план — кофе.", "Мой план: кофе.\n"),
                 ("Я — честно — устал.", "Я, честно, устал.\n"),
                 ("Хотел уйти — но остался.", "Хотел уйти, но остался.\n"),
                 ("С 10—12 октября.", "С 10–12 октября.\n")]
        for original, expected in cases:
            with self.subTest(original=original):
                self.assertEqual(normalize(original, "ru-social")["text"], expected)

    def test_ambiguous_dash_never_becomes_wrong_hyphen(self):
        result = normalize("Не умеешь — не берись.", "ru-social")
        self.assertIsNone(result["text"])
        self.assertEqual(result["candidate"], "Не умеешь — не берись.\n")
        self.assertEqual(result["report"]["status"], "NEEDS_REWRITE")
        self.assertNotIn(" - ", result["candidate"])

    def test_quoted_sources_not_rewritten(self):
        value = '«Давайте разберёмся. На данный момент вы абсолютно правы» не мой стиль.'
        self.assertEqual(analyze(value)["findings"], [])
        result = normalize(value, "ru-social")
        self.assertIn('"Давайте разберёмся. На данный момент вы абсолютно правы"', result["text"])

    def test_empty_intro_only_full_sentence(self):
        self.assertEqual(normalize("Давайте разберёмся. Ёлка стоит у окна.", "ru")["text"], "Ёлка стоит у окна.\n")
        self.assertEqual(normalize("Давайте разберёмся с расчётом.", "ru")["text"], "Давайте разберёмся с расчётом.\n")

    def test_explicit_preserve_and_brand(self):
        value = "Бренд На данный момент представил коллекцию. O’Connor посмотрел, но ничего не купил."
        result = normalize(value, "ru-social", preserve=["На данный момент", "O’Connor"])
        self.assertEqual(result["text"], value + "\n")
        self.assertTrue(result["report"]["preservation"]["passed"])

    def test_emoji_zwj_modifiers_tags_and_future_joiners(self):
        emojis = "👩🏽‍💻 👨‍👩‍👧‍👦 🏳️‍🌈 👩‍❤️‍💋‍👩 ❤️ 1️⃣ 🏴\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F"
        for mode in ("ru", "ru-social"):
            self.assertEqual(normalize(emojis, mode)["text"], emojis + "\n")

    def test_literal_urls_numbers_names_articles(self):
        value = 'Николай Ёлкин, артикул ЁЖ-42, дата 12.10.2026, цена 1 250,50 ₽. URL https://example.com/a—b?q=«Ёж»&n=8.5'
        result = normalize(value, "ru-social")
        # Literal URL conflicts with the no-em-dash rule; don't percent-encode or corrupt it.
        self.assertIsNone(result["text"])
        self.assertTrue(result["report"]["preservation"]["passed"])
        self.assertIn("https://example.com/a—b?q=«Ёж»&n=8.5", result["candidate"])

    def test_short_text_not_penalized_by_english_metrics(self):
        report = analyze("Ёжик спит.")
        self.assertEqual(report["verdict"], "CLEAN")
        self.assertEqual(report["metrics"]["rhythm"]["status"], "INCONCLUSIVE")
        self.assertNotIn("human_score", report)

    def test_rhythm_requires_sufficient_material(self):
        sentences = [f"Каждый новый небольшой {noun} спокойно помогает нам проверять детали рабочего проекта перед началом долгой важной встречи."
                     for noun in ("макет", "расчёт", "договор", "чертёж", "список", "отчёт", "эскиз")]
        report = analyze(" ".join(sentences))
        self.assertEqual(report["metrics"]["rhythm"]["status"], "MEASURED")
        self.assertIn("uniform-rhythm", {f["id"] for f in report["findings"]})
        self.assertNotIn("uniform-rhythm", {f["id"] for f in analyze("Пишем коротко. Пишем понятно.")["findings"]})

    def test_repetition_distinguishes_numbers_and_negation(self):
        for value in ("Я не покупал этот товар в магазине вчера. Я покупал этот товар в магазине вчера.",
                      "У нас 12 новых заявок от покупателей. У нас 8 новых заявок от покупателей."):
            self.assertNotIn("repeated-thought", {f["id"] for f in analyze(value)["findings"]})

    def test_extensible_custom_lexicon(self):
        custom = json.loads(json.dumps(RULES))
        custom["patterns"].append({"id":"custom","category":"filler","regex":"супер-пупер","severity":"note","recommendation":"Проверьте голос автора."})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "словарь.json"
            path.write_text(json.dumps(custom,ensure_ascii=False),encoding="utf-8-sig")
            report = analyze("Это супер-пупер штука.", rules=load_rules(path))
            self.assertIn("custom", {f["id"] for f in report["findings"]})

    def test_invalid_lexicons_fail_clearly(self):
        for value in ({}, {"version":1}, []):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.json"
                path.write_text(json.dumps(value),encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_rules(path)

    def test_custom_lexicon_cannot_add_semantic_regex_rewrites(self):
        value=json.loads(json.dumps(RULES))
        value["safe_replacements"].append({"find":"не покупал","replace":"купил"})
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"unsafe.json"
            path.write_text(json.dumps(value),encoding="utf-8")
            with self.assertRaises(ValueError):
                load_rules(path)

    def test_whole_draft_quotes_are_analyzed(self):
        report=analyze('«Это не просто чашка, это новый уровень успеха.»')
        self.assertIn("not-just",{f["id"] for f in report["findings"]})

    def test_zero_width_digit_joining_rolls_back(self):
        value="Артикул: 12\u200b34. Не покупал."
        result=normalize(value,"ru-social")
        self.assertIsNone(result["text"])
        self.assertEqual(result["candidate"],value)
        self.assertFalse(result["report"]["preservation"]["passed"])

    def test_deterministic_mixed_layout_invariants(self):
        rng=random.Random(917)
        parts=['На данный момент я не купил ёлку.', 'Мой план — чай.', 'Кот 👩🏽‍💻 спит.',
               'Цена 8,50 ₽. Номер ЁЖ-42.', 'URL https://example.com/a?n=8.5',
               'Сказал «на данный момент».', 'Погулял. Вернулся домой.', '1. Взять ключи.']
        for n in range(120):
            value=rng.choice(['\n','\n\n',' ']).join(rng.sample(parts,rng.randint(1,6)))
            for mode in ('ru','ru-social'):
                with self.subTest(n=n,mode=mode):
                    first=normalize(value,mode)
                    candidate=first['text'] if first['text'] is not None else first['candidate']
                    self.assertTrue(first['report']['preservation']['passed'])
                    second=normalize(candidate,mode)
                    self.assertEqual(first['text'],second['text'])
                    self.assertEqual(first['candidate'],second['candidate'])


class RussianCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ru проверка ")
        self.work = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, script, *args, text=None, env=None):
        return subprocess.run([sys.executable,str(HUMAN/script),*map(str,args)],input=text,
                              cwd=self.work,capture_output=True,encoding="utf-8",env=env,timeout=15)

    def test_bom_crlf_windows_path_and_utf8_output(self):
        path = self.work / "русский пост.txt"
        path.write_bytes(b"\xef\xbb\xbf"+'На данный момент «ёлка» стоит.\r\n\r\nКот 👩🏽‍💻 ничего не купил.\r\n'.encode("utf-8"))
        output = self.work / "выход/пост.txt"
        env = dict(os.environ,PYTHONIOENCODING="cp1251",PYTHONUTF8="0")
        result = self.cli("humanize.py",path,"--mode","ru-social","--out",output,env=env)
        self.assertEqual(result.returncode,0,result.stderr)
        value = output.read_text(encoding="utf-8")
        self.assertEqual(value,'Сейчас "ёлка" стоит. Кот 👩🏽‍💻 ничего не купил.\n')
        result = self.cli("detect.py",output,"--mode","ru-social","--json",env=env)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)["authorship"],"NOT_ASSESSED")

    def test_three_modes_stdin_json(self):
        for mode in ("en","ru","ru-social"):
            for script in ("humanize.py","detect.py"):
                with self.subTest(mode=mode,script=script):
                    result=self.cli(script,"-","--mode",mode,"--json",text="Ёж спит. Кот 👨‍👩‍👧‍👦 не покупал молоко.")
                    self.assertIn(result.returncode,(0,1),result.stderr)
                    json.loads(result.stdout)

    def test_blocked_output_not_created_or_overwritten(self):
        output=self.work/"existing.txt"
        output.write_text("keep existing result",encoding="utf-8")
        result=self.cli("humanize.py","-","--mode","ru-social","--out",output,text="Москва — столица России.")
        self.assertEqual(result.returncode,3)
        self.assertEqual(result.stdout,"")
        self.assertEqual(output.read_text(encoding="utf-8"),"keep existing result")
        result=self.cli("humanize.py","-","--mode","ru-social","--json",text="Москва — столица России.")
        self.assertEqual(result.returncode,3)
        self.assertIsNone(json.loads(result.stdout)["text"])

    def test_compare_actual_ru_reports(self):
        before=self.work/"до.txt"; after=self.work/"после.txt"
        before.write_text("В современном мире ключевой аспект очень важен.",encoding="utf-8")
        after.write_text("Ёжик спит.",encoding="utf-8")
        result=self.cli("detect.py",before,after,"--mode","ru","--json")
        self.assertEqual(result.returncode,0,result.stderr)
        reports=json.loads(result.stdout)
        self.assertEqual([r["verdict"] for r in reports],["REVIEW","CLEAN"])

    def test_optional_platform_limits_no_auto_truncation(self):
        path=self.work/"settings.json"
        path.write_text(json.dumps({"name":"custom network","max_chars":10,"max_hashtags":0}),encoding="utf-8")
        value="Ёжик спит у окна. #ёлка"
        result=self.cli("humanize.py","-","--mode","ru-social","--platform-settings",path,"--json",text=value)
        self.assertEqual(result.returncode,1,result.stderr)
        payload=json.loads(result.stdout)
        self.assertEqual(payload["text"],value+"\n")
        self.assertEqual({f["id"] for f in payload["report"]["analysis"]["findings"]},{"platform-length","platform-hashtags"})

    def test_bad_config_and_mode_errors(self):
        path=self.work/"bad.json";path.write_text('{}',encoding="utf-8")
        for script in ("humanize.py","detect.py"):
            result=self.cli(script,"-","--mode","ru","--lexicon",path,text="Ёж спит.")
            self.assertEqual(result.returncode,2)
            self.assertNotIn("Traceback",result.stderr)
        self.assertEqual(self.cli("humanize.py","-","--mode","ru-vk",text="Ёж спит.").returncode,2)
        self.assertEqual(self.cli("humanize.py","-","--mode","ru-social",text=" ").returncode,2)

    def test_en_default_unchanged_and_emoji_fixed(self):
        text="I paid 40 dollars in March. It failed."
        implicit=self.cli("humanize.py","-","--json",text=text)
        explicit=self.cli("humanize.py","-","--mode","en","--json",text=text)
        self.assertEqual(implicit.stdout,explicit.stdout)
        implicit=self.cli("detect.py","-","--json",text=text)
        explicit=self.cli("detect.py","-","--mode","en","--json",text=text)
        self.assertEqual(implicit.stdout,explicit.stdout)
        self.assertEqual(implicit.returncode,explicit.returncode)
        emojis="👩🏽‍💻 👨‍👩‍👧‍👦 🏳️‍🌈 🏴\U000E0067\U000E0062\U000E007F"
        result=self.cli("humanize.py","-","--json",text=emojis)
        self.assertEqual(json.loads(result.stdout)["text"],emojis+"\n")


if __name__=="__main__":
    unittest.main()

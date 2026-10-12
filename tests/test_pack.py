"""Offline regressions; all input is synthetic and no account is contacted."""
import ast
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from install import install
from validate import SKILLS, TOOLS, frontmatter, validate


def module(name, relative):
    path = ROOT / "skills" / relative
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


hookscore = module("tested_hookscore", "ig-reel/hookscore.py")
beats = module("tested_beats", "ig-reel/beats.py")
caption = module("tested_caption", "ig-caption/caption.py")
humanize = module("tested_humanize", "ig-human/humanize.py")
detect = module("tested_detect", "ig-human/detect.py")
swipe = module("tested_swipe", "ig-viral/swipe.py")
LEX = humanize.load_lexicon()


class PackTest(unittest.TestCase):
    def test_all_manifests_and_resources(self):
        self.assertEqual(validate()["skills"], 13)
        for name in SKILLS:
            self.assertEqual(frontmatter(ROOT / "skills" / name / "SKILL.md")[0]["name"], name)

    def test_python_syntax(self):
        paths = list((ROOT / "skills").rglob("*.py")) + list((ROOT / "scripts").glob("*.py"))
        for path in paths:
            ast.parse(path.read_text(encoding="utf-8"))

    def test_installer_cyrillic_spaces_and_idempotence(self):
        with tempfile.TemporaryDirectory(prefix="ig проект ") as directory:
            dest, count = install(directory)
            self.assertEqual(count, 13)
            self.assertEqual(install(directory)[1], 0)
            for name in SKILLS:
                self.assertTrue((dest / name / "references/codex.md").is_file())
                self.assertEqual((dest / name / "LICENSE").read_bytes(), (ROOT / "LICENSE").read_bytes())
            result = subprocess.run([sys.executable, str(dest / "ig-viral/swipe.py"),
                                     str(ROOT / "examples/captured.tsv"), "--json"],
                                    capture_output=True, encoding="utf-8", cwd=directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["reels"][0]["formula_id"], 9)
            self.assertIsNotNone(payload["reels"][0]["hook_score"])

    def test_installer_conflict_before_any_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / ".agents/skills/ig-viral"
            bad.mkdir(parents=True)
            (bad / "SKILL.md").write_text("unrelated local skill", encoding="utf-8")
            with self.assertRaises(ValueError):
                install(directory)
            self.assertEqual(list(bad.parent.iterdir()), [bad])

    def test_installer_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(install(directory, dry_run=True)[1], 13)
            self.assertFalse((Path(directory) / ".agents").exists())

    def test_installer_missing_project(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                install(Path(directory) / "absent")

    def test_installer_utf8_stdout(self):
        with tempfile.TemporaryDirectory(prefix="ig проект ") as directory:
            env = dict(os.environ, PYTHONIOENCODING="cp1251")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/install.py"),
                                     "--project", directory, "--dry-run"],
                                    capture_output=True, encoding="utf-8", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("проект", result.stdout)


class AlgorithmsTest(unittest.TestCase):
    def test_upstream_scoring_parity(self):
        fixture = json.loads((ROOT / "tests/fixtures/upstream-results.json").read_text(encoding="utf-8"))
        for case in fixture["hooks"]:
            self.assertEqual(json.loads(json.dumps(hookscore.run(case["text"]))), case["result"])
        for case in fixture["beats"]:
            self.assertEqual(beats.analyse(case["text"], target=30), case["result"])
        for case in fixture["captions"]:
            self.assertEqual(caption.analyse(case["text"]), case["result"])
        for case in fixture["humanize"]:
            self.assertEqual(json.loads(json.dumps(humanize.humanize(case["text"], LEX))), case["result"])
        for case in fixture["detect"]:
            self.assertEqual(json.loads(json.dumps(detect.run(case["text"], LEX))), case["result"])

    def test_hooks_strong_vs_greeting(self):
        self.assertGreater(hookscore.run("I lost $18,000 on one missing clause.")[1],
                           hookscore.run("Hey guys, today I wanted to talk about content strategy.")[1])

    def test_beats_known_duration(self):
        data = beats.analyse("I lost 18000 dollars today.\nSave this clause.", wpm=120)
        self.assertEqual(data["total_words"], 8)
        self.assertEqual(data["total_seconds"], 4.0)
        self.assertEqual(data["beats"][1]["start"], 2.5)

    def test_caption_visible_cut_and_limit(self):
        data = caption.analyse("x" * 2201)
        self.assertEqual(len(data["visible"]), 125)
        self.assertEqual(data["verdict"], "FIX")

    def test_caption_tags_and_keywords(self):
        text = "5 hours saved on client proposals. Save this.\n#one #two #three #four #five #six"
        data = caption.analyse(text, keywords=["client proposals", "absent phrase"])
        self.assertEqual(len(data["hashtags"]), 6)
        self.assertEqual(next(c for c in data["checks"] if c["check"] == "HASHTAGS")["status"], "FAIL")
        self.assertIn("absent phrase", next(c for c in data["checks"] if c["check"] == "SEARCH TERMS")["detail"])

    def test_humanize_invisible_typography_urls_and_cyrillic_transport(self):
        text = 'Пример: “текст”…\u200b I leverage robust tools — https://example.com/leverage'
        clean, report = humanize.humanize(text, LEX)
        self.assertIn('Пример: "текст"...', clean)
        self.assertNotIn("\u200b", clean)
        self.assertNotIn("—", clean)
        self.assertIn("https://example.com/leverage", clean)
        self.assertTrue(report["invisible"])
        # This is a Unicode test, not evidence of Russian language quality.

    def test_short_detector_is_inconclusive(self):
        checks, _, verdict = detect.run("I paid 40 dollars.", LEX)
        self.assertIn("too short", checks["BURSTINESS"][1])
        self.assertNotEqual(verdict, "PASS")

    def test_swipe_exact_ranking_and_zero(self):
        rows = swipe.read_rows(str(ROOT / "examples/captured.tsv"))
        data = swipe.analyse(rows, swipe.load_formulas(swipe.HOOKS))
        self.assertEqual([r["outlier"] for r in data["reels"]], [60.0, 40.0, 0.0])
        self.assertEqual(data["baseline"], "account median")
        self.assertIn("example.com", data["reels"][0]["url"])
        self.assertIn("0.0x", swipe.to_markdown(data))

    def test_swipe_mixed_baselines_are_labelled(self):
        rows = [{"account": "a", "views": 10, "median": 5, "followers": 20, "hook": "steal this"},
                {"account": "b", "views": 10, "median": None, "followers": 20, "hook": "steal this"}]
        data = swipe.analyse(rows, None)
        self.assertTrue(data["baseline"].startswith("mixed"))
        self.assertEqual({r["baseline_kind"] for r in data["reels"]}, {"account median", "follower count"})

    def test_swipe_shorthand_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.tsv"
            path.write_text("account\tviews\thook\na\t1.2M\tsteal this", encoding="utf-8")
            with self.assertRaises(ValueError):
                swipe.read_rows(path)


class CliTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ig данные ")
        self.work = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, tool, *args, text=None, env=None):
        return subprocess.run([sys.executable, str(ROOT / "skills" / tool), *map(str, args)],
                              cwd=self.work, input=text, capture_output=True, encoding="utf-8",
                              env=env, timeout=20)

    def test_all_six_help(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                result = self.cli(tool, "--help")
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_six_examples(self):
        inputs = ["caption.txt", "draft.txt", "draft.txt", "script.txt", "hooks.txt", "captured.tsv"]
        for tool, name in zip(TOOLS, inputs):
            with self.subTest(tool=tool):
                result = self.cli(tool, ROOT / "examples" / name, "--json")
                self.assertIn(result.returncode, (0, 1), result.stderr)
                self.assertIsInstance(json.loads(result.stdout), (dict, list))

    def test_bom_crlf_and_cyrillic_file_path(self):
        path = self.work / "черновик с пробелами.txt"
        path.write_bytes(b"\xef\xbb\xbf" + 'Пример: “слова”…\r\nI paid 40 dollars.\r\n'.encode("utf-8"))
        result = self.cli("ig-human/humanize.py", path, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        clean = json.loads(result.stdout)["text"]
        self.assertIn('Пример: "слова"...', clean)
        self.assertNotIn("\ufeff", clean)
        self.assertNotIn("\r", clean)

    def test_all_six_utf8_stdin_and_piped_stdout(self):
        inputs = ["5 hours. Save this. Пример.", "I paid 40 dollars. Пример.",
                  '“Пример”… I paid 40 dollars.', "I paid 40 dollars.\nSave this.",
                  "I lost 18000 dollars on one clause. Пример.",
                  "account\tmedian\tviews\thook\n@пример\t100\t300\tsteal this 4 line clause"]
        env = dict(os.environ, PYTHONIOENCODING="cp1251", PYTHONUTF8="0")
        for tool, text in zip(TOOLS, inputs):
            with self.subTest(tool=tool):
                result = self.cli(tool, "-", "--json", text=text, env=env)
                self.assertIn(result.returncode, (0, 1), result.stderr)
                json.loads(result.stdout)

    def test_relative_output_and_parent_creation(self):
        result = self.cli("ig-viral/swipe.py", ROOT / "examples/captured.tsv", "--out", "swipe.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("60.0x", (self.work / "swipe.md").read_text(encoding="utf-8"))
        result = self.cli("ig-human/humanize.py", ROOT / "examples/draft.txt", "--out", "новый каталог/clean.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.work / "новый каталог/clean.txt").is_file())

    def test_environment_and_home_path_expansion(self):
        path = self.work / "draft.txt"
        path.write_text('Пример. I leverage tools.', encoding="utf-8")
        env = dict(os.environ, IG_TEST_FOLDER=str(self.work), HOME=str(self.work), USERPROFILE=str(self.work))
        result = self.cli("ig-human/humanize.py", "${IG_TEST_FOLDER}/draft.txt", "--out", "~/output.txt", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Пример", (self.work / "output.txt").read_text(encoding="utf-8"))

    def test_review_exit_codes_match_json_and_text(self):
        for tool, text in [("ig-human/detect.py", "I paid 40 dollars."),
                           ("ig-reel/hookscore.py", "Hey guys, today we discuss strategy."),
                           ("ig-caption/caption.py", "x" * 2201)]:
            with self.subTest(tool=tool):
                self.assertEqual(self.cli(tool, "-", text=text).returncode, 1)
                self.assertEqual(self.cli(tool, "-", "--json", text=text).returncode, 1)

    def test_missing_files_are_clear_errors(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                result = self.cli(tool, self.work / "missing.txt")
                self.assertEqual(result.returncode, 2)
                self.assertIn("error:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_empty_input(self):
        for tool in ("ig-reel/beats.py", "ig-reel/hookscore.py", "ig-viral/swipe.py"):
            with self.subTest(tool=tool):
                self.assertEqual(self.cli(tool, "-", text="").returncode, 2)

    def test_invalid_numeric_options(self):
        for option, value in [("--wpm", "0"), ("--wpm", "nan"), ("--target", "-1")]:
            with self.subTest(option=option, value=value):
                result = self.cli("ig-reel/beats.py", "-", option, value, text="I paid 40 dollars.")
                self.assertEqual(result.returncode, 2)
        self.assertEqual(self.cli("ig-caption/caption.py", "-", "--truncate", "0", text="test").returncode, 2)

    def test_custom_lexicon_bom_path(self):
        lexicon = self.work / "словарь.json"
        lexicon.write_text(json.dumps(LEX), encoding="utf-8-sig")
        result = self.cli("ig-human/humanize.py", "-", "--lexicon", lexicon, "--json", text="I leverage tools.")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_malformed_json_is_error(self):
        path = self.work / "bad.json"
        path.write_text("{bad", encoding="utf-8")
        result = self.cli("ig-viral/swipe.py", ROOT / "examples/captured.tsv", "--hooks", path)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()

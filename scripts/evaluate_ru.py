"""Report synthetic editorial-cue findings; never authorship accuracy."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/ig-human"))
from ru_engine import analyze, normalize


def evaluate():
    cases = json.loads((ROOT / "tests/fixtures/ru-corpus.json").read_text(encoding="utf-8"))["cases"]
    results = {}
    for mode in ("ru", "ru-social"):
        rows = []
        for case in cases:
            source = analyze(case["text"], mode)
            style = [f for f in source["findings"] if f["category"] not in ("formatting", "platform")]
            reviewed = any(f["severity"] == "warning" for f in style)
            result = normalize(case["text"], mode)
            value = result["text"] if result["text"] is not None else result["candidate"]
            second = normalize(value, mode)
            rows.append({"id": case["id"], "label": case["label"], "split": case["split"],
                "style_warning": reviewed, "finding_ids": sorted({f["id"] for f in source["findings"]}),
                "status": result["report"]["status"], "data_preserved": result["report"]["preservation"]["passed"],
                "idempotent": result["text"] == second["text"] and result["candidate"] == second["candidate"]})
        results[mode] = {"cases": len(rows), "data_preserved": sum(r["data_preserved"] for r in rows),
            "idempotent": sum(r["idempotent"] for r in rows),
            "template_cases_warned": [r["id"] for r in rows if r["label"] == "template" and r["style_warning"]],
            "template_cases_missed": [r["id"] for r in rows if r["label"] == "template" and not r["style_warning"]],
            "human_or_edge_warnings": [r["id"] for r in rows if r["label"] != "template" and r["style_warning"]],
            "blocked_normalization": [r["id"] for r in rows if r["status"] == "NEEDS_REWRITE"], "rows": rows}
    return {"task": "IG_HUMAN_RU_V1", "baseline": "3f83e07", "date": "2026-10-12",
            "interpretation": "Synthetic, author-labelled editorial regression; no AI-authorship or independent population benchmark.",
            "modes": results}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="optional JSON report path")
    args = parser.parse_args()
    result = evaluate()
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    brief = {mode: {k:v for k,v in data.items() if k != "rows"} for mode,data in result["modes"].items()}
    print(json.dumps(brief,indent=2,ensure_ascii=False))

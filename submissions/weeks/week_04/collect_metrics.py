"""Collect Homework 4's numbers into metrics.json, from the variant cache and the executed notebook.

Week 4 helper: lives in this folder only and is not imported by any notebook. Run from the repo root:
    python submissions/weeks/week_04/collect_metrics.py
"""
import json
import pathlib

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
CACHE = REPO / "data" / "derived" / "scoreboard1"
NOTEBOOK = HERE / "04_scoreboard1.ipynb"
REPORT = HERE / "scoreboard1_report_catou88.json"
SCORE, KS, KS_P = "nll/yr (area record)", "ks (area record)", "ks_p (area record)"

results = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(CACHE.glob("*.json"))}
base = pd.DataFrame(results["baseline"]["rows"]).set_index("hemicycle")[SCORE]
digest = results["baseline"]["fingerprint"]["digest"]

board = []
for name, r in results.items():
    rows = pd.DataFrame(r["rows"]).set_index("hemicycle")
    d = rows[SCORE] - base.loc[rows.index]
    board.append(dict(
        name=name, kind=r["kind"], knobs=r["knobs"], fitted_parameters=r["n_params"],
        held_out_nll=float(rows[SCORE].mean()), between_wing_sd=float(rows[SCORE].std(ddof=1)),
        paired_vs_baseline=float(d.mean()), paired_se=float(d.std(ddof=1) / np.sqrt(len(d))),
        paired_median=float(d.median()), wings_better=int((d < 0).sum()),
        ks_median=float(rows[KS].median()), ks_not_rejected_5pct=int((rows[KS_P] > 0.05).sum()),
        in_sample_nll=-float(r["in_sample"]), seconds=float(r["seconds"]),
        fitted_stage_params=r["shared"]["stages"], question=r["question"],
        same_fingerprint=r["fingerprint"]["digest"] == digest))
board = sorted(board, key=lambda row: (row["kind"] == "bound", row["paired_vs_baseline"]))

nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
errors = [o["ename"] for c in code_cells for o in c.get("outputs", []) if o["output_type"] == "error"]
unexecuted = sum(1 for c in code_cells if c.get("execution_count") is None)


def stdout_of(index):
    return "".join("".join(o["text"]) for o in nb["cells"][index].get("outputs", [])
                   if o["output_type"] == "stream" and o["name"] == "stdout")


metrics = dict(
    protocol_fingerprint=results["baseline"]["fingerprint"],
    execution=dict(code_cells=len(code_cells), errors=errors, unexecuted_code_cells=unexecuted,
                   method="in-process IPython cell execution (no Jupyter kernel), MPLBACKEND=Agg, "
                          "variants pre-fitted into the cache by parallel processes running the "
                          "notebook's own code; BUTTERFLAI_STUDENT=catou88"),
    variants_cached=len(results),
    leaderboard=board,
    submission=json.loads(REPORT.read_text(encoding="utf-8")),
    printed=dict(model_choice=stdout_of(61), knobs_vs_combination=stdout_of(63),
                 gaming_table=stdout_of(69), plausibility=stdout_of(76)),
)
(HERE / "metrics.json").write_text(json.dumps(metrics, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"metrics.json: {len(board)} variants, notebook errors {errors}, unexecuted code cells {unexecuted}")

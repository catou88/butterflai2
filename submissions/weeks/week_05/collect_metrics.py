"""Collect Homework 5's numbers into metrics.json, from the Week 5 caches and the executed notebook.

Week 5 helper: it lives in this folder only and no notebook imports it. Run from the repository root,
after the notebook has been executed (the caches under data/derived/week05/<profile>/ must exist):
    python submissions/weeks/week_05/collect_metrics.py
"""
import json
import pathlib

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROFILE = "taste"                                   # the profile the submitted notebook was run on
WEEK5 = REPO / "data" / "derived" / "week05" / PROFILE
NOTEBOOK = HERE / "05_neural_fields.ipynb"
SCORE, KS, KS_P = "nll/yr (area record)", "ks (area record)", "ks_p (area record)"


def load(folder):
    """Every cached result in a folder, keyed by file stem."""
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))}


def rows(result):
    return pd.DataFrame(result["rows"]).set_index("hemicycle")


parametric = load(WEEK5 / "parametric")
neural = load(WEEK5 / "neural")
champion = parametric["gate-tanh_x__profile-asymmetric__shift-from_amplitude_1p__width-instantaneous"]
digest = champion["fingerprint"]["digest"]

board = []
for name, result in {**parametric, **neural}.items():
    held = rows(result)
    diff = held[SCORE] - rows(champion).loc[held.index, SCORE]
    board.append(dict(
        name=name, kind=result["kind"], fitted_parameters=result["n_params"],
        seed=result.get("seed"), epochs=result.get("epochs"), lr=result.get("lr"),
        scored_wings=list(held.index), held_out_nll=float(held[SCORE].mean()),
        per_wing_nll={h: float(v) for h, v in held[SCORE].items()},
        paired_vs_champion=float(diff.mean()),
        paired_se=float(diff.std(ddof=1) / np.sqrt(len(diff))) if len(diff) > 1 else None,
        wings_better_than_champion=int((diff < 0).sum()),
        ks_median=float(held[KS].median()), ks_not_rejected_5pct=int((held[KS_P] > 0.05).sum()),
        in_sample_nll=-float(result["in_sample"]), seconds=float(result["seconds"]),
        same_fingerprint=result["fingerprint"]["digest"] == digest))
board.sort(key=lambda row: (len(row["scored_wings"]), row["paired_vs_champion"]), reverse=False)

nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
errors = [o["ename"] for c in code_cells for o in c.get("outputs", []) if o["output_type"] == "error"]
unexecuted = sum(1 for c in code_cells if c.get("execution_count") is None)
live_raises = sum(1 for c in code_cells if "".join(c["source"]).lstrip().startswith("raise NotImplementedError"))


def stdout_of(marker):
    """The stdout of the first code cell whose source contains `marker` (robust to cell renumbering)."""
    for cell in code_cells:
        if marker in "".join(cell["source"]):
            return "".join("".join(o["text"]) for o in cell.get("outputs", [])
                           if o["output_type"] == "stream" and o["name"] == "stdout")
    return None


metrics = dict(
    profile=PROFILE,
    protocol_fingerprint=champion["fingerprint"],
    execution=dict(code_cells=len(code_cells), errors=errors, unexecuted_code_cells=unexecuted,
                   live_raise_not_implemented=live_raises,
                   method="in-process IPython cell execution (no Jupyter kernel), MPLBACKEND=Agg, "
                          "CPU only (torch CPU build), from an empty data/derived/week05 cache"),
    results=board,
    printed=dict(
        agreement=stdout_of("largest disagreement with the numpy likelihood"),
        warm_start=stdout_of("PRETRAIN = warm_start("),
        unconditional=stdout_of("UNCONDITIONAL = fit_neural("),
        budget_and_leak=stdout_of("draw_watched(axes[0]"),
        learning_rate_and_budgets=stdout_of("draw_response(axes[0]"),
        chosen_field_counts=stdout_of("CHOSEN_FIT = fit_neural("),
        neural_runs_and_seed_spread=stdout_of("SEED_RUNS = {"),
        board=stdout_of("BOARD, BOARD_STATS = neural_board("),
        plausibility=stdout_of("NEURAL_PLAUSIBLE, NEURAL_SYNTHETIC"),
        field_diagnostics=stdout_of("TIMING = pd.DataFrame("),
        extension=stdout_of("EXTRA_SEEDS = ")),
)
(HERE / "metrics.json").write_text(json.dumps(metrics, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"metrics.json: {len(board)} cached results · notebook errors {errors} · "
      f"unexecuted {unexecuted} · live raises {live_raises}")

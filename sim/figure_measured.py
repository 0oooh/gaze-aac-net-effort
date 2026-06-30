"""Figures that combine the net-effort model with MEASURED model accuracy.

Reads results/measured_*.json (written by measure_p.py) and produces:
  fig4_savings_vs_c.png   raw vs gross vs net savings as correction cost grows,
                          at a model's measured top-1 accuracy
  fig5_models_on_breakeven.png   the (p, c) breakeven with measured models placed
                                 on the accuracy axis

Run measure_p.py first for at least one model.
"""

import os
import glob
import json
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import net_effort as ne  # breakeven_c, C_BAND, etc.

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def load_measured():
    out = {}
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "measured_*.json"))):
        tag = os.path.basename(path)[len("measured_"):-len(".json")]
        if tag == "smoke":
            continue
        with open(path) as f:
            out[tag] = json.load(f)
    return out


def fig_savings_vs_c(res, path):
    c = np.array(res["c_values"])
    gross = np.array(res["gross"]) * 100
    net = np.array(res["net"]) * 100
    raw = res["raw_KS"] * 100
    p = res["p_top1"]

    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    ax.axhline(raw, color="C2", lw=2, ls="--",
               label=f"raw KS (reported-style) = {raw:.0f}%")
    ax.plot(c, gross, color="C0", lw=2, label="gross (with scan cost)")
    ax.plot(c, net, color="C3", lw=2.5, label="net (with correction cost)")
    ax.axhline(0, color="0.4", lw=1)
    ax.axvspan(*ne.C_BAND, color="0.5", alpha=0.12, lw=0, label="realistic c band")

    ax.set_xlabel("correction-cost ratio  c")
    ax.set_ylabel("savings  (% of characters)")
    ax.set_title("How accounting for correction cost changes the savings\n"
                 f"model = {res['model']}, measured top-1 p = {p:.2f}")
    ax.legend(loc="lower left", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_models_on_breakeven(measured, path):
    p = np.linspace(0.15, 0.92, 500)
    cstar = ne.breakeven_c(p)  # NaN where prediction never helps

    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    ax.plot(p, cstar, color="k", lw=2.5, label="breakeven c*  (always-predict)")
    ax.fill_between(p, cstar, 10, where=~np.isnan(cstar), color="#d66", alpha=0.18)
    ax.fill_between(p, 0, cstar, where=~np.isnan(cstar), color="#69d", alpha=0.16)
    ax.axhspan(*ne.C_BAND, color="0.4", alpha=0.10, lw=0)
    ax.text(0.70, 9.1, "net LOSS", color="#a33", fontsize=12, weight="bold")
    ax.text(0.84, 0.5, "net SAVE", color="#36a", fontsize=12, weight="bold")

    colors = ["C1", "C4", "C5", "C6"]
    for (tag, res), col in zip(sorted(measured.items(), key=lambda kv: kv[1]["p_top1"]), colors):
        pv = res["p_top1"]
        ax.axvline(pv, color=col, lw=2, ls=":", label=f"{res['model']} (p={pv:.2f})")

    ax.set_xlim(0.15, 0.92)
    ax.set_ylim(0, 10)
    ax.set_xlabel("prediction accuracy  p  (measured top-1 next word)")
    ax.set_ylabel("correction-cost ratio  c")
    ax.set_title("Where do real models fall relative to the breakeven?\n"
                 "(grey band = realistic gaze correction cost)")
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    measured = load_measured()
    if not measured:
        print("no measured_*.json found; run measure_p.py first")
        return
    # primary = smallest-p model present (clearest illustration); any works
    primary = min(measured.values(), key=lambda r: r["p_top1"])
    fig_savings_vs_c(primary, os.path.join(RESULTS_DIR, "fig4_savings_vs_c.png"))
    fig_models_on_breakeven(measured, os.path.join(RESULTS_DIR, "fig5_models_on_breakeven.png"))
    print("models on file:", {t: round(r["p_top1"], 3) for t, r in measured.items()})
    print("wrote fig4_savings_vs_c.png, fig5_models_on_breakeven.png")


if __name__ == "__main__":
    main()

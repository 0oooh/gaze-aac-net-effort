"""Confidence-gating: offer a prediction only when the model's own confidence
is high enough. Tests whether gating beats always-predict, using the measured
per-prediction records (correct, word_len, confidence) from measure_p.py.

Honesty guards:
- The gate threshold tau is chosen on a TRAIN split and evaluated on a held-out
  TEST split, so the reported gated savings are not tau picked on the test set.
- We report the offer rate and the mean word length of offered vs skipped
  words, because high-confidence predictions tend to be short common words
  (small M), which limits how much gating can save.

Policy: offer iff confidence >= tau. Offered + wrong pays correction c*rho;
offered + correct saves M-(alpha+v); skipped contributes 0 (typed manually).
net savings fraction = sum(saving over offered) / sum(M over all words).
"""

import os
import json
import glob
import argparse
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import net_effort as ne  # ALPHA, V_MID, RHO_MID, C_BAND

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def load_records(tag):
    with open(os.path.join(RESULTS_DIR, f"records_{tag}.json")) as f:
        d = json.load(f)
    rec = np.array(d["records"], dtype=float)  # cols: correct, M, conf
    return d["model"], rec[:, 0].astype(bool), rec[:, 1], rec[:, 2]


def net_fraction(correct, M, conf, tau, c, alpha=ne.ALPHA, v=ne.V_MID, rho=ne.RHO_MID):
    """Net savings fraction at gate tau and correction ratio c."""
    offered = conf >= tau
    save = np.where(correct, M - (alpha + v), -(v + c * rho))
    num = save[offered].sum()
    den = M.sum()
    return num / den, offered.mean()


def calibration(correct, conf, nbins=10):
    edges = np.linspace(0, 1, nbins + 1)
    mids, acc, cnt = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf >= lo) & (conf < hi if hi < 1 else conf <= hi)
        mids.append((lo + hi) / 2)
        cnt.append(int(m.sum()))
        acc.append(float(correct[m].mean()) if m.any() else np.nan)
    return np.array(mids), np.array(acc), np.array(cnt)


def fig_gating_curve(correct, M, conf, model, path):
    taus = np.linspace(0, float(conf.max()), 120)
    fig, ax = plt.subplots(figsize=(7.6, 5.2))
    for c, col in zip([2.0, 4.0, 6.0], ["C0", "C1", "C3"]):
        nets = np.array([net_fraction(correct, M, conf, t, c)[0] for t in taus]) * 100
        ax.plot(taus, nets, color=col, lw=2, label=f"c = {c:.0f}")
        # always-predict = tau 0; mark its (negative) value
        ax.scatter([0], [nets[0]], color=col, zorder=5)
        # optimal
        bi = int(np.nanargmax(nets))
        ax.scatter([taus[bi]], [nets[bi]], color=col, marker="*", s=140, zorder=6)
    ax.axhline(0, color="0.4", lw=1)
    ax.set_xlabel("confidence gate  tau  (offer only if top-1 prob >= tau)")
    ax.set_ylabel("net savings  (% of characters)")
    ax.set_title("Confidence-gating vs always-predict\n"
                 f"model = {model}   (dot = always-predict, star = best gate)")
    ax.legend(title="correction cost", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_calibration(correct, conf, model, path):
    mids, acc, cnt = calibration(correct, conf)
    base = correct.mean()
    fig, ax = plt.subplots(figsize=(7.0, 5.0))
    ax.plot(mids, acc, "o-", color="C0", lw=2, label="accuracy in bin")
    ax.axhline(base, color="C3", ls="--", label=f"base rate p = {base:.2f}")
    ax.plot([0, 1], [0, 1], color="0.7", ls=":", label="perfect calibration")
    for x, a, n in zip(mids, acc, cnt):
        if not np.isnan(a):
            ax.annotate(str(n), (x, a), fontsize=7, ha="center", va="bottom", color="0.4")
    ax.set_xlabel("model confidence (top-1 prob)")
    ax.set_ylabel("actual accuracy")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(f"Is confidence informative?  ({model}; numbers = bin count)")
    ax.legend(fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def train_test_report(correct, M, conf, seed=0):
    n = len(correct)
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    half = n // 2
    tr, te = idx[:half], idx[half:]
    taus = np.linspace(0, float(conf.max()), 200)
    rows = []
    for c in [2.0, 4.0, 6.0]:
        # pick tau* on train
        tr_nets = [net_fraction(correct[tr], M[tr], conf[tr], t, c)[0] for t in taus]
        tau_star = taus[int(np.nanargmax(tr_nets))]
        # evaluate on test
        always_te, _ = net_fraction(correct[te], M[te], conf[te], 0.0, c)
        gated_te, offer_te = net_fraction(correct[te], M[te], conf[te], tau_star, c)
        rows.append((c, tau_star, always_te * 100, gated_te * 100, offer_te * 100))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="gpt2")
    args = ap.parse_args()

    model, correct, M, conf = load_records(args.tag)
    fig_gating_curve(correct, M, conf, model, os.path.join(RESULTS_DIR, "fig6_gating_curve.png"))
    fig_calibration(correct, conf, model, os.path.join(RESULTS_DIR, "fig7_calibration.png"))

    print(f"model={model}  n={len(correct)}  base p={correct.mean():.3f}")
    # high-confidence words are shorter (common words) -- show the tradeoff
    hi = conf >= 0.3
    if hi.any():
        print(f"mean word len: offered(conf>=0.3)={M[hi].mean():.2f}  "
              f"skipped={M[~hi].mean():.2f}  (high-conf words are shorter)")
    print("\ntrain/test (tau* picked on train, evaluated on test):")
    print("  c   tau*    always(test)   gated(test)   offer%")
    for c, t, a, g, o in train_test_report(correct, M, conf):
        print(f"  {c:.0f}   {t:.3f}    {a:7.1f}%       {g:6.1f}%     {o:4.0f}%")
    print("\nwrote fig6_gating_curve.png, fig7_calibration.png")


if __name__ == "__main__":
    main()

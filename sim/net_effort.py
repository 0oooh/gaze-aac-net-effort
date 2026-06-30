"""Net-effort breakeven model for prediction in gaze AAC.

Implements the closed-form model from docs/design.md with the grounded ranges
from docs/params.md, and renders the breakeven figures into ../results/.

The model is analytical (an expectation), so results are exactly reproducible;
no random sampling is needed.

Per-opportunity expected change in effort (in selections) vs. typing manually,
when a prediction is offered:

    delta_offer = v + p*alpha - p*M + (1 - p) * r,   with r = c * rho

Negative delta = net effort saved (good). Positive delta = net loss.
Always-predict corresponds to offering at every opportunity (a = 1), so its
per-opportunity net effort equals delta_offer.

Breakevens:
    accuracy:          p* = (v + r) / (M - alpha + r)         # offer helps iff p > p*
    correction ratio:  c* = (p*(M - alpha) - v) / ((1 - p) * rho)   # always-predict
                                                                    # loses for c > c*
"""

import os
import numpy as np
import matplotlib

matplotlib.use("Agg")  # file output only, no display
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

# --- Parameters (docs/params.md, word regime) -----------------------------
# Fixed constants. v and rho are "estimated" (weak) -> we sweep them in the
# sensitivity figure rather than trusting a single value.
M = 5.0       # manual cost of the predicted word (selections)
ALPHA = 1.0   # accept a shown prediction
V_MID = 1.5   # review/scan cost (estimated)
RHO_MID = 2.0 # base correction overhead when wrong (estimated)

# Realistic bands (for shading; not hard limits).
P_BAND = (0.5, 0.7)   # realistic top-1 LLM-AAC accuracy
C_BAND = (2.0, 6.0)   # realistic gaze/motor correction-cost ratio

# Sweep ranges.
P_RANGE = (0.30, 0.90)
C_RANGE = (1.0, 10.0)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


# --- Model ----------------------------------------------------------------
def delta_offer(p, c, M=M, alpha=ALPHA, v=V_MID, rho=RHO_MID):
    """Per-opportunity net effort change (selections) when offering a prediction.

    Negative = saves effort. Accepts scalars or numpy arrays for p, c.
    """
    r = c * rho
    return v + p * alpha - p * M + (1.0 - p) * r


def breakeven_p(c, M=M, alpha=ALPHA, v=V_MID, rho=RHO_MID):
    """Accuracy p* above which offering helps, as a function of c."""
    r = c * rho
    return (v + r) / (M - alpha + r)


def breakeven_c(p, M=M, alpha=ALPHA, v=V_MID, rho=RHO_MID):
    """Correction ratio c* above which always-predict is a net loss, given p.

    Returns NaN where prediction never helps (numerator <= 0), i.e. even with
    zero correction cost the review cost already outweighs the saving.
    """
    num = p * (M - alpha) - v
    den = (1.0 - p) * rho
    c = np.where(num > 0, num / np.where(den == 0, np.nan, den), np.nan)
    return c


# --- Figures --------------------------------------------------------------
def _shade_bands(ax):
    ax.axvspan(*P_BAND, color="0.5", alpha=0.12, lw=0)
    ax.axhspan(*C_BAND, color="0.5", alpha=0.12, lw=0)


def fig_heatmap(path):
    """Fig 1: delta_offer over (p, c), with the breakeven contour and bands."""
    p = np.linspace(*P_RANGE, 241)
    c = np.linspace(*C_RANGE, 241)
    P, C = np.meshgrid(p, c)
    Z = delta_offer(P, C)

    vmax = float(np.max(np.abs(Z)))
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    mesh = ax.pcolormesh(P, C, Z, cmap="RdBu_r", norm=norm, shading="auto")
    cs = ax.contour(P, C, Z, levels=[0.0], colors="k", linewidths=2)
    ax.clabel(cs, fmt="breakeven (delta=0)", fontsize=9)
    _shade_bands(ax)

    cb = fig.colorbar(mesh, ax=ax)
    cb.set_label("net effort per prediction (selections)\n<0 saves   >0 net loss")
    ax.set_xlabel("prediction accuracy  p  (top-1)")
    ax.set_ylabel("correction-cost ratio  c")
    ax.set_title("Always-predict net effort\n(shaded = realistic p and c bands)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_breakeven_p(path):
    """Fig 2: required accuracy p* rises with correction cost c."""
    c = np.linspace(*C_RANGE, 400)
    pstar = breakeven_p(c)

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.plot(c, pstar, color="C3", lw=2.5, label="p*  (offer helps iff p > p*)")
    ax.axhspan(*P_BAND, color="0.5", alpha=0.15, lw=0, label="realistic p band")
    ax.axvspan(*C_BAND, color="C0", alpha=0.10, lw=0, label="realistic c band")
    ax.set_xlabel("correction-cost ratio  c")
    ax.set_ylabel("breakeven accuracy  p*")
    ax.set_ylim(0, 1)
    ax.set_title("Accuracy needed to justify predicting rises with correction cost")
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_sensitivity(path):
    """Fig 3: how the breakeven c*(p) moves under the weak params v and rho."""
    p = np.linspace(*P_RANGE, 400)
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), sharey=True)

    for v, style in zip([0.5, 1.5, 3.0], ["-", "--", ":"]):
        axes[0].plot(p, breakeven_c(p, v=v), "C0", ls=style, lw=2,
                     label=f"v = {v}")
    axes[0].set_title("sensitivity to review cost v  (rho = %.1f)" % RHO_MID)

    for rho, style in zip([1.0, 2.0, 3.0], ["-", "--", ":"]):
        axes[1].plot(p, breakeven_c(p, rho=rho), "C1", ls=style, lw=2,
                     label=f"rho = {rho}")
    axes[1].set_title("sensitivity to correction unit rho  (v = %.1f)" % V_MID)

    for ax in axes:
        ax.axhspan(*C_BAND, color="0.5", alpha=0.15, lw=0)
        ax.axvspan(*P_BAND, color="C2", alpha=0.10, lw=0)
        ax.set_xlabel("prediction accuracy  p")
        ax.set_ylim(0, 10)
        ax.legend(fontsize=9, loc="upper left")
        ax.text(0.97, 0.03, "always-predict loses ABOVE each curve",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=8,
                color="0.3")
    axes[0].set_ylabel("breakeven correction ratio  c*")
    fig.suptitle("Where always-predict turns into a net loss (c* vs p)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def write_summary(path):
    """Plain-language key numbers at the realistic midpoints."""
    p0 = sum(P_BAND) / 2      # 0.6
    lines = []
    lines.append("Net-effort breakeven -- key numbers (word regime)")
    lines.append("params: M=%.1f alpha=%.1f v=%.1f rho=%.1f" % (M, ALPHA, V_MID, RHO_MID))
    lines.append("")
    for p0 in [0.5, 0.6, 0.7, 0.8]:
        cstar = float(breakeven_c(np.array(p0)))
        verdict = ("never helps" if np.isnan(cstar)
                   else "always-predict loses for c > %.2f" % cstar)
        lines.append("p = %.2f  ->  %s" % (p0, verdict))
    lines.append("")
    pmid = 0.6
    lines.append("At realistic p=0.60, c* = %.2f; realistic gaze c band is %.0f-%.0f,"
                 % (float(breakeven_c(np.array(pmid))), *C_BAND))
    lines.append("so across most of the realistic c band, always-predict is a net loss")
    lines.append("=> a state-gated policy (predict only when payoff>0) dominates.")
    lines.append("")
    lines.append("Caveat: v and rho are estimated; see fig 3 sensitivity. The finding")
    lines.append("shape (c* exists and rises with p) is robust; the exact c* is not.")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return "\n".join(lines)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    fig_heatmap(os.path.join(RESULTS_DIR, "fig1_heatmap.png"))
    fig_breakeven_p(os.path.join(RESULTS_DIR, "fig2_breakeven_p.png"))
    fig_sensitivity(os.path.join(RESULTS_DIR, "fig3_sensitivity.png"))
    summary = write_summary(os.path.join(RESULTS_DIR, "summary.txt"))
    print(summary)
    print("\nwrote 3 figures + summary.txt to results/")


if __name__ == "__main__":
    main()

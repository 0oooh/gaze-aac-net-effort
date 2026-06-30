"""Net savings vs correction cost across three AAC prediction regimes.

Implements docs/regimes.md. The point of this figure is the qualitative
contrast that defuses the "you attacked a strawman" critique:
  A top-1 commit       -> declines with c
  B top-k suggestion   -> FLAT in c (correction cost never enters)
  C abbreviation expand -> declines steepest (SpeakFaster's own regime)

Hit rates p1/pk/pe are placeholders to be replaced with measured (top-1/top-k
from measure_p) and literature (expansion) values; the crossover structure is
robust to their exact values.
"""

import os
import json
import argparse
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import net_effort as ne  # M, ALPHA, V_MID, RHO_MID, C_BAND

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

# Regime parameters (documented assumptions; see docs/regimes.md).
M_WORD = ne.M            # 5
ALPHA = ne.ALPHA         # 1
V = ne.V_MID             # 1.5 scan one item
RHO = ne.RHO_MID         # 2
K = 5                    # suggestion list length
BETA = 0.4               # sublinear scan growth
L = 6                    # phrase length (words) for expansion
WORD_LEN = 5             # chars+space per word
M_PHRASE = WORD_LEN * L  # 30
A_TYPED = L + 1          # abbreviation keystrokes + invoke

# Hit rates -- PLACEHOLDERS pending measurement/literature (docs/regimes.md).
# The structural claim (B is flat in c; A, C decline) holds for ANY values;
# these only set where the curves cross.
P1 = 0.30   # top-1 next-word (measure_p: gpt2~0.23, qwen pending)
PK = 0.60   # top-k next-word (to measure)
PE = 0.55   # abbreviation-expansion exact (SpeakFaster/KWickChat region)


def frac_A(c, p1=P1):
    r = c * RHO
    return (p1 * (M_WORD - (ALPHA + V)) - (1 - p1) * (V + r)) / M_WORD


def frac_B(pk=PK):  # c-independent by construction
    scan_k = V * (1 + BETA * (K - 1))
    return (pk * (M_WORD - ALPHA) - scan_k) / M_WORD


def frac_C(c, pe=PE):
    scan = V * L
    save_hit = M_PHRASE - (A_TYPED + ALPHA + scan)
    save_wrong = -(A_TYPED + scan + c * RHO * L)
    return (pe * save_hit + (1 - pe) * save_wrong) / M_PHRASE


def crossover(f_decl, f_flat, c_grid):
    """Smallest c where the flat regime overtakes the declining one (else None)."""
    diff = f_flat - f_decl(c_grid)
    sign = np.sign(diff)
    idx = np.where(np.diff(sign) > 0)[0]
    return float(c_grid[idx[0] + 1]) if len(idx) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-measured", default=None,
                    help="tag of results/measured_<tag>.json to use p1, pk(top-5)")
    ap.add_argument("--pe", type=float, default=PE)
    args = ap.parse_args()

    p1, pk, pe, src = P1, PK, args.pe, "placeholder"
    if args.from_measured:
        with open(os.path.join(RESULTS_DIR, f"measured_{args.from_measured}.json")) as f:
            d = json.load(f)
        p1, pk, src = d["p_top1"], d["p_top5"], d["model"]

    c = np.linspace(1.0, 10.0, 400)
    a = frac_A(c, p1) * 100
    b = np.full_like(c, frac_B(pk) * 100)
    cc = frac_C(c, pe) * 100

    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    ax.plot(c, a, "C0", lw=2.5, label=f"A: top-1 commit (p1={p1:.2f})")
    ax.plot(c, b, "C2", lw=2.5, label=f"B: top-{K} suggestion (pk={pk:.2f}) -- flat in c")
    ax.plot(c, cc, "C3", lw=2.5, label=f"C: abbrev expansion (pe={pe:.2f})")
    ax.axhline(0, color="0.4", lw=1)
    ax.axvspan(*ne.C_BAND, color="0.5", alpha=0.12, lw=0, label="realistic gaze c band")

    xAB = crossover(lambda cc_: frac_A(cc_, p1), frac_B(pk), c)
    xCB = crossover(lambda cc_: frac_C(cc_, pe), frac_B(pk), c)
    ytop = ax.get_ylim()[1]
    span = ytop - ax.get_ylim()[0]
    for j, (x, lab) in enumerate([(xAB, "B beats A"), (xCB, "B beats C")]):
        if x:
            ax.axvline(x, color="0.5", ls=":", lw=1)
            ax.text(x + 0.1, ytop - (0.04 + 0.06 * j) * span, f"{lab} @ c={x:.1f}",
                    fontsize=8, va="top", color="0.3")

    ax.set_xlabel("correction-cost ratio  c")
    ax.set_ylabel("net savings  (% of characters)")
    ax.set_title("Correction cost hits commit and expansion, not suggestion lists\n"
                 f"(p1, pk {'measured: ' + src if args.from_measured else 'placeholder'})")
    ax.legend(fontsize=8.5, loc="lower left")
    fig.tight_layout()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    fig.savefig(os.path.join(RESULTS_DIR, "fig8_regimes.png"), dpi=150)
    plt.close(fig)

    print(f"source={src}  p1={p1:.3f} pk={pk:.3f} pe={pe:.3f}")
    print(f"frac_B (c-independent) = {frac_B(pk)*100:.1f}%")
    print(f"crossover B>A at c={xAB}, B>C at c={xCB}  (gaze band {ne.C_BAND})")
    for cv in (1, 2, 4, 6):
        print(f"  c={cv}:  A={frac_A(cv, p1)*100:6.1f}%  B={frac_B(pk)*100:6.1f}%  "
              f"C={frac_C(cv, pe)*100:6.1f}%")
    print("wrote results/fig8_regimes.png")


if __name__ == "__main__":
    main()

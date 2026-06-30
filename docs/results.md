# Results (living)

What we have measured so far. Updated as runs land. Numbers come from
`sim/measure_p.py` and `sim/figure_measured.py`; see `design.md` for the model
and `params.md` for the cost parameters.

## Method

We reproduce the AAC keystroke-savings simulation (the methodology of
SpeakFaster / KWickChat / character-based AAC) with one addition: we price the
cost of correcting wrong predictions.

- A real language model predicts the next word at each word boundary of a
  corpus (Brown, seeded sample). We measure top-1 accuracy `p` empirically --
  it is no longer an assumed number.
- For the same predictions we compute three savings levels:
  - **raw KS**: characters saved on correct predictions, ignoring interaction
    cost. This is what prior work reports.
  - **gross**: raw minus the scan cost `v` paid on every shown prediction.
  - **net**: gross minus correction cost (`c * rho`) paid when a committed
    prediction is wrong -- the regime real high-throughput AAC lives in
    (abbreviation expansion, phrase commit, scanning interfaces).
- `c` (gaze correction-cost ratio) is swept; cost constants are from
  `params.md`; word length `M` is the real per-word length.

## Measured accuracy

| model | measured top-1 p | n predictions |
|-------|------------------|---------------|
| GPT-2 small (124M) | 0.23 | 800 |
| GPT-2 medium (355M) | 0.27 | 700 |
| Qwen2.5-1.5B (2024) | 0.32 | 600 |

A modern 2024 model (Qwen2.5-1.5B) reaches only 0.32 -- still far left of the
~0.7-0.85 bar. This supports an **entropy-ceiling** reading: top-1 exact
next-word prediction is inherently bounded well below the bar (human next-word
top-1 is ~0.25-0.3), so always-on top-1 commit prediction cannot pay off in the
high-correction-cost gaze regime *regardless of model strength*. That makes the
finding structural, not an artifact of a weak model -- and motivates the regime
analysis below (top-k / expansion change the structure, not just the accuracy).

## Finding so far

1. **The savings metric is inflated by ignoring correction cost.** At GPT-2
   small's measured accuracy, raw KS reads about +16%, but net savings is
   negative across the entire realistic gaze correction-cost band -- predicting
   at every word *costs* effort once corrections are priced (fig4).
2. **There is a clear accuracy bar.** Always-predicting only nets a saving
   inside the realistic gaze band (c = 2-6) when top-1 accuracy is roughly
   above 0.7-0.85 (fig5). Whether frontier conversational models clear that bar
   in real AAC use is the empirical question this frames -- and the motivation
   for a state-gated (predict-only-when-confident) policy.

## Confidence-gating (offer only when the model is confident)

Policy: offer a prediction only when its top-1 probability >= a gate `tau`;
otherwise stay silent (user types manually). `tau` is chosen on a train split
and evaluated on a held-out test split, so the numbers are not `tau` fit to the
test set.

- **Confidence is strongly informative** (fig7): accuracy rises monotonically
  with confidence, from ~5% in the lowest bin to ~68% in the highest; the model
  is roughly calibrated. So the gating signal is real.
- **Gating drastically cuts the loss of always-predict** (fig6): at c=2 it moves
  net effort from about -86% toward 0; the worse the correction cost, the bigger
  the rescue (c=6: from -217% toward 0).
- **But with a model this weak, the optimal gate suppresses prediction**
  (net ~= 0, offer ~= 0%). GPT-2's most-confident predictions top out at ~68%
  accuracy, below the per-offer breakeven (~78% at c=2 for the short, common
  words that score high confidence -- and high-confidence words are indeed
  shorter, 4.1 vs 5.1 chars, which shrinks their savings).

| c | always-predict (test) | best gated (test) | offer rate |
|---|----------------------|-------------------|-----------|
| 2 | -86% | 0% | 0% |
| 4 | -151% | 0% | 0% |
| 6 | -217% | 0% | 0% |

**Honest takeaway.** At current small-LM strength, the right policy in the gaze
regime is to predict very little; confidence-gating is the mechanism that safely
realizes that (it caps the loss at ~0 instead of -86%+) and would yield positive
savings once a model's confident-prediction accuracy clears the breakeven bar.
This pushes against the field's always-suggest default. It also sharpens the
next questions: does a frontier conversational model clear the bar, and is the
real gaze correction cost `c` actually in the 2-6 band.

## Prediction regimes (this is not a strawman)

The top-1-commit result could be dismissed as attacking a UI nobody uses. So we
model the realistic spectrum (`regimes.md`, fig8):

- **A top-1 commit** -- net savings declines with `c`.
- **B top-k suggestion list** -- net savings is **flat in `c`** (a miss costs
  only a scan, never a correction; `c` does not enter the formula).
- **C abbreviation expansion (SpeakFaster's own paradigm)** -- best at low `c`,
  but declines **steepest** (a wrong expansion deletes a whole phrase, scaled by
  `c`).

The crossover: expansion wins at low `c` (~< 1.7 with placeholder rates), but in
the realistic gaze band (c = 2-6) the **suggestion list dominates** both commit
and expansion. So the honest claim is not "prediction is bad" -- it is that the
optimal UI depends on correction cost, and the field's most aggressive
paradigms (commit, expansion) are exactly the ones that collapse in the
high-correction-cost gaze regime. The structural part (B is flat in `c` while A
and C decline) holds for any parameter values; only the crossover location
depends on the hit rates (still to be measured) and the weak cost params.

A small confirming detail: with Qwen2.5 (p=0.32), confidence-gating begins to
eke out a *positive* net at c=2 (about +0.2% by offering only its top ~8%
most-confident predictions) -- the gating policy "turns on" as accuracy rises,
exactly as predicted.

## Honesty / limitations

- GPT-2 small is a weak predictor; its low `p` is a lower bound. A frontier
  conversational model (SpeakFaster-grade) would sit further right on fig5.
  The breakeven analysis sweeps `p`, so measured models are *placed* on the
  axis rather than treated as the whole story.
- `v` (scan) and `rho` (correction unit) are estimated; the conclusion's shape
  is robust but exact crossover points are not (see `params.md` sensitivity).
- Corpus is Brown (general English), not AAC-specific; a conversational / AAC
  corpus is a planned refinement.
- `c` is still swept, not measured. Measuring real gaze correction cost is the
  next empirical leg (it is what turns "if c is 2-6" into "c is measured to be
  X").
- The gating result uses the harsh *commit* regime (a wrong offer is acted on
  and must be corrected). A pure *suggestion* UI, where a wrong offer costs only
  a glance, would let gating net positive more easily; reporting both regimes is
  a planned refinement.

## Figures
- `../results/fig4_savings_vs_c.png` -- raw vs gross vs net at measured p.
- `../results/fig5_models_on_breakeven.png` -- models on the (p, c) breakeven.
- `../results/fig6_gating_curve.png` -- net savings vs confidence gate `tau`.
- `../results/fig7_calibration.png` -- accuracy vs model confidence.
- `../results/fig8_regimes.png` -- net savings vs `c` for the three UI regimes.

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

Bigger model -> higher `p` (0.23 -> 0.27), but both sit far left of the
~0.7-0.85 bar. The trajectory motivates measuring a frontier conversational
model (the SpeakFaster regime) as the rightmost point.

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

## Figures
- `../results/fig4_savings_vs_c.png` -- raw vs gross vs net at measured p.
- `../results/fig5_models_on_breakeven.png` -- models on the (p, c) breakeven.

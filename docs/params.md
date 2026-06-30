# Parameters: grounded ranges for the net-effort model

Companion to `design.md`. Each parameter is tagged by confidence:
**grounded** (taken from a source in `sources.md`), **estimated** (derived from
related numbers; weak), or **swept** (varied as an axis, not fixed). The honesty
of the result depends on not pretending an estimated number is grounded.

## Units

- 1 **selection** = one dwell-based key/candidate choice. All costs are in
  selections; time is reported in parallel.
- Dwell-time anchor: ~500 ms per selection (range 282–876 ms across
  novice/expert; Majaranta 2009, CHI doi:10.1145/1518701.1518758).

## Opportunity-unit regimes (set before simulating)

The "prediction opportunity" unit fixes the meaning of `M`:

- **Word regime (default for the first simulator):** predict the next word.
  Average English word ~4.7 letters + space => `M ~ 5` selections.
- **Phrase regime (SpeakFaster-style):** predict a multi-word span; `M ~ 20–30`.
  Higher savings ceiling but lower exact-match `p` and higher `v`. Modeled
  later, not first.

## Parameter table (word regime)

| sym | meaning | value / range | confidence | basis |
|-----|---------|---------------|------------|-------|
| `M` | manual cost of predicted span | ~5 selections | grounded | avg English word length (~4.7 letters + space) |
| `alpha` | accept a shown prediction | ~1 selection | estimated | one dwell on the candidate |
| `v` | review/scan a shown prediction | ~1–2 selection-eq | estimated (weak) | 1–2 fixations @200–300 ms vs ~500 ms dwell; indirect support: SpeakFaster savings did not raise WPM (arXiv:2312.01532) |
| `rho` | base correction overhead when wrong (extra, beyond retyping `M`) | ~1 if rejected pre-accept; ~3 if accepted then deleted | estimated | dismiss (~1) vs delete inserted span + re-init (~M-ish) |
| `p` | prediction accuracy (top-1) | sweep [0.3, 0.9]; realistic band 0.5–0.7 | swept / grounded-ish | LLM-AAC accuracy is high for top-k savings but lower top-1 (SpeakFaster, KWickChat ~71% savings @ WER threshold) |
| `c` | correction-cost ratio (gaze/motor vs base) | sweep [1, 10]; argued realistic band ~2–6 | swept | dwell + re-fixation + Midas-touch recovery make gaze correction multiples costlier (Jacob 1990; Majaranta 2006/2009) |
| `a` | aggressiveness = offer rate | sweep [0, 1] | swept | policy variable |

`r = c * rho` is the correction overhead used in the model.

## Sweep axes vs fixed constants

- **Sweep (the experiment):** `p`, `c`, `a`. The finding lives in `p x c` space:
  the breakeven `p* = (v + r)/(M - alpha + r)` and the `c*` above which
  always-predict (`a = 1`) is a net loss.
- **Fixed constants (with sensitivity checks):** `M`, `alpha`, `v`, `rho`.
  Because `v` and `rho` are estimated, re-run the breakeven at low/mid/high
  values of each and report whether `c*` moves into or out of the realistic
  band. If the conclusion flips under plausible `v`/`rho`, say so.

## Honesty notes

- The two soft numbers are `v` (review cost) and `c` (correction ratio). The
  whole contribution is essentially "what happens to the breakeven as `c`
  grows," so `c` is deliberately a swept axis, not a claimed constant.
- `p` for real LLM-AAC top-1 is the number most worth tightening with a direct
  measurement later; the sweep brackets the uncertainty for now.
- These are able-bodied-derived anchors degraded by `c`; we do not claim
  patient-population values. Stated as a limitation.

## Links
- Model: `design.md`. Sources: `sources.md` (clusters A, C).

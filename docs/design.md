# Design: Net-Effort Breakeven for Prediction in Gaze AAC

Status: **frozen v0** (Week 1). Changes after this require a dated note below.

## 1. Question

LLM-assisted AAC systems advertise *keystroke savings* from prediction. A wrong
prediction, however, is not free — it must be reviewed, and if accepted,
deleted and retyped. For a motor-impaired user typing by eye gaze, that
correction is disproportionately expensive. **When does offering a prediction
yield a net loss once correction cost is priced in?**

## 2. Net-effort model

All costs are in a common unit (number of gaze selections; time is a secondary
unit reported in parallel). At a *prediction opportunity* (e.g. a pause / word
boundary), the system may offer a predicted span whose manual entry would cost
`M`. Parameters:

| sym | meaning |
|-----|---------|
| `M` | manual cost of the target span — the savings ceiling |
| `α` | cost to accept a shown prediction |
| `v` | cost to **review/scan** a shown prediction (paid whenever one is shown, right or wrong) |
| `p` | prediction accuracy = P(correct \| offered) |
| `r` | **correction overhead** when a prediction is wrong, `r = c · ρ` |
| `c` | **correction-cost ratio** — asymmetry; high for gaze / motor-impaired input |
| `a` | **aggressiveness** = offer rate at opportunities (always-predict ⇒ `a = 1`) |

Expected effort *change vs. typing manually*, per opportunity, when a prediction
is offered:

```
Δ_offer = p·(v + α − M)        # correct: pay review+accept, save M
        + (1 − p)·(v + r)      # wrong:  pay review+correction, still type M
        = v + p·α − p·M + (1 − p)·r
```

Offering with rate `a`: `ΔNetEffort = a · Δ_offer` (not offering ⇒ Δ = 0).

## 3. Breakeven (the result shape)

Offering helps (Δ_offer < 0) iff the expected saving beats review + expected
correction:

```
p·(M − α)  >  v + (1 − p)·r
```

Solving for the accuracy breakeven:

```
p*  =  (v + r) / (M − α + r)
```

- Always-predict (`a = 1`) is **net-negative whenever `p < p*`**.
- `p*` **rises with `r` (hence with `c`)**: the more expensive corrections are,
  the higher the accuracy required to justify predicting at all.
- Equivalently, fixing realistic `p`, there is a correction-cost ratio `c*`
  above which always-predict loses — and we test whether the gaze / motor-
  impaired regime sits above `c*`.

## 4. Conditions compared

1. **never-predict** (`a = 0`) — floor, Δ = 0.
2. **always-predict** (`a = 1`) — the prevailing approach (SpeakFaster-style).
3. **state-gated** (`a = f(state)`) — offer only when the expected payoff is
   positive; the proposed policy.

## 5. Metrics

- Primary: **net effort** = (selections saved) − (selections spent correcting),
  per condition. Reported in selections and in time.
- Secondary: gross savings (to show the savings-vs-net gap), wrong-prediction
  rate, breakeven `p*` and `c*`.

## 6. How `c` is grounded (avoids hand-waving)

`c` and `v` are not invented: anchor them to measured gaze-input numbers —
dwell selection error rate and re-entry cost from the eye-typing literature
(e.g. Majaranta dwell studies) and webcam accuracy (WebGazer ~4° error). The
simulation sweeps a *range* of `c`; grounding only fixes where the realistic
band lies.

## 7. Scope / honesty

This is a **simulation + modeling** study with a demo instance, not a clinical
user study. The contribution is the breakeven characterization and the
demonstration that gross savings can mask net loss. Real-user validation is
explicitly named as future work (and the pitch to a host lab).

---

### Change log
- v0 (Week 1): initial freeze.

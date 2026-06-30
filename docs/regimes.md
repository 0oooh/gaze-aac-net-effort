# Prediction regimes: where correction cost bites (and where it doesn't)

Companion to `design.md`. Pre-empts the "you attacked a strawman" critique by
modeling the realistic spectrum of AAC prediction UIs, not just top-1 commit.
The honest claim is not "prediction is bad" but "the correction-cost penalty is
specific to *commit-style* prediction; suggestion lists sidestep it, at a scan
cost."

Common symbols (selections): `M` manual cost of the target span, `alpha` accept/
select, `v` scan one shown item, `rho` base correction unit, `c` correction-cost
ratio, `r = c*rho`. Savings fraction = E[selections saved] / E[manual selections]
(positive = saves effort).

## Regime A -- top-1 commit  (the harsh, c-sensitive one)

One predicted word is offered and the user commits to it (auto-accept,
single-suggestion, or scanning UI where re-deciding is costly).

```
save | correct (p1):  M - (alpha + v)
     | wrong  (1-p1): -(v + r)            # delete + retype, scaled by c
fracA = [ p1*(M - (alpha+v)) - (1-p1)*(v + r) ] / M
```

c enters through `r`. This is the regime measured in `results.md`.

## Regime B -- top-k suggestion list  (the c-robust one)

The system shows `k` candidates; the user selects their word if it is in the
list, otherwise types manually. With oracle selection (the user only accepts
when their word is shown), a miss costs only the scan, never a correction.

```
scan_k = v * (1 + beta*(k-1))            # scanning k items (beta<1, sublinear)
save | hit  (pk):   M - (alpha + scan_k)
     | miss (1-pk): -(scan_k)            # scanned, did not find, typed manually
fracB = [ pk*(M - alpha) - scan_k ] / M
```

**`c` does not appear.** Net savings is governed by the top-k hit rate `pk`
versus the scan cost, not by correction cost. This is the key contrast: in a
high-correction-cost gaze setting, suggestion lists are robust where commit is
not -- but scanning a longer list is itself expensive for a gaze user, so small
`k` is preferred. (Residual mis-selection can reintroduce a small `c` term;
oracle selection is the optimistic bound.)

## Regime C -- abbreviation expansion  (SpeakFaster's regime; most c-sensitive)

The user types an abbreviation (about one initial per word) for an `L`-word
phrase; the model expands it. Big save when right, big delete when wrong, both
scaled by phrase length.

```
M_phrase = ~ (word_len+1) * L     a_typed = ~ L + 1     scan = v*L
save | hit  (pe):   M_phrase - (a_typed + alpha + v*L)
     | wrong (1-pe): -(a_typed + v*L + c*rho*L)         # delete whole phrase
fracC = [ pe*save_hit + (1-pe)*save_wrong ] / M_phrase
```

The correction term `c*rho*L` scales with phrase length, so this is the *most*
correction-cost-sensitive regime -- which is exactly SpeakFaster's own paradigm.
Far from a strawman, our critique bites hardest here.

## Hypotheses (what the regime figure should show)

1. B is flat in `c`; A declines with `c`; C declines steepest.
2. There is a crossover `c*` (expected inside the realistic gaze band) above
   which the suggestion list overtakes commit/expansion, because it does not pay
   correction.
3. Actionable design rule: under high gaze correction cost, prefer small-`k`
   suggestion lists over commit/expansion; reserve aggressive expansion for
   low-correction-cost or high-accuracy settings.

## Parameters to ground (not invent)

- `p1`, `pk` (top-1, top-k next-word accuracy): measure (extend `measure_p.py`
  to record top-k hits). `pe` (expansion accuracy): from SpeakFaster / KWickChat.
- `scan_k` shape (`beta`), `L`: from eye-typing scan-time literature; swept.
- `c`, `rho`: still the correction-cost numbers to measure next (`params.md`).

## Links
- Model: `design.md`. Code: `../sim/regimes.py`. Results: `results.md`.

# Wiki index

Catalog of the maintained knowledge base. See `../CLAUDE.md` for the schema.

## Schema
- [`../CLAUDE.md`](../CLAUDE.md) — principles, wiki structure, workflows.

## Raw sources (immutable)
- [`sources.md`](sources.md) — verified reading list, grouped by cluster
  (AAC + LLM, gaze-as-state, eye-typing input, datasets).
- [`venues.md`](venues.md) — target publication venues (ACM CHI/ASSETS/ETRA);
  lab -> venue alignment for cold-email framing.

## Wiki pages
- [`design.md`](design.md) — net-effort breakeven model; frozen v0.
- [`params.md`](params.md) — grounded ranges for the model parameters
  (`M, alpha, v, p, c, rho`); sweep axes are `p, c, a`.
- `notes/` — (planned) per-paper notes; anchors: SpeakFaster, Trnka & McCoy
  2008, Mott et al. 2017 (cascading dwell).

## Code and results
- [`../sim/net_effort.py`](../sim/net_effort.py) — closed-form model; fig1-3.
- [`../sim/measure_p.py`](../sim/measure_p.py) — measures real LM next-word
  accuracy `p`; computes raw vs gross vs net savings.
- [`../sim/figure_measured.py`](../sim/figure_measured.py) — fig4, fig5.
- [`results.md`](results.md) — measured findings so far (living).
- `../results/` — fig1-3 (model), fig4 (savings vs c), fig5 (models on
  breakeven), measured_*.json, summary.txt.

## Audit trail
- [`log.md`](log.md) — append-only chronological log of decisions and passes.

## Open threads
- Decide the "prediction opportunity" unit (per word / per pause / per
  sentence) before building the simulator. See `design.md` section 2.
- Tighten `v` and `rho` (estimated) via sensitivity sweeps in the simulator.
- Pre-register the interesting-vs-null interpretation before running sweeps.

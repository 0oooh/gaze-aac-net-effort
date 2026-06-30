# Wiki index

Catalog of the maintained knowledge base. See `../CLAUDE.md` for the schema.

## Schema
- [`../CLAUDE.md`](../CLAUDE.md) — principles, wiki structure, workflows.

## Raw sources (immutable)
- [`sources.md`](sources.md) — verified reading list, grouped by cluster
  (AAC + LLM, gaze-as-state, eye-typing input, datasets).

## Wiki pages
- [`design.md`](design.md) — net-effort breakeven model; frozen v0.
- `params.md` — (planned) grounded ranges for the model parameters
  (`M, alpha, v, p, c, rho`) pulled from `sources.md`.
- `notes/` — (planned) per-paper notes; anchors: SpeakFaster, Trnka & McCoy
  2008, Mott et al. 2017 (cascading dwell).

## Audit trail
- [`log.md`](log.md) — append-only chronological log of decisions and passes.

## Open threads
- Decide the "prediction opportunity" unit (per word / per pause / per
  sentence) before building the simulator. See `design.md` section 2.
- Ground `c` and `v` to measured gaze numbers (`params.md`).
- Pre-register the interesting-vs-null interpretation before running sweeps.

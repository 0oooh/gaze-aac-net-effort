# Log

Append-only audit trail. One line per decision, ingest, or lint pass.
Format: `YYYY-MM-DD [tag] message`. Tags: setup, decision, ingest, lint, build.

2026-06-30 [setup] Repo created as isolated git repo; public remote 0oooh/gaze-aac-net-effort; MIT license.
2026-06-30 [decision] Scope fixed: simulation + modeling of net effort (savings minus correction cost) with a webcam dwell demo. Real-time pause-type classification demoted to optional stretch goal to remove the central gamble.
2026-06-30 [decision] Bilingual doc convention: name.md (EN, committed) + name.ko.md (KO, gitignored). No emoji in any output. Strategy docs stay private.
2026-06-30 [ingest] Froze design v0: net-effort model, breakeven p* = (v+r)/(M-alpha+r), three conditions (never/always/state-gated). See design.md.
2026-06-30 [ingest] Compiled verified reading list into sources.md from web-verified searches (AAC+LLM, gaze-as-state, eye-typing, datasets clusters).
2026-06-30 [setup] Adopted Karpathy LLM-Wiki pattern: CLAUDE.md schema + docs/index.md + docs/log.md + docs/sources.md.
2026-06-30 [ingest] params.md: grounded ranges with confidence tags. Sweep axes p,c,a; constants M~5,alpha~1,v~1-2,rho~1-3 (v,rho weak -> sensitivity). Default word regime (M~5). Decision: first simulator uses word regime.
2026-06-30 [ingest] venues.md: field home is ACM (CHI/ASSETS/ETRA), not IEEE. Realistic tier: CHI LBW / ASSETS poster / ETRA short / arXiv / SLPAT. Lab->venue alignment recorded.
2026-06-30 [build] sim/net_effort.py: closed-form model + 3 figures. FINDING (not null): at mid params (M5,alpha1,v1.5,rho2), c* = 1.12 at p=0.6, 2.17 at p=0.7, 4.25 at p=0.8 -> across most of the realistic gaze c band (2-6), always-predict is a net loss; state-gating dominates. v,rho estimated -> shape robust, exact c* not.
2026-06-30 [decision] To break the circularity (self-chosen p), measure p empirically with a real LM on a corpus = same offline method as the AAC literature, then price correction cost on top. Desk-feasible, no IRB.
2026-06-30 [build] sim/measure_p.py + figure_measured.py: GPT-2 small measured top-1 p=0.23 (n=800, Brown). raw KS=16% but net savings negative across realistic c band (fig4). fig5: always-predict nets a saving in gaze c band only when p>~0.7-0.85. Captures top-1 confidence per prediction for later confidence-gating. results.md written. Adding larger models for the p trajectory.
2026-06-30 [build] GPT-2 medium measured p=0.27 (n=700). Bigger model -> higher p, still far below the bar.
2026-06-30 [build] sim/gating.py: confidence-gating, train/test split. Confidence strongly informative (fig7: acc 5%->68% across conf, roughly calibrated). Gating slashes always-predict loss toward 0 (fig6) but optimal gate SUPPRESSES (net~0, offer~0%) because GPT-2 top confidence tops at ~68% < per-offer breakeven ~78%. Takeaway: weak LMs -> predict little; gating caps loss and would net positive once accuracy clears the bar. Pushes against always-suggest default.
2026-06-30 [build] Generalized measure_p to any HF causal LM + MPS. Qwen2.5-1.5B (2024) measured top-1 p=0.315 (n=600) -- still far below the 0.7-0.85 bar. Supports entropy-ceiling reading: finding is structural, not weak-model artifact. Qwen gating turns on at c=2 (gated +0.2%, offer 8%).
2026-06-30 [build] regimes.md + sim/regimes.py (fig8): top-1 commit (c-sensitive) vs top-k suggestion (FLAT in c) vs abbreviation expansion (steepest). In gaze band c=2-6 suggestion list dominates; expansion wins only at low c. Defuses strawman: correction cost specifically hits commit/expansion (SpeakFaster's paradigm), not suggestion lists. Structural claim (B flat) holds for any params; hit rates p1/pk/pe are placeholders to measure.
2026-06-30 [build] Measured top-k (extend measure_p, top-k first-token beams; records now 5-col t1/t3/t5/M/conf; gating updated). top-1->top-5: gpt2 0.23->0.41, medium 0.28->0.47, Qwen 0.35->0.55 (uplift ~+0.20). regimes.py --from-measured grounds fig8 with measured rates: B beats A at c~1.2, B beats C at c~1.9, suggestion list dominates the whole gaze band. pe (expansion) still a literature placeholder.

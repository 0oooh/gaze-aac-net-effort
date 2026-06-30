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

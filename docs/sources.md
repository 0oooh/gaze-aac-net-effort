# Sources (raw, immutable)

Curated, web-verified reading list. Append new entries; do not rewrite existing
ones. Links below were checked to resolve at time of entry. Items flagged
"provisional" had metadata that was not fully re-verified.

## A. AAC + LLM prediction (domain; what to differentiate from)

- **SpeakFaster** — Cai et al., *Nature Communications* 2024.
  arXiv:2312.01532 · doi:10.1038/s41467-024-53873-3 · PMC11530652.
  LLM abbreviation expansion for eye-gaze ALS typing; ~57% simulated motor
  savings, 29–60% faster entry for two users. Key: reports that keystroke
  savings did **not** translate to faster WPM — the savings-vs-net gap.
- **Context-Aware Abbreviation Expansion** — Cai et al., NAACL 2022.
  arXiv:2205.03767 · ACL 2022.naacl-main.91. SpeakFaster precursor; up to ~77%
  keystroke savings. Does not model wrong-expansion correction cost.
- **Adapting LLMs for Character-based AAC** — Gaines & Vertanen, Findings of
  EMNLP 2025. arXiv:2501.10582. Per-character predictions from subword LLMs +
  AAC-relevance domain adaptation. Accuracy-focused; no correction-cost model.
- **KWickChat** — Shen et al. (Kristensson group), IUI 2022.
  doi:10.1145/3490099.3511145 · github.com/CambridgeIIS/KWickChat. Keyword ->
  full sentence; ~71% savings at a WER threshold (savings conditioned on
  accuracy — a step toward cost-awareness).
- **PrAACT** — Pereira et al., *Expert Systems with Applications* 2024.
  doi:10.1016/j.eswa.2023.122417. Transformer for symbol/card prediction;
  prediction quality only.
- **Trnka & McCoy 2008** — ACL P08-2066. Keystroke savings is settings-dependent
  and capped (~58% ceiling). The canonical "savings can mislead" reference;
  closest prior methodology critique to extend.
- **C-PAK** — TACCESS 2022. doi:10.1145/3544101. Correcting/completing
  abbreviated prefix keystrokes — rare focus on the correction side.
  (provisional: author/venue not fully re-verified.)

## B. Gaze as a real-time state signal (method borrowed; AAC context is the gap)

Note the tracker column: every demonstrated state signal used research-grade or
head-mounted hardware, not a webcam.

- **Detecting Reading-Induced Confusion (EEG + Eye Tracking)** — Zhuang et al.
  (Maes, MIT Media Lab), arXiv:2508.14442. Tracker: Pupil Core (head-mounted).
  Confusion leans on EEG; gaze alone weaker.
- **From Gaze to Guidance** — Danry et al. (MIT/MSR), arXiv:2604.08062.
  Tracker: Meta Aria glasses. Gaze-aware multimodal LLM help during reading.
- **Towards Attention-Aware LLMs** — Zhang, arXiv:2511.06468. Hardware
  unspecified; single-author proposal — weigh rigor accordingly.
- **See Where You Read with Eye Gaze + LLM** — Yang et al., arXiv:2409.19454 ·
  ACM TIoT doi:10.1145/3803853. Tracker: Tobii Pro Spark. Line-level position
  signal; motivates how hard fine resolution is even with a good tracker.
- **Bixler & D'Mello** — mind-wandering detection during reading, UMUAI 2016.
  doi:10.1007/s11257-015-9167-1. Tracker: Tobii. Diagnostic features: long
  fixations, word skips, pupil variability. (Classroom follow-up:
  doi:10.1007/s11257-019-09228-5.)
- **Towards Predicting Reading Comprehension From Gaze Behavior** — ETRA 2020.
  doi:10.1145/3379156.3391335.
- **Mezière et al.** — Eye-tracking measures predict reading comprehension,
  *Reading Research Quarterly* 2023. doi:10.1002/rrq.498. Strongest predictors:
  reading speed, fixation duration, saccade length, regression rate. These
  degrade most at webcam sampling/resolution.
- **Gaze Tutor** — D'Mello et al., *IJHCS* 2012. doi:10.1016/j.ijhcs.2012.01.004.
  Tracker: Tobii. Canonical closed-loop gaze-reactive intervention.

## C. Eye-typing / dwell input and the cost of errors (baseline + cost angle)

- **Mott, Williams, Wobbrock, Morris — Dynamic Cascading Dwell Times** — CHI
  2017. doi:10.1145/3025453.3025517. Per-key dwell scaled by predicted
  likelihood: likely keys easier, unlikely harder — literally encodes error-cost
  asymmetry in the UI. Most on-point for our cost angle; Wobbrock (target lab).
- **Majaranta et al. — Effects of feedback and dwell time** — UAIS 2006.
  doi:10.1007/s10209-006-0034-z. Dwell/feedback vs speed and accuracy.
- **Majaranta et al. — Fast gaze typing with adjustable dwell** — CHI 2009.
  doi:10.1145/1518701.1518758. Dwell 876->282 ms, error 1.28%->0.36%, ~20 wpm.
- **EyeSwipe (Kurauchi et al.)** — CHI 2016. doi:10.1145/2858036.2858335.
  Dwell-free gaze-path typing; shifts error from Midas-touch to decoding.
- **Kristensson & Vertanen — potential of dwell-free eye typing** — ETRA 2012.
  doi:10.1145/2168556.2168605. Upper bound ~46 wpm with a perfect recognizer.
- **Jacob — What you look at is what you get** — CHI 1990
  (cs.tufts.edu/~jacob/papers/chi90.pdf). Origin of the Midas Touch problem.
- **WebGazer** — Papoutsaki et al., IJCAI 2016
  (cs.brown.edu/people/apapouts/papers/ijcai2016webgazer.pdf). Browser webcam
  tracker; ~4 deg error, ~tens of Hz, time-dependent drift. Anchor for webcam
  parameter grounding and the demo backend.
- **Webcam gaze estimation accuracy** — *Frontiers in Robotics and AI* 2024.
  doi:10.3389/frobt.2024.1369566. Recent webcam-vs-Tobii numbers (~1.75 cm best).
- **Sarcar — usability of dwell-free eye typing** — arXiv:1601.06359.
- **Wobbrock — EyeWrite** — COGAIN 2007
  (andrewd.ces.clemson.edu/research/vislab/docs/Wobbrock-COGAIN-07.pdf).
- (provisional) Raiha & Ovaska, CHI 2012 (dwell vs errors/workload);
  Majaranta & Raiha "Twenty Years of Eye Typing," ETRA 2002 — confirm links.

## D. Public eye-tracking datasets (de-risk: degrade-and-measure path)

- **SB-SAT** — github.com/ahnchive/SB-SAT. EyeLink 1000 Hz; SAT reading with
  per-question comprehension correctness AND subjective difficulty. Keystone for
  reading-state labels.
- **OneStop** — *Nature Scientific Data* 2025
  (nature.com/articles/s41597-025-06272-2). 360 participants; 486 comprehension
  questions + four reading regimes.
- **ZuCo / ZuCo 2.0** — osf.io/2urht; zuco-benchmark.github.io. EEG + EyeLink;
  reading-task-type labels.
- **WebQAmGaze** — arXiv:2303.17876. Webcam-quality reading + comprehension;
  validates the low-grade end without simulation. (Label granularity: verify in
  data files.)
- **CELER** — github.com/berzak/celer (PMC9692049). Per-sentence comprehension
  questions; can also serve as a labeled source.
- **GECO** (lt3.ugent.be), **Provo** (osf.io/sjefs), **MECO**
  (meco-read.com) — high-grade reading corpora; linguistic norms, limited
  cognitive-state labels. Use as clean "source" signal to degrade.
- **WebGazer / GazeCapture / EyeT4Empathy** — webcam-quality characterization.
- **SpeakFaster Observer** — CHI 2023, doi:10.1145/3544549.3573870. 130+ hrs
  real gaze-keystroke AAC logs; access gated.
- **Fine-Grained Prediction of Reading Comprehension from Eye Movements** —
  EMNLP 2024 (2024.emnlp-main.198). Prior art: comprehension predicted from
  gaze at ~65% (vs ~54% baseline) on SB-SAT — signal exists but is modest.

## Not yet covered
- Target-lab paper sweep (Froehlich/GazePointAR, Findlater/VizXpress,
  Azenkot, Vogel, Carrington, Bigham) — the verifying agent was interrupted;
  re-run before drafting cold emails.

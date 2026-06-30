# gaze-aac-net-effort

**When does LLM prediction actually help in gaze-based AAC — once you price the cost of correcting wrong predictions?**

Most LLM-assisted AAC systems report *keystroke savings* from prediction. But a
wrong prediction is not free: for a motor-impaired user typing by eye gaze,
deleting and re-entering text is disproportionately expensive. This project
models **net effort** — savings *minus* the cost of correcting wrong
predictions — and asks when an "always-predict" policy is actually a net loss.

## Research question

Given prediction accuracy `p`, correction-cost ratio `c`, and prediction
aggressiveness `a`, where is the **breakeven** beyond which always-predicting
(the prevailing approach) yields *negative* net effort — and does that regime
coincide with realistic gaze / motor-impaired input conditions?

## Contribution (planned)

- A net-effort model and breakeven analysis for prediction-gating in gaze AAC.
- A baseline webcam gaze-typing demo (dwell keyboard + LLM prediction + logging).
- An honest, simulation-grounded characterization — not a clinical user study.

## Status

🚧 Early. Design and scaffold stage.

## License

MIT — see [LICENSE](LICENSE). Note: this repo depends on third-party gaze
libraries (e.g. WebGazer.js) as external dependencies rather than bundling
their source; check each dependency's own license before redistribution.

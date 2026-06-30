# CLAUDE.md — gaze-aac-net-effort

Schema and working rules for this repository. This project follows Andrej
Karpathy's **LLM-Wiki** pattern: a compounding, interlinked knowledge base that
is maintained as we read sources and make decisions, rather than re-derived each
session.

## Coding principles

1. **Think before coding.** Surface assumptions explicitly. When more than one
   interpretation exists, name them and ask before proceeding. Advocate for the
   simpler approach. Name confusion instead of guessing.
2. **Simplicity first.** Minimum code that solves the problem; nothing
   speculative. No unrequested features, single-use abstractions, or error
   handling for implausible scenarios. Ask: would a senior engineer call this
   overcomplicated?
3. **Surgical changes.** Touch only what the request needs. Preserve existing
   style. Remove only dead code your own change introduced; report pre-existing
   dead code without deleting it.
4. **Goal-driven execution.** Turn each request into verifiable success
   criteria. State a brief plan with steps and verification checkpoints.

## Wiki structure (three layers)

- **Raw sources (immutable):** `docs/sources.md` — the curated, verified
  reading list. Append new references; do not rewrite existing entries. Every
  entry must have a link that was actually verified to resolve.
- **Wiki (LLM-maintained):** `docs/index.md` (catalog), `docs/log.md`
  (append-only audit trail), and topic pages such as `docs/design.md`,
  `docs/params.md`, and per-paper notes under `docs/notes/`.
- **Schema (this file):** structure and workflows.

## Workflows

- **Ingest** (a source is read / a decision is made): update the relevant wiki
  pages (notes, params, design), add cross-links `[[page]]`, append one
  `docs/log.md` line. Never edit a raw source entry except to add a new one.
- **Query** (answering a research question): synthesize from wiki pages, cite
  `docs/sources.md` entries. If the answer is reusable, persist it as a wiki
  page and link it from `docs/index.md`.
- **Lint** (periodic): flag contradictions, stale claims, orphaned pages,
  missing cross-links, and — critically — any citation whose link was not
  verified. Record the lint pass in `docs/log.md`.

## Project conventions

- **No emoji** in any file, commit, or output. Plain text only.
- **Bilingual docs:** substantive deliverables (design, params, writeup) are
  written as a pair — `name.md` (English, committed) and `name.ko.md` (Korean,
  gitignored via `*.ko.md`). Infrastructure/reference files (this file,
  `index.md`, `log.md`, `sources.md`) are English-only.
- **Privacy:** application strategy, target-professor lists, cold-email tactics,
  and any company/IP discussion stay LOCAL and gitignored. Never commit them.
  Company IP separation is a hard constraint.
- **Git isolation:** this folder is its own git repo. Run git only from inside
  it; never entangle with the home-directory checkout.
- **Citations:** verify every link resolves before adding it. A fabricated
  citation is worse than a missing one.

## What this project is

A simulation + modeling study (with a webcam gaze-typing demo) of **net effort**
in gaze AAC: keystroke savings from LLM prediction *minus* the cost of
correcting wrong predictions. Core result: the breakeven beyond which an
always-predict policy is a net loss. See `docs/design.md`. It is not a clinical
user study; real-user validation is named as future work.

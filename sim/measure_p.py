"""Measure real next-word prediction accuracy (p) with a language model, then
compute raw vs gross vs net keystroke savings under correction cost.

This replaces the assumed p in docs/params.md with a measured one, using the
same offline-simulation methodology as the AAC keystroke-savings literature
(e.g. KWickChat used GPT-2). The contribution layered on top: account for the
cost of correcting wrong predictions, which the standard "savings" metric omits.

Three savings levels per the same predictions:
  raw KS : fraction of characters saved on correct predictions, ignoring all
           interaction cost  (this is what prior work reports)
  gross  : raw minus the scan cost v paid on every shown prediction
  net    : gross minus correction cost (c*rho) paid when a committed
           prediction is wrong  (the regime real high-throughput AAC lives in)

Costs (alpha, v, rho) come from docs/params.md; word length M is the real
per-word length from the corpus. c (correction-cost ratio) is swept.
"""

import os
import json
import random
import argparse
import numpy as np
import torch

# Cost params (docs/params.md, word regime). M is per-word (real length).
ALPHA = 1.0   # accept a shown prediction
V_MID = 1.5   # scan/review a shown prediction
RHO_MID = 2.0 # base correction overhead when a committed prediction is wrong
C_BAND = (2.0, 6.0)
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

_PUNCT = set(".,;:!?\"'`()[]{}<>-_/\\|@#$%^&*+=~")


def clean_word(w):
    return w.strip().strip("".join(_PUNCT)).lower()


def load_sentences(n, seed, min_words=6):
    import nltk
    from nltk.corpus import brown
    sents = [s for s in brown.sents() if len(s) >= min_words]
    rng = random.Random(seed)
    rng.shuffle(sents)
    return sents[:n]


def load_model(name):
    from transformers import GPT2LMHeadModel, GPT2TokenizerFast
    tok = GPT2TokenizerFast.from_pretrained(name)
    model = GPT2LMHeadModel.from_pretrained(name)
    model.eval()
    torch.manual_seed(0)
    return tok, model


@torch.no_grad()
def predict_next_word(tok, model, context_text, max_tokens=6):
    """Greedy-decode the next whitespace-delimited word after context_text.

    Returns (predicted_word, top1_confidence). Uses KV caching so each extra
    token is cheap. top1_confidence is the softmax prob of the first predicted
    token -- the model's own confidence, for later confidence-gating.
    """
    ids = tok.encode(context_text, return_tensors="pt")
    out = model(ids, use_cache=True)
    past = out.past_key_values
    logits = out.logits[0, -1]
    first_conf = float(torch.softmax(logits, dim=-1).max())
    nxt = int(logits.argmax())
    pieces = [nxt]
    last = torch.tensor([[nxt]])
    for _ in range(1, max_tokens):
        out = model(last, past_key_values=past, use_cache=True)
        past = out.past_key_values
        nxt = int(out.logits[0, -1].argmax())
        if tok.decode([nxt]).startswith(" "):  # next word started
            break
        pieces.append(nxt)
        last = torch.tensor([[nxt]])
    return tok.decode(pieces).strip(), first_conf


def measure(model_name, n_sentences, seed, max_preds=None):
    tok, model = load_model(model_name)
    sents = load_sentences(n_sentences, seed)
    records = []  # (correct: bool, word_len: int, confidence: float)
    n_pred = 0
    for sent in sents:
        words = [w for w in sent if any(ch.isalnum() for ch in w)]
        for i in range(1, len(words)):
            context = " ".join(words[:i])
            target = clean_word(words[i])
            if not target:
                continue
            pred_word, conf = predict_next_word(tok, model, context)
            records.append((clean_word(pred_word) == target, len(target), conf))
            n_pred += 1
            if max_preds and n_pred >= max_preds:
                return records, model_name
    return records, model_name


def savings_curves(records, c_values, alpha=ALPHA, v=V_MID, rho=RHO_MID):
    correct = np.array([r[0] for r in records], dtype=bool)
    M = np.array([r[1] for r in records], dtype=float)
    totalM = float(M.sum())
    p = float(correct.mean())

    # raw KS: chars saved on correct predictions, no interaction cost.
    raw = float(M[correct].sum()) / totalM

    out = {"p_top1": p, "n": len(records), "mean_word_len": float(M.mean()),
           "raw_KS": raw, "gross": [], "net": []}
    for c in c_values:
        r = c * rho
        # gross: correct -> save M-(alpha+v); wrong -> -v (scanned, ignored)
        gross = (np.where(correct, M - (alpha + v), -v)).sum() / totalM
        # net: wrong prediction is committed -> pay correction r, no save
        net = (np.where(correct, M - (alpha + v), -(v + r))).sum() / totalM
        out["gross"].append(float(gross))
        out["net"].append(float(net))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt2")
    ap.add_argument("--sentences", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-preds", type=int, default=None)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    records, name = measure(args.model, args.sentences, args.seed, args.max_preds)
    c_values = list(np.linspace(1.0, 10.0, 19))
    res = savings_curves(records, c_values)
    res["model"] = name
    res["c_values"] = c_values

    os.makedirs(RESULTS_DIR, exist_ok=True)
    tag = args.tag or name.replace("/", "_")
    with open(os.path.join(RESULTS_DIR, f"measured_{tag}.json"), "w") as f:
        json.dump(res, f, indent=2)
    # Per-prediction records for downstream confidence-gating analysis.
    with open(os.path.join(RESULTS_DIR, f"records_{tag}.json"), "w") as f:
        json.dump({"model": name,
                   "records": [[int(c), int(m), round(conf, 5)]
                               for (c, m, conf) in records]}, f)

    print(f"model={name}  n={res['n']}  measured top-1 p={res['p_top1']:.3f}"
          f"  mean_word_len={res['mean_word_len']:.2f}")
    print(f"raw KS (reported-style) = {res['raw_KS']*100:.1f}%")
    for c in (1.0, 2.0, 4.0, 6.0):
        i = c_values.index(min(c_values, key=lambda x: abs(x - c)))
        print(f"  c={c:.0f}:  gross={res['gross'][i]*100:5.1f}%   "
              f"net={res['net'][i]*100:6.1f}%")
    print(f"\nwrote results/measured_{tag}.json")


if __name__ == "__main__":
    main()

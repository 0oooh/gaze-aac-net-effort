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


def pick_device():
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_model(name, device=None):
    """Load any HuggingFace causal LM (GPT-2, Qwen2.5, Llama, SmolLM, ...)."""
    from transformers import AutoTokenizer, AutoModelForCausalLM
    device = device or pick_device()
    tok = AutoTokenizer.from_pretrained(name)
    dtype = torch.float16 if device in ("mps", "cuda") else torch.float32
    model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=dtype)
    model.to(device).eval()
    torch.manual_seed(0)
    return tok, model, device


@torch.no_grad()
def _complete_word(tok, model, device, first_id, ctx_past, max_tokens):
    """Greedily complete one word starting from first_id, reusing the context KV."""
    pieces = [first_id]
    last = torch.tensor([[first_id]], device=device)
    past = ctx_past
    for _ in range(1, max_tokens):
        out = model(last, past_key_values=past, use_cache=True)
        past = out.past_key_values
        nid = int(out.logits[0, -1].argmax())
        if tok.decode([nid]).startswith((" ", "▁")):  # next word started
            break
        pieces.append(nid)
        last = torch.tensor([[nid]], device=device)
    return tok.decode(pieces).strip()


@torch.no_grad()
def predict_topk_words(tok, model, device, context_text, k=5, max_tokens=6):
    """Return (top-k candidate next words, top-1 confidence).

    The context is forwarded once; the k most likely first tokens each branch
    from that shared KV cache and are greedily completed to a word. This
    approximates the top-k next *words* by top-k first-token beams -- a
    documented approximation (a longer word's later tokens are decoded greedily).
    """
    ids = tok.encode(context_text, return_tensors="pt").to(device)
    out = model(ids, use_cache=True)
    ctx_past = out.past_key_values
    logits = out.logits[0, -1].float()
    top1_conf = float(torch.softmax(logits, dim=-1).max())
    first_ids = torch.topk(logits, k).indices.tolist()
    words = [_complete_word(tok, model, device, fid, ctx_past, max_tokens)
             for fid in first_ids]
    return words, top1_conf


def measure(model_name, n_sentences, seed, max_preds=None):
    tok, model, device = load_model(model_name)
    sents = load_sentences(n_sentences, seed)
    records = []  # (top1, top3, top5, word_len, confidence)
    n_pred = 0
    for sent in sents:
        words = [w for w in sent if any(ch.isalnum() for ch in w)]
        for i in range(1, len(words)):
            context = " ".join(words[:i])
            target = clean_word(words[i])
            if not target:
                continue
            cands, conf = predict_topk_words(tok, model, device, context, k=5)
            cands = [clean_word(w) for w in cands]
            t1 = int(cands[:1].count(target) > 0)
            t3 = int(target in cands[:3])
            t5 = int(target in cands[:5])
            records.append((t1, t3, t5, len(target), conf))
            n_pred += 1
            if max_preds and n_pred >= max_preds:
                return records, model_name
    return records, model_name


def savings_curves(records, c_values, alpha=ALPHA, v=V_MID, rho=RHO_MID):
    rec = np.array(records, dtype=float)  # cols: t1,t3,t5,M,conf
    correct = rec[:, 0].astype(bool)
    M = rec[:, 3]
    totalM = float(M.sum())
    p = float(correct.mean())

    # raw KS: chars saved on correct predictions, no interaction cost.
    raw = float(M[correct].sum()) / totalM

    out = {"p_top1": p, "p_top3": float(rec[:, 1].mean()),
           "p_top5": float(rec[:, 2].mean()),
           "n": len(records), "mean_word_len": float(M.mean()),
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
                   "records": [[int(t1), int(t3), int(t5), int(m), round(conf, 5)]
                               for (t1, t3, t5, m, conf) in records]}, f)

    print(f"model={name}  n={res['n']}  top-1 p={res['p_top1']:.3f}"
          f"  top-3 p={res['p_top3']:.3f}  top-5 p={res['p_top5']:.3f}"
          f"  mean_word_len={res['mean_word_len']:.2f}")
    print(f"raw KS (reported-style) = {res['raw_KS']*100:.1f}%")
    for c in (1.0, 2.0, 4.0, 6.0):
        i = c_values.index(min(c_values, key=lambda x: abs(x - c)))
        print(f"  c={c:.0f}:  gross={res['gross'][i]*100:5.1f}%   "
              f"net={res['net'][i]*100:6.1f}%")
    print(f"\nwrote results/measured_{tag}.json")


if __name__ == "__main__":
    main()

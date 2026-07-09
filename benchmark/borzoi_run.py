#!/usr/bin/env python3
"""Borzoi/Flashzoi directional scoring on the frozen held-out set.
Runs on a GPU host (>=24GB VRAM). Scores ref/alt 524kb windows, reduces to a
signed direction per variant x context using context-matched track deltas.

Usage: python3 borzoi_run.py
Inputs (same dir): test_uniq_variants.parquet (unique test variants),
                   split_manifest.csv (for context mapping)
Output: borzoi_predictions.csv  (variant_id,rsid,context,borzoi_effect,borzoi_dir)
"""
import numpy as np, pandas as pd, torch, os
from borzoi_pytorch import Borzoi
from borzoi_pytorch.pytorch_borzoi_model import TRACKS_DF

SEQLEN = 524288
IDX = {"A":0,"C":1,"G":2,"T":3}

def one_hot(seq):
    x = np.zeros((4, len(seq)), dtype=np.float32)
    for i,b in enumerate(seq):
        j = IDX.get(b, -1)
        if j>=0: x[j,i]=1.0
    return x

# Context -> track biosample regex (Borzoi human tracks: DNASE/ATAC/CAGE/RNA)
CTX_PAT = {
 "K562 (erythroleukemia)":      r"K562",
 "HepG2 (hepatocellular)":      r"HepG2",
 "immune (THP-1 macrophage)":   r"macrophage|monocyte|CD14|myeloid|THP",
 "microglia (HMC3)":            r"macrophage|monocyte|microglia|myeloid",
 "brain (mouse tissue MPRA)":   r"brain|neuron|astrocyte|cortex",
 "HEK293T (control)":           r"HEK|embryonic kidney|kidney",
}
# assays whose delta reflects enhancer activity/accessibility
ASSAY_PAT = r"DNASE|ATAC|CAGE"

def fetch_seq(chrom, pos, flank=SEQLEN//2):
    # On the GPU host, use a local genome FASTA or pyfaidx; here we assume a
    # prefetched sequences file 'seqs_524kb.npz' keyed by rsid to avoid network.
    raise NotImplementedError("provide seqs_524kb.npz keyed by rsid, or wire pyfaidx to a local hg38 FASTA")

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = Borzoi.from_pretrained("johahi/borzoi-replicate-0").to(device).eval()
    tdf = TRACKS_DF
    uniq = pd.read_parquet("test_uniq_variants.parquet")
    seqs = np.load("seqs_524kb.npz")  # rsid -> 524kb ref sequence string
    # precompute context -> track row indices
    ctx_idx = {}
    for ctx,pat in CTX_PAT.items():
        m = tdf["description"].str.contains(pat, case=False, regex=True, na=False) & \
            tdf["assay"].str.contains(ASSAY_PAT, case=False, regex=True, na=False)
        ctx_idx[ctx] = np.where(m.values)[0]
    rows=[]
    for r in uniq.itertuples():
        ref_seq = str(seqs[r.rsid])
        c = len(ref_seq)//2
        alt_seq = ref_seq[:c] + r.alt + ref_seq[c+1:]
        with torch.no_grad():
            xr = torch.tensor(one_hot(ref_seq)[None]).to(device)
            xa = torch.tensor(one_hot(alt_seq)[None]).to(device)
            yr = model(xr)[0].cpu().numpy()  # (T, bins)
            ya = model(xa)[0].cpu().numpy()
        # center bins
        b = yr.shape[1]//2
        cen = slice(b-4, b+4)
        for ctx in eval_contexts(r):
            ti = ctx_idx[ctx]
            if len(ti)==0: eff=np.nan
            else:
                dr = np.log2(ya[ti][:,cen].sum(1)+1) - np.log2(yr[ti][:,cen].sum(1)+1)
                eff = float(np.mean(dr))
            rows.append(dict(rsid=r.rsid, context=ctx, borzoi_effect=eff,
                             borzoi_dir=int(np.sign(eff)) if eff==eff else 0))
    pd.DataFrame(rows).to_csv("borzoi_predictions.csv", index=False)
    print("wrote borzoi_predictions.csv", len(rows), "rows")

def eval_contexts(r):
    # contexts this variant is tested in — from split_manifest
    global _man
    return _man[_man.rsid==r.rsid].context.unique().tolist()

if __name__ == "__main__":
    _man = pd.read_csv("split_manifest.csv")
    _man = _man[_man.fold=="test"]
    main()

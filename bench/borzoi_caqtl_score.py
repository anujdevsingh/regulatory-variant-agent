#!/usr/bin/env python3
"""Borzoi directional scoring on Kosoy microglia caQTL test variants.
Direction = sign(alt - ref) over central bins, microglia/macrophage ATAC+DNase tracks.
"""
import json, numpy as np, pandas as pd, torch
from borzoi_pytorch import Borzoi
from borzoi_pytorch.pytorch_borzoi_model import TRACKS_DF
import pysam

DEV = "cuda" if torch.cuda.is_available() else "cpu"
SEQLEN = 524288
CENTER_BINS = 5
MG_RX = r"microglia|macrophage|monocyte|myeloid|CD14|dendritic"

model = Borzoi.from_pretrained("johahi/borzoi-replicate-0").to(DEV).eval()

# accessibility tracks (DNASE/ATAC) in microglia/macrophage lineage
desc = TRACKS_DF["description"].astype(str)
acc = desc.str.upper().str.contains("DNASE") | desc.str.upper().str.contains("ATAC")
mg  = desc.str.contains(MG_RX, case=False, regex=True, na=False)
sel = TRACKS_DF.index[acc & mg].tolist()
print(f"microglia/macrophage accessibility tracks: {len(sel)}", flush=True)
print("sample:", desc[sel][:8].tolist(), flush=True)

fa = pysam.FastaFile("hg38.fa")
BASE = {"A":0,"C":1,"G":2,"T":3}
def onehot(seq):
    x = np.zeros((4,len(seq)),dtype=np.float32)
    for i,b in enumerate(seq):
        j = BASE.get(b,-1)
        if j>=0: x[j,i]=1.0
    return x

def predict(chrom, pos, allele):
    half = SEQLEN//2
    start = pos-1-half; end = pos-1+half
    s = fa.fetch(chrom, max(0,start), end).upper()
    if start<0: s = "N"*(-start)+s
    if len(s)<SEQLEN: s = s + "N"*(SEQLEN-len(s))
    s = list(s[:SEQLEN]); s[half] = allele
    x = torch.tensor(onehot("".join(s))[None]).to(DEV)
    with torch.no_grad():
        y = model(x)[0].detach().cpu().numpy()   # (tracks, bins)
    mid = y.shape[1]//2
    sl = slice(mid-CENTER_BINS//2, mid+CENTER_BINS//2+1)
    return float(y[sel][:, sl].mean())

df = pd.read_csv("caqtl_test_for_borzoi.csv")
out = {}
for i,r in df.iterrows():
    ch = f"chr{r.chrom}"
    try:
        rv = predict(ch, int(r.pos_hg38), r.ref)
        av = predict(ch, int(r.pos_hg38), r.alt)
        out[r.variant_id] = av - rv
    except Exception as e:
        out[r.variant_id] = None
        print(f"ERR {r.variant_id}: {e}", flush=True)
    if i%50==0: print(f"{i}/{len(df)}", flush=True)
json.dump(out, open("borzoi_caqtl_scores.json","w"))
n=len([v for v in out.values() if v is not None])
z=len([v for v in out.values() if v==0.0])
print(f"DONE {n} scored, {z} exactly-zero", flush=True)

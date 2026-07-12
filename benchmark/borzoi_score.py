#!/usr/bin/env python3
"""Borzoi/Flashzoi directional scoring on the held-out benchmark set.
Fetches inputs from the public repo, scores ref/alt accessibility per context, writes JSON."""
import sys, json, numpy as np, pandas as pd, urllib.request, io, time

REPO="https://raw.githubusercontent.com/anujdevsingh/regulatory-direction-independence/main"
def fetch(path):
    for _ in range(5):
        try: return urllib.request.urlopen(f"{REPO}/{path}", timeout=60).read()
        except Exception as e:
            print("retry", path, e); time.sleep(3)
    raise RuntimeError(path)

# --- load test variants (from committed benchmark) ---
tv = pd.read_csv(io.BytesIO(fetch("benchmark/split_manifest.csv")), dtype={"chrom":str})
tv = tv[tv.fold=="test"].copy()
print("test rows:", len(tv), "unique variant_id:", tv.variant_id.nunique(), flush=True)

# --- Borzoi ---
import torch
from borzoi_pytorch import Borzoi
from borzoi_pytorch.pytorch_borzoi_model import TRACKS_DF as T
dev="cuda"
model = Borzoi.from_pretrained("johahi/borzoi-replicate-0").to(dev).eval()
SEQLEN=524288
print("model loaded; tracks", T.shape, flush=True)

# accessibility tracks (DNASE/ATAC) + context biosample regex
desc = T["description"].astype(str)
is_acc = desc.str.contains("DNASE|ATAC", case=False)
CTX_RX = {
 "K562 (erythroleukemia)": r"K562",
 "HepG2 (hepatocellular)": r"HepG2",
 "HEK293T (control)": r"HEK|embryonic kidney|293",
 "immune (THP-1 macrophage)": r"macrophage|monocyte|THP|myeloid|CD14",
 "microglia (HMC3)": r"macrophage|monocyte|microglia|myeloid",
 "brain (mouse tissue MPRA)": r"neuron|astrocyte|brain|cortex|neural",
}
ctx_track_idx={}
for ctx,rx in CTX_RX.items():
    idx = T[is_acc & desc.str.contains(rx, case=False)].index.to_numpy()
    ctx_track_idx[ctx]=idx
    print("ctx", ctx, "n_tracks", len(idx), flush=True)

# --- sequence fetch: UCSC DAS or twobit via API; use UCSC REST ---
CHROM_LEN={"1":248956422,"2":242193529,"3":198295559,"4":190214555,"5":181538259,
"6":170805979,"7":159345973,"8":145138636,"9":138394717,"10":133797422,"11":135086622,
"12":133275309,"13":114364328,"14":107043718,"15":101991189,"16":90338345,"17":83257441,
"18":80373285,"19":58617616,"20":64444167,"21":46709983,"22":50818468,"X":156040895,"Y":57227415}

def get_seq(chrom, center, length=SEQLEN):
    half=length//2
    start=center-half-1; end=center+half-1  # 0-based, center is 1-based pos -> center base at index half
    clen=CHROM_LEN.get(str(chrom), 250000000)
    lpad = max(0, -start); rpad = max(0, end-clen)
    fstart=max(0,start); fend=min(clen,end)
    url=f"https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=chr{chrom};start={fstart};end={fend}"
    for _ in range(5):
        try:
            j=json.loads(urllib.request.urlopen(url, timeout=90).read())
            seq=j["dna"].upper()
            seq="N"*lpad + seq + "N"*rpad  # pad to full length; center stays at index half
            if len(seq)!=length: seq=seq[:length].ljust(length,"N")
            return seq
        except Exception as e:
            print("seq retry", e); time.sleep(3)
    raise RuntimeError(f"seq {chrom}:{center}")

MAP={"A":0,"C":1,"G":2,"T":3}
def one_hot(seq):
    x=np.zeros((4,len(seq)),dtype=np.float32)
    for i,b in enumerate(seq):
        j=MAP.get(b,-1)
        if j>=0: x[j,i]=1.0
    return x

@torch.no_grad()
def predict(x):  # x: (4,L)
    t=torch.from_numpy(x[None]).to(dev)
    out=model(t)  # (1, T, bins)
    return out[0].float().cpu().numpy()

# center bin range for the variant (middle bins)
def center_score(pred, track_idx):
    nb=pred.shape[1]; c=nb//2
    win=pred[track_idx, c-2:c+3]  # 5 central bins ~160bp
    return float(win.mean())

uniq = tv.drop_duplicates("variant_id")[["variant_id","chrom","pos_hg38","ref","alt"]].reset_index(drop=True)
results={}
t0=time.time()
for i,row in uniq.iterrows():
    seq=get_seq(row.chrom, int(row.pos_hg38))
    half=len(seq)//2
    # ref: ensure center base = ref (UCSC gives reference genome)
    center_base=seq[half]
    ref_seq=seq
    alt_seq=seq[:half]+row.alt+seq[half+1:]
    xr=one_hot(ref_seq); xa=one_hot(alt_seq)
    pr=predict(xr); pa=predict(xa)
    rec={"center_base":center_base,"ref":row.ref,"alt":row.alt}
    for ctx,idx in ctx_track_idx.items():
        if len(idx)==0: continue
        d=center_score(pa,idx)-center_score(pr,idx)  # alt - ref
        rec[ctx]=d
    results[row.variant_id]=rec
    if (i+1)%25==0: print(f"  {i+1}/{len(uniq)}  {time.time()-t0:.0f}s", flush=True)

json.dump({"results":results,"n":len(results),"ctx_track_counts":{k:len(v) for k,v in ctx_track_idx.items()}},
          open("borzoi_scores.json","w"))
print("DONE", len(results), "variants", f"{time.time()-t0:.0f}s", flush=True)

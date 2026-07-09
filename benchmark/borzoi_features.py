#!/usr/bin/env python3
"""Extract Borzoi per-context accessibility-delta features for ALL harmonized variants
(train+test), batched. Output: borzoi_features.json {variant_id: {ctx: delta,...}}."""
import json, numpy as np, pandas as pd, urllib.request, io, time
REPO="https://raw.githubusercontent.com/anujdevsingh/regulatory-variant-agent/main"
def fetch(path):
    for _ in range(6):
        try: return urllib.request.urlopen(f"{REPO}/{path}", timeout=60).read()
        except Exception as e: print("retry",path,e); time.sleep(3)
    raise RuntimeError(path)
man=pd.read_csv(io.BytesIO(fetch("benchmark/split_manifest.csv")), dtype={"chrom":str})
uniq=man.drop_duplicates("variant_id")[["variant_id","chrom","pos_hg38","ref","alt"]].reset_index(drop=True)
print("unique variants:", len(uniq), flush=True)

import torch
from borzoi_pytorch import Borzoi
from borzoi_pytorch.pytorch_borzoi_model import TRACKS_DF as T
dev="cuda"; SEQLEN=524288
model=Borzoi.from_pretrained("johahi/borzoi-replicate-0").to(dev).eval()
desc=T["description"].astype(str); is_acc=desc.str.contains("DNASE|ATAC",case=False)
CTX_RX={"K562 (erythroleukemia)":r"K562","HepG2 (hepatocellular)":r"HepG2",
"HEK293T (control)":r"HEK|embryonic kidney|293","immune (THP-1 macrophage)":r"macrophage|monocyte|THP|myeloid|CD14",
"microglia (HMC3)":r"macrophage|monocyte|microglia|myeloid","brain (mouse tissue MPRA)":r"neuron|astrocyte|brain|cortex|neural"}
ctx_idx={c:T[is_acc&desc.str.contains(rx,case=False)].index.to_numpy() for c,rx in CTX_RX.items()}
print("track counts:",{c:len(v) for c,v in ctx_idx.items()},flush=True)

CHROM_LEN={"1":248956422,"2":242193529,"3":198295559,"4":190214555,"5":181538259,"6":170805979,
"7":159345973,"8":145138636,"9":138394717,"10":133797422,"11":135086622,"12":133275309,"13":114364328,
"14":107043718,"15":101991189,"16":90338345,"17":83257441,"18":80373285,"19":58617616,"20":64444167,
"21":46709983,"22":50818468,"X":156040895,"Y":57227415}
def get_seq(chrom,center,length=SEQLEN):
    half=length//2; start=center-half-1; end=center+half-1
    clen=CHROM_LEN.get(str(chrom),250000000); lpad=max(0,-start); rpad=max(0,end-clen)
    fstart=max(0,start); fend=min(clen,end)
    url=f"https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=chr{chrom};start={fstart};end={fend}"
    for _ in range(6):
        try:
            j=json.loads(urllib.request.urlopen(url,timeout=90).read()); seq=j["dna"].upper()
            seq="N"*lpad+seq+"N"*rpad
            if len(seq)!=length: seq=seq[:length].ljust(length,"N")
            return seq
        except Exception as e: print("seq retry",e); time.sleep(3)
    raise RuntimeError(f"seq {chrom}:{center}")
MAP={"A":0,"C":1,"G":2,"T":3}
def oh(seq):
    x=np.zeros((4,len(seq)),dtype=np.float32)
    for i,b in enumerate(seq):
        j=MAP.get(b,-1)
        if j>=0: x[j,i]=1.0
    return x
@torch.no_grad()
def predict_batch(xs):  # list of (4,L)
    t=torch.from_numpy(np.stack(xs)).to(dev)
    out=model(t)  # (B,T,bins)
    return out.float().cpu().numpy()
def cscore(pred,idx):
    nb=pred.shape[1]; c=nb//2; return pred[idx,c-2:c+3].mean()

BATCH=4
feats={}; t0=time.time(); buf=[]; meta=[]
def flush():
    global buf,meta
    if not buf: return
    preds=predict_batch(buf)
    # preds rows alternate ref,alt for each variant in meta
    for k,(vid) in enumerate(meta):
        pr=preds[2*k]; pa=preds[2*k+1]
        feats[vid]={c:float(cscore(pa,idx)-cscore(pr,idx)) for c,idx in ctx_idx.items() if len(idx)>0}
    buf=[]; meta=[]
for i,row in uniq.iterrows():
    seq=get_seq(row.chrom,int(row.pos_hg38)); half=len(seq)//2
    alt=seq[:half]+row.alt+seq[half+1:]
    buf.append(oh(seq)); buf.append(oh(alt)); meta.append(row.variant_id)
    if len(meta)>=BATCH: flush()
    if (i+1)%40==0: print(f"  {i+1}/{len(uniq)} {time.time()-t0:.0f}s",flush=True)
flush()
json.dump({"features":feats,"n":len(feats),"ctx_track_counts":{c:len(v) for c,v in ctx_idx.items()}},
          open("borzoi_features.json","w"))
print("DONE",len(feats),f"{time.time()-t0:.0f}s",flush=True)

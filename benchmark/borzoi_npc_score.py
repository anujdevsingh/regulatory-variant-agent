#!/usr/bin/env python3
"""Borzoi directional scoring on the 788 NPC test variants (brain-lineage MPRA expansion)."""
import json, numpy as np, pandas as pd, urllib.request, time

tv = pd.read_csv("npc_test_for_borzoi.csv", dtype={"chrom":str})
print("NPC test rows:", len(tv), "unique:", tv.variant_id.nunique(), flush=True)

import torch
from borzoi_pytorch import Borzoi
from borzoi_pytorch.pytorch_borzoi_model import TRACKS_DF as T
dev="cuda"
model = Borzoi.from_pretrained("johahi/borzoi-replicate-0").to(dev).eval()
SEQLEN=524288
print("model loaded; tracks", T.shape, "cuda", torch.cuda.is_available(), flush=True)

desc = T["description"].astype(str)
is_acc = desc.str.contains("DNASE|ATAC", case=False)
# NPC = neural progenitor -> neural/brain accessibility tracks (same family as brain context)
NPC_RX = r"neuron|astrocyte|brain|cortex|neural|neuroblastoma|SH-SY5Y|glia|hippocamp|iPSC.*neuro"
npc_idx = T[is_acc & desc.str.contains(NPC_RX, case=False)].index.to_numpy()
print("NPC neural accessibility tracks:", len(npc_idx), flush=True)
# show a few track descriptions for the record
for k in npc_idx[:12]: print("  track:", desc.loc[k], flush=True)

CHROM_LEN={"1":248956422,"2":242193529,"3":198295559,"4":190214555,"5":181538259,
"6":170805979,"7":159345973,"8":145138636,"9":138394717,"10":133797422,"11":135086622,
"12":133275309,"13":114364328,"14":107043718,"15":101991189,"16":90338345,"17":83257441,
"18":80373285,"19":58617616,"20":64444167,"21":46709983,"22":50818468,"X":156040895,"Y":57227415}

def get_seq(chrom, center, length=SEQLEN):
    half=length//2
    start=center-half-1; end=center+half-1
    clen=CHROM_LEN.get(str(chrom),250000000)
    lpad=max(0,-start); rpad=max(0,end-clen)
    fstart=max(0,start); fend=min(clen,end)
    url=f"https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=chr{chrom};start={fstart};end={fend}"
    for _ in range(5):
        try:
            j=json.loads(urllib.request.urlopen(url,timeout=90).read()); seq=j["dna"].upper()
            seq="N"*lpad+seq+"N"*rpad
            if len(seq)!=length: seq=seq[:length].ljust(length,"N")
            return seq
        except Exception as e:
            print("seq retry",e); time.sleep(3)
    raise RuntimeError(f"seq {chrom}:{center}")

MAP={"A":0,"C":1,"G":2,"T":3}
def one_hot(seq):
    x=np.zeros((4,len(seq)),dtype=np.float32)
    for i,b in enumerate(seq):
        j=MAP.get(b,-1)
        if j>=0: x[j,i]=1.0
    return x

@torch.no_grad()
def predict(x):
    t=torch.from_numpy(x[None]).to(dev)
    return model(t)[0].float().cpu().numpy()

def center_score(pred, idx):
    nb=pred.shape[1]; c=nb//2
    return float(pred[idx, c-2:c+3].mean())

uniq=tv.drop_duplicates("variant_id")[["variant_id","chrom","pos_hg38","ref","alt"]].reset_index(drop=True)
results={}; t0=time.time()
for i,row in uniq.iterrows():
    seq=get_seq(row.chrom,int(row.pos_hg38)); half=len(seq)//2
    center_base=seq[half]
    ref_seq=seq; alt_seq=seq[:half]+row.alt+seq[half+1:]
    pr=predict(one_hot(ref_seq)); pa=predict(one_hot(alt_seq))
    d=center_score(pa,npc_idx)-center_score(pr,npc_idx)
    results[row.variant_id]={"center_base":center_base,"ref":row.ref,"alt":row.alt,"npc_delta":d}
    if (i+1)%25==0: print(f"  {i+1}/{len(uniq)} {time.time()-t0:.0f}s",flush=True)
json.dump({"results":results,"n":len(results),"npc_track_count":int(len(npc_idx))},open("borzoi_npc_scores.json","w"))
print("DONE",len(results),f"{time.time()-t0:.0f}s",flush=True)

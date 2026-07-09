#!/usr/bin/env python3
import json, numpy as np, pandas as pd, urllib.request, time
tv=pd.read_csv("chen_test_for_borzoi.csv", dtype={"chrom":str})
print("Chen test rows:", len(tv), flush=True)
import torch
from borzoi_pytorch import Borzoi
from borzoi_pytorch.pytorch_borzoi_model import TRACKS_DF as T
dev="cuda"; model=Borzoi.from_pretrained("johahi/borzoi-replicate-0").to(dev).eval()
SEQLEN=524288
desc=T["description"].astype(str); is_acc=desc.str.contains("DNASE|ATAC",case=False)
MG_RX=r"macrophage|monocyte|microglia|myeloid|CD14"
SH_RX=r"neuron|astrocyte|brain|cortex|neural|neuroblastoma|SH-SY5Y"
mg_idx=T[is_acc & desc.str.contains(MG_RX,case=False)].index.to_numpy()
sh_idx=T[is_acc & desc.str.contains(SH_RX,case=False)].index.to_numpy()
print("MG tracks",len(mg_idx),"SH tracks",len(sh_idx),flush=True)
CL={"1":248956422,"2":242193529,"3":198295559,"4":190214555,"5":181538259,"6":170805979,"7":159345973,"8":145138636,"9":138394717,"10":133797422,"11":135086622,"12":133275309,"13":114364328,"14":107043718,"15":101991189,"16":90338345,"17":83257441,"18":80373285,"19":58617616,"20":64444167,"21":46709983,"22":50818468,"X":156040895,"Y":57227415}
def get_seq(chrom,center,length=SEQLEN):
    half=length//2; start=center-half-1; end=center+half-1; clen=CL.get(str(chrom),250000000)
    lpad=max(0,-start); rpad=max(0,end-clen); fs=max(0,start); fe=min(clen,end)
    url=f"https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom=chr{chrom};start={fs};end={fe}"
    for _ in range(5):
        try:
            j=json.loads(urllib.request.urlopen(url,timeout=90).read()); s=j["dna"].upper(); s="N"*lpad+s+"N"*rpad
            return (s[:length].ljust(length,"N"))
        except Exception as e: print("retry",e); time.sleep(3)
    raise RuntimeError(f"{chrom}:{center}")
MAP={"A":0,"C":1,"G":2,"T":3}
def oh(seq):
    x=np.zeros((4,len(seq)),dtype=np.float32)
    for i,b in enumerate(seq):
        j=MAP.get(b,-1)
        if j>=0: x[j,i]=1.0
    return x
@torch.no_grad()
def pred(x): return model(torch.from_numpy(x[None]).to(dev))[0].float().cpu().numpy()
def cs(p,idx): nb=p.shape[1]; c=nb//2; return float(p[idx,c-2:c+3].mean())
res={}; t0=time.time()
for i,row in tv.iterrows():
    idx=mg_idx if "microglia" in row.context else sh_idx
    seq=get_seq(row.chrom,int(row.pos_hg38)); half=len(seq)//2
    pr=pred(oh(seq)); pa=pred(oh(seq[:half]+row.alt+seq[half+1:]))
    res[row.variant_id]={"delta":cs(pa,idx)-cs(pr,idx),"context":row.context,"center":seq[half]}
    if (i+1)%25==0: print(f"  {i+1}/{len(tv)} {time.time()-t0:.0f}s",flush=True)
json.dump({"results":res,"n":len(res),"mg_tracks":int(len(mg_idx)),"sh_tracks":int(len(sh_idx))},open("borzoi_chen_scores.json","w"))
print("DONE",len(res),f"{time.time()-t0:.0f}s",flush=True)

#!/usr/bin/env python3
"""Wedge model: grammar-aware directional prediction.
Features = motif-Δ (49) + Borzoi per-context accessibility deltas + motif-grammar
(co-occurrence/interaction) + context one-hot. GBT trained on NON-TEST folds only.
Eval on identical held-out set with bootstrap CIs. Two regimes: cross-context & on-wedge-only.
"""
import json, numpy as np, pandas as pd, pickle
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score

SEED=0
data=pd.read_parquet("bench/data_with_features.parquet")  # motif features + fold + context
data["chrom"]=data["chrom"].astype(str)
feat_meta=json.load(open("bench/feat_meta.json")); motif_cols=feat_meta["feat_cols"]

# --- Borzoi per-context features ---
bz=json.load(open("bench/borzoi_features.json"))["features"]
CTXS=["K562 (erythroleukemia)","HepG2 (hepatocellular)","HEK293T (control)",
      "immune (THP-1 macrophage)","microglia (HMC3)","brain (mouse tissue MPRA)"]
def bz_vec(vid):
    r=bz.get(vid,{})
    return [r.get(c,0.0) for c in CTXS]
bzmat=np.array([bz_vec(v) for v in data.variant_id])
for i,c in enumerate(CTXS):
    data[f"bz_{i}"]=bzmat[:,i]
# Borzoi delta IN THE VARIANT'S OWN CONTEXT (the matched-track signal)
ctx_to_i={c:i for i,c in enumerate(CTXS)}
data["bz_own"]=[bz.get(v,{}).get(c,0.0) for v,c in zip(data.variant_id,data.context)]
bz_cols=[f"bz_{i}" for i in range(len(CTXS))]+["bz_own"]

# --- motif-grammar interaction features ---
# top wedge TFs (by column-name substring) x their co-occurrence products
wedge_tf=[c for c in motif_cols if any(k in c.upper() for k in
          ["SPI1","MEF2","CEBP","ETS","IRF","NFKB","RELB","SPIB","RUNX","BATF","FOS","JUN"])]
M=data[motif_cols].values
# grammar feat 1: max resident motif magnitude (context of the variant window)
data["gram_maxabs"]=np.abs(M).max(1)
# grammar feat 2: n motifs with |Δ|>1 bit (how many motifs the variant perturbs)
data["gram_ncoop"]=(np.abs(M)>1.0).sum(1)
# grammar feat 3: signed sum over wedge TFs (net activator/repressor shift)
data["gram_wedge_sum"]=data[wedge_tf].sum(1) if wedge_tf else 0.0
# grammar feat 4: product of largest positive and largest negative motif Δ (grammar conflict)
data["gram_conflict"]=M.max(1)*M.min(1)
gram_cols=["gram_maxabs","gram_ncoop","gram_wedge_sum","gram_conflict"]

# --- context one-hot ---
for c in CTXS: data[f"ctx_{ctx_to_i[c]}"]=(data.context==c).astype(int)
ctx_cols=[f"ctx_{i}" for i in range(len(CTXS))]

ALL_FEATS=motif_cols+bz_cols+gram_cols+ctx_cols
data["y"]=(data.direction>0).astype(int)
train=data[data.fold=="train"].copy(); test=data[data.fold=="test"].copy().reset_index(drop=True)
print("train",len(train),"test",len(test),"feats",len(ALL_FEATS),flush=True)

wedge_ctx=["immune (THP-1 macrophage)","microglia (HMC3)","brain (mouse tissue MPRA)"]
rng=np.random.default_rng(SEED)
def boot_ci(y,pred,score,nb=2000):
    y=np.asarray(y);pred=np.asarray(pred);score=np.asarray(score);n=len(y)
    acc=(pred==y).mean()
    try: au=roc_auc_score(y,score) if len(np.unique(y))>1 else np.nan
    except: au=np.nan
    A=[];U=[]
    for _ in range(nb):
        ix=rng.integers(0,n,n);A.append((pred[ix]==y[ix]).mean());yy=y[ix]
        if len(np.unique(yy))>1:
            try:U.append(roc_auc_score(yy,score[ix]))
            except:pass
    al,ah=np.percentile(A,[2.5,97.5]);ul,uh=(np.percentile(U,[2.5,97.5]) if U else (np.nan,np.nan))
    return dict(acc=acc,acc_lo=al,acc_hi=ah,auroc=au,auc_lo=ul,auc_hi=uh,n=int(n))

def eval_model(clf, tr, te, label):
    clf.fit(tr[ALL_FEATS].values, tr.y.values)
    te=te.copy()
    te["p"]=clf.predict_proba(te[ALL_FEATS].values)[:,1]
    te["pred"]=(te.p>0.5).astype(int)
    rows=[]
    for ctx in ["ALL"]+CTXS+["WEDGE-POOLED"]:
        if ctx=="ALL": sub=te
        elif ctx=="WEDGE-POOLED": sub=te[te.context.isin(wedge_ctx)]
        else: sub=te[te.context==ctx]
        if len(sub)<5: continue
        r=boot_ci(sub.y.values,sub.pred.values,sub.p.values); r.update(context=ctx,model=label); rows.append(r)
    return pd.DataFrame(rows), te, clf

# Regime A: cross-context (train on ALL non-test folds incl off-wedge)
gbt=HistGradientBoostingClassifier(max_depth=3,max_iter=300,learning_rate=0.05,
    min_samples_leaf=20,l2_regularization=1.0,early_stopping=True,validation_fraction=0.2,
    random_state=SEED)
resA,teA,clfA=eval_model(gbt,train,test,"Wedge-GBT (cross-context)")

# Regime A2: logistic on same features (regularized linear alternative)
lr=make_pipeline(StandardScaler(),LogisticRegression(max_iter=3000,C=0.5,random_state=SEED))
resA2,teA2,clfA2=eval_model(lr,train,test,"Wedge-Logistic (cross-context)")

# Regime B: on-wedge-only training (honest lower bound)
trw=train[train.context.isin(wedge_ctx)].copy()
gbtB=HistGradientBoostingClassifier(max_depth=2,max_iter=150,learning_rate=0.05,
    min_samples_leaf=8,l2_regularization=2.0,random_state=SEED)
try:
    resB,teB,clfB=eval_model(gbtB,trw,test,"Wedge-GBT (on-wedge only)")
except Exception as e:
    print("regime B failed:",e); resB=pd.DataFrame()

allres=pd.concat([resA,resA2,resB],ignore_index=True)
allres.to_csv("bench/wedge_results.csv",index=False)
pickle.dump({"model":clfA,"feats":ALL_FEATS,"seed":SEED},open("bench/wedge_model.pkl","wb"))
teA[["variant_id","rsid","context","direction","y","p","pred"]].to_csv("bench/wedge_predictions.csv",index=False)

print("\n=== WEDGE MODEL RESULTS (on-wedge pooled) ===",flush=True)
for lab in allres.model.unique():
    r=allres[(allres.model==lab)&(allres.context=="WEDGE-POOLED")]
    if len(r): 
        rr=r.iloc[0]; print(f"{lab}: {rr.acc:.3f} [{rr.acc_lo:.3f},{rr.acc_hi:.3f}] AUROC {rr.auroc:.3f} n={int(rr.n)}",flush=True)
print("\nrs6733839:")
rs=teA[teA.rsid=="rs6733839"][["context","direction","p","pred"]]
print(rs.to_string(index=False),flush=True)

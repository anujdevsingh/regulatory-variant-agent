#!/usr/bin/env python
"""
score_variant.py — trace a noncoding variant to the TF motif it affects, from sequence.

Reusable pipeline (built with Claude Science):
  rsID/coords -> fetch GRCh38 window -> ChromBPNet ref/alt prediction
             -> cell-type scan -> in-silico mutagenesis -> JASPAR motif scan

Example:
  python score_variant.py --rsid rs6733839 \
      --model models/Microglia_chrombpnet_nobias.h5 --outdir results/

Models: the 6 brain cell-type ChromBPNet models (Microglia, Astrocytes, Excitatory/
Inhibitory neurons, Oligodendrocytes, OPCs) from PsychENCODE, Zenodo 10.5281/zenodo.10605867
(trained on Corces scATAC pseudobulk; see SCOPING.md). Download the tar, extract
Zenodo/data/chrombpnet/*_chrombpnet_nobias.h5.
"""
import argparse, json, os, urllib.request
import numpy as np

INPUT_LEN = 2114
BASES = "ACGT"; BIDX = {b: i for i, b in enumerate(BASES)}

def fetch_variant(rsid):
    """Resolve an rsID to GRCh38 (chrom, 1-based pos, ref, alt) via Ensembl."""
    url = f"https://rest.ensembl.org/variation/human/{rsid}"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    j = json.loads(urllib.request.urlopen(req, timeout=40).read().decode())
    m = next(x for x in j["mappings"] if x["assembly_name"] == "GRCh38")
    alleles = m["allele_string"].split("/")  # e.g. C/G/T
    ref = alleles[0]
    alt = j.get("minor_allele") or alleles[1]
    return m["seq_region_name"], int(m["start"]), ref, alt

def fetch_window(chrom, pos):
    """Fetch the INPUT_LEN window centered on a 1-based position (GRCh38)."""
    start = pos - INPUT_LEN // 2
    end = start + INPUT_LEN - 1
    url = (f"https://api.genome.ucsc.edu/getData/sequence?"
           f"genome=hg38;chrom=chr{chrom};start={start-1};end={end}")
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    seq = json.loads(urllib.request.urlopen(req, timeout=40).read().decode())["dna"].upper()
    assert len(seq) == INPUT_LEN
    return seq, start, pos - start  # sequence, window start, variant index

def onehot(s):
    a = np.zeros((len(s), 4), np.float32)
    for i, c in enumerate(s):
        if c in BIDX: a[i, BIDX[c]] = 1
    return a

def predict(model, X):
    prof, lc = model.predict(X, verbose=0)
    return prof, lc.squeeze(-1)

def score(model, ref_seq, alt_seq):
    from scipy.special import softmax
    from scipy.spatial.distance import jensenshannon
    X = np.stack([onehot(ref_seq), onehot(alt_seq)])
    prof, lc = predict(model, X)
    log2fc = (lc[1] - lc[0]) / np.log(2)
    jsd = float(jensenshannon(softmax(prof[0]), softmax(prof[1]), base=2))
    return dict(ref_count=float(np.exp(lc[0])), alt_count=float(np.exp(lc[1])),
                log2fc=float(log2fc), jsd=jsd)

def ism(model, ref_seq, vidx, half=25):
    """Saturation ISM around the variant: mean |Δ log-count| per position."""
    ref = onehot(ref_seq)
    base_lc = predict(model, ref[None])[1][0]
    seqs, meta = [], []
    for p in range(vidx - half, vidx + half + 1):
        rb = int(ref[p].argmax())
        for b in range(4):
            if b == rb: continue
            s = ref.copy(); s[p] = 0; s[p, b] = 1
            seqs.append(s); meta.append(p)
    lc = predict(model, np.array(seqs))[1]
    delta = np.abs(lc - base_lc)
    imp = {}
    for p, d in zip(meta, delta):
        imp.setdefault(p, []).append(d)
    positions = list(range(vidx - half, vidx + half + 1))
    return np.array([np.mean(imp[p]) for p in positions]), np.arange(-half, half + 1)

def jaspar_pfm(mid):
    url = f"https://jaspar.elixir.no/api/v1/matrix/{mid}/"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    j = json.loads(urllib.request.urlopen(req, timeout=40).read().decode())
    return j["name"], np.array([j["pfm"][b] for b in BASES], float)

def pwm_logodds(M, bg=0.25, pseudo=0.5):
    M = M + pseudo
    return np.log2((M / M.sum(0, keepdims=True)) / bg)

def revcomp(s):
    c = {"A": "T", "T": "A", "C": "G", "G": "C", "N": "N"}
    return "".join(c[x] for x in reversed(s))

def best_overlap(seq, lo, vloc):
    L = lo.shape[1]; best = (-1e9, None, None)
    for strand in ["+", "-"]:
        s = seq if strand == "+" else revcomp(seq)
        for i in range(len(s) - L + 1):
            start = i if strand == "+" else len(seq) - L - i
            if not (start <= vloc <= start + L - 1): continue
            sc = sum(lo[BIDX[s[i + j]], j] for j in range(L) if s[i + j] in BIDX)
            if sc > best[0]: best = (sc, strand, start)
    return best

def motif_scan(ref_seq, alt_seq, vidx, motif_ids, half=25):
    lo, hi = vidx - half, vidx + half + 1
    ref_w, alt_w, vloc = ref_seq[lo:hi], alt_seq[lo:hi], half
    out = {}
    for mid in motif_ids:
        name, pfm = jaspar_pfm(mid)
        L = pwm_logodds(pfm)
        r = best_overlap(ref_w, L, vloc); a = best_overlap(alt_w, L, vloc)
        out[mid] = dict(name=name, ref_score=round(r[0], 2), alt_score=round(a[0], 2),
                        delta=round(a[0] - r[0], 2))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rsid"); ap.add_argument("--chrom"); ap.add_argument("--pos", type=int)
    ap.add_argument("--ref"); ap.add_argument("--alt")
    ap.add_argument("--model", required=True, help="path to a *_chrombpnet_nobias.h5")
    ap.add_argument("--motifs", nargs="+", default=["MA0052.4", "MA0497.1"],
                    help="JASPAR matrix IDs to scan (default MEF2A, MEF2C)")
    ap.add_argument("--outdir", default="results")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    import tensorflow as tf

    if args.rsid:
        chrom, pos, ref, alt = fetch_variant(args.rsid)
        name = args.rsid
    else:
        chrom, pos, ref, alt = args.chrom, args.pos, args.ref, args.alt
        name = f"chr{chrom}:{pos}:{ref}>{alt}"
    seq, start, vidx = fetch_window(chrom, pos)
    assert seq[vidx] == ref, f"ref mismatch: window has {seq[vidx]}, expected {ref}"
    alt_seq = seq[:vidx] + alt + seq[vidx + 1:]

    model = tf.keras.models.load_model(args.model, compile=False)
    result = {"variant": name, "chrom": chrom, "pos_grch38": pos, "ref": ref, "alt": alt,
              "model": os.path.basename(args.model)}
    result["prediction"] = score(model, seq, alt_seq)
    imp, rel = ism(model, seq, vidx)
    result["ism_peak_rel"] = int(rel[int(imp.argmax())])
    result["ism_variant_importance"] = float(imp[len(imp)//2])
    result["motifs"] = motif_scan(seq, alt_seq, vidx, args.motifs)

    out = os.path.join(args.outdir, f"{name.replace(':','_').replace('>','_')}_result.json")
    json.dump(result, open(out, "w"), indent=2)
    print(json.dumps(result, indent=2))
    print(f"\nwritten: {out}")

if __name__ == "__main__":
    main()

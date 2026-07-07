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

def calibrate(model, obs_log2fc, null_bed, n_null=250, seed=7):
    """Locate an observed log2FC in a null of common SNPs sampled from an ATAC peak BED.

    Downloads/reads a narrowPeak BED, samples peaks, pulls common SNPs (MAF>=0.05,
    enriched by low rsID) inside them via Ensembl, scores each ref/alt through the
    same model, and returns the observed variant's percentile + z-score against the
    null distribution of |log2FC|. Standard "how big is this effect among accessible
    common variants" calibration.
    """
    import gzip, random
    rng = random.Random(seed)
    op = gzip.open if null_bed.endswith(".gz") else open
    peaks = []
    with op(null_bed, "rt") as f:
        for line in f:
            c = line.split("\t")
            ch = c[0].replace("chr", "")
            if ch in {str(i) for i in range(1, 23)} | {"X"} and int(c[2]) - int(c[1]) >= 200:
                peaks.append((ch, int(c[1]), int(c[2])))
    rng.shuffle(peaks)

    def overlap_snvs(ch, s, e):
        mid = (s + e) // 2
        url = (f"https://rest.ensembl.org/overlap/region/human/{ch}:{mid-450}-{mid+450}"
               "?feature=variation;content-type=application/json")
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
        try:
            recs = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        except Exception:
            return []
        out = []
        for r in recs:
            rid = r.get("id", "")
            if not rid.startswith("rs"):
                continue
            try:
                if int(rid[2:]) >= 200_000_000:  # low rsID enriches for common variants
                    continue
            except ValueError:
                continue
            al = r.get("alleles", [])
            if len(al) == 2 and all(len(x) == 1 and x in BASES for x in al) and r.get("start") == r.get("end"):
                out.append((rid, r["seq_region_name"], r["start"], al[0], al[1]))
        return out

    cand = {}
    for p in peaks:
        if len(cand) >= n_null * 4:
            break
        for rid, ch, pos, ref, alt in overlap_snvs(*p):
            cand[rid] = (ch, pos, ref, alt)
    # MAF filter (batched)
    ids = list(cand)
    common = []
    for i in range(0, len(ids), 200):
        chunk = ids[i:i + 200]
        req = urllib.request.Request("https://rest.ensembl.org/variation/human",
                                     data=json.dumps({"ids": chunk}).encode(),
                                     headers={"Content-Type": "application/json", "Accept": "application/json"})
        try:
            j = json.loads(urllib.request.urlopen(req, timeout=90).read().decode())
        except Exception:
            continue
        for rid, rec in j.items():
            if rec.get("MAF") is not None and float(rec["MAF"]) >= 0.05:
                common.append(rid)
    rng.shuffle(common)
    common = common[:n_null]
    # score null
    null = []
    for rid in common:
        ch, pos, ref, alt = cand[rid]
        try:
            seq, vidx = fetch_window(ch, pos)
        except Exception:
            continue
        if len(seq) != INPUT_LEN or seq[vidx] != ref:
            continue
        s = score(model, seq, seq[:vidx] + alt + seq[vidx + 1:])
        null.append(s["log2fc"])
    null = np.array(null)
    absn = np.abs(null)
    return {"null_n": int(len(null)),
            "null_mean": float(null.mean()), "null_sd": float(null.std()),
            "percentile_signed": float((null < obs_log2fc).mean() * 100),
            "percentile_abs": float((absn < abs(obs_log2fc)).mean() * 100),
            "zscore_abs": float((abs(obs_log2fc) - absn.mean()) / absn.std())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rsid"); ap.add_argument("--chrom"); ap.add_argument("--pos", type=int)
    ap.add_argument("--ref"); ap.add_argument("--alt")
    ap.add_argument("--model", required=True, help="path to a *_chrombpnet_nobias.h5")
    ap.add_argument("--motifs", nargs="+", default=["MA0052.4", "MA0497.1"],
                    help="JASPAR matrix IDs to scan (default MEF2A, MEF2C)")
    ap.add_argument("--outdir", default="results")
    ap.add_argument("--calibrate", metavar="PEAK_BED",
                    help="narrowPeak BED (.bed/.bed.gz); score a common-SNP null from these "
                         "peaks and report the variant's percentile + z-score")
    ap.add_argument("--n-null", type=int, default=250, help="null size for --calibrate")
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
    if args.calibrate:
        result["calibration"] = calibrate(model, result["prediction"]["log2fc"],
                                           args.calibrate, n_null=args.n_null)

    out = os.path.join(args.outdir, f"{name.replace(':','_').replace('>','_')}_result.json")
    json.dump(result, open(out, "w"), indent=2)
    print(json.dumps(result, indent=2))
    print(f"\nwritten: {out}")

if __name__ == "__main__":
    main()

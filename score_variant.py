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


# ---------------------------------------------------------------------------
# Credible-set mode: score a published fine-mapping credible set through the
# model and ask whether the fine-mapped variant also has the largest effect.
# ---------------------------------------------------------------------------
# Default column schema = Schwartzentruber et al. 2021 Nat Genet, Suppl. Table 8
# (sheet "8-SNP Fine-mapping"). Override any column via the --cs-col-* flags.
CS_DEFAULT_COLS = dict(locus="locus name", rsid="rsids", pos="pos hg38",
                       ref="ref", alt="alt", eff="Eff allele",
                       prob="mean prob", gwas_p="GWAS P")


def parse_credible_set(xlsx, locus, min_prob=0.01, sheet="8-SNP Fine-mapping",
                       cols=None):
    """Read a fine-mapping supplementary table and return the credible set.

    Filters to `locus`, keeps biallelic SNVs with fine-mapping probability
    >= `min_prob`, and resolves which allele to score (the fine-mapping effect
    allele when it differs from ref; otherwise the alternate). Returns a list
    of dicts sorted by descending probability.
    """
    import pandas as pd
    c = dict(CS_DEFAULT_COLS, **(cols or {}))
    df = pd.read_excel(xlsx, sheet_name=sheet, header=0)
    sub = df[df[c["locus"]].astype(str) == locus].copy()
    if sub.empty:
        raise SystemExit(f"no rows for locus {locus!r} in column {c['locus']!r}; "
                         f"available loci include: "
                         f"{sorted(df[c['locus']].dropna().astype(str).unique())[:10]}")
    sub = sub[sub[c["prob"]].astype(float) >= min_prob]
    rows = []
    for _, r in sub.iterrows():
        ref, alt, eff = str(r[c["ref"]]), str(r[c["alt"]]), str(r[c["eff"]])
        if len(ref) != 1:
            continue
        alts = [a for a in alt.split(",") if len(a) == 1 and a in BASES]
        if not alts:
            continue
        if eff in alts and eff != ref:
            use_alt, src = eff, "effect"
        elif eff == ref:
            use_alt, src = alts[0], "eff=ref"
        else:
            use_alt, src = alts[0], "first-alt"
        gp = r[c["gwas_p"]] if c["gwas_p"] in sub.columns else None
        rows.append(dict(rsid=str(r[c["rsid"]]), pos=int(r[c["pos"]]), ref=ref, alt=use_alt,
                         eff_allele=eff, allele_src=src, prob=float(r[c["prob"]]),
                         gwas_p=(float(gp) if gp is not None else None)))
    rows.sort(key=lambda x: -x["prob"])
    return rows


def credible_set_scan(model, chrom, cs_rows, focus_rsid=None):
    """Score every variant in a credible set ref->alt and rank by |log2FC|.

    Aligns each variant to the hg38 reference (swapping ref/alt if the deposited
    ref matches the genome's alt), batch-scores through the model, and reports
    each variant's log2FC, |effect| rank, and the Spearman correlation between
    fine-mapping probability and predicted |effect| across the set.
    """
    from scipy.stats import spearmanr
    prepped, skipped = {}, {}
    for v in cs_rows:
        try:
            seq, _, vidx = fetch_window(chrom, v["pos"])
        except Exception as ex:
            skipped[v["rsid"]] = repr(ex)[:60]; continue
        if len(seq) != INPUT_LEN:
            skipped[v["rsid"]] = "bad window length"; continue
        g = seq[vidx]
        if g == v["ref"]:
            r0, a0 = v["ref"], v["alt"]
        elif g == v["alt"]:
            r0, a0 = v["alt"], v["ref"]
        else:
            skipped[v["rsid"]] = f"genome({g})!=ref/alt({v['ref']}/{v['alt']})"; continue
        prepped[v["rsid"]] = (seq, seq[:vidx] + a0 + seq[vidx + 1:], r0, a0, v)
    if not prepped:
        raise SystemExit("no credible-set variants could be aligned to the genome")

    rids = list(prepped)
    Xref = np.stack([onehot(prepped[r][0]) for r in rids])
    Xalt = np.stack([onehot(prepped[r][1]) for r in rids])
    lcr = predict(model, Xref)[1]
    lca = predict(model, Xalt)[1]
    log2fc = (lca - lcr) / np.log(2)

    rows = []
    for i, r in enumerate(rids):
        seq, alt_seq, r0, a0, v = prepped[r]
        rows.append(dict(rsid=r, pos=v["pos"], ref=r0, alt=a0, allele_src=v["allele_src"],
                         prob=v["prob"], gwas_p=v["gwas_p"],
                         log2fc=float(log2fc[i]), abs=float(abs(log2fc[i]))))
    # |effect| rank (1 = largest)
    order = sorted(range(len(rows)), key=lambda i: -rows[i]["abs"])
    for rank, i in enumerate(order, 1):
        rows[i]["effect_rank"] = rank
    rows.sort(key=lambda x: -x["prob"])

    probs = np.array([x["prob"] for x in rows])
    absfc = np.array([x["abs"] for x in rows])
    rho, p = (spearmanr(probs, absfc) if len(rows) > 2 else (float("nan"), float("nan")))
    top = max(rows, key=lambda x: x["abs"])
    stats = dict(n=len(rows), n_skipped=len(skipped), skipped=skipped,
                 spearman_rho=float(rho), spearman_p=float(p),
                 top_prob_variant=rows[0]["rsid"], top_prob=rows[0]["prob"],
                 top_prob_effect_rank=rows[0]["effect_rank"],
                 top_effect_variant=top["rsid"], top_effect_abs=top["abs"], top_effect_prob=top["prob"])
    if focus_rsid:
        f = next((x for x in rows if x["rsid"] == focus_rsid), None)
        if f:
            stats["focus"] = dict(rsid=focus_rsid, prob=f["prob"],
                                  log2fc=f["log2fc"], effect_rank=f["effect_rank"], of=len(rows))
    return rows, stats


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
    # credible-set mode
    ap.add_argument("--credible-set", metavar="TABLE.xlsx",
                    help="fine-mapping supplementary table (.xlsx); score its credible set "
                         "for a locus through the model and rank variants by predicted effect")
    ap.add_argument("--cs-locus", default="BIN1",
                    help="locus name to filter the credible-set table to (default BIN1)")
    ap.add_argument("--cs-min-prob", type=float, default=0.01,
                    help="min fine-mapping probability to include (default 0.01)")
    ap.add_argument("--cs-chrom", default="2",
                    help="chromosome of the credible-set locus (default 2, for BIN1)")
    ap.add_argument("--cs-sheet", default="8-SNP Fine-mapping",
                    help="worksheet name in the credible-set table")
    ap.add_argument("--cs-col", nargs=2, action="append", metavar=("KEY", "COLNAME"),
                    default=[], help="override a column mapping, e.g. --cs-col prob 'PP'. "
                    f"keys: {', '.join(CS_DEFAULT_COLS)}")
    args = ap.parse_args()

    # ---- credible-set mode: standalone, does not need a single --rsid/coords ----
    if args.credible_set:
        os.makedirs(args.outdir, exist_ok=True)
        import tensorflow as tf
        cols = {k: v for k, v in args.cs_col}
        cs_rows = parse_credible_set(args.credible_set, args.cs_locus,
                                     min_prob=args.cs_min_prob, sheet=args.cs_sheet, cols=cols)
        model = tf.keras.models.load_model(args.model, compile=False)
        focus = args.rsid if args.rsid else None
        rows, stats = credible_set_scan(model, args.cs_chrom, cs_rows, focus_rsid=focus)
        base = os.path.join(args.outdir, f"credible_set_{args.cs_locus}")
        json.dump(rows, open(base + ".json", "w"), indent=2)
        json.dump(stats, open(base + "_stats.json", "w"), indent=2)
        print(json.dumps(stats, indent=2))
        print(f"\ncredible set ({stats['n']} variants, {stats['n_skipped']} skipped), "
              f"ranked by fine-mapping probability:")
        for r in rows:
            mark = "  <-- focus" if focus and r["rsid"] == focus else ""
            print(f"  {r['rsid']:14s} PP={r['prob']:.3f}  log2FC={r['log2fc']:+.4f}  "
                  f"|effect| rank {r['effect_rank']}/{stats['n']}{mark}")
        print(f"\nSpearman(prob, |effect|) rho={stats['spearman_rho']:+.3f} "
              f"p={stats['spearman_p']:.3f}")
        print(f"written: {base}.json, {base}_stats.json")
        return
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

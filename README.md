# regulatory-variant-agent

**Trace a noncoding disease variant to the transcription-factor motif it disrupts — directly from DNA sequence.**

Built with **Claude Science** for the *Built with Claude: Life Sciences* hackathon (Research track, Jul 2026).

Given a noncoding variant, this project predicts its effect on chromatin accessibility from sequence (ChromBPNet), then uses in-silico mutagenesis to localize *which* transcription-factor motif the variant breaks — validated against a known, literature-backed mechanism.

## The finding it reproduces

**Test case: `rs6733839`** — one of the strongest common Alzheimer's-disease GWAS signals, ~28 kb upstream of **BIN1**.

- **Location:** chr2:127,135,234 (GRCh38), **C→T** (T = AD-risk allele, MAF ≈ 0.40)
- **Hypothesis (from the literature):** the risk allele disrupts a **MEF2** binding site in a **microglia-specific enhancer**, altering BIN1 regulation.
- **Expected result:** the T allele *lowers* predicted microglial accessibility, and ISM localizes the effect to a **MEF2 motif** (JASPAR MEF2A `MA0052.4` / MEF2C `MA0497.1`).

## Pipeline

```
rs6733839 (C→T, GRCh38)
   → build REF + ALT windows (2,114 bp, variant-centered)
   → ChromBPNet forward pass (ref & alt)
   → Δ = log(alt counts) − log(ref counts)         # variant effect score (expect negative)
   → in-silico mutagenesis / DeepSHAP contributions (±30 bp)
   → match disrupted bases to JASPAR (TFMoDISco-lite / FIMO / Tomtom)
   → confirm the C→T base sits in a MEF2 motif and the risk allele weakens the match
```

## Status

- [x] Scoping + literature grounding + data/tool verification → [`SCOPING.md`](SCOPING.md)
- [ ] Resolve cell-type model (microglia vs bulk cortex — the #1 risk)
- [ ] Score rs6733839 end-to-end (ref/alt Δ)
- [ ] ISM + JASPAR motif match
- [ ] Validate against published mechanism
- [ ] Demo video + write-up

## Data & models

- **Model:** [ChromBPNet](https://github.com/kundajelab/chrombpnet) (base-resolution ATAC CNN, Tn5-bias-factorized, supports ISM + DeepSHAP). Corces-lab brain models as a cross-check.
- **Accessibility data:** ENCODE brain ATAC-seq (bulk cortex/cerebellum: `ENCSR729FNL`, `ENCSR802GEV`). Ideal = a microglia/myeloid track (see `SCOPING.md`).
- **Motifs:** JASPAR CORE vertebrates.

See [`SCOPING.md`](SCOPING.md) for the full method lineage, verified accessions, and caveats.

## License

MIT — see [`LICENSE`](LICENSE).

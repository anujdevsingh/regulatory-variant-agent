# Benchmark test set — data sources & harmonization

Held-out variant test set for the **directional wedge** benchmark: predicting the
SIGN of a noncoding regulatory variant's effect (alt vs. ref allele) in a named
cell context. Assembled 2026-07-08 (widest-net-then-filter scope).

## Sources (measured direction only)

| source | assay | contexts | n variants | access |
|---|---|---|---|---|
| **2025 context-dependent AD MPRA** (PMC12265656, DOI 10.1101/2025.07.11.659973) | MPRA | THP-1 macrophage (immune), HMC3 microglia, brain (mouse tissue), HEK293T | 175 | EuropePMC supplementaryFiles `media-10.xlsx` |
| **van Arensbergen 2019 SuRE raQTL** (PMC6609452, DOI 10.1038/s41588-019-0455-2) | SuRE | K562, HepG2 | 1,982 (subsampled from 33,420 significant, seed=0) | OSF osf.io/w5bzq, component `6y9td` (raQTL list) |

**On-wedge** (microglia / brain / immune): the AD MPRA contexts — this is where the
grounding variant rs6733839 and the observed directional failure live.
**Off-wedge** (K562 / HepG2): the large, well-powered SuRE raQTL set — a general
directional test. Reported per-context; the wedge claim is evaluated on-wedge.

## Sources considered but not included
- **Cooper et al. 2022 Science** (DOI 10.1126/science.abi8654) — the ideal on-wedge
  AD MPRA (5,706 AD/PSP variants). **Closed-access, not in PMC**; per-variant
  supplement not freely retrievable here. Recorded as a constraint.
- **Kircher 2019 saturation MPRA** (PMC6687891, GSE126550) — off-wedge cell types
  (LDLR/TERT/SORT1 in HepG2/HEK293T etc.); processed per-variant effects are in a
  figure-PDF, machine-readable data is the 12 GB GEO RAW tar. Host
  `mpra.gs.washington.edu` was unreachable this session. Deferred.

## Harmonization convention
- Coordinates lifted to **GRCh38** via Ensembl `/variation/homo_sapiens` (batch POST).
- **Direction = sign(activity_alt − activity_ref)** in the variant's cell context.
  - AD MPRA: `ref=Major`, `alt=Minor`; `direction = −sign(logFC_Major_Minor)`.
  - SuRE: `direction = sign(alt.mean − ref.mean)`; alleles from the raQTL file.
- Alleles cross-checked against the Ensembl allele string: 2,155 exact match,
  2 reverse-complement (valid, strand-flipped), 0 true mismatches.
- Zero-direction ties dropped.
- rs6733839 sanity check: direction = −1 (risk-T represses) in BOTH immune and
  microglia — matches the validated MPRA failure mode (results/MPRA_VALIDATION.md).

## Files
- `benchmark/harmonized_variants.csv` — 2,157 variants, one row per variant×context.
- `benchmark/harmonized_context_summary.csv` — per-source/per-context counts,
  direction balance (46–58% alt-up → naive majority baseline ≈ 50%), chromosomes.

The locus/chromosome split manifest (test vs. train folds) is committed separately
(Step 2). Split is by chromosome, never by variant.

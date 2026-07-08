# DATA.md — where every dataset lives

**Short answer:** small, derived results (JSON, figures, the credible-set score
table) are **committed in this repo** under `results/`. Large or licensed source
data — the ChromBPNet model weights, reference genome sequence, the fine-mapping
supplementary table, ENCODE peak files — are **not committed**; they are fetched
on demand by the tool (from Ensembl / UCSC / JASPAR / AlphaGenome) or downloaded
once from their public archive. This file says exactly which is which and how to
re-fetch anything that isn't here.

Anything matching the patterns in [`.gitignore`](.gitignore) — `*.h5`, `*.hdf5`,
`*.npz`, `*.bigWig`, `*.bam`, `data/`, `models/` — is deliberately kept out of
git. Keeping model weights and genome files out of version control is standard
practice; they are large, immutable, and better fetched from their canonical
source.

---

## 1. Committed in this repo (`results/`)

These are the derived analysis outputs — small, and the actual deliverables of
the project. They are in git and need no download.

| File | What it is | Size |
|---|---|---|
| `results/RESULTS.md` | single-variant analysis write-up (rs6733839) | ~4 KB |
| `results/CALIBRATION.md` | percentile/z-score calibration write-up | ~3 KB |
| `results/ALLELIC_SERIES.md` | credible-set analysis write-up | ~4 KB |
| `results/AG_MULTIMODAL_RESULTS.md` | AlphaGenome multimodal cross-check write-up | ~5 KB |
| `results/scores_microglia.json` | rs6733839 ref/alt ChromBPNet result | <1 KB |
| `results/scores_by_celltype.json` | 6 brain cell-type scores | ~1 KB |
| `results/calibration.json`, `robustness.json` | calibration + bias-handling stats | <1 KB |
| `results/bin1_credible_set.json` | 25-variant credible set, ranked, scored | ~6 KB |
| `results/credible_set_stats.json` | credible-set summary stats | <1 KB |
| `results/ag_rs6733839_scores.csv` | **AlphaGenome raw scores: 12,848 tracks × 24 cols** | ~3.7 MB |
| `results/fig1_variant_prediction.png` | ref/alt profile + ISM | ~180 KB |
| `results/fig2_celltype_and_attribution.png` | cell-type scan + attribution | ~90 KB |
| `results/fig3_deepshap_attribution.png` | expected-gradients attribution | ~90 KB |
| `results/fig4_calibration.png` | calibration against null SNPs | ~85 KB |
| `results/fig5_credible_set.png` | fine-mapping PP vs predicted effect | ~80 KB |
| `results/fig6_alphagenome_multimodal.png` | AlphaGenome multimodal cross-check | ~90 KB |

The `ag_rs6733839_scores.csv` is the largest committed file (~3.7 MB) but is kept
in-repo deliberately: it is the full AlphaGenome output and small enough for git,
so the multimodal result is fully reproducible from the repo alone.

---

## 2. NOT committed — fetched on demand by the tool (no manual download)

`score_variant.py` retrieves these live at run time over public APIs. Nothing to
download by hand; you just need network access.

| Data | Source (API) | Used for | License / terms |
|---|---|---|---|
| Variant coordinates & alleles (rsID → GRCh38) | **Ensembl REST** (`rest.ensembl.org`) | `--rsid` resolution, null-SNP sampling | Ensembl: no restriction on use ([EMBL-EBI terms](https://www.ebi.ac.uk/about/terms-of-use)) |
| Reference sequence (hg38 windows) | **UCSC Genome Browser API** (`api.genome.ucsc.edu`) | 2,114 bp input windows | UCSC: free for academic/non-profit; genome data unrestricted |
| TF motif matrices (PFMs) | **JASPAR** REST (`jaspar.elixir.no/api`) | motif scan (MEF2A `MA0052.4`, MEF2C `MA0497.1`, or any `--motifs` IDs) | JASPAR: CC BY-NC-SA / open |
| Multimodal variant effects (ATAC/DNase/TF-ChIP/RNA-seq) | **AlphaGenome API** (Google DeepMind) | `AG_MULTIMODAL_RESULTS.md` layer | AlphaGenome API terms; **requires an API key** (env var `ALPHAGENOME`) |

---

## 3. NOT committed — download once, then point the tool at it

These are large or licensed files kept out of git. Download once and pass the
path via the relevant flag.

### ChromBPNet brain models (required for all scoring)
- **What:** 6 brain cell-type ChromBPNet models (Microglia, Astrocytes,
  Excitatory & Inhibitory neurons, Oligodendrocytes, OPCs), bias-corrected heads
  (`*_chrombpnet_nobias.h5`, ~26 MB each). Base-resolution ATAC CNNs, Tn5-bias
  factorized.
- **Provenance:** trained on **Corces scATAC pseudobulk** (source ATAC: GEO
  **GSE147672**) by the PsychENCODE / Weng group. Method:
  [ChromBPNet](https://github.com/kundajelab/chrombpnet).
- **Where:** Zenodo record **10.5281/zenodo.10605867** — a single ~920 MB tar
  (one model per cell type, **no cross-validation folds**).
- **How:** download the tar from Zenodo, extract, and the models land at
  `Zenodo/data/chrombpnet/*_chrombpnet_nobias.h5`. Point `--model` at one.
- **License:** as deposited on Zenodo (open access).

### Fine-mapping credible set (required for `--credible-set` mode)
- **What:** SNP-level fine-mapping supplementary table (mean causal probability
  across FINEMAP / PAINTOR / GCTA-COJO), sheet `8-SNP Fine-mapping`.
- **Source:** **Schwartzentruber et al. 2021**, *Nature Genetics*,
  DOI **10.1038/s41588-020-00776-w**, Supplementary Table 8.
- **Where:** the supplementary bundle for **PMC7610386** — file
  `EMS118040-supplement-Supplementary_Tables_1_14.xlsx` (via Europe PMC:
  `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7610386/supplementaryFiles`).
- **How:** download the xlsx and pass it to `--credible-set TABLE.xlsx`
  (`--cs-locus BIN1`). Column names default to this table's schema.
- **License:** journal supplementary material (© the authors / publisher);
  redistribute per the article's terms — hence not committed here.

### ENCODE null peaks (optional, for `--calibrate`)
- **What:** cortex ATAC-seq IDR peaks (narrowPeak `.bed.gz`), accession
  **ENCFF221FSW**, used to sample a null of common SNPs for calibration.
- **Where:** ENCODE portal (`www.encodeproject.org`).
- **How:** download the `.bed.gz` and pass it to `--calibrate PEAK_BED`.
- **License:** ENCODE data — free to use; please cite the ENCODE Consortium.

---

## 4. Key identifiers (quick reference)

| Thing | Identifier |
|---|---|
| Test variant | rs6733839, chr2:127,135,234 (GRCh38), C>T (T = AD-risk) |
| ChromBPNet models | Zenodo 10.5281/zenodo.10605867 |
| Source scATAC | GEO GSE147672 (Corces et al.) |
| Fine-mapping table | Schwartzentruber 2021, DOI 10.1038/s41588-020-00776-w, Suppl. Table 8 (PMC7610386) |
| ENCODE null peaks | ENCFF221FSW |
| Motifs | JASPAR MA0052.4 (MEF2A), MA0497.1 (MEF2C) |
| Multimodal model | AlphaGenome (Avsec et al. 2026, Nature) |

---

*Reproducibility note:* the two runtime environments differ by network reach —
data fetching (Ensembl/UCSC/Europe PMC) runs in a general Python env; model
scoring runs in a TensorFlow 2.13 / numpy<2 env (`requirements.txt`). See
[`SCOPING.md`](SCOPING.md) for the full method lineage and verified accessions.

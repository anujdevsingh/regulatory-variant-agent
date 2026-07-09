# Chen/Liu 3'-UTR MPRA (source #4) — benchmark addition

**Source:** Chen, Liu et al. "Regulatory mechanisms driven by functional 3'-UTR variants
in alcohol use disorder and related traits." Genome Biology 2026, DOI
10.1186/s13059-026-04176-x (published 2026-06-29; bioRxiv preprint PMC10871301).
Conference-abstract precursor: PMC8827855 (J Clin Transl Sci 2021).
Data: GEO GSE253841 (GSE253841_unique_counts.txt.gz — variant-summed DNA/RNA barcode
counts, SH-SY5Y + microglia, 6 replicates each, open).

**Assay:** 3'-UTR MPRA in SH-SY5Y neuroblastoma and a microglial cell line. 13,515
3'-UTR SNPs from neurological/AUD GWAS loci. NOTE: this measures POST-TRANSCRIPTIONAL
regulation (mRNA stability via 3'-UTR), a DIFFERENT regulatory layer than the
enhancer/chromatin-accessibility MPRAs in the rest of the benchmark. It enters as its
own clearly-labeled context and tests a related but distinct question.

**How direction was computed (measured):**
- activity = log2((RNA_cpm+1)/(DNA_cpm+1)) per allele per replicate; skew = alt - ref;
  direction = sign(mean skew across 6 replicates); paired t-test across replicates.
- Coverage filter >=200 reads/allele in DNA and RNA.
- HONEST LIMITATION: the deposited counts are VARIANT-SUMMED, not per-barcode, so we
  cannot reproduce the paper's barcode-level GLMM significance (they report ~400 SH-SY5Y
  / ~657 microglia FDR-significant; our simple t-test finds far fewer at FDR<0.05).
  We therefore use a CONFIDENT-DIRECTION set at nominal p<0.01 (direction estimate, not
  the paper's significance calls) — 350 microglia + 214 SH-SY5Y variants.
- hg38 coords via Ensembl (487/488 rsIDs). Added to frozen chr split (test 2,6,11,19).

**Result — all models at chance (consistent with NPC + on-wedge findings):**

| context | model | acc | 95% CI | AUROC | n |
|---|---|---|---|---|---|
| microglia (3'UTR) | PWM floor | 0.488 | [.402,.583] | — | 127 |
| microglia (3'UTR) | Logistic-motif | 0.543 | [.457,.630] | — | 127 |
| microglia (3'UTR) | AlphaGenome | 0.480 | [.401,.567] | 0.488 | 127 |
| SH-SY5Y (3'UTR) | PWM floor | 0.397 | [.288,.507] | — | 73 |
| SH-SY5Y (3'UTR) | Logistic-motif | 0.521 | [.411,.630] | — | 73 |
| SH-SY5Y (3'UTR) | AlphaGenome | 0.452 | [.342,.562] | 0.428 | 73 |
| (majority class) | microglia 0.551 / SH-SY5Y 0.616 | | | | |

Borzoi row: GPU-gated (instance deleted after NPC run) — not scored. Given AlphaGenome
and both floors are at chance here, and Borzoi was at chance on the larger NPC set, a
Borzoi run is unlikely to change the conclusion; can be added if a GPU is reconnected.

**Interpretation:** In REAL microglia measured data (the exact cell type where rs6733839
fails), direction is NOT predictable from sequence by AlphaGenome or motif models — even
at the post-transcriptional layer. This is a further independent confirmation of the
project's central null, now in the on-target cell type. Caveat: 3'-UTR layer ≠ the
enhancer layer of rs6733839's mechanism, and significance is a direction estimate not
the paper's GLMM. It does NOT substitute for microglia caQTL/enhancer data (Kosoy,
still access-gated), which remains the pivotal missing piece for the enhancer wedge.

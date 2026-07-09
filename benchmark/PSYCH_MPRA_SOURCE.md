# Psychiatric cross-disorder MPRA (Lee et al. 2025, Cell) — benchmark expansion

**Source:** Lee et al., "Massively parallel reporter assays investigate shared genetic
variants of eight psychiatric disorders." Cell (2025). DOI 10.1016/j.cell.2024.12.022.
PMC11890967. Data: GEO GSE244011 (DNA/RNA barcode count matrices, open).
Code: github.com/thewonlab/crossdisorder-MPRA.

**Assay:** Bulk MPRA in hiPSC-derived neural progenitor cells (NPCs), 22 replicates,
REF/ALT oligo pairs. This is a BRAIN-LINEAGE context — the closest *scalable* proxy to
the microglia/immune failure context, NOT microglia or immune itself.

**How direction was computed (measured, not predicted):**
- Downloaded GSE244011_dnaMatrix.csv.gz + GSE244011_rnaMatrix.csv.gz (14,494 variants,
  keyed chr:pos_REF:ALT, hg19).
- Per replicate i, REF and ALT oligos share one library → JOINT per-replicate CPM
  normalization over (REF_i + ALT_i) total depth. (Independent REF/ALT normalization
  produced a spurious 83/17 direction imbalance — a normalization artifact, corrected.)
- allele activity = log2((RNA_norm+1)/(DNA_norm+1)); allelic skew = activity_alt - activity_ref.
- direction = sign(mean skew across 22 replicates); significance = paired 1-sample
  t-test across replicates, BH-FDR.
- Coverage filter: >=100 total DNA reads per allele. Significant set: FDR<0.05.
- Direction balance among significant variants: 50.7% alt-up (balanced — NOT an easy
  majority-class test set).

**Liftover:** hg19 -> hg38 via UCSC hg19ToHg38.over.chain (pyliftover). 14,262/14,270
covered variants lifted cleanly, all same-chromosome. Build confirmed hg19 by Ensembl
GRCh37 allele match (6/6) vs GRCh38 mismatch.

**Integration:** 3,665 significant variants added as context
"neural progenitor (hiPSC NPC MPRA)", direction = sign(alt-ref), same as all sources.
1 variant overlapped the existing benchmark and was dropped to keep folds disjoint.
Added to the FROZEN chromosome split (test = chr 2,6,11,19; never by variant):
788 test / 2,877 train.

**On-wedge training set: 62 -> 2,939 variants** (47x). rs6733839 is NOT in this set
(psychiatric, not AD-specific) — it remains anchored by the AD MPRA + Kosoy microglia caQTL.

**Honest caveat:** NPC is brain-lineage, not the exact microglia/immune context where
rs6733839 fails. This source tests whether the directional wedge holds in brain-lineage
broadly and provides the volume to train a real model. The exact-context anchor (microglia)
still depends on source #4 (Kosoy caQTL).

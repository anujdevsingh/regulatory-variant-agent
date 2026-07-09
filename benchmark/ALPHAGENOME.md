# AlphaGenome on the held-out set (corrected: per-variant_id, deduped)

Scored all held-out variant×context rows with **AlphaGenome** (Avsec et al. 2026,
Nature) via the DeepMind API (non-commercial), at its native **1 Mb context**.

> **Two corrections applied.** (1) The first pass keyed batch results by rsID; 5
> multi-allelic rsIDs had later alt-allele scores overwrite earlier ones. Rescored
> keyed by `variant_id`. (2) The harmonized set had 6 duplicate variant×context
> rows (same variant tested in multiple AD-MPRA enhancer constructs); these were
> aggregated to one row each (mean effect), so all n's now count unique
> variant×context observations. Numbers below are final.

## Method
- `score_variant`, ATAC + DNASE recommended scorers, DIFF_LOG2_SUM (alt−ref).
- Direction per variant×context = sign of the mean effect over context-matched
  biosample tracks (K562→K562; HepG2→HepG2; immune→macrophage/monocyte;
  microglia→macrophage/monocyte/microglia; brain→neuron/astrocyte; HEK293T→HEK/kidney).
- 1 Mb window: AlphaGenome's headline strength is long context; rs6733839 failed
  despite it, so native context is the fair incumbent test.

## Results (direction accuracy, 95% bootstrap CI, seed=0)
| context | n | accuracy | AUROC |
|---|---|---|---|
| ALL | 519 | 0.651 [0.611,0.692] | 0.724 |
| K562 (off-wedge) | 233 | 0.682 [0.622,0.742] | 0.744 |
| HepG2 (off-wedge) | 212 | 0.651 [0.585,0.717] | 0.738 |
| immune THP-1 (on-wedge) | 31 | 0.581 [0.419,0.742] | 0.610 |
| microglia HMC3 (on-wedge) | 7 | 0.286 [0.000,0.571] | 0.600 |
| brain MPRA (on-wedge) | 18 | 0.556 [0.333,0.778] | 0.700 |
| **on-wedge pooled** | **56** | **0.536 [0.411,0.661]** | **0.592** |

## Reading (honest)
- **Off-wedge:** AlphaGenome is strong (0.65–0.68 acc, AUROC ~0.74), clearly above
  the floors — expected for cell lines resembling its ENCODE/GTEx training data.
- **On-wedge:** pooled accuracy 0.536, CI spans 0.5 →
  **not significantly above chance** at this power (n=56),
  and not separable from the floor baselines. rs6733839 remains a directional miss
  (AG +1 in immune/microglia; MPRA measured −1).

## Incumbent-leakage note
Off-wedge K562/HepG2 SuRE variants may be in-distribution for AlphaGenome (ENCODE
tracks in training) — flatters off-wedge numbers. On-wedge MPRA is the honest OOD test.

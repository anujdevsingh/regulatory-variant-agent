# AlphaGenome on the held-out set

Scored all 524 held-out variant×context rows with **AlphaGenome** (Avsec et al.
2026, Nature) via the DeepMind API (non-commercial), at its native **1 Mb context**.

## Method
- `score_variant` with ATAC + DNASE recommended scorers, DIFF_LOG2_SUM (alt−ref).
- Direction per variant×context = sign of the mean effect over tracks whose
  biosample matches the context (K562→K562; HepG2→HepG2; immune→macrophage/monocyte;
  microglia→macrophage/monocyte/microglia; brain→neuron/astrocyte; HEK293T→HEK/kidney).
- 1 Mb window chosen deliberately: AlphaGenome's headline strength is long context,
  and the rs6733839 failure happened *despite* it. Testing at native context is the
  fair incumbent test.

## Results (direction accuracy + AUROC, 95% bootstrap CI, seed=0)
| context | n | accuracy | AUROC |
|---|---|---|---|
| ALL | 524 | 0.651 [0.613,0.693] | 0.719 [0.677,0.760] |
| K562 (off-wedge) | 233 | 0.682 [0.622,0.742] | 0.744 |
| HepG2 (off-wedge) | 212 | 0.651 [0.585,0.712] | 0.738 |
| immune THP-1 (on-wedge) | 32 | 0.500 [0.344,0.656] | 0.529 |
| microglia HMC3 (on-wedge) | 8 | 0.375 | 0.667 |
| brain MPRA (on-wedge) | 18 | 0.556 [0.333,0.778] | 0.675 |
| **on-wedge pooled** | **58** | **0.500 [0.362,0.638]** | **0.550 [0.394,0.702]** |

## Reading
- **Off-wedge:** AlphaGenome is strong (0.65–0.68 acc, AUROC ~0.74) and clearly
  beats the floor baselines — as expected for a frontier model on well-characterized
  cell lines that resemble its ENCODE/GTEx training data.
- **On-wedge:** AlphaGenome sits at **chance** (pooled 0.500, CI spans 0.5), despite
  1 Mb context. rs6733839 reproduced backwards: AG predicts +1 (accessibility up for
  risk-T) in immune/microglia; MPRA measured −1 (represses). This is the documented
  wedge failure, now on a held-out set.

## Incumbent-leakage note
The off-wedge K562/HepG2 SuRE variants may be partly in-distribution for AlphaGenome
(ENCODE K562/HepG2 tracks are in its training data) — this can flatter its off-wedge
numbers. The on-wedge MPRA contexts are the honest out-of-distribution test, and that
is exactly where it is at chance.

## Files
- `benchmark/alphagenome_results.csv`, `benchmark/alphagenome_predictions.csv`.

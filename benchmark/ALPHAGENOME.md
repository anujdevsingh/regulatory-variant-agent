# AlphaGenome on the held-out set (corrected: scored per variant_id)

Scored all 524 held-out variant×context rows with **AlphaGenome** (Avsec et al.
2026, Nature) via the DeepMind API (non-commercial), at its native **1 Mb context**.

> **Correction (multi-allelic bug fixed).** The first pass keyed the batch results
> by rsID; 5 multi-allelic rsIDs (rs2288912, rs72838288, rs10416371, rs10838702,
> rs189835276) had their later alt-allele scores overwrite earlier ones, so 18/524
> rows (12/58 on-wedge) carried a sibling allele's score. Rescored keyed by
> `variant_id` (chrom:pos:ref>alt); every allele now scored independently. All
> numbers below are from the corrected run.

## Method
- `score_variant` with ATAC + DNASE recommended scorers, DIFF_LOG2_SUM (alt−ref).
- Direction per variant×context = sign of the mean effect over tracks whose
  biosample matches the context (K562→K562; HepG2→HepG2; immune→macrophage/monocyte;
  microglia→macrophage/monocyte/microglia; brain→neuron/astrocyte; HEK293T→HEK/kidney).
- 1 Mb window chosen deliberately: AlphaGenome's headline strength is long context,
  and the rs6733839 failure happened *despite* it. Testing at native context is fair.

## Results (direction accuracy + AUROC, 95% bootstrap CI, seed=0)
| context | n | accuracy | AUROC |
|---|---|---|---|
| ALL | 524 | 0.653 [0.615,0.695] | 0.726 |
| K562 (off-wedge) | 233 | 0.682 [0.622,0.742] | 0.744 |
| HepG2 (off-wedge) | 212 | 0.651 [0.585,0.712] | 0.738 |
| immune THP-1 (on-wedge) | 32 | 0.594 [0.438,0.750] | 0.629 |
| microglia HMC3 (on-wedge) | 8 | 0.375 | 0.667 |
| brain MPRA (on-wedge) | 18 | 0.556 [0.333,0.778] | 0.700 |
| **on-wedge pooled** | **58** | **0.552 [0.414,0.690]** | **0.616** |

## Reading (honest)
- **Off-wedge:** AlphaGenome is strong (0.65–0.68 acc, AUROC ~0.74) and clearly
  beats the floor baselines — as expected for a frontier model on cell lines that
  resemble its ENCODE/GTEx training data.
- **On-wedge:** AlphaGenome pooled accuracy is **0.552 — above 0.5 as a point
  estimate, but the 95% CI [0.414,0.690] spans chance, so it is NOT significantly
  above chance** at this power (n=58). It is also not separable from the floor
  baselines on-wedge (logistic 0.534, PWM 0.500 — all CIs overlap).
- rs6733839 remains a directional miss: AlphaGenome predicts +1 (accessibility up
  for risk-T) in immune/microglia; MPRA measured −1 (represses). The documented
  failure holds for that variant even though pooled on-wedge accuracy is ~0.55.

## Incumbent-leakage note
The off-wedge K562/HepG2 SuRE variants may be partly in-distribution for AlphaGenome
(ENCODE K562/HepG2 tracks are in its training data) — this flatters its off-wedge
numbers. The on-wedge MPRA contexts are the honest out-of-distribution test.

## Files
- `benchmark/alphagenome_results.csv`, `benchmark/alphagenome_predictions.csv`.

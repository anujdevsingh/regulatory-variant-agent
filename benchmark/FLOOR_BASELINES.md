# Floor baselines — motif-only direction prediction (deduped)

Two trivial, motif-only baselines on the frozen held-out set
(`benchmark/split_manifest.csv`, test = chr 2,6,11,19). The FLOOR every incumbent
and every model must clear.

## Features
- 49 JASPAR CORE vertebrate PWMs (jaspar.elixir.no), incl. wedge-critical Spi1,
  MEF2A/C/D, SPIB, CEBP, NFKB, IRF, ETS families.
- Per variant × motif: **Δ = best-overlap log-odds(alt) − best-overlap log-odds(ref)**,
  windows overlapping the variant, both strands, ±25 bp.

## Baselines
1. **PWM Δ-score** — direction = sign of the largest-|Δ| motif.
2. **Logistic (motif Δ)** — L2 logistic regression on 49 motif-Δ features,
   StandardScaler, C=1.0, seed=0. **Fit on train folds only.**

## Results (direction accuracy, 95% bootstrap CI, 2000 resamples, seed=0)
| context | n | PWM Δ | Logistic |
|---|---|---|---|
| ALL | 519 | 0.472 [0.430,0.513] | 0.578 [0.538,0.618] |
| K562 (off-wedge) | 233 | 0.446 [0.386,0.511] | 0.579 [0.515,0.640] |
| HepG2 (off-wedge) | 212 | 0.500 [0.434,0.566] | 0.585 [0.519,0.651] |
| immune THP-1 (on-wedge) | 31 | 0.387 [0.226,0.581] | 0.452 [0.290,0.613] |
| microglia HMC3 (on-wedge) | 7 | 0.571 [0.143,0.857] | 0.857 [0.571,1.000] |
| brain MPRA (on-wedge) | 18 | 0.722 [0.500,0.889] | 0.611 [0.389,0.833] |
| **on-wedge pooled** | **56** | **0.518 [0.393,0.643]** | **0.554 [0.429,0.679]** |

## Reading
- **Off-wedge (K562/HepG2):** logistic-on-motifs ~0.58 — motif Δ carries real
  directional signal in well-powered cell lines.
- **On-wedge:** both baselines' CIs span chance (pooled ~0.52–0.55). Motif features
  alone cannot reliably call direction where the effect is context-dependent — the
  quantified wedge.
- On-wedge N is small (7–36; pooled 56); recorded as a limitation.

## Files
- `benchmark/floor_baseline_results.csv`, `benchmark/floor_predictions.csv`,
  `benchmark/fig_floor_baselines.png`.

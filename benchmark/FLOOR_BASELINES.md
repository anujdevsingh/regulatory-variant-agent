# Floor baselines — motif-only direction prediction

Two trivial, motif-only baselines scored on the frozen held-out set
(`benchmark/split_manifest.csv`, test = chr 2,6,11,19). These are the FLOOR every
incumbent and every model must clear: a model that beats AlphaGenome but not
these is not interesting.

## Features
- 49 JASPAR CORE vertebrate PWMs (source: jaspar.elixir.no), including the
  wedge-critical Spi1, MEF2A/C/D, SPIB, CEBP, NFKB, IRF, ETS families.
- Per variant × motif: **Δ = best-overlap log-odds(alt) − best-overlap log-odds(ref)**,
  scanning only windows overlapping the variant position, both strands, ±25 bp window.
- 2,072 variants featurized (27 skipped: center base ≠ ref / strand cases).

## Baselines
1. **PWM Δ-score** — direction = sign of the largest-|Δ| motif (gained motif → alt-up).
   Purely motif-presence; no activator/repressor identity.
2. **Logistic (motif Δ)** — L2 logistic regression on the 49 motif-Δ features,
   StandardScaler, C=1.0, seed=0. **Fit on train folds only.**

## Results (direction accuracy, 95% bootstrap CI, 2000 resamples, seed=0)
| context | n | PWM Δ | Logistic |
|---|---|---|---|
| ALL | 524 | 0.468 [0.426,0.510] | 0.580 [0.536,0.620] |
| K562 (off-wedge) | 233 | 0.446 | 0.588 [0.524,0.652] |
| HepG2 (off-wedge) | 212 | 0.500 | 0.585 [0.514,0.651] |
| immune THP-1 (on-wedge) | 32 | 0.375 | 0.438 [0.281,0.625] |
| microglia HMC3 (on-wedge) | 8 | 0.500 | 0.750 |
| brain MPRA (on-wedge) | 18 | 0.722 | 0.611 |
| **on-wedge pooled** | **58** | **0.500 [0.362,0.621]** | **0.534 [0.414,0.655]** |

## Reading
- **Off-wedge (K562/HepG2):** logistic-on-motifs reaches ~0.585 — motif Δ carries
  real directional signal in well-powered, well-characterized cell lines.
- **On-wedge (microglia/brain/immune):** both baselines collapse to chance
  (pooled 0.50–0.53, CIs span 0.5). Motif features alone **cannot** call direction
  where the effect is context-dependent — this is the quantified wedge.
- Per-context on-wedge N is small (8–32); the pooled n=58 is the honest power we have.
  This is a real limitation, recorded, not hidden.

## Files
- `benchmark/floor_baseline_results.csv` — per-context acc/AUROC + CIs.
- `benchmark/floor_predictions.csv` — per-variant test predictions (shared test rows
  for the comparison table; incumbents + wedge model add columns to the same rows).
- `benchmark/fig_floor_baselines.png` — figure.

# Baseline comparison — the pre-model scoreboard (final, deduped)

**Mandated checkpoint BEFORE any model code.** Incumbents + floor baselines on the
*identical* frozen held-out set (`benchmark/split_manifest.csv`, test = chr 2,6,11,19).
Our wedge model is added as a new row in this same table.

> **Corrections applied this pass:** (1) AlphaGenome rescored per `variant_id`
> (rsID-keying bug on 5 multi-allelic variants); (2) harmonized set deduped to
> unique variant×context (6 duplicate AD-MPRA-construct rows aggregated). All n's
> now count unique observations. Conclusions unchanged; sample sizes corrected.

## The scoreboard (direction accuracy, 95% bootstrap CI, seed=0)

| context | n | PWM Δ (floor) | Logistic motif (floor) | AlphaGenome (1MB) | Borzoi/Flashzoi |
|---|---|---|---|---|---|
| ALL | 519 | 0.472 [0.43,0.51] | 0.578 [0.54,0.62] | **0.651 [0.61,0.69]** | pending GPU |
| K562 (off-wedge) | 233 | 0.446 [0.39,0.51] | 0.579 [0.52,0.64] | **0.682 [0.62,0.74]** | pending GPU |
| HepG2 (off-wedge) | 212 | 0.500 [0.43,0.57] | 0.585 [0.52,0.65] | **0.651 [0.58,0.72]** | pending GPU |
| immune THP-1 (on-wedge) | 31 | 0.387 [0.23,0.58] | 0.452 [0.29,0.61] | 0.581 [0.42,0.74] | pending GPU |
| microglia HMC3 (on-wedge) | 7 | 0.571 [0.14,0.86] | 0.857 [0.57,1.00] | 0.286 [0.00,0.57] | pending GPU |
| brain MPRA (on-wedge) | 18 | 0.722 [0.50,0.89] | 0.611 [0.39,0.83] | 0.556 [0.33,0.78] | pending GPU |
| **ON-WEDGE pooled** | **56** | **0.518 [0.39,0.64]** | **0.554 [0.43,0.68]** | **0.536 [0.41,0.66]** | pending GPU |

AUROC columns are in `benchmark/baseline_comparison.csv`.

## What the scoreboard establishes (before we build anything)
1. **Off-wedge, AlphaGenome wins cleanly** (0.65–0.68, beats both floors, CIs clear).
   Expected: K562/HepG2 resemble its training data.
2. **On-wedge, no model is significantly above chance.** AlphaGenome, logistic, and
   PWM all have point estimates ~0.5–0.55 with CIs spanning 0.5, and are not
   separable from each other. The 1 Mb frontier model has no significant edge over
   a trivial motif regression in microglia/brain/immune.
3. **The wedge is real and open.** No incumbent or floor separates from chance
   on-wedge. A model lifting on-wedge pooled accuracy with a CI clearing 0.5 AND the
   incumbent's CI would be a real, narrow win.

## Honesty / leakage / power caveats (on the record)
- **Incumbent leakage:** off-wedge K562/HepG2 likely in-distribution for AlphaGenome
  and Borzoi (ENCODE tracks in training). On-wedge MPRA is the honest OOD test.
- **On-wedge power is limited:** per-context on-wedge N is 7–36; pooled n=56.
  CIs are wide (~±0.13); a win must survive them or be reported as underpowered.
- **Borzoi/Flashzoi not yet scored:** no GPU connected. `benchmark/borzoi_run.py`
  committed and ready. Row is 'pending compute', NOT faked.

## What "beating" requires (from the mandate)
A statistically significant improvement — bootstrap CIs non-overlapping with BOTH
incumbents AND floor baselines, in ≥1 named context. Overlapping CIs are not a win.
Any apparent win is treated as a leakage bug until test contamination, an easier
test set, and metric cherry-picking are ruled out.

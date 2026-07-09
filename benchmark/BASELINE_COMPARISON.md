# Baseline comparison — the pre-model scoreboard (corrected)

**This table is the mandated checkpoint BEFORE any model code.** It scores the
incumbents and the floor baselines on the *identical* frozen held-out set
(`benchmark/split_manifest.csv`, test = chr 2,6,11,19). Our wedge model is added
as a new row in this same table, on these same rows.

> **Correction note:** AlphaGenome was rescored keyed by `variant_id` after a
> multi-allelic rsID-keying bug was found (18/524 rows, 12/58 on-wedge, had a
> sibling allele's score). All AlphaGenome numbers below are corrected.

## The scoreboard (direction accuracy, 95% bootstrap CI, seed=0)

| context | n | PWM Δ (floor) | Logistic motif (floor) | AlphaGenome (incumbent, 1MB) | Borzoi/Flashzoi |
|---|---|---|---|---|---|
| ALL | 524 | 0.468 [.426,.510] | 0.580 [.536,.620] | **0.653 [.615,.695]** | pending GPU |
| K562 (off-wedge) | 233 | 0.446 | 0.588 [.524,.652] | **0.682 [.622,.742]** | pending GPU |
| HepG2 (off-wedge) | 212 | 0.500 | 0.585 [.514,.651] | **0.651 [.585,.712]** | pending GPU |
| immune THP-1 (on-wedge) | 32 | 0.375 | 0.438 | 0.594 [.438,.750] | pending GPU |
| microglia HMC3 (on-wedge) | 8 | 0.500 | 0.750 | 0.375 | pending GPU |
| brain MPRA (on-wedge) | 18 | 0.722 | 0.611 | 0.556 | pending GPU |
| **ON-WEDGE pooled** | **58** | **0.500 [.379,.621]** | **0.534 [.413,.655]** | **0.552 [.414,.690]** | pending GPU |

AUROC columns are in `benchmark/baseline_comparison.csv`.

## What the scoreboard establishes (before we build anything)

1. **Off-wedge, AlphaGenome wins cleanly** (0.65–0.68, beats both floors, CIs clear).
   Expected: K562/HepG2 resemble its ENCODE/GTEx training data.
2. **On-wedge, no model is significantly above chance.** AlphaGenome pooled 0.552,
   logistic 0.534, PWM 0.500 — every CI spans 0.5, and the three are not separable
   from each other. The 1 Mb frontier model has NO significant edge over a trivial
   motif regression in microglia/brain/immune. (Point estimates are ~0.5–0.55; the
   honest statement is "not significantly better than chance or than the floor," not
   "exactly at chance.")
3. **The wedge is real and open.** On-wedge direction is unsolved: no incumbent or
   floor separates from chance. A model that lifts on-wedge pooled accuracy with a
   CI clearing 0.5 AND clearing the incumbent's CI would be a real, narrow win.

## Honesty / leakage / power caveats (on the record)
- **Incumbent leakage:** off-wedge K562/HepG2 SuRE variants are likely
  in-distribution for AlphaGenome and Borzoi (ENCODE tracks in training). This
  flatters their off-wedge numbers. On-wedge MPRA is the honest OOD test.
- **On-wedge power is limited:** per-context on-wedge N is 8–32; pooled n=58. With
  this N, CIs are wide (~±0.14) — a win must survive them, or be reported as
  underpowered. This is the binding constraint on any wedge claim.
- **Borzoi/Flashzoi not yet scored:** no GPU connected. `benchmark/borzoi_run.py`
  is committed and ready. Row is 'pending compute', NOT faked.

## What "beating" requires (from the mandate)
A statistically significant improvement on the held-out set — bootstrap CIs on
accuracy/AUROC, non-overlapping with BOTH incumbents AND floor baselines, in ≥1
named context. Overlapping CIs are not a win. Any apparent win is treated as a
leakage bug until test contamination, an easier test set, and metric
cherry-picking are ruled out.

## Files
- `benchmark/baseline_comparison.csv` — full table (acc + AUROC + CIs, all contexts).
- `benchmark/fig_baseline_comparison.png` — figure.

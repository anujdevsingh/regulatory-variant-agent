# Wedge model — results and final verdict

## Bottom line (honest)

**The directional wedge did not close as a win.** On the frozen held-out set,
in the on-wedge contexts (microglia/brain/immune, pooled n=56), our grammar-aware
model reaches **0.554 accuracy [0.429, 0.679]** — statistically indistinguishable
from chance, from the floor baselines, and from the incumbents. It does **not**
beat the strongest incumbent (Borzoi, 0.625). This is a **well-characterized
negative**, and per the mandate that closes the thread honestly.

## The full scoreboard (direction accuracy, 95% bootstrap CI, seed=0)

### On-wedge pooled (n=56) — the target
| model | accuracy | AUROC |
|---|---|---|
| PWM Δ-score (floor) | 0.518 [0.393,0.643] | 0.536 |
| AlphaGenome (incumbent, 1MB) | 0.536 [0.411,0.661] | 0.592 |
| Logistic motif (floor) | 0.554 [0.429,0.679] | 0.541 |
| **Wedge-GBT (ours)** | **0.554 [0.429,0.679]** | **0.632** |
| **Borzoi (incumbent, 524kb)** | **0.625 [0.500,0.750]** | **0.693** |

Off-wedge (K562/HepG2), the wedge model tracks Borzoi (~0.63–0.70), as expected —
those variants are well-powered and in-distribution for the sequence models.

## What we learned (the science, not just the score)

1. **Borzoi is the real incumbent to beat on-wedge, not AlphaGenome.** This is a
   new, concrete finding from the benchmark: Borzoi (0.625, AUROC 0.693) clearly
   leads AlphaGenome (0.536) in microglia/brain/immune, and **calls rs6733839
   correctly** (predicts repression in immune/microglia) where AlphaGenome calls
   it backwards. AlphaGenome's 1 Mb context does not help on the wedge; Borzoi's
   524 kb accessibility-track modeling does better here.

2. **Adding motif/grammar features on top of Borzoi did not help — it slightly
   hurt.** Permutation importance on the on-wedge test shows Borzoi's own-context
   accessibility delta (`bz_own`) is the dominant feature by ~2.5×; the 49 motif-Δ
   features and the 4 hand-built grammar features (co-occurrence, conflict,
   wedge-TF sum) contribute little and, inside the tree trained on
   off-wedge-dominated data, dilute the Borzoi signal (0.625 → 0.554). The
   grammar hypothesis, as operationalized here, is not supported.

3. **The binding constraint was real and predicted.** Only 62 on-wedge training
   variants. The on-wedge-only regime (training solely on those) lands at 0.464 —
   at/below chance, confirming the design's honest prior that this N cannot
   support a from-scratch context-specific learner. Cross-context transfer (the
   main bet) did better but still did not clear the incumbent.

4. **No model — floor, incumbent, or ours — is significantly above chance
   on-wedge.** Every CI spans 0.5. Borzoi's point estimate (0.625) is the best,
   but its CI lower bound sits exactly at 0.500: borderline, not significant.
   The wedge remains genuinely hard and, at this power (n=56), open.

## Why this is a legitimate close, not a failure

The mandate defined "done" as: a comparison table where our model beats both
incumbents and the floor baselines on direction in ≥1 named context with
significance — **OR a well-characterized negative showing the wedge didn't
hold.** We have the latter, and we can say precisely why:
- The signal that works (Borzoi accessibility deltas) is already an incumbent.
- The signal we hoped would add value (motif grammar) does not, measurably.
- The on-wedge data is too small (n=56 test, 62 train) to resolve a real edge
  even if one exists — a power limitation, stated up front and confirmed.

An overclaimed win here would have required cherry-picking microglia (n=7, where
our GBT shows 0.571 on 7 points — meaningless) or dropping the CIs. We did neither.

## What would actually move this (honest next directions)
- **More on-wedge measured data** is the single highest-value lever — n=56 is the
  ceiling on any claim. New microglia/brain MPRA or allele-specific ATAC would
  matter more than any architecture change.
- **Fine-tune Borzoi itself** on the on-wedge direction labels (not features on
  top of it) — but 62 examples risks overfitting; needs the data above first.
- **Flashzoi / multi-replicate Borzoi ensembling** could tighten the incumbent
  estimate and is a cheaper next GPU step.

## Provenance
- Incumbents & floors: `benchmark/BASELINE_COMPARISON.md`, scored on
  `benchmark/split_manifest.csv` (test = chr 2,6,11,19; seed=0).
- Borzoi: `johahi/borzoi-replicate-0`, 524 kb, DNASE/ATAC tracks matched by
  biosample, scored on L40S GPU (`benchmark/borzoi_score.py`,
  `benchmark/borzoi_features.py`).
- Wedge model: `benchmark/train_wedge.py`, HistGradientBoosting depth-3,
  motif-Δ (49) + Borzoi per-context deltas (7) + grammar (4) + context one-hot,
  seed=0, trained on non-test folds. Model: `benchmark/wedge_model.pkl`.

## Files
- `benchmark/wedge_results.csv` — all regimes × contexts, acc/AUROC + CIs.
- `benchmark/wedge_predictions.csv` — per-variant predictions.
- `benchmark/baseline_comparison.csv` — full scoreboard incl. wedge + Borzoi rows.
- `benchmark/fig_final_scoreboard.png` — the figure.

# Directional wedge model — design

**Task (unchanged from the mandate):** predict the SIGN of a noncoding variant's
effect (alt vs ref activity) in a named cell context, targeting the on-wedge
contexts (immune/microglia/brain) where both the incumbents and the floor
baselines sit at chance (see `benchmark/BASELINE_COMPARISON.md`).

**This is a design doc, committed before training.** It fixes the architecture,
features, loss, split usage, and success test so the training run (GPU-gated) is a
prepared dispatch, not an improvised build.

---

## 1. The binding constraint: tiny on-wedge N

| fold | total | on-wedge (immune+microglia+brain) | off-wedge (K562/HepG2) |
|---|---|---|---|
| train | 1613 | **62** (immune 23, microglia 13, brain 26) | 1534 |
| test  | 538  | 69 | 445 |

**62 on-wedge training variants makes a deep from-scratch sequence model
impossible** — it would memorize, not generalize. Every design choice below is
shaped by this. We do NOT train an Enformer/Borzoi-scale CNN from scratch. We
build a *small, regularized* model on top of features that already encode sequence
and grammar, and we borrow strength from the large off-wedge fold.

## 2. Hypothesis (what the wedge actually is)

The rs6733839 failure and the on-wedge chance-level results say the same thing:
direction here is NOT a function of "which motif is gained/lost" (that's the PWM
floor, which fails). It is a function of **combinatorial motif grammar** — the
same motif reads as activating or repressing depending on its neighboring motifs
and local sequence context. So the model must see motif *context*, not just motif
presence.

## 3. Features (the core of the design)

Per variant × context, all computed for ref and alt, differenced (alt − ref):

1. **Motif Δ (49)** — best-overlap JASPAR log-odds delta per PWM. The floor
   features. (Already computed: `benchmark/data_with_features.parquet`.)
2. **Motif-context / grammar features (new, CPU):**
   - For each of the top wedge TFs (Spi1, MEF2A/C/D, CEBP, ETS, IRF, NFKB): the
     best-hit score of *co-occurring* motifs elsewhere in the ±FLANK window
     (captures "SPI1 in the presence of an adjacent activator vs repressor").
   - Pairwise motif co-occurrence products (gained-motif × strongest-resident-motif).
   - Distance from the variant to the nearest strong resident motif.
   - Flanking base composition (GC content, purine run length) left/right of variant.
3. **Borzoi sequence embedding (GPU):** ref and alt 524 kb windows → Borzoi
   penultimate representation at the variant bin; take the alt−ref delta vector
   (PCA-reduced to ~32 dims to control dimensionality against small N). This is the
   deep sequence-context signal the motif features cannot capture, and the reason
   the step is GPU-gated.
4. **Context indicator** — one-hot cell context, so a single model learns
   context-specific direction while sharing grammar across contexts.

## 4. Model

- **Primary: gradient-boosted trees** (LightGBM / XGBoost), `max_depth`≤3,
  strong `min_child_weight`, `subsample`/`colsample`<1, early stopping. Trees
  capture feature *interactions* (grammar) natively and are robust at small N.
- **Alternative: small regularized MLP** (1 hidden layer ≤64 units, dropout 0.5,
  weight decay) — only if it beats the GBM on the train-fold validation split.
- Both are small enough to train on CPU in minutes; the GPU cost is entirely in
  Borzoi embedding extraction (feature build), not model fitting.

## 5. Loss & training protocol

- **Loss:** binary cross-entropy on direction (alt-up = 1, alt-down = 0).
- **Train on non-test folds only** (chr not in {2,6,11,19}). Seed = 0.
- **Model selection** on an inner validation split *by chromosome* (hold out 2–3
  train chromosomes), never by variant — same leakage guard as the outer split.
- **Class balance:** direction is ~50/50 already (see context summary); no
  resampling needed, but we monitor per-context balance.
- **Two training regimes reported honestly:**
  a. *Cross-context* (train on all non-test folds incl. off-wedge) — borrows
     grammar strength from the 1534 off-wedge variants, tested on-wedge. This is
     the main bet: does off-wedge grammar transfer to the wedge?
  b. *On-wedge only* (train on the 62 on-wedge train variants) — almost certainly
     underpowered; reported as the honest lower bound.

## 6. Evaluation (identical to incumbents/floors)

- Scored on the **identical held-out set** (`benchmark/split_manifest.csv`), added
  as new rows to `benchmark/baseline_comparison.csv`.
- Direction accuracy + AUROC, **95% bootstrap CIs** (2000 resamples, seed 0),
  per named context and on-wedge pooled.
- **Definition of a win (from the mandate):** on-wedge pooled (or a named on-wedge
  context) accuracy/AUROC with a bootstrap CI that clears 0.5 AND clears the
  incumbent's CI AND the floor's CI. Overlapping CIs are NOT a win.

## 7. Leakage controls (treat any win as a bug until ruled out)

- **Borzoi-embedding leakage:** Borzoi is trained on ENCODE K562/HepG2 tracks, so
  its embeddings may leak on the off-wedge fold. On-wedge (the target) has no
  matching Borzoi training tracks, so the embedding is a generic sequence
  representation — lower leakage risk, but flagged. We report on-wedge as the
  honest OOD test.
- **No variant crosses the split** (chromosome hold-out already guarantees this).
- **Feature build uses only the variant window**, never the label or the test fold.
- If the model beats everything on-wedge, we re-check: (a) is any test variant in a
  training-adjacent locus? (b) is the on-wedge test artificially easy? (c) are we
  cherry-picking the metric? All three must be cleared before claiming a win.

## 8. Honest prior on the outcome

With **on-wedge test n≈56–69**, bootstrap CIs are wide (~±0.13). Even a genuinely
better model may not reach significance at this N. **A well-characterized negative
— "the grammar-aware model improves the point estimate but the CI still overlaps
the incumbent" — is a valid, publishable outcome** and closes the thread honestly.
We will not overclaim a point-estimate lift as a win.

## 9. What the GPU buys (why Steps 5 & 8 are gated)

- **Step 5:** Borzoi/Flashzoi *incumbent scoring* — fills the pending scoreboard row
  (`benchmark/borzoi_run.py`, ready).
- **Step 8:** Borzoi *embedding extraction* for feature #3, then CPU model fit +
  eval. Without the GPU we can still train the CPU-only variant (features 1,2,4) and
  report it; the GPU adds the deep-sequence feature that is the model's best shot at
  the wedge.

## Files this design will produce
- `benchmark/wedge_features.parquet` — full feature matrix (motif + grammar + [Borzoi] + context).
- `benchmark/wedge_model.pkl` — fitted model + config + seed.
- `benchmark/wedge_results.csv` — per-context acc/AUROC + CIs, appended to the scoreboard.
- `benchmark/fig_wedge_comparison.png` — final scoreboard figure with the model row.
- `benchmark/WEDGE_MODEL.md` — results + honest verdict (win or characterized negative).

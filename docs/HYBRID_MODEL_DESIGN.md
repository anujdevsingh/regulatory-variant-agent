# Hybrid multi-model variant-effect predictor — study & design

**Project:** regulatory-direction-independence (BIN1 / rs6733839), Claude Science Researcher track
**Phase 1 deliverable:** SOTA method survey + design of a hybrid ChromBPNet + AlphaGenome scoring method
**Status:** design doc — no code run yet; AlphaGenome API key needed for the build phase

---

## 0. Why we're doing this (the research reframing)

Up to now we ran the best *available public* model (a microglia ChromBPNet) and analyzed one variant. That is using a tool, not doing research. The research question we can genuinely advance:

> **Do the current best sequence models agree on the regulatory effect of a fine-mapped causal variant — and if we combine a specialized model with a general SOTA model, do we get a more accurate, better-calibrated, and more mechanistically complete prediction than either alone?**

rs6733839 is the ideal test case because we already hit a real puzzle: it is the fine-mapped causal variant at BIN1 (posterior 0.998, Schwartzentruber 2021) yet the microglia ChromBPNet gives it only a tiny, median-ranked accessibility effect. That discrepancy is exactly what a multimodal model might resolve.

**Scope decision (honest):** we are NOT training a foundation model from scratch — that needs months of compute and, critically, a ground-truth benchmark we don't have. The novel contribution is a **method** that integrates the top models, not a new neural network.

---

## 1. The two models we're combining

### ChromBPNet (what we already run)
- **Input / output:** 2,114 bp one-hot -> profile (1,000 bp) + total counts, for ONE assay (ATAC/DNase) in ONE cell type.
- **Strengths:** cell-type specific (we have a true microglia model), runs locally, fully interpretable (ISM, DeepSHAP-style attribution, TF-MoDISco), bias-corrected head.
- **Limits:** sees only ~2 kb of local context; predicts only accessibility; single modality — blind to whether a variant changes expression, TF binding, or splicing.

### AlphaGenome (the SOTA we're adding) — grounded in Avsec et al. 2026, *Nature* (DOI 10.1038/s41586-025-10014-0)
- **Input / output:** takes **1 Mb of DNA sequence** and predicts **thousands of genome tracks at up to single-base-pair resolution** — the paper states 5,930 human tracks across 11 output types. *(paper, verified from full text)*
- **Modalities:** gene expression, transcription initiation, **chromatin accessibility**, histone modifications, **transcription-factor binding**, chromatin contact maps, and splicing. *(paper)*
- **Benchmark performance (as reported by the authors — not independently verified by us):**
  - "matches or exceeds the strongest available external models in **25 of 26** evaluations of variant effect prediction." *(abstract, verified in full text)*
  - On accessibility QTLs specifically: **+8.0% versus ChromBPNet**, averaged across five datasets. *(paper Methods)*
  - Predicted vs observed effect sizes: **Pearson r = 0.74 for caQTLs**, r = 0.55 for SPI1 bQTLs. *(paper)*
  - Performance "generalized ... within specific cell types such as **microglia**." *(paper — directly relevant to us)*
- **Access:** Google DeepMind API, free non-commercial key (no local weights). Black-box relative to ChromBPNet.

**Why they're complementary:** ChromBPNet = a high-resolution, interpretable, cell-type-specific *microscope* on accessibility. AlphaGenome = a long-range, multimodal *survey* across many readouts. Neither is strictly better — they answer different questions. That is the basis for a hybrid.

---

## 2. The hybrid method — design

Three layers on top of the two base predictors. Each is a concrete, implementable component (ML-engineering work: ensembling, calibration, logic — not model training).

### Layer 1 — Harmonized variant scoring
Score every variant through both models on a common definition:
- ChromBPNet: log2FC of predicted ATAC counts (ref vs alt), microglia model — **already built** in `score_variant.py`.
- AlphaGenome: query the API for the same variant (chrom/pos/ref/alt, hg38) and pull the **chromatin-accessibility** effect for the matching brain/microglia track, plus the **expression** and **TF-binding** effects.
- Normalize both to a common sign convention (+ = more open / more expressed).

### Layer 2 — Consensus & confidence call (the novel logic)
For each variant, output a structured confidence tier rather than a single number:
- **High confidence** — both models agree on sign AND both non-negligible -> strong regulatory candidate.
- **Model-specific** — only the specialized (microglia ChromBPNet) fires -> possible cell-type-specific effect the general model averages out.
- **Multimodal-only** — AlphaGenome fires on expression/TF-binding but accessibility is flat in both -> the variant likely acts through a mechanism ChromBPNet cannot see (this is the hypothesis for rs6733839).
- **Disagreement** — opposite signs -> flag as low-confidence / needs wet-lab.

This confidence layer is the "make the tool the star" contribution: the instrument reports not just an effect but *how much to trust it and through what mechanism*.

### Layer 3 — Calibration & benchmark
- Reuse the existing null-percentile calibration for each model.
- **Benchmark against measured caQTLs:** take a public brain/microglia caQTL set with measured allelic effects, predict all through both models + the hybrid, and report predicted-vs-measured correlation. This yields a real accuracy number for each model AND for the hybrid — the honest definition of "accuracy" we currently lack.

---

## 3. What this will tell us about rs6733839 (the scientific payoff)

The open puzzle: rs6733839 is the causal variant but tiny on microglial accessibility. The hybrid directly tests three explanations:
1. **Mechanism is expression / TF binding, not accessibility** — if AlphaGenome shows a clear expression or MEF2/PU.1 binding effect while accessibility stays flat, that *resolves* the puzzle (Layer-2 "multimodal-only" tier).
2. **Effect is real but the microglia ChromBPNet under-calls it** — if AlphaGenome's microglia accessibility track shows a larger effect, that's a model-capability gap.
3. **The effect genuinely is small** — if both models agree it's tiny, our original honest finding is confirmed by the SOTA, which is itself a strong, defensible result.

Every outcome is publishable-quality honest science. There is no "failure" branch.

---

## 4. Build plan (next sessions)

1. **[you] Get an AlphaGenome API key** (free, non-commercial) and add it under Customize -> Credentials. *(blocks Layer 1 for AlphaGenome)*
2. **Layer 1** — add an `alphagenome` scorer module; score rs6733839 + the 25-variant credible set through it. Compare to ChromBPNet side by side.
3. **Layer 2** — implement the consensus/confidence logic; produce a per-variant confidence table + figure.
4. **Layer 3** — find a public brain/microglia caQTL dataset; benchmark all three (ChromBPNet, AlphaGenome, hybrid) predicted-vs-measured.
5. **Write-up** — extend RESULTS with the hybrid finding; update the tool + README.

**Timeline fit:** Layers 1-2 are ~1 session once the key exists; Layer 3 (benchmark) is ~1 session of data wrangling. Comfortable within the window.

---

## 5. Honest limitations to state up front
- AlphaGenome numbers in Section 1 are the **authors' reported benchmarks**, quoted from the paper, not re-measured by us.
- AlphaGenome is a black-box API — we cannot do attribution on it the way we can with ChromBPNet; interpretability stays with the specialized model.
- The hybrid is a *method-level* contribution (ensembling + calibration + confidence logic), not a newly trained model.
- The caQTL benchmark is only as good as the public dataset we can find; brain/microglia caQTL data is limited.

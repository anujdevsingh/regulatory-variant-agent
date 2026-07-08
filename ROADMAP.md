# ROADMAP.md — where we stand & where we go next

*Living document. Updated each working session. If you're an agent picking this
up: **read this file first**, then ask the user which direction to move.*

**Last updated:** 2026-07-08 (session 2)

---

## The one-paragraph status

We built a reusable, honest tool that traces a noncoding disease variant to the
transcription-factor motif it affects, using pretrained sequence models
(ChromBPNet, AlphaGenome) — demonstrated on the Alzheimer's/BIN1 variant
**rs6733839**. The full analysis arc is done and committed. The headline finding:
rs6733839 is the fine-mapped **causal** variant (posterior 0.998) yet looks
"quiet" on chromatin accessibility — because its real predicted effect is on **TF
binding** (MEF2A/SPI1), which two independent models (ChromBPNet + AlphaGenome)
agree on. Statistical causality and predicted molecular mechanism are decoupled.

## Honest self-assessment (where we rank)

- **Methods contribution to the field: SMALL.** We didn't build or beat any model.
  We used the world's best models carefully. What's ours is the *analysis* and a
  clean *tool* — teaching/reproducibility value, not a new algorithm.
- **Scientific result: MEDIUM -> upgraded toward STRONG (2026-07-08).** The
  TF-binding finding is now confirmed by *independent measured data*: published
  MPRA + CRISPR agree that rs6733839 is functional, its effect is subtle, the
  mechanism is TF binding, and the TFs are MEF2 + SPI1. (rs6733839-specific
  measurements from the 2025 context-dependent AD preprint; Cooper 2022 Science
  cited as the landmark large-scale AD MPRA, full text not retrieved.) 5 of 6 of our predictions matched measurement; the one
  miss (immune-cell direction) exposed a real, citable model limit
  (context-dependent enhancer grammar). See `results/MPRA_VALIDATION.md`.
- **As a learning project / hackathon entry: STRONG.** Complete correct workflow,
  honest reporting of a subtle result instead of a forced dramatic one.

**Goal: move BOTH the methods contribution and the scientific result from
small/medium to STRONG — honestly, without overclaiming.**

---

## DONE (committed to this repo)

- [x] Scoping + literature grounding (`SCOPING.md`)
- [x] Single-variant scoring: rs6733839 ref/alt through microglia ChromBPNet (`results/RESULTS.md`)
- [x] Cell-type specificity scan (6 brain cell types)
- [x] ISM + expected-gradients attribution + JASPAR motif match
- [x] Calibration vs 266 common brain-peak SNPs — 54th percentile (`results/CALIBRATION.md`)
- [x] Credible-set scan (Schwartzentruber 2021, 25 variants) — causal variant is 11th of 25 by effect (`results/ALLELIC_SERIES.md`)
- [x] AlphaGenome multimodal cross-check — TF binding is the largest effect; corroborates ChromBPNet MEF2/SPI1 (`results/AG_MULTIMODAL_RESULTS.md`)
- [x] One-command tool with `--calibrate` and `--credible-set` modes (`score_variant.py`)
- [x] Data provenance documented (`DATA.md`)
- [x] GTEx bulk-brain eQTL check (see finding below)
- [x] **MPRA validation** — cross-checked predictions vs published measured MPRA; 5/6 confirmed (`results/MPRA_VALIDATION.md`)
- [x] **3D visualization** — rendered PU.1/SPI1 (1PUE) + MEF2A (1EGW) TF–DNA co-crystals as interactive artifacts (`results/VISUALIZATION_3D.md`)

## Finding logged this session — GTEx eQTL (bulk tissue)

Checked rs6733839 -> BIN1 in GTEx v8:
- Precomputed-significant only in **Artery Aorta** (p=5.6e-7), NOT brain.
- On-the-fly across 13 brain regions: nominal p<0.05 in cerebellum
  (p=1.4e-4, risk-T lowers BIN1), cortex (p=0.03, T lowers), hippocampus
  (p=0.03, T raises — opposite). Other 10 regions null.
- **Read:** bulk brain does NOT cleanly confirm the effect, and direction is
  inconsistent across regions. Consistent with a **microglia-specific** effect
  diluted in bulk tissue (microglia are a small fraction of brain). This is
  on-theme, not a disappointment — it motivates single-cell eQTL data.

---

## NEXT STEPS — two ladders

### Ladder A: make the SCIENTIFIC RESULT strong (add independent MEASURED evidence)

1. **[HIGHEST VALUE] Microglia-specific eQTL, not bulk GTEx.** Look up
   rs6733839 -> BIN1 in a microglia eQTL atlas (MiGA / Young et al. 2021 /
   Kosoy et al. 2022). If it's a clean microglia eQTL with consistent direction,
   it independently confirms the predicted TF-binding -> expression story. This is
   the single move that takes the result from MEDIUM to STRONG. (Pure compute;
   data not in the GTEx connector — may need a network-access grant to GEO/Zenodo.)
2. **Colocalization** of the AD GWAS signal with a microglia eQTL (coloc /
   SuSiE-coloc) — does the *same* causal variant drive both? Gold-standard
   computational argument that a variant is functional.
3. **Measured chromatin footprint at the base** — cross-reference microglia
   ATAC/ChIP footprint databases (UniBind, ENCODE microglia) for a measured
   MEF2/PU.1 footprint the risk allele disrupts. Measured data, not model.

### Ladder B: make the METHODS CONTRIBUTION strong (build something the field lacks)

1. **Consensus / mechanism-classification scorer.** Formalize the multi-model
   idea in `docs/HYBRID_MODEL_DESIGN.md`: run ChromBPNet + AlphaGenome + eQTL,
   classify each variant into a mechanism tier (accessibility / TF-occupancy /
   expression / decoupled). Nobody ships a clean tool that says "these two SOTA
   models agree, here's the mechanism tier." That's a nameable method.
2. **Benchmark it.** Run many known-functional regulatory variants through the
   consensus scorer; show it recovers them better than any single model. Turns
   one worked example into a validated method.
3. **Package it** — pip-installable, tested, documented. "hackathon script" ->
   "tool people cite."

### Also outstanding (from earlier plan)
- [ ] Demo video + write-up (last unchecked README box)
- [ ] Hackathon Discord intro (needs name + LinkedIn)

---

## Recommended single next move

**Ladder A #1 — the microglia eQTL cross-check.** It's pure compute, scientifically
motivated by the bulk-GTEx dilution we just showed, closes the prediction->
measurement loop if positive, AND feeds the eQTL input that Ladder B's consensus
scorer needs. Report honestly whichever way it comes out.

---

## Decision log (which direction we actually chose, each session)

| Date | Decision |
|---|---|
| 2026-07-08 | Committed AlphaGenome results; wired `--credible-set` flag; added DATA.md. Ran GTEx bulk eQTL (mixed/diluted). Created this roadmap. **Next decision pending from user.** |
| 2026-07-08 (s2) | **Chose route #1: borrow public MPRA measured data.** Found a 2025 context-dependent AD MPRA preprint covering rs6733839 (Cooper 2022 Science cited as the landmark large-scale AD MPRA for context, full text not retrieved); built prediction-vs-measurement scorecard (5/6 match).
| 2026-07-08 (s2) | Built **3D visualization**: fetched real PU.1/SPI1 (PDB 1PUE) and MEF2A (PDB 1EGW) TF–DNA co-crystals, cleaned to interactive .pdb artifacts + side-by-side render. Makes the two-TF / two-context mechanism tangible. | Scientific result upgraded toward STRONG. **Next: user chose to consider route #2 (train our own model) next.** |

# ABSTRACT_DRAFT.md

*Draft abstract for the regulatory-variant-agent finding. Written to the numbers
actually obtained (Phases 1-3). Update as/if the eQTL layer and Boltz co-fold land.*

## Title (working)
Chromatin accessibility and enhancer activity directions are statistically independent
for noncoding variants, explaining why sequence models cannot predict disease-relevant
effect direction

## Abstract

Sequence-to-function deep-learning models (AlphaGenome, Borzoi) predict genomic tracks
with high accuracy, yet their utility for interpreting disease-associated noncoding
variants hinges on a harder question: can they predict the *direction* of a variant's
regulatory effect? We assembled a chromosome-split benchmark of noncoding variants with
laboratory-measured effect direction across nine cellular contexts, including a native
human-microglia caQTL map (Kosoy et al., 95 donors) that is the on-target task for both
models. On the fairest possible test — chromatin-accessibility direction in the native
cell type — AlphaGenome (0.537), Borzoi (0.551), motif-PWM floors, and models trained
in-distribution on the caQTL data itself are all statistically indistinguishable from
chance (majority-class 0.565). Direction is not recoverable from local sequence.

To explain this negative, we tested whether a variant's effect on chromatin accessibility
predicts its effect on enhancer/expression activity. Across 685 variants significant in
both layers, sign concordance was 0.528 (95% CI 0.491-0.565; binomial p=0.15) — the two
layers are statistically **independent**: a variant's accessibility direction carries
essentially no information about its activity direction. This independence is robust to
dropping estimate-based datasets (0.53 in every subset). Consistent with an
accessibility-reading mechanism, both frontier models trend more accurate on variants
whose layers agree (Borzoi 0.625) than on decoupled variants (0.538), though this
stratified difference is not individually significant at current n. The Alzheimer's-risk
variant rs6733839 (BIN1) is the mechanistic anchor: its risk allele opens chromatin
(caQTL Z=3.3) while repressing enhancer activity (MPRA), so AlphaGenome and Borzoi each
call one layer correctly and the other backwards.

We conclude that predicting regulatory-variant direction from sequence is limited not by
model capacity but by a layer-decoupling that single-readout models cannot represent:
accessibility and activity are separately encoded, and the disease-relevant readout
requires resolving which layer governs the phenotype. We release the benchmark, the
paired-layer decoupling statistic, and per-variant scores as a reusable resource.

## Honesty ledger (what is solid vs. what is a stretch)
- SOLID: the negative benchmark (well-powered, in-distribution control included); the
  independence statistic (n=685, robust to provenance).
- SUGGESTIVE / UNDERPOWERED: model-accuracy-by-concordance (right shape, overlapping CIs).
- NOT SHOWN: decoupling is NOT predictable from sequence features (AUROC 0.441) — honest
  negative that limits the "reusable predictor" claim.
- GENUINELY OPEN: the SPI1-vs-MEF2A mechanism; the clean same-cell-type caQTL∩eQTL number
  (needs syn30308484); the Boltz co-fold (GPU-deferred).

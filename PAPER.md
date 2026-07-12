# Chromatin accessibility and enhancer activity effect-directions are statistically independent for noncoding variants, and this limits sequence-model variant interpretation

**Anuj Dev Singh**
Repository: `anujdevsingh/regulatory-direction-independence` · Preprint draft · 2026-07-12

---

## Abstract

Sequence-to-function deep-learning models such as AlphaGenome and Borzoi predict
genomic assay tracks with high accuracy, and are increasingly used to interpret
disease-associated noncoding variants. Their practical value hinges on a harder
question than track prediction: can they predict the **direction** (sign) of a
variant's regulatory effect in a defined cell context? We assembled a
chromosome-split benchmark of noncoding variants with laboratory-measured effect
direction spanning nine cellular contexts, including a native human-microglia
chromatin-accessibility QTL (caQTL) map from 95 donors (Kosoy et al., 2022) that
is the on-target prediction task for both models. On the fairest achievable test —
chromatin-accessibility direction in the native cell type — AlphaGenome
(0.537, 95% CI 0.485–0.587), Borzoi (0.551, 0.499–0.601), motif-PWM floors, and
models trained in-distribution on the caQTL data itself are all statistically
indistinguishable from chance (majority-class baseline 0.565). Effect direction is
not recoverable from local sequence at any model capacity we tested.

To explain this negative, we asked whether a variant's effect on chromatin
accessibility predicts its effect on gene expression. In the cleanest available
test — caQTL versus expression QTL (eQTL) in the *same 95 microglia donors* —
sign concordance across 354 variants significant in both layers was 0.506
(95% CI 0.455–0.556; binomial p = 0.87): the two layers are statistically
**independent**, with no cross-cell-type confound. A secondary caQTL-versus-
enhancer-activity comparison (685 variants, MPRA/SuRE) reproduced this (0.528,
0.491–0.565) and was robust to removing estimate-derived datasets. Consistent with
models reading a single (accessibility) layer, both frontier models trend more
accurate on variants whose layers agree than on decoupled variants, though this
stratified difference is not individually significant at present sample size.

The Alzheimer's-disease risk variant rs6733839 (upstream of *BIN1*) anchors the
mechanism across three measured layers in microglia: the risk allele opens
chromatin (caQTL Z = 3.3), raises *BIN1* expression (eQTL Z = 6.4), yet represses
episomal enhancer activity (MPRA). A Boltz-2 co-fold of the MEF2A dimer on the
local enhancer sequence is high-confidence for both alleles (interface pTM 0.978)
and shows a tighter protein–DNA interface at the risk allele (+12.5% contacts),
consistent with a risk-allele-created MEF2A site. We conclude that predicting
regulatory-variant direction from sequence is limited not by model capacity but by
an accessibility–activity decoupling that single-readout models cannot represent.
We release the benchmark, the paired-layer independence statistic, and all
per-variant scores as a reusable resource.

---

## 1. Introduction

Genome-wide association studies place the large majority of disease-associated
variants in noncoding sequence, where interpretation requires predicting a
variant's effect on gene regulation. Deep-learning models trained to map DNA
sequence to functional genomic assays — DeepSEA and Basset in the first
generation, and now long-context models such as Borzoi (524 kb) and AlphaGenome
(1 Mb) — achieve strong correlations on held-out track prediction and are widely
used for in-silico variant scoring.

Track-prediction accuracy, however, is not the quantity a variant-interpretation
pipeline needs. The clinically and mechanistically relevant question is
directional: does a given variant *increase* or *decrease* accessibility, binding,
or expression in the relevant cell type? Directional accuracy is rarely reported
as such, and where it has been examined the picture is discouraging: correlations
of predicted with measured effects on causal-variant benchmarks remain modest.

We set out to test directional prediction rigorously in a single disease-relevant
setting — microglia/brain/immune context, motivated by the *BIN1* Alzheimer's
locus and its lead variant rs6733839 — and to do so under a benchmark-first
discipline: assemble a held-out, chromosome-split test set of variants with
*measured* direction; score the leading models and floor baselines on the
identical set; report bootstrap confidence intervals rather than point estimates;
and treat any apparent win as a leakage bug until excluded. This report is the
result. It is, deliberately, a negative result with a mechanistic explanation:
we find that direction is not predictable, we show *why* through a layer-decoupling
analysis, and we anchor the mechanism on a single well-characterized variant.

---

## 2. Methods

### 2.1 Benchmark assembly
We harmonized noncoding variants with measured effect direction from four public
sources into a single convention (direction = sign of the effect attributed to the
alternate allele in the variant's cell context): the 2025 context-dependent
Alzheimer's MPRA (THP-1 macrophage, HMC3 microglia, brain, HEK293T); SuRE raQTL
(K562, HepG2); a hiPSC neural-progenitor MPRA (GSE244011); and a 3′-UTR MPRA
(microglia, SH-SY5Y; GSE253841). The assembled set contains 6,377 variant×context
rows across nine contexts. A native human-microglia caQTL map (Kosoy et al. 2022;
Synapse syn30308248; meta-analysis over 95 donors) contributed 1,478 variants with
measured chromatin-accessibility direction, added as a distinct context.

### 2.2 Split
All evaluation uses a fixed split by **chromosome** (test = chr 2, 6, 11, 19; chr2
forced to retain *BIN1*/rs6733839; seed 0), never by variant, to prevent
LD-driven leakage. The manifest is committed.

### 2.3 Models and baselines, all scored on the identical held-out set
- **AlphaGenome** (API): 1 Mb context, ATAC + DNase modalities, DIFF_LOG2_SUM
  scorer, direction = sign of mean effect over context-matched biosample tracks.
- **Borzoi** (`johahi/borzoi-replicate-0`, open weights): 524 kb windows, direction
  = sign of alt−ref over five central bins of microglia/macrophage accessibility
  tracks, run on an L40S GPU.
- **Floor 1 — motif PWM Δ-score**: sign of the largest-magnitude JASPAR motif
  score change at the variant (49-PWM vertebrate panel).
- **Floor 2 — logistic-on-motifs**: L2 logistic regression on per-motif Δ features,
  fit on training folds only.
- **In-distribution controls** (caQTL set): logistic and gradient-boosted trees
  trained on the caQTL training folds themselves — an upper bound on what local
  sequence features can extract.

### 2.4 Statistics
Direction accuracy and AUROC are reported with 95% bootstrap confidence intervals
(≥2,000 resamples, seed 0). Sign-concordance between layers is tested against 0.5
with an exact binomial test and 5,000-resample bootstrap CIs. A "win" was defined
in advance as a bootstrap CI non-overlapping with both incumbents and both floors
in ≥1 named context.

### 2.5 Layer-decoupling analysis
We paired each variant's microglia caQTL direction with (a) its microglia eQTL
direction in the same 95 donors (Kosoy meta-eQTL, Synapse syn30308484; primary,
confound-free), and (b) its enhancer-activity direction from MPRA/SuRE (secondary).
Concordance was computed on variants significant in both layers (|caQTL Z| > 1.96;
activity FDR < 0.05 or p < 0.01; eQTL |Z| > 1.96).

### 2.6 Structural co-fold
The MEF2A MADS-box dimer (sequence from PDB 1EGW) was co-folded with the 17-bp
*BIN1* enhancer duplex centered on rs6733839, for both alleles, using Boltz-2
(5 diffusion samples, 3 recycling steps, MSA server). Interface was quantified as
protein–DNA atom pairs within 4 Å.

---

## 3. Results

### 3.1 No model predicts accessibility direction in the native cell type

On the native microglia caQTL test set (361 held-out variants) — the fairest test
either frontier model can be given, since chromatin accessibility is precisely what
they are trained to predict, in the exact cell type of interest — every method sits
at chance (Figure 1, Table 1). AlphaGenome reaches 0.537 (95% CI 0.485–0.587),
Borzoi 0.551 (0.499–0.601), the motif floor 0.493, and neither clears the 0.565
majority-class rate. Borzoi's run had no zero-inflation (all 361 variants fall
inside microglia accessibility peaks), so this is an uncontaminated read. Decisively,
models trained **in-distribution** on the caQTL data itself remain at chance
(logistic 0.529; boosted trees 0.499): the directional signal is not present in the
local sequence, independent of model capacity. No method meets the pre-registered
win criterion; this is a well-powered negative.

**Table 1. Direction accuracy on native microglia caQTL (n = 361).**

| Method | Accuracy (95% CI) | AUROC |
|---|---|---|
| Motif PWM Δ-score (floor) | 0.493 (0.443–0.543) | — |
| Logistic-on-motifs (in-distribution) | 0.529 (0.479–0.579) | 0.544 |
| Boosted trees (in-distribution) | 0.499 (0.446–0.549) | 0.501 |
| AlphaGenome (1 Mb) | 0.537 (0.485–0.587) | 0.547 |
| Borzoi (524 kb) | 0.551 (0.499–0.601) | 0.562 |
| Majority-class baseline | 0.565 | — |

### 3.2 Chromatin-accessibility and expression directions are independent

To explain the negative, we tested whether accessibility direction predicts
expression direction in the same cells. Using the microglia caQTL and eQTL maps
from the *same 95 donors* — eliminating any cross-cell-type confound — sign
concordance among 354 variants significant in both layers was 0.506 (95% CI
0.455–0.556; binomial p = 0.87), indistinguishable from 0.5 (Figure 3). Every
stratum (all-paired, caQTL-significant, eQTL-significant) fell on 0.5. The
secondary caQTL-versus-enhancer-activity comparison (685 variants significant in
both layers) reproduced this at 0.528 (0.491–0.565; p = 0.15), and the value was
stable at ~0.53 when estimate-derived datasets were dropped (paper-statistic-only:
0.530). A variant's chromatin-accessibility direction therefore carries
essentially no information about its expression/activity direction.

We emphasize the precise nature of this finding: the layers are **statistically
independent**, not systematically *anti*-correlated. Independence is sufficient to
explain the directional-prediction failure — a model that reads one layer cannot
recover the sign of the other — but it is a quieter statement than a systematic
sign-flip, and we report it as such.

### 3.3 Decoupling is not predictable from sequence, and the model-failure link is directional but underpowered

A logistic model on effect magnitudes, caQTL significance, lineage, and 49 motif-Δ
features failed to predict which variants decouple (chromosome-split AUROC 0.441,
95% CI 0.361–0.524), an honest negative that limits any "reusable decoupling
predictor" claim. Splitting model accuracy against activity direction by
concordance showed the hypothesized shape — both models more accurate on concordant
variants (AlphaGenome 0.594, Borzoi 0.625) than decoupled ones (both 0.538) — but
the confidence intervals overlap, so the stratified effect is suggestive rather
than significant at current n (Figure 2C).

### 3.4 rs6733839 anchors the mechanism across three measured layers

The lead *BIN1* Alzheimer's variant rs6733839 is present in all three microglia
layers with strong, measured signals (Table 2). The risk allele opens chromatin and
raises *BIN1* expression — the two native-genome readouts agree — while repressing
episomal enhancer activity in MPRA. Both AlphaGenome and Borzoi call one layer
correctly and the other backwards, each in a different direction: there is no single
model that is "right" about this variant, precisely because the layers it reads
disagree with the layer it is scored against.

**Table 2. rs6733839 (Alzheimer's risk allele, T) across measured microglia layers.**

| Layer | Measured effect of risk-T | Evidence |
|---|---|---|
| Chromatin accessibility (caQTL) | **opens** (+) | Kosoy, Z = 3.3 |
| Gene expression (eQTL, *BIN1*) | **up** (+) | Kosoy, Z = 6.4 |
| Enhancer activity (MPRA) | **represses** (−) | 2025 AD-MPRA |

### 3.5 A structural co-fold shows a tighter MEF2A interface at the risk allele

Boltz-2 co-folds of the MEF2A dimer on the *BIN1* enhancer were high-confidence for
both alleles (interface pTM 0.978; complex pLDDT 0.98), indicating a well-defined
complex (Figure 4). The risk-allele complex made more protein–DNA contacts than the
non-risk complex (287 vs 255 within 4 Å; +12.5%), consistent with the sequence-level
prediction that the risk allele creates a stronger MEF2A motif (+7.56 bits by
JASPAR) and with the measured chromatin-opening and expression-increase. Which
transcription factor mediates the *repressive* MPRA effect remains unresolved: the
originating AD-MPRA study attributes it to SPI1, whereas our sequence and structural
evidence favor a MEF2A site-creation event. We report both and force neither.

---

## 4. Discussion

Across every context we assembled — neural-progenitor MPRA, 3′-UTR MPRA, and a
native microglia caQTL map — the direction of a noncoding variant's regulatory
effect is not predictable from sequence, by frontier models, floor baselines, or
models trained in-distribution. The consistency across contexts and the
in-distribution control together argue that this is a property of the
prediction problem, not of any particular model's capacity.

The paired-layer analysis supplies a mechanism. Chromatin accessibility and gene
expression respond to a variant in statistically independent directions
(same-donor concordance 0.506). A sequence model that predicts one functional
layer therefore cannot, even in principle, recover the sign of another layer it was
not trained on — and the disease-relevant readout (expression) is frequently the
one it is not reading. rs6733839 makes the abstraction concrete: a single variant
that opens chromatin, raises expression, and yet represses an isolated enhancer
fragment, so that the "correct" model depends entirely on which assay one scores
against.

The practical implication for variant-interpretation pipelines is cautionary:
accessibility-direction predictions from sequence models should not be read as
expression-direction predictions. The two are empirically decoupled, and conflating
them will produce confidently wrong directional calls on exactly the
context-dependent variants that matter most for disease.

---

## 5. Limitations

We state these plainly, as they bound the claims above.

1. **Independence, not systematic decoupling.** Our headline is that the layers are
   *independent* (concordance ≈ 0.5), not that they systematically flip. This
   explains the prediction failure but is a weaker statement than a directed
   anti-correlation, and we do not claim the latter.
2. **The model-failure-by-concordance link is underpowered.** The effect has the
   predicted direction but overlapping CIs; a larger same-cell-type paired set is
   needed to establish significance.
3. **Decoupling is not itself predictable** from the sequence features we tested
   (AUROC 0.441), so we do not offer a decoupling classifier as a tool.
4. **No wet-lab validation.** The MEF2A site-creation, the thermodynamic
   interpretation, and the Boltz-2 co-fold are computational; the +12.5% interface
   difference is a single-model geometric readout, not a free-energy calculation.
5. **The responsible TF for the MPRA repression is unresolved** (SPI1 vs MEF2A).
6. **Some activity-layer directions are our re-estimates** from public count
   matrices rather than the original papers' models; the core result is robust to
   dropping these, but they are flagged in the provenance audit.
7. **In-distribution flattering of incumbents.** Some benchmark variants may lie in
   the incumbents' training data (ENCODE/GTEx); this can only inflate their scores,
   and they are still at chance.

---

## 6. Data and code availability

All data, split manifests, per-variant scores, figures, and analysis code are in
the repository `anujdevsingh/regulatory-direction-independence` under `results/` and
`bench/`, committed per stage with configuration and seed. Key public sources:
Kosoy et al. 2022 microglia caQTL/eQTL (Synapse syn30308248 / syn30308484;
AD Knowledge Portal); 2025 context-dependent AD-MPRA; SuRE raQTL
(van Arensbergen et al.); GSE244011; GSE253841. Structure predictions used Boltz-2
(github.com/jwohlwend/boltz); variant scoring used AlphaGenome (API) and Borzoi
(`johahi/borzoi-replicate-0`).

---

## Figures

**Figure 1.** Direction accuracy on the native microglia caQTL test set: both
frontier models and all baselines at chance.
`results/fig_caqtl_result.png`

**Figure 2.** Layer-decoupling at scale (caQTL vs MPRA/SuRE activity): sign
agreement, independence by stratum, and model accuracy split by concordance.
`results/decoupling/fig_phase1_decoupling.png`

**Figure 3.** Clean same-donor test — microglia caQTL vs eQTL: chromatin and
expression effect-directions are statistically independent.
`results/decoupling/fig_caqtl_eqtl_clean.png`

**Figure 4.** Boltz-2 co-fold of MEF2A dimer on the *BIN1* enhancer: high-confidence
complexes for both alleles, tighter protein–DNA interface at the risk allele.
`results/decoupling/fig_boltz_cofold.png`

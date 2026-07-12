# Predicting the direction of noncoding regulatory-variant effects from DNA sequence: a well-powered negative, and a mechanistic explanation

**Project:** regulatory-direction-independence · **Anchor variant:** rs6733839 (chr2:127135234, C>T; AD-risk allele T; ~25 kb upstream of BIN1) · **Focus context:** microglia / brain / immune

---

## Summary

We asked a single, narrow, decision-relevant question: given a noncoding DNA
variant and a cell context, can a model predict the **direction** (sign) of its
regulatory effect — up or down — better than the current best sequence models?
We benchmarked the two leading models (Google **AlphaGenome**, open-source
**Borzoi**) against floor baselines (a JASPAR motif PWM Δ-score and
logistic/boosted-tree models on motif features) on held-out variants with
laboratory-measured direction, split by chromosome so no variant leaks between
train and test.

**Result: direction-from-sequence is at chance for every model, in every context
we could assemble — including the fairest possible test.** This is a robust,
well-powered negative, not a weak signal we failed to capture.

**But the anchor variant rs6733839 revealed why**, and that mechanism is the
real contribution.

---

## The benchmark

Held-out, measured-direction variants harmonized to one convention
(direction = sign of the effect on the alternate allele), split by chromosome
(test = chr 2, 6, 11, 19; seed 0; never split by variant). Sources:

| Context | Assay | Layer |
|---|---|---|
| Neural progenitor (hiPSC NPC) | MPRA | enhancer activity |
| Microglia / SH-SY5Y | 3'-UTR MPRA | post-transcriptional |
| K562 / HepG2 | SuRE raQTL | enhancer activity |
| **Microglia (Kosoy 2022)** | **caQTL** | **chromatin accessibility** |

Total ~6,400 variant×context rows across 9 contexts, plus the 1,478-variant
native-microglia caQTL set (361 held out) added from the on-target Kosoy study.

## The pivotal test

The Kosoy microglia caQTL data (95 human donors) is the *on-target* dataset: the
exact cell type where rs6733839 fails, and the chromatin-accessibility layer that
AlphaGenome and Borzoi are **natively trained to predict**. This is the fairest
test either model can be given.

**Native microglia caQTL, 361 held-out variants (95% bootstrap CI, seed 0):**

| Model | Direction accuracy | AUROC |
|---|---|---|
| Motif PWM (floor) | 0.493 [.443,.543] | — |
| Logistic-motifs (in-distribution) | 0.529 [.479,.579] | 0.544 |
| Boosted trees (in-distribution) | 0.499 [.446,.549] | 0.501 |
| AlphaGenome | 0.537 [.485,.587] | 0.547 |
| Borzoi | 0.551 [.499,.601] | 0.562 |
| *(majority class)* | *0.565* | — |

Every model is at chance. No CI clears the 0.565 majority-class rate. Borzoi's
run had zero zero-inflation (all 361 variants sit inside microglia accessibility
peaks), so this is an uncontaminated read. Critically, even models trained
**in-distribution** on the caQTL data itself remain at chance — the directional
signal is not recoverable from local sequence, regardless of model capacity.

## Why the incumbents fail on rs6733839 — the mechanism

rs6733839 is present in the Kosoy data with a strong signal
(effect_allele = T, Beta = +0.147, Z = 3.34). The risk-T allele **opens
chromatin** in microglia. But an independent MPRA measured that the same risk-T
allele **represses enhancer activity**. These are opposite signs on two different
molecular layers — and each frontier model is right on one and wrong on the other:

| Layer | Measured (risk-T) | AlphaGenome | Borzoi |
|---|---|---|---|
| Chromatin accessibility (caQTL) | OPENS (+) | opens → **correct** | closes → **wrong** |
| Enhancer output (MPRA) | REPRESSES (−) | activates → **wrong** | down → **correct** |

There is no single model that is "right" about rs6733839. The variant opens
chromatin *while* repressing transcription. Which model looks correct depends
entirely on which molecular layer is measured. This **accessibility↔activity
decoupling** — not any single model's error — is the true difficulty ("wedge"):
a model reading accessibility correctly still gets the disease-relevant activity
direction backwards, because for this variant the two layers disagree.

(The transcription factor responsible for the MPRA repression is not settled: the
originating AD-MPRA study models it as SPI1-mediated, whereas our JASPAR analysis
finds the risk-T allele creates a strong new MEF2A site (+7.56 bits) while SPI1 is
essentially unchanged (+0.18). The caQTL result is independent of that question.)

## Interpretation

1. **A well-powered negative on the general task.** Direction-from-sequence is at
   chance across every context (NPC n=788, 3'-UTR microglia/SH, native microglia
   caQTL n=361), for frontier models, floor baselines, and in-distribution models
   alike. Increasing model capacity is unlikely to help when the signal is absent
   from the input.

2. **A mechanistic explanation, not just a null.** The rs6733839 case shows the
   negative is not mysterious: single-layer predictions (accessibility) can be
   correct while the disease-relevant readout (activity/expression) moves the
   opposite way. Predicting *direction* well requires resolving *which layer*
   governs the phenotype — a harder, multi-layer problem than current
   sequence→track models pose.

3. **Honest close.** Per the project's definition of done, a well-characterized
   negative is a legitimate result. We did not build a model that beats the
   incumbents on direction, because the task as posed is not learnable from the
   available data — and we can state precisely why.

## What would change the answer (open directions)

- **Selective prediction / abstention:** call direction only on high-confidence
  variants (large effect, strong motif) and measure accuracy on that subset — a
  possible honest win against forced-choice incumbents.
- **Predict the decoupling itself:** reframe the target as "do a variant's
  chromatin and activity directions agree?" — a novel, potentially learnable
  question our multi-layer data uniquely sets up.
- **Add the expression layer:** microglia eQTL (Kosoy syn30308484) completes the
  chromatin→activity→expression picture for rs6733839.

## Reproducibility

All data, splits, configs, scores, and figures are committed to the repository
(`anujdevsingh/regulatory-direction-independence`). Chromosome split, seed=0, bootstrap
CIs on every accuracy/AUROC. AlphaGenome via API (1 Mb context, ATAC+DNASE,
context-matched biosample tracks); Borzoi (johahi/borzoi-replicate-0, 524 kb,
microglia/macrophage accessibility tracks) on an L40S GPU.

# Effect-direction of noncoding regulatory variants is not predictable from sequence because chromatin accessibility and gene expression decouple: a benchmark and mechanistic analysis in human microglia

**Anuj Dev Singh**^1^

^1^ Independent Researcher, New Delhi, India

**Correspondence:** Anuj Dev Singh, anujdev9928@gmail.com; web: https://www.codewithanuj.com/

**ORCID:** https://orcid.org/0009-0002-4374-3990

---

## Abstract

**Background.** Sequence-to-function deep-learning models — DeepSEA and Basset in the
first generation, and the long-context models Borzoi and AlphaGenome today — predict
genomic assay tracks with high accuracy and are increasingly used to interpret the
noncoding variants that underlie most disease-associated genetic risk. Their utility for
variant interpretation rests on a harder question than track prediction: can they predict
the *direction* (sign) of a variant's regulatory effect in a defined cell context? This
quantity is rarely benchmarked directly.

**Results.** We assembled a chromosome-split benchmark of noncoding variants with
laboratory-measured effect direction spanning nine cellular contexts (6,377
variant×context measurements), and added a native human-microglia chromatin-accessibility
QTL (caQTL) map from 95 donors as an on-target test for both frontier models. On the
fairest achievable test — chromatin-accessibility direction in the native cell type —
AlphaGenome (accuracy 0.537, 95% CI 0.485–0.587), Borzoi (0.551, 0.499–0.601),
motif-PWM floor baselines, and models trained in-distribution on the caQTL data itself
were all statistically indistinguishable from chance (majority-class baseline 0.565).
To explain this, we tested whether a variant's effect on chromatin accessibility predicts
its effect on gene expression in the *same 95 donors* (caQTL versus expression QTL).
Sign concordance across 354 variants significant in both layers was 0.506 (95% CI
0.455–0.556; binomial p = 0.87) — the two layers are statistically independent, with no
cross-cell-type confound. A secondary caQTL-versus-enhancer-activity comparison (685
variants, MPRA/SuRE) reproduced this (0.528, 0.491–0.565) and survived removal of
estimate-derived datasets. The Alzheimer's-disease risk variant rs6733839 (upstream of
*BIN1*) anchors the mechanism: the risk allele opens chromatin (caQTL Z = 3.3), raises
*BIN1* expression (eQTL Z = 6.4), yet represses episomal enhancer activity (MPRA). A
Boltz-2 co-fold of the MEF2A dimer on the local enhancer is high-confidence for both
alleles (interface pTM 0.978) and shows a tighter protein–DNA interface at the risk allele
(+12.5% contacts), consistent with a risk-allele-created MEF2A motif.

**Conclusions.** Predicting regulatory-variant effect-direction from sequence is limited
not by model capacity but by an accessibility–activity decoupling that single-readout
models cannot represent. Directional predictions from a model trained on one functional
layer should not be interpreted as predictions for another. We release the harmonized
benchmark, the paired-layer independence statistic, and all per-variant scores as a
reusable community resource.

**Keywords:** noncoding variants; variant effect prediction; deep learning; chromatin
accessibility; expression QTL; microglia; Alzheimer's disease; *BIN1*; benchmark;
sequence-to-function models

---

## Background

Genome-wide association studies (GWAS) localize the large majority of disease-associated
variants to noncoding sequence, where mechanistic interpretation requires predicting a
variant's effect on gene regulation. A decade of sequence-to-function deep learning has
transformed this problem: DeepSEA [1] and Basset [2] first showed that convolutional
networks trained on ENCODE chromatin data could predict the regulatory impact of single
nucleotide changes; the field has since scaled to long-context transformer and U-Net
architectures — Borzoi, which predicts RNA-seq coverage and other assays over 524 kb
windows [4], and AlphaGenome, which processes up to one megabase at base-pair resolution
across eleven molecular modalities [3]. These models advance the state of the art on
held-out track prediction and are now routinely used for in-silico variant scoring.

Track-prediction accuracy, however, is not the quantity a variant-interpretation pipeline
needs. The clinically and mechanistically actionable question is directional: does a given
variant *increase* or *decrease* accessibility, transcription-factor binding, or expression
in the relevant cell type? The ground truth for this question comes from functional assays —
massively parallel reporter assays, including saturation mutagenesis of regulatory elements
at single-base resolution [8], and QTL maps — against which model predictions can be scored.
Directional accuracy is nonetheless seldom reported as a headline metric,
and independent evaluations on causal-variant benchmarks have found that effect-size
correlations for state-of-the-art models remain modest [5]. Whether the leading models can
reliably call the *sign* of a variant's effect — particularly for the context-dependent,
combinatorial regulatory logic that characterizes disease loci — has not been established
on a like-for-like, held-out benchmark.

We addressed this in a single disease-relevant setting: the microglia/brain/immune context,
motivated by the *BIN1* Alzheimer's-disease locus and its lead noncoding variant rs6733839.
We adopted a benchmark-first discipline throughout: assemble a held-out test set of variants
with laboratory-*measured* direction; split by chromosome to prevent linkage-driven leakage;
score the leading models against floor baselines and in-distribution controls on the
*identical* set; report bootstrap confidence intervals rather than point estimates; and
treat any apparent improvement as a potential leakage artifact until excluded. The result
reported here is, deliberately, a negative one with a mechanistic explanation. We find that
effect-direction is not predictable from local sequence at any model capacity we tested; we
show *why* through a paired-layer decoupling analysis in matched donors; and we anchor the
mechanism on a single, deeply characterized variant.

---

## Methods

### Benchmark assembly and direction convention
We harmonized noncoding variants with measured effect direction from public sources into a
single convention: **direction = sign of the effect attributed to the alternate allele in
the variant's cell context.** Sources were (i) a 2025 context-dependent Alzheimer's-disease
massively parallel reporter assay (MPRA) covering THP-1 macrophage, HMC3 microglia, brain
tissue, and HEK293T [13]; (ii) SuRE raQTL data for K562 and HepG2 [7]; (iii) a hiPSC
neural-progenitor MPRA (GEO GSE244011); and (iv) a 3′-UTR MPRA in microglia and SH-SY5Y
(GEO GSE253841). The assembled matrix comprises 6,377 variant×context measurements across
nine contexts. Coordinates were harmonized to GRCh38 (hg19 sources lifted with UCSC
liftOver); allele orientation was reconciled to the reference/alternate convention and
strand-corrected where required.

### On-target chromatin and expression layers
A native human-microglia caQTL map (Kosoy et al. [6]; meta-analysis over 95 donors; AD
Knowledge Portal / Synapse syn30308248) contributed measured chromatin-accessibility
direction; the matched microglia meta-eQTL map from the same donors (Synapse syn30308484)
contributed measured expression direction. For each variant we retained the strongest
association (maximum |Z|) and harmonized the reported effect allele to our
reference/alternate convention.

### Chromosome split
All evaluation uses a fixed split by **chromosome** (test = chr 2, 6, 11, 19; chr2 forced
to retain *BIN1*/rs6733839; random seed 0), never by variant, to prevent
linkage-disequilibrium leakage between train and test. The split manifest is version-
controlled with the data.

### Models, baselines, and controls (all scored on the identical held-out set)
- **AlphaGenome** [3] via the public API: 1 Mb context; ATAC and DNase modalities;
  DIFF_LOG2_SUM variant scorer; predicted direction = sign of the mean effect over
  biosample tracks matched to the target context by a curated regular expression.
- **Borzoi** [4] (open weights, replicate 0): 524 kb input windows; predicted direction =
  sign of alt−ref over the five central prediction bins of microglia/macrophage
  accessibility tracks; executed on an NVIDIA L40S GPU.
- **Floor baseline 1 — motif PWM Δ-score:** sign of the largest-magnitude change in JASPAR
  [11] motif log-odds score at the variant (49-PWM curated vertebrate panel).
- **Floor baseline 2 — logistic-on-motifs:** L2-regularized logistic regression on
  per-motif Δ features, fit on training folds only.
- **In-distribution controls (caQTL set):** logistic regression and gradient-boosted trees
  trained directly on the caQTL training folds — an upper bound on the directional signal
  extractable from local sequence features.

### Statistics
Direction accuracy and AUROC are reported with 95% bootstrap confidence intervals (≥2,000
resamples; seed 0). Between-layer sign concordance is tested against 0.5 with an exact
binomial test and 5,000-resample bootstrap intervals. A "win" was defined a priori as a
bootstrap CI non-overlapping with both incumbents and both floor baselines in at least one
named context.

### Layer-decoupling analysis
Each variant's microglia caQTL direction was paired with (a) its microglia eQTL direction
in the same 95 donors (primary, confound-free) and (b) its enhancer-activity direction from
MPRA/SuRE (secondary). Concordance was computed on variants significant in both layers
(|caQTL Z| > 1.96; activity FDR < 0.05 or p < 0.01; |eQTL Z| > 1.96). A drop-one sensitivity
analysis removed estimate-derived activity datasets (those for which we re-estimated
direction from public count matrices rather than using the original study's model).

### Predicting decoupling
We trained an L2 logistic model to predict, per variant, whether the caQTL and activity
signs disagree, using effect magnitudes, caQTL significance, cell lineage, and 49 motif-Δ
features, evaluated under the same chromosome split (AUROC with bootstrap CI).

### Structural co-fold
The MEF2A MADS-box dimer (sequence from PDB 1EGW) was co-folded with the 17-bp *BIN1*
enhancer duplex centered on rs6733839, for both alleles, using Boltz-2 [12] with five
diffusion samples, three recycling steps,
and MSA-server profiles. The protein–DNA interface was quantified as the number of
protein–DNA atom pairs within 4 Å.

---

## Results

### No model predicts accessibility direction in the native cell type
On the native microglia caQTL test set (361 held-out variants) — the fairest test either
frontier model can be given, since chromatin accessibility is precisely what they are
trained to predict, in the exact cell type of interest — every method sits at chance
(Figure 1; Table 1). AlphaGenome reached 0.537 (95% CI 0.485–0.587), Borzoi 0.551
(0.499–0.601), the motif floor 0.493, and none cleared the 0.565 majority-class rate.
Borzoi's run had no zero-inflation (all 361 variants fell inside microglia accessibility
peaks), confirming an uncontaminated read. Decisively, models trained *in-distribution* on
the caQTL data itself remained at chance (logistic 0.529; gradient-boosted trees 0.499):
the directional signal is not present in the local sequence, independent of model capacity.
No method met the pre-registered win criterion. This is a well-powered negative result.

**Table 1. Direction accuracy on the native human-microglia caQTL test set (n = 361).**

| Method | Accuracy (95% CI) | AUROC |
|---|---|---|
| Motif PWM Δ-score (floor) | 0.493 (0.443–0.543) | — |
| Logistic-on-motifs (in-distribution) | 0.529 (0.479–0.579) | 0.544 |
| Gradient-boosted trees (in-distribution) | 0.499 (0.446–0.549) | 0.501 |
| AlphaGenome (1 Mb context) | 0.537 (0.485–0.587) | 0.547 |
| Borzoi (524 kb context) | 0.551 (0.499–0.601) | 0.562 |
| Majority-class baseline | 0.565 | — |

### Chromatin-accessibility and expression effect-directions are statistically independent
To explain the negative, we tested whether accessibility direction predicts expression
direction in the same cells. Using the microglia caQTL and eQTL maps from the *same 95
donors* — eliminating any cross-cell-type confound — sign concordance among 354 variants
significant in both layers was 0.506 (95% CI 0.455–0.556; binomial p = 0.87),
indistinguishable from 0.5 (Figure 3; Table 2). Every stratum (all-paired, caQTL-
significant, eQTL-significant) fell on 0.5. The secondary caQTL-versus-enhancer-activity
comparison (685 variants significant in both layers) reproduced this at 0.528
(0.491–0.565; p = 0.15), and the value was stable at ~0.53 when estimate-derived datasets
were dropped (paper-statistic-only subset: 0.530; Figure 2). A variant's chromatin-
accessibility direction therefore carries essentially no information about its
expression/activity direction. We are precise about the nature of the finding: the layers
are statistically *independent*, not systematically *anti*-correlated. Independence is
sufficient to explain the directional-prediction failure — a model reading one layer
cannot recover the sign of another — but it is a quieter claim than a systematic sign-flip,
and we report it as such.

**Table 2. Same-donor microglia caQTL–eQTL sign concordance, by significance stratum.**

| Stratum | n | Concordance (95% CI) | Binomial p |
|---|---|---|---|
| All paired (no significance filter) | 1,322 | 0.511 (0.485–0.538) | 0.43 |
| Significant in both layers | 354 | 0.506 (0.455–0.556) | 0.87 |
| caQTL-significant | 617 | 0.519 (0.480–0.558) | 0.38 |
| eQTL-significant | 744 | 0.503 (0.466–0.538) | 0.91 |

### Decoupling is not predictable, and the model-failure link is directional but underpowered
A logistic model on effect magnitudes, caQTL significance, lineage, and 49 motif-Δ features
failed to predict which variants decouple (chromosome-split AUROC 0.441, 95% CI
0.361–0.524) — an honest negative that precludes offering a decoupling classifier as a tool.
Stratifying model accuracy against activity direction by concordance showed the hypothesized
shape — both models more accurate on concordant variants (AlphaGenome 0.594, Borzoi 0.625)
than on decoupled ones (both 0.538) — but the confidence intervals overlap, so this
stratified effect is suggestive rather than significant at present sample size (Figure 2).

### rs6733839 anchors the mechanism across three measured layers
The lead *BIN1* Alzheimer's variant rs6733839, fine-mapped as the credible causal variant
at this locus [9], is present in all three microglia layers with strong, measured signals
(Table 3). Functional regulatory variation in dementia-associated transcriptional networks
has been characterized more broadly by massively parallel assays [10]. The risk allele opens chromatin and raises *BIN1*
expression — the two native-genome readouts agree — while repressing episomal enhancer
activity in the reporter assay. Both AlphaGenome and Borzoi call one layer correctly and the
other backwards, each in a different direction; there is no single model that is "right"
about this variant, precisely because the layers it reads disagree with the layer against
which it is scored.

**Table 3. rs6733839 (Alzheimer's risk allele, T) across measured microglia layers.**

| Layer | Measured effect of risk-T | Evidence |
|---|---|---|
| Chromatin accessibility (caQTL) | opens (+) | Kosoy et al., Z = 3.3 |
| Gene expression (eQTL, *BIN1*) | up (+) | Kosoy et al., Z = 6.4 |
| Episomal enhancer activity (MPRA) | represses (−) | 2025 AD-MPRA |

### A structural co-fold shows a tighter MEF2A interface at the risk allele
Boltz-2 co-folds of the MEF2A dimer on the *BIN1* enhancer were high-confidence for both
alleles (interface pTM 0.978; complex pLDDT 0.98), indicating a well-defined complex
(Figure 4). The risk-allele complex made more protein–DNA contacts than the non-risk
complex (287 versus 255 within 4 Å; +12.5%), consistent with the sequence-level prediction
that the risk allele creates a stronger MEF2A motif (+7.56 bits by JASPAR) and with the
measured chromatin-opening and expression increase. The transcription factor mediating the
*repressive* reporter-assay effect remains unresolved: the originating AD-MPRA study
attributes it to SPI1, whereas our sequence and structural evidence favor a MEF2A
site-creation event. We report both interpretations and force neither.

---

## Discussion

Across every context we assembled — neural-progenitor MPRA, 3′-UTR MPRA, and a native
microglia caQTL map — the direction of a noncoding variant's regulatory effect is not
predictable from sequence, by frontier models, by floor baselines, or by models trained
in-distribution. The consistency across contexts, together with the in-distribution control,
argues that this is a property of the prediction problem rather than of any particular
model's capacity.

The paired-layer analysis supplies a mechanism. Chromatin accessibility and gene expression
respond to a variant in statistically independent directions (same-donor concordance 0.506).
A sequence model that predicts one functional layer therefore cannot, even in principle,
recover the sign of another layer on which it was not trained — and the disease-relevant
readout, expression, is frequently the one it is not reading. rs6733839 renders the
abstraction concrete: a single variant that opens chromatin, raises expression, and yet
represses an isolated enhancer fragment, so that the "correct" model depends entirely on
which assay one scores against.

The practical implication for variant-interpretation pipelines is cautionary. Accessibility-
direction predictions from sequence models should not be read as expression-direction
predictions; the two are empirically decoupled, and conflating them will produce confidently
wrong directional calls on exactly the context-dependent variants that matter most for
disease. This does not diminish the value of these models for track prediction or for
prioritizing which variants are regulatory; it bounds their use for calling the *direction*
of effect on a specific downstream readout.

Two directions would strengthen the claim. First, a larger same-cell-type paired set would
give the model-failure-by-concordance stratification the power to reach significance.
Second, orthogonal single-locus validation (allele-specific transcription-factor binding or
a reporter titration at rs6733839) would elevate the MEF2A mechanism from a
sequence-and-structure prediction to direct evidence. Both are natural extensions; neither
is required for the central, well-powered result reported here.

---

## Conclusions

Effect-direction of noncoding regulatory variants is not recoverable from local sequence by
current models, and this is explained by a statistical independence between a variant's
chromatin-accessibility and gene-expression effects rather than by insufficient model
capacity. We provide a harmonized, chromosome-split benchmark with measured direction across
nine contexts, a matched-donor decoupling statistic, a full set of per-variant scores for
two frontier models and floor baselines, and a structurally anchored case study at the
*BIN1* Alzheimer's locus. We release these as a reusable resource for the community and as a
cautionary reference point for directional variant interpretation.

---

## Limitations

We state these plainly, as they bound the claims above.

1. The headline is that the layers are statistically *independent* (concordance ≈ 0.5), not
   that they systematically flip; this explains the prediction failure but is a weaker claim
   than a directed anti-correlation, which we do not make.
2. The model-failure-by-concordance link has the predicted direction but overlapping
   confidence intervals; a larger same-cell-type paired set is needed for significance.
3. Decoupling is not itself predictable from the sequence features we tested (AUROC 0.441),
   so we do not offer a decoupling classifier.
4. There is no wet-lab validation; the MEF2A site-creation, its thermodynamic
   interpretation, and the Boltz-2 co-fold are computational, and the +12.5% interface
   difference is a single-model geometric readout, not a free-energy calculation.
5. The transcription factor responsible for the reporter-assay repression is unresolved
   (SPI1 versus MEF2A).
6. Some activity-layer directions are our re-estimates from public count matrices rather
   than the original studies' models; the core result is robust to dropping these, and they
   are flagged in the provenance record.
7. Some benchmark variants may lie within the incumbent models' training data (ENCODE/GTEx);
   this can only inflate their scores, and they remain at chance.

---

## Declarations

### Availability of data and materials
All data, split manifests, per-variant model scores, figures, and analysis code supporting
the conclusions of this article are available in the repository
`github.com/anujdevsingh/regulatory-direction-independence` under the `bench/` and `results/`
directories, committed per analysis stage with configuration and random seed. Primary public
datasets: human-microglia caQTL and meta-eQTL summary statistics (Kosoy et al. [6]; AD
Knowledge Portal / Synapse syn30308248 and syn30308484), which are registered-access — freely
downloadable after creating an account and agreeing to the portal's data-use terms, with no
sponsor approval required; SuRE raQTL [7]; the 2025 context-dependent AD-MPRA [13]; GEO
GSE244011 and GSE253841 (open). Structure predictions used Boltz-2 [12]; variant scoring used
the AlphaGenome API [3] (non-commercial terms) and Borzoi open weights (replicate 0) [4].
Genome build GRCh38.

### Ethics approval and consent to participate
Not applicable. This study is a secondary analysis of previously published, de-identified
public datasets and does not involve new human or animal subjects.

### Consent for publication
Not applicable.

### Competing interests
The author declares no competing interests.

### Funding
This research received no specific grant from any funding agency in the public, commercial,
or not-for-profit sectors. It was conducted independently by the author.

### Authors' contributions
A.D.S. conceived the study, assembled the benchmark, performed all analyses, produced the
figures, and wrote the manuscript.

### Acknowledgements
This work was carried out during the Claude Science hackathon. Data assembly, analysis, and
figure and manuscript preparation were performed by the author with the assistance of an
AI research agent (Anthropic Claude, operated within the Claude Science environment) under
the author's direction and scientific review. All study design choices, methodological
decisions, interpretations, and final claims are the author's, and the author takes full
responsibility for the content. We thank the Kosoy et al. authors and the AD Knowledge Portal
for the microglia QTL resources, and the authors of the MPRA/SuRE datasets used here.

---

## References

1. Zhou J, Troyanskaya OG. Predicting effects of noncoding variants with deep learning-based
   sequence model. *Nat Methods* 12:931–934 (2015). doi:10.1038/nmeth.3547
2. Kelley DR, Snoek J, Rinn JL. Basset: learning the regulatory code of the accessible
   genome with deep convolutional neural networks. *Genome Res* 26:990–999 (2016).
   doi:10.1101/gr.200535.115
3. Avsec Ž, et al. AlphaGenome: advancing regulatory variant effect prediction with a
   unified DNA sequence model. *bioRxiv* 2025.06.25.661532 (2025).
   doi:10.1101/2025.06.25.661532
4. Linder J, Srivastava D, Yuan H, et al. Predicting RNA-seq coverage from DNA sequence as a
   unifying model of gene regulation. *Nat Genet* 57:949–961 (2025).
   doi:10.1038/s41588-024-02053-6
5. Kathail P, Bajwa A, Ioannidis NM. Leveraging genomic deep learning models for non-coding
   variant effect prediction. *arXiv* 2411.11158 (2024).
6. Kosoy R, et al. Genetics of the human microglia regulome refines Alzheimer's disease risk
   loci. *Nat Genet* 54:1145–1154 (2022). doi:10.1038/s41588-022-01149-1
7. van Arensbergen J, et al. High-throughput identification of human SNPs affecting
   regulatory element activity. *Nat Genet* 51:1160–1169 (2019).
   doi:10.1038/s41588-019-0455-2
8. Kircher M, et al. Saturation mutagenesis of disease-associated regulatory elements at
   single base-pair resolution. *Nat Commun* 10:3583 (2019). doi:10.1038/s41467-019-11526-w
9. Schwartzentruber J, et al. Genome-wide meta-analysis, fine-mapping and integrative
   prioritization implicate new Alzheimer's disease risk genes. *Nat Genet* 53:392–402
   (2021). doi:10.1038/s41588-020-00776-w
10. Cooper YA, et al. Functional regulatory variants implicate distinct transcriptional
    networks in dementia. *Science* 377:eabi8654 (2022). doi:10.1126/science.abi8654
11. Castro-Mondragon JA, et al. JASPAR 2022: the ninth release of the open-access database
    of transcription factor binding profiles. *Nucleic Acids Res* 50:D165–D173 (2022).
    doi:10.1093/nar/gkab1113
12. Passaro S, Wohlwend J, et al. Boltz-2: structure and affinity prediction (2025).
    Software: github.com/jwohlwend/boltz
13. Context-dependent regulatory variants in Alzheimer's disease. *bioRxiv*
    2025.07.11.659973 (2025). doi:10.1101/2025.07.11.659973

---

## Figure legends

**Figure 1.** Direction accuracy on the native human-microglia caQTL test set (n = 361).
Both frontier models (AlphaGenome, Borzoi), motif floor baselines, and in-distribution
controls fall at or below the majority-class baseline (0.565); error bars are 95% bootstrap
confidence intervals.
`results/fig_caqtl_result.png`

**Figure 2.** Layer-decoupling at scale (caQTL versus MPRA/SuRE enhancer activity). Sign
agreement by stratum, robustness to dropping estimate-derived datasets, and model accuracy
stratified by concordant versus decoupled variants.
`results/decoupling/fig_phase1_decoupling.png`

**Figure 3.** Clean same-donor test: microglia caQTL versus eQTL. (A) Per-variant effect
sizes coloured by concordance, with rs6733839 (*BIN1*) marked. (B) Sign concordance with
95% confidence intervals across significance strata; all strata are indistinguishable from
independence (0.5).
`results/decoupling/fig_caqtl_eqtl_clean.png`

**Figure 4.** Boltz-2 co-fold of the MEF2A dimer on the *BIN1* enhancer, shown in a shared
orientation for the reference (non-risk C) and alternate (risk T) alleles. Both complexes
are high-confidence (interface pTM 0.978); the risk allele forms a tighter protein–DNA
interface (+12.5% contacts within 4 Å). The rs6733839 site is marked.
`results/decoupling/fig_boltz_cofold.png`

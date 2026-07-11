# Publication-plan execution — Phases 1–3 results

*Executed against docs/PUBLICATION_PLAN.md. Honest reporting: each phase's
definition-of-done is met or the gap is named. GPU-gated Boltz co-fold (Phase 3.1)
deferred — SSH auth to the GPU host dropped mid-session; it is nice-to-have polish,
not load-bearing.*

## Phase 1 — the decoupling statistic (THE CORE)

### 1.1b CLEAN same-donor caQTL∩eQTL (added after eQTL download syn30308484)
The primary, cleanest pairing — chromatin accessibility vs gene expression in the SAME
95 microglia donors, no cross-cell-type confound. 1,322 of our variants matched the
microglia meta-eQTL map; harmonized to alt-allele convention (0 mismatches).
- **caQTL–eQTL sign concordance, sig-in-both: 0.506 [0.455, 0.556], n=354, p=0.87**
- All paired: 0.511 [0.485,0.538] (n=1322); caQTL-sig: 0.519; eQTL-sig: 0.503.
**This is the definitive result the plan was built toward, and it CONFIRMS independence
cleanly** — chromatin and expression directions are statistically indistinguishable from
50/50 in the native cell type, with no cross-lineage proxy. (`caqtl_eqtl_concordance.csv`,
`fig_caqtl_eqtl_clean.png`.)

rs6733839 three-layer (microglia): chromatin OPENS (+, Z=3.3), expression BIN1 UP (+, Z=6.4),
enhancer-activity MPRA REPRESSES (−). Native-genome layers (chromatin+expression) AGREE;
the episomal MPRA disagrees — consistent with the variant acting in genomic context, not
as an isolated enhancer element.

### 1.1 Paired-layer set (secondary caQTL∩activity route)
Built `results/decoupling/paired_layers.csv`: variants with BOTH a microglia caQTL
direction (Kosoy syn30308248, paper statistic) AND an activity direction (MPRA/SuRE).
- **Total paired: 1,478** — feasibility gate (≥150) cleared many times over.
- Significant-in-both (|caQTL Z|>1.96 AND activity FDR<0.05 / p<0.01): **685**
  (neural/immune 73, cross-lineage K562/HepG2 612).
- NOTE: the plan's *primary cleanest* pairing (caQTL∩eQTL, same 95 donors) needs the
  eQTL file syn30308484, not yet downloaded. This is the caQTL∩activity secondary route,
  which the plan explicitly authorizes. eQTL would upgrade the same-cell-type power.

### 1.2 Decoupling rate — THE HEADLINE NUMBER
Concordance = fraction where chromatin and activity signs AGREE:
- **All sig-in-both: 0.528 [0.491, 0.565], n=685, binomial p=0.15**
- Neural/immune: 0.507 [0.384, 0.616], n=73, p=1.0
- Cross-lineage: 0.531 [0.492, 0.570], n=612, p=0.14

**Interpretation (honest):** chromatin and activity signs are **statistically
INDEPENDENT** (concordance indistinguishable from 0.5), NOT systematically opposite.
This is a real, well-powered characterization: knowing a variant's chromatin direction
tells you essentially nothing about its activity direction. It is a *null of dependence*,
which is subtly different from (and less flashy than) "the layers systematically flip."

### 1.3 Is decoupling predictable?
Logistic model (|effects|, caQTL Z, lineage, 49 motif-Δ features), chromosome-split:
- **AUROC 0.441 [0.361, 0.524]** — CI spans 0.5. **Decoupling is NOT predictable** from
  these sequence/effect features. Honest negative.

### 1.4 Model failure vs decoupling — the hypothesis figure
Model accuracy AGAINST ACTIVITY direction, split by concordance (sig-in-both):
| Subset | AlphaGenome | Borzoi |
|---|---|---|
| Concordant | 0.594 [.500,.688] | 0.625 [.531,.719] |
| Decoupled | 0.538 [.430,.634] | 0.538 [.441,.634] |
**Right shape** — both models do better when layers agree (Borzoi's concordant CI clears
0.5) and drop to chance when they decouple — **but CIs overlap; not significant** at this n.
Directionally supports "models read one layer, fail when it's the wrong sign," under-powered.

## Phase 2 — data defensibility
### 2.1 Provenance audit (`results/decoupling/provenance_audit.csv`)
Headline data (Kosoy caQTL) and SuRE/AD-MPRA are PAPER STATISTICS. Two sources are OUR
ESTIMATES: PSYCH_MPRA (NPC, our joint-norm skew, not paper GLMM) and CHEN_3'UTR
(variant-summed t-test, explicitly not the paper's barcode GLMM) — flagged as
robustness-only.
### 2.3 Drop-one sensitivity — the null SURVIVES
- Full: 0.528 [.491,.565] | Drop estimates (PSYCH+CHEN): 0.532 [.495,.571] |
  Paper-statistic-only (SuRE): 0.530 [.492,.570].
Concordance stays ~0.53 everywhere. **The independence finding is not an artifact of
estimate-based data.**

## Phase 3 — rs6733839 mechanism
### 3.1 Boltz-2 co-fold — DEFERRED (GPU auth dropped mid-session). Not load-bearing.
### 3.2 MEF2 vs SPI1 (`results/decoupling/tf_evidence_rs6733839.csv`)
- Sequence (JASPAR): risk-T CREATES a +7.56-bit MEF2A site; SPI1 ~unchanged (+0.18).
- Chromatin (MEASURED caQTL): risk-T opens — consistent with gaining an activating site.
- AlphaGenome TF-ChIP (predicted): MEF2A top signal (0.315) > SPI1.
- The 2025 AD-MPRA paper attributes the *repression* to SPI1 (their model).
**Weight of evidence:** sequence + measured chromatin favor MEF2A site-creation; the
activity-repression mechanism is genuinely unsettled. Report both; do not force one.
Measured footprinting (Phase 3.2 stretch) would settle it — not done this session.

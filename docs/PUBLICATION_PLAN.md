# PUBLICATION_PLAN.md — from hackathon project to a publishable finding

*Hand-off document. If you're an agent (Claude Science) picking this up: read
this file top to bottom, then work the phases in order. Each task names its
data, method, and a **definition of done**. Report honestly whichever way each
result comes out — the paper is a negative + a mechanism, so a clean "no" is
still a result. Do NOT overclaim.*

**Author:** anujdevsingh · **Repo:** anujdevsingh/regulatory-direction-independence
**Created:** 2026-07-11 · **Scope:** ~3–5 weeks of mostly-analysis work (NOT hackathon scope)

---

## 0. The one claim we are building toward

> **Across many noncoding variants, the direction of a variant's effect on
> chromatin *accessibility* and its effect on *gene expression / enhancer
> activity* systematically decouple. This decoupling is why frontier sequence
> models (AlphaGenome, Borzoi) cannot predict the disease-relevant direction —
> shown at scale, and anchored mechanistically on the BIN1 Alzheimer's variant
> rs6733839.**

Everything below serves that one sentence. The negative benchmark you already
have becomes *interesting* only once the decoupling statistic (Phase 1) explains
it. That link is the paper.

**Honest venue calibration:** a strong **bioRxiv preprint** at minimum; if the
decoupling scales cleanly and is even weakly predictable, this is
**Genome Biology / Bioinformatics / NAR Genomics & Bioinformatics** tier
(rigorous negative + a named mechanism + a reusable tool). It is **not**
Nature/Cell — that would need new wet-lab experiments. Do not aim there; aim for
the honest, defensible venue and actually land it.

**Write the abstract FIRST** (before any new compute). It forces the story and
tells you which numbers you actually need. Draft it, commit it to
`docs/ABSTRACT_DRAFT.md`, and update it as results land.

---

## Phase 1 — Turn the anecdote into a statistic  ← THE CORE OF THE PAPER

Right now the accessibility↔activity decoupling is shown for **one** variant
(rs6733839). One variant is a story. We need a **number across many variants**.

### 1.1 — Build the paired-layer variant set  (do this first; it is the feasibility gate)

**Primary dataset (cleanest, on-target):** intersect the two Kosoy 2022 microglia
resources — *same 95 donors, same cells*:
- **caQTL** (chromatin accessibility) — Synapse **syn30308248** — *already
  downloaded and harmonized* (1,478 of our variants have direction).
- **eQTL** (gene expression) — Synapse **syn30308484** — *needs downloading from
  the same AD Knowledge Portal open tier.*

For every variant present in **both**, record `sign(caQTL Beta)` and
`sign(eQTL Beta)`. This is the paired accessibility-vs-expression table.

**Secondary datasets (orthogonal activity layer, for replication):** variants
that have a caQTL direction AND a measured MPRA/activity direction —
Lee NPC MPRA (**GSE244011**), van Arensbergen SuRE raQTL (**osf.io/w5bzq**),
AD-MPRA (**PMC12265656**). Use these to show the decoupling isn't a
caQTL-vs-eQTL artifact.

> **⚠ Pivotal feasibility gate — check the intersection size BEFORE building
> anything downstream.** rs6733839 proves the intersection is non-empty, but the
> claim needs *power*. If the microglia caQTL∩eQTL set is < ~150 variants, the
> "at scale" claim is weak.
> **Fallback ladder if too small:** (a) add caQTL∩MPRA and pool layers as
> "accessibility vs activity/expression"; (b) broaden to a second cell type
> where both layers exist (K562: DNase-/caQTL + SuRE/MPRA are both large); (c) if
> still underpowered, the honest paper narrows to "we could not power the
> decoupling test in microglia — here is exactly how much data it would take."
> **Report the intersection count as the first result. Do not proceed silently
> if it's small.**

**Definition of done:** a committed table `results/decoupling/paired_layers.csv`
(variant, caQTL sign+Beta, eQTL/MPRA sign+Beta, context, source) and a one-line
report of N in each pairing.

### 1.2 — Quantify the decoupling

For each pairing, compute the **concordance rate**: fraction of variants where
accessibility and expression/activity move the *same* direction.
- Binomial test vs 50% (are signs independent?); McNemar where paired.
- **Bootstrap 95% CIs on every rate** (match the rigor already in the repo).
- Report per-context and pooled. Restrict to variants significant in both layers
  (pre-register the significance threshold; do a sensitivity sweep of it).

**Definition of done:** "**X% of microglia variants decouple** (95% CI […],
p=…), N=…" — one headline number with a CI. Figure: 2×2 sign-agreement / scatter
of caQTL Beta vs eQTL Beta colored by concordance.

### 1.3 — Is the decoupling *predictable*?  (the constructive turn reviewers like)

Turn the negative into a partial positive: can we predict *which* variants
decouple? Features per variant: |effect| in each layer, distance to TSS,
motif class present (MEF2 / SPI1 / CTCF / …), chromatin state, conservation
(phyloP). Fit a logistic model (chromosome-split, seed 0, bootstrap CI — reuse
your existing harness). Even weak-but-real predictability (AUROC > 0.5 with CI
clearing 0.5) is a genuine positive contribution riding on top of the negative.

**Definition of done:** AUROC-for-decoupling with CI + a feature-importance
figure. If it's at chance, report that honestly — "decoupling is not predictable
from these features" is still publishable.

### 1.4 — Link the model failure to the decoupling  ← the key figure of the paper

Split the benchmark variants into **concordant** vs **decoupled**. Re-score
AlphaGenome and Borzoi on each subset. **Hypothesis: the models are near chance
on decoupled variants and better on concordant ones.** If true, this is the
sentence that makes the whole paper: *"frontier models fail on direction because
they read one layer, and one layer is systematically the wrong sign for
decoupled variants."*

**Definition of done:** a table — model direction-accuracy on concordant vs
decoupled subsets, with CIs — and the interpretation stated plainly (holds or
doesn't).

---

## Phase 2 — Clean the measured data  (defensibility; kills the reviewer attack)

Your own docs admit some directions are *estimates*, not the source papers'
statistics (the Chen 3'-UTR set explicitly can't reproduce the paper's GLMM).
Fix this where it carries weight.

### 2.1 — Data-provenance audit
Extend `DATA.md` into a table: every dataset → how direction was derived → is it
**the paper's own published statistic** or **our estimate from summed counts**?
Flag every "estimate" row.

### 2.2 — Replace estimates on any headline dataset
For datasets that carry the main claim, use the **paper's published per-variant
effect + significance** (from supplementary tables) instead of a home-brewed
estimate — or reproduce their model properly (barcode-level GLMM). Specifically:
- **Chen 3'-UTR (GSE253841):** get barcode-level counts and run their GLMM, OR
  demote it to a *supporting/robustness* row, not a headline row.
- **Lee NPC (GSE244011):** confirm the direction is the paper's call, not an
  estimate; use their supplementary effect sizes if available.

### 2.3 — Sensitivity / drop-one analysis
Show the **main decoupling result survives dropping the weakest (estimate-based)
datasets**. This directly defuses "your data is noisy." A result that holds
without the shaky inputs is bulletproof.

**Definition of done:** every headline number traces to a paper's own statistics
or a properly reproduced model; a committed sensitivity table showing the claim
holds when estimate-based datasets are removed.

---

## Phase 3 — Structural + TF resolution  (close the rs6733839 mechanism)

The anchor variant's mechanism has two loose ends.

### 3.1 — Run the staged Boltz-2 co-fold
The ref/alt MEF2A–DNA YAMLs are already staged in `results/boltz/`. Run them on
a **GPU host** (L40S used previously). Report the ref-vs-alt interface / affinity
difference — or, honestly, "no structural difference resolved at this
resolution." Either outcome is fine and reportable.

### 3.2 — Settle MEF2 vs SPI1 with *measured* data
Currently unsettled: your JASPAR scan says risk-T **creates a MEF2A site**
(+7.56 bits); the source AD-MPRA study attributes repression to **SPI1**;
AlphaGenome predicts **both** go up. Resolve with measured microglia TF evidence:
- **Footprinting** (TOBIAS or HINT) on microglia ATAC (Nott 2019, or the Kosoy
  peaks) at chr2:127,135,234 — does the risk allele change a MEF2 or a PU.1/SPI1
  footprint?
- **UniBind / ENCODE microglia ChIP** for measured MEF2 and PU.1 occupancy at the
  locus.
- Reconcile against AlphaGenome's ChIP predictions.

Report the **weight of evidence** honestly. Do not force a single TF — "two TFs
implicated, measured footprint favors X" is a fine, defensible conclusion.

**Definition of done:** Boltz result reported (either direction); an
evidence-weighted TF statement backed by measured data, not just a motif scan.

---

## Phase 4 — Assemble the paper

You already have most of the pieces (figures, methods, reproducibility, MIT repo).
- Abstract (from Phase 0, now filled with real numbers) → Intro → Methods →
  Results → Discussion.
- **Results order:** (1) benchmark negative [have it] → (2) decoupling statistic
  [Phase 1] → (3) model failure concentrates on decoupled variants [1.4] →
  (4) rs6733839 mechanism as the worked case [Phase 3].
- Deposit: code + all data pointers already public. Add a Zenodo DOI snapshot of
  the repo at submission.

**Definition of done:** a complete draft in `paper/` + a bioRxiv-ready PDF.

---

## Compute & data-access reckoning (be honest about gating)

| Need | Status |
|---|---|
| Kosoy microglia caQTL (syn30308248) | ✅ have it |
| Kosoy microglia **eQTL** (syn30308484) | ⬜ download — same portal, open tier |
| MPRA sets (GSE244011, PMC12265656, osf.io/w5bzq) | ✅ / public |
| AlphaGenome API | ✅ have key |
| GPU (Boltz-2 co-fold, Borzoi re-scoring) | ⬜ needs a GPU host (L40S) |
| Footprinting inputs (Nott 2019 microglia ATAC) | ⬜ public, needs fetching |

Most of the work is **analysis on data you already have or can openly get**. The
only hard gates are one GPU session (Phase 3.1 + any Borzoi re-scoring) and
downloading the eQTL + footprint files.

---

## Scope discipline — what NOT to do

- **Do NOT train a new model.** You already have a well-characterized negative;
  another model won't change the story and burns weeks.
- **Do NOT add more benchmark contexts** than Phase 1 needs. The paper's value is
  the *decoupling statistic + the model-failure link*, not more benchmarking.
- **Do NOT chase Nature/Cell.** That needs wet-lab validation you can't do here.
- The single highest-value move is **Phase 1.1's intersection check**. If that's
  well-powered, you have a paper. If it isn't, you learn that in a day and pivot
  the framing — before investing in Phases 2–3.

---

## Priority order (if time is short)

1. **Phase 1.1 + 1.2** — the decoupling number. Everything hinges on this.
2. **Phase 1.4** — link model failure to decoupling (the key figure).
3. **Phase 2** — clean data so the number survives review.
4. **Phase 1.3** — predict-the-decoupling (bonus positive result).
5. **Phase 3** — structural/TF close on rs6733839 (nice-to-have polish).

---

## ⚠ Reminder: the hackathon is due first

Submissions are due **2026-07-13 9PM ET**. This plan is a **post-hackathon**
research effort (3–5 weeks). Ship the hackathon **demo video + 100–200 word
summary first** (see `ROADMAP.md`), then start Phase 1. Don't let the paper eat
the deadline.

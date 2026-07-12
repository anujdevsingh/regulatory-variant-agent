# regulatory-direction-independence

**Can sequence-to-function models predict the *direction* of a noncoding variant's regulatory effect? A benchmark, a negative result, and the mechanism behind it — in human microglia.**

Built with **Claude Science** for the *Built with Claude: Life Sciences* hackathon (Research track, Jul 2026).

📄 **Preprint:** [`MANUSCRIPT_bioRxiv.pdf`](MANUSCRIPT_bioRxiv.pdf) — full journal-formatted manuscript (also [`MANUSCRIPT_bioRxiv.md`](MANUSCRIPT_bioRxiv.md)).
📈 **Roadmap / provenance:** [`ROADMAP.md`](ROADMAP.md) — living log of every stage with config, seed, and data-split manifest.

---

## The finding in one paragraph

Sequence-to-function deep-learning models (Borzoi, AlphaGenome, and the DeepSEA/Basset lineage before them) predict genomic assay *tracks* with high accuracy and are increasingly used to interpret disease-associated noncoding variants. But the question a variant-interpretation pipeline actually needs answered is directional: does this variant push accessibility / expression **up or down** in the relevant cell type? We benchmarked that directly, in the microglia / brain / immune context where the disease biology lives. **On the fairest achievable test — chromatin-accessibility direction in the native cell type — every model is at chance:** AlphaGenome 0.537, Borzoi 0.551, motif-PWM floors, and even models trained in-distribution on the data itself, all statistically indistinguishable from a majority-class baseline (0.565). We then show *why*: in the **same 95 donors**, a variant's effect on chromatin accessibility and its effect on gene expression are **statistically independent** (sign concordance 0.506, 95% CI 0.455–0.556, p = 0.87). A model that reads one regulatory layer cannot recover the direction of another layer it does not read.

---

## Results

### 1. No model predicts accessibility direction in the native cell type

![Directional benchmark in native microglia — all models at chance](results/fig_caqtl_result.png)

Direction accuracy with 95% bootstrap CIs on the held-out human-microglia caQTL test (95-donor map). AlphaGenome and Borzoi are scored on their intended task, in their intended cell context, and neither separates from the majority-class baseline. This is not a model-capacity problem — in-distribution training lands at chance too.

### 2. The decoupling is systematic, at scale

![Accessibility vs activity direction decoupling across contexts](results/decoupling/fig_phase1_decoupling.png)

Across paired regulatory layers, the sign of a variant's accessibility effect does not predict the sign of its activity effect. The relationship sits at coin-flip across every stratification tested.

### 3. Same-donor caQTL vs eQTL — the clean number

![Same-donor caQTL vs eQTL sign concordance](results/decoupling/fig_caqtl_eqtl_clean.png)

The definitive test, free of any cross-cell-type confound: in the *same 95 microglia donors*, chromatin-accessibility QTLs and expression QTLs agree on direction only 50.6% of the time (n = 354 variants significant in both layers; p = 0.87). Accessibility and expression effect-directions are statistically independent.

### 4. rs6733839 (BIN1 / Alzheimer's) anchors the mechanism

![Boltz-2 co-fold: MEF2A on the BIN1 enhancer, both alleles](results/decoupling/fig_boltz_cofold.png)

The lead *BIN1* Alzheimer's variant makes it concrete. It **opens** chromatin (caQTL Beta +0.147, Z 3.3) and **raises** BIN1 expression (eQTL Beta +0.482, Z 6.4) in microglia — the two native-genome layers agree — while **repressing** episomal enhancer activity in a reporter assay. Three measured layers, not all in the same direction. A Boltz-2 protein–DNA co-fold shows the risk allele grips the MEF2A transcription factor more tightly (287 vs 255 interface contacts, +12.5%; both alleles high-confidence, interface pTM 0.978), consistent with the risk allele creating a stronger MEF2 site.

---

## Why this matters

The practical takeaway for anyone using sequence models to interpret variants: **do not trust a single-layer model's direction call on the variants that matter most for disease.** The models are excellent at what they were trained for (track prediction) and unreliable at the directional question they are increasingly asked. This repo provides an open, chromosome-split benchmark and every per-variant score so the field has a like-for-like way to measure directional accuracy.

---

## Repository layout

```
bench/         harmonized benchmark: variants with measured direction, split manifest, per-model scores
results/       figures + result tables (caQTL scoreboard, floor baselines, ...)
  decoupling/  Phase 1–3 decoupling analysis, same-donor caQTL∩eQTL, Boltz co-fold, structures
docs/          publication plan, hackathon summary, demo video guide
MANUSCRIPT_bioRxiv.md / .pdf    the preprint
ROADMAP.md     living provenance log (per-stage config, seed, split)
score_variant.py                the sequence-based variant-scoring tool (see below)
```

Everything is committed per analysis stage with configuration and random seed. Genome build GRCh38 throughout.

### Benchmark data sources

| Source | Layer / context | Access |
|---|---|---|
| Kosoy et al. 2022 caQTL + meta-eQTL (95 microglia donors) | chromatin accessibility, expression | AD Knowledge Portal / Synapse (registered — account + data-use terms, no sponsor) |
| SuRE raQTL (K562, HepG2) | episomal activity | open (OSF) |
| 2025 context-dependent AD-MPRA | THP-1, HMC3, brain, HEK293T | open |
| GSE244011, GSE253841 | NPC MPRA, 3′-UTR MPRA | open (GEO) |

Variant scoring used the AlphaGenome API (non-commercial terms) and Borzoi open weights (replicate 0). Structure prediction used Boltz-2.

---

## The `score_variant.py` tool

The repo also contains the sequence-based variant-interpretation tool built in the earlier phase of the project: given an rsID, it predicts a variant's chromatin-accessibility effect from a pretrained **ChromBPNet** model, runs in-silico mutagenesis + attribution to localize which bases the model weights, and matches the region to **JASPAR** motifs.

```bash
pip install -r requirements.txt
# download the brain ChromBPNet models (Zenodo 10.5281/zenodo.10605867), then:
python score_variant.py --rsid rs6733839 \
    --model models/Microglia_chrombpnet_nobias.h5 --outdir results/
```

It supports `--calibrate PEAK_BED` (percentile + z-score against a common-SNP null) and `--credible-set TABLE.xlsx` (score a published fine-mapping credible set and test whether the fine-mapped variant is also the largest-effect one). This tool is a *component* of the project, not its headline result — the benchmark and the decoupling finding above are the contribution.

---

## Citation

If you use this benchmark or the analysis, please cite the preprint (see [`MANUSCRIPT_bioRxiv.md`](MANUSCRIPT_bioRxiv.md) for the full reference list and author details).

Built with Claude Science; all study design, methodological decisions, and claims are the author's, who takes full responsibility for the content.

# Model-Training Brief — attempting to beat the current best on noncoding variant-effect prediction

*Route #2 of the roadmap. This is the document an agent (or you) needs before
writing a single line of training code: what the task is, what data exists, what
the current best models are and how they work, where they actually fail, the
concrete ways to try to beat them, how you'd prove it, and an honest reckoning of
the difficulty and compute. Read this first each time we work on the "train our
own model" thread.*

---

## 0. Honest framing (read this before getting excited)

"Beat the best model" needs a precise definition or it is meaningless. The
current best general model — **AlphaGenome** (Avsec et al. 2026, Nature) — reports
matching or exceeding the strongest external models in **25 of 26** variant-effect
evaluations, was trained by Google DeepMind on human+mouse genomes at 1 Mb context
and single-base resolution across thousands of tracks. **We will not beat that
head-to-head as a generalist.** That is a multi-team, large-TPU-budget effort.

The realistic and honest goal is to **beat the best model *on a specific, narrow
task where the generalist is known to be weak*** — a wedge. That is how almost
every "new SOTA" paper actually wins: not everywhere, but on one well-chosen slice.
Our whole project has already *found* a candidate wedge (Section 2).

---

## 1. The task, defined precisely

Pick ONE of these; do not blur them (the benchmarks and the winning architecture
differ by task):

- **T1 — Sequence→activity, cell-type-resolved chromatin.** Given a DNA window,
  predict ATAC/DNase/ChIP signal per cell type; score a variant by ref−alt. This
  is ChromBPNet/Enformer territory.
- **T2 — Variant→direction+magnitude of regulatory effect** (the MPRA/raQTL task).
  Predict whether ref or alt allele *increases* reporter activity, and by how much.
- **T3 — Variant→causal prioritization** (fine-mapping / eQTL): rank which variant
  in a locus is causal.

Our project touched all three; the sharpest wedge is **T2 with a direction focus
in a specific cell context** (see Section 2).

---

## 2. The wedge — where the current best actually fails

Grounded, not wishful. Two independent sources point at the same gap:

1. **Our own finding (this repo).** For rs6733839, our models (ChromBPNet,
   AlphaGenome) and even the MPRA paper's own ML models predicted the *wrong
   direction* in immune cells: they said the risk-T allele *raises* activity;
   measured MPRA showed it *represses* via SPI1. The reason is that the variant
   sits in a **context-dependent repressor** whose direction flips with the
   surrounding enhancer grammar. Single-window sequence→accessibility models do not
   resolve *direction under combinatorial motif context*. (See
   `results/MPRA_VALIDATION.md`.)
2. **The field's own benchmarks.** A 2025 controlled comparison (54,859 SNPs across
   4 cell lines, MPRA/raQTL/eQTL) found that even under a unified benchmark, the
   *direction and magnitude of enhancer effects* remains the hard part, and that
   simpler CNNs were often *more reliable* than large models for it. Noncoding
   variant-effect prediction correlations on causal-eQTL benchmarks still sit below
   ~0.6 for SOTA. The generalists win on average tracks, not on hard directional
   calls.

**The wedge, stated as a claim you could actually win:** *"A model that predicts
the DIRECTION of a regulatory variant's effect in a specified cell context,
conditioned on local motif grammar, beats AlphaGenome/Borzoi ref−alt scores on
held-out MPRA/raQTL direction calls."* Narrow, measurable, and grounded in a real
observed failure.

---

## 3. The data (what exists, what to train on, what to hold out)

Full inventory and sources are in `DATA.md`. For training specifically:

**Sequence→activity training data (T1):**
- ENCODE ATAC-seq / DNase-seq / TF-ChIP-seq bigWigs (the substrate Enformer/Borzoi
  train on; thousands of tracks). Corces brain/microglia ATAC (this project's
  cell types). scATAC (GSE147672) for cell-type resolution.
- These are large (TB-scale for the full compendium). A wedge model uses a curated
  subset (e.g. brain/microglia/immune tracks only).

**Variant-labeled data (T2/T3) — the scarce, valuable part:**
- **MPRA:** Cooper et al. 2022 *Science* (DOI 10.1126/science.abi8654; 5,706
  AD/PSP variants — abstract retrieved this session); the 2025 context-dependent
  AD MPRA (PMC12265656); Kircher/Vockley saturation-MPRA sets;
  ENCODE/lentiMPRA compendia. These give *measured* ref/alt activity — the direct
  supervision the generalists mostly *don't* train on.
- **raQTL** (reporter-activity QTLs, SuRE data, van Arensbergen).
- **eQTL:** GTEx v10 (bulk), microglia eQTL atlases (MiGA, Young 2021, Kosoy 2022).
- **caQTL:** chromatin-accessibility QTLs for the T1 story.

**Key insight:** the generalists are trained on *tracks* (T1) and score variants
*zero-shot*. Our wedge can train **directly on the measured variant labels** (T2)
that they don't use — that is a legitimate data advantage on the directional task.

---

## 4. The current-best landscape & architectures (what you're up against)

The supervised sequence→function lineage (this is the relevant family):

| Model | Year | Context | Resolution | Architecture | Note |
|---|---|---|---|---|---|
| DeepSEA / Basset | 2015 | ~1 kb | peak | CNN | founders; per-cell chromatin classification |
| Basenji/Enformer | 2021 | 196 kb | 128 bp | CNN trunk + Transformer | long-range via attention |
| Sei | 2021 | ~4 kb | — | CNN | sequence→"regulatory activity" classes |
| ChromBPNet | 2023 | ~2 kb | **base** | CNN + bias model | base-resolution, bias-corrected; ISM-friendly |
| Borzoi | 2025 | 524 kb | 32 bp | U-Net + Transformer | predicts RNA-seq coverage directly |
| Flashzoi | 2025 | 524 kb | 32 bp | Borzoi + rotary/FlashAttn-2 | ~faster Borzoi |
| **AlphaGenome** | 2026 | **1 Mb** | **base** | conv + transformer + 2D pair track | current best; multimodal, 25/26 VEP wins |

Self-supervised **DNA language models** (a different paradigm — pretrain then
fine-tune): Nucleotide Transformer, DNABERT-2, HyenaDNA (SSM, long context),
Caduceus (Mamba/bi-directional SSM), Evo/Evo2 (very long context), ModernGENA
(ModernBERT-for-DNA, efficient baseline, 2026). These win on *efficiency* and
*label-free pretraining*, and are strong when labeled data is scarce — but on
supervised regulatory tasks the task-specific supervised models above generally
still lead.

**Architectural levers that matter for the wedge:**
- **Base resolution** (ChromBPNet, AlphaGenome) — required to see a single-SNP motif
  change. 32-bp binning (Borzoi) blurs it.
- **Efficient long context** — SSMs (Mamba/Hyena) and rotary+FlashAttention give
  long range without quadratic cost; useful if distal grammar matters.
- **Explicit motif/pairwise structure** — AlphaGenome's 2D pair track; or explicit
  TF-motif priors. Directly relevant to "context-dependent grammar."
- **Cell-type conditioning** — a conditioning embedding so one model does many cell
  types (vs one model per type).

---

## 5. Concrete ways to try to beat them (matched to the wedge)

Ordered by realism-to-payoff:

1. **Fine-tune / distill a generalist for the directional task (highest ROI).**
   Take Borzoi/Flashzoi (open weights) or Enformer embeddings, add a small
   supervised head trained on *measured MPRA/raQTL direction labels* in the target
   cell types. You are adding the exact supervision they lack. This is the most
   likely way to actually beat zero-shot AlphaGenome on T2 direction.
2. **A motif-grammar-aware directional head.** Feed ISM/attribution features + local
   JASPAR motif occupancy (like our own analysis produced) into a model that
   predicts direction, explicitly capturing activator/repressor context. Small,
   trainable on modest GPU, and squarely aimed at the observed failure mode.
3. **Cell-type-conditioned base-resolution CNN trained on curated tracks + MPRA
   multitask.** Train ChromBPNet-style on brain/microglia/immune tracks *and*
   co-supervise on MPRA direction (multitask). From-scratch but on a curated slice,
   not the whole genome compendium.
4. **From scratch, full generalist.** Not recommended as a first move — this is the
   AlphaGenome-scale effort. Only sensible with large GPU/TPU budget and a team.

---

## 6. How you'd PROVE you beat the best (evaluation protocol)

A claim of "new SOTA" is only as good as the benchmark. Non-negotiables:

- **Held-out, never-seen variants.** Split by locus/chromosome, not by variant, to
  avoid leakage.
- **Compare on the SAME task and metric as the incumbent.** For T2: AUROC/AUPRC for
  direction, Pearson/Spearman for magnitude, on public MPRA/raQTL (Cooper 2022,
  Kircher saturation-MPRA, SuRE raQTL) and the causal-eQTL benchmark.
- **Beat the incumbent's OWN scores on YOUR test set.** Run Borzoi/Flashzoi (open)
  and AlphaGenome (API) ref−alt on the identical held-out set; report side by side.
- **Report where you LOSE too.** A wedge model that wins on direction may lose on
  magnitude or on other cell types — say so. (Honesty mandate.)
- **Ablations:** show the wedge component (motif grammar / MPRA supervision) is what
  drives the gain.

Public benchmark suites to use: the evaluation categories from Kathail, Bajwa &
Ioannidis 2024 (arXiv 2411.11158, "Leveraging genomic deep learning models for
the prediction of non-coding variant effects"); the 2025 comparative-benchmark datasets (MPRA/raQTL/eQTL, 54,859 SNPs);
CAGI regulatory-variant challenges; gReLU / Borzoi eval harnesses.

---

## 7. Compute & difficulty — the honest reckoning

- **Fine-tune head (strategy 1–2):** feasible on 1 GPU (hours–days). This is the
  realistic entry point.
- **From-scratch curated CNN (strategy 3):** multi-GPU, days–weeks.
- **From-scratch generalist (strategy 4):** large GPU/TPU cluster, weeks; effectively
  out of scope for a solo effort.
- **No compute target is currently connected to this project.** Any real training
  needs a GPU host (Compute panel) or an external cluster. Until then, this thread
  stays at design + data-prep.

Difficulty is HIGH and the failure mode is subtle: it is very easy to *appear* to
beat SOTA via test leakage, an easier test set, or a metric the incumbent wasn't
optimized for. The evaluation discipline in Section 6 is the actual hard part.

---

## 8. Recommended staged plan

1. **Lock the wedge & benchmark first** (no training): assemble the held-out
   MPRA/raQTL direction test set; run Borzoi + AlphaGenome ref−alt on it; record
   their accuracy — *especially their directional errors*. This establishes the bar
   and confirms the wedge is real before we build anything.
2. **Strategy 2 (motif-grammar directional head)** as the first model — cheap,
   aimed at the observed failure, trainable on modest GPU.
3. **Strategy 1 (fine-tune Borzoi head on MPRA)** as the stronger contender.
4. Only then consider strategy 3.

Each stage ends with the same side-by-side comparison table vs the incumbents.

---

## 9. What the agent must know (checklist) + the exact prompt

An agent picking this up needs, in order: (a) the wedge and why it's grounded
(§2); (b) the precise task T1/T2/T3 (§1); (c) the data split + leakage rules (§3,§6);
(d) the incumbents to beat and their open-weight availability (§4); (e) the
evaluation table it must produce (§6); (f) the compute reality (§7); (g) the
honesty mandate — report losses, avoid leaked benchmarks.

The concrete kickoff prompt is in `docs/MODEL_TRAINING_PROMPT.md`.

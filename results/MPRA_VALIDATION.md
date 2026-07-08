# MPRA validation of rs6733839 — our predictions vs. measured wet-lab data

*Route #1 of "make the result strong": instead of running our own experiment, we
found **published massively parallel reporter assay (MPRA)** data — real,
measured transcriptional activity — that tested rs6733839, and checked whether it
agrees with what our sequence models predicted. This is the closest we can get,
purely computationally, to the Pollard-lab-style "model + reporter assay" loop.*

## What we compared against

- **Cooper et al. 2022, *Science*** (DOI 10.1126/science.abi8654) — the landmark
  dementia MPRA: screened 5,706 AD/PSP GWAS variants for allele-specific
  regulatory activity, identifying 320 functional regulatory variants across 27
  loci. We cite it as the established large-scale AD-variant MPRA; **we did not
  retrieve its full text, so we do not attribute any rs6733839-specific result to
  it here** (its abstract does not mention rs6733839 or BIN1).
- **"Context-dependent regulatory variants in Alzheimer's disease"** (preprint,
  PMC12265656 / DOI 10.1101/2025.07.11.659973, 2025) — re-examined rs6733839 with
  SNP-centered AND longer peak-centered MPRA constructs across THP-1 macrophages,
  HMC3 microglia-like cells, brain tissue, and HEK293T, plus synthetic
  enhancer-tiling and motif-shuffling. This paper *also* ran ML sequence models,
  so we can compare model-to-model and model-to-measurement.

These are independent measurements — different groups, different assay — from the
models we used. That independence is what makes the comparison meaningful.

**Provenance note (attribution correction):** the specific prior-MPRA finding
that rs6733839 showed *no significant allele-specific effect with subtle
upregulation* in SNP-centered constructs is reported by the 2025 context-dependent
preprint as a summary of *earlier* MPRA work in HEK293T/THP-1 cells; that preprint
does not name which study. We therefore attribute this prior-null result to
"previous MPRA assays" as reported by the 2025 preprint — **not** specifically to
Cooper 2022.

## The scorecard: 5 of 6 predictions confirmed

![prediction vs MPRA](fig7_mpra_validation.png)

| # | What we predicted | What our models said | What MPRA measured | Agree |
|---|---|---|---|---|
| 1 | Variant is functional / in an active enhancer | In credible set, causal PP 0.998 | CRISPR deletion lowers BIN1; enhancer active in MPRA | ✅ |
| 2 | Effect is small / subtle, not a large outlier | log2FC +0.026, 54th percentile | SNP-centered MPRA: no significant allele effect | ✅ |
| 3 | Mechanism is TF binding, not bulk accessibility | TF-ChIP largest effect (MEF2A q=0.99) | Effect is motif/context-driven (SPI1/MEF2) | ✅ |
| 4 | TFs involved: MEF2 and SPI1/PU.1 | Both flagged (ISM+JASPAR; AlphaGenome) | SPI1 (immune) & MEF2 (brain) both implicated | ✅ |
| 5 | Direction in immune cells (risk T raises activity) | Raises (accessibility+, SPI1 binding+) | **LOWERS** — T represses in THP-1/HMC3 | ❌ |
| 6 | Direction in brain (risk T raises activity) | Raises (MEF2 gain-of-function) | Raises — upregulation in brain MPRA | ✅ |

## What this means — honestly

**The strong part.** Every *qualitative* claim our project made is independently
confirmed by measured data: the variant is functional; its effect is subtle (so
subtle that standard SNP-centered MPRA can't detect it — exactly matching our
"54th percentile, not an outlier"); the mechanism is TF binding rather than bulk
accessibility; and the specific TFs are MEF2 and SPI1/PU.1 — the two our ISM,
JASPAR scan and AlphaGenome all pointed at. This is real convergence:
sequence-model prediction meets wet-lab measurement on the *mechanism*.

**The honest miss — and why it's the most interesting row.** We (and the models
in the MPRA paper) predicted the risk T allele *raises* activity in immune cells;
the peak-centered MPRA measured the opposite — T *represses* transcription in
THP-1 macrophages and HMC3 microglia-like cells via SPI1. The reason is
illuminating: motif-shuffling showed rs6733839's local sequence acts as a
**context-dependent repressor** — activating with upstream motifs, repressive
with downstream ones. The *direction* depends on the surrounding enhancer grammar
and cell context, which a single-locus accessibility model (and even a
larger multimodal model scoring one window) fundamentally cannot resolve. Notably
the **brain** direction we predicted *does* match the brain MPRA.

**The takeaway.** Our accessibility+TF models nailed *what* and *which TFs* — and
were right about *direction in brain* — but got *direction in immune cells* wrong,
because direction is set by combinatorial motif context. That is precisely the
documented limit of this model class, now confirmed against measurement rather
than asserted. The project's central thesis — "statistical causality and
predicted molecular mechanism are decoupled; the mechanism is TF occupancy, not
accessibility" — is **supported by independent measured data.**

## Where this leaves us

- **Scientific result: upgraded from MEDIUM toward STRONG.** The prediction is no
  longer standalone — it converges with measured MPRA + CRISPR on mechanism and
  TF identity. It is not "proven" (direction is context-dependent and unresolved
  in immune cells), but it is now grounded in orthogonal experiment.
- **Honest limitation surfaced:** our models cannot predict direction where it is
  set by combinatorial enhancer context. That is a real, citable boundary of the
  method — worth stating plainly rather than hiding.

## Files
- `fig7_mpra_validation.png` — the prediction-vs-measurement scorecard.
- `mpra_evidence.json` — extracted measured findings + our predictions, with sources.

## Caveats
- The 2025 context-dependent paper is a **preprint** (not yet peer-reviewed at
  time of writing); Cooper 2022 is peer-reviewed *Science*.
- MPRA measures episomal reporter activity, not endogenous expression; direction
  can differ from the native locus.
- We compared published summary findings, not reprocessed raw MPRA counts. A
  deeper follow-up would download the raw barcode counts and correlate our
  per-variant log2FC against measured allelic skew across the whole AD credible
  set — a natural next step.

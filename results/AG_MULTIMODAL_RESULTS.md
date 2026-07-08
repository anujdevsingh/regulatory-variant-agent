# AlphaGenome cross-check of rs6733839 — Layer 1 of the hybrid method

**Variant:** rs6733839, chr2:127,135,234 (GRCh38), C>T (T = AD-risk allele)
**Model:** AlphaGenome (Avsec et al. 2026, Nature) via the Google DeepMind API, 1 Mb input window centered on the variant.
**What we asked:** score the variant across four modalities — chromatin accessibility (ATAC), DNase sensitivity, transcription-factor binding (ChIP), and gene expression (RNA-seq) — and compare to what the specialized microglia ChromBPNet told us.

AlphaGenome returned **12,848 track-level effect scores** (167 ATAC + 305 DNase + 1,617 TF-ChIP + 10,759 RNA-seq). Each score is a log2 fold-change (alt vs ref) plus a genome-wide quantile.

---

## The headline: the multimodal view resolves the ChromBPNet puzzle

With ChromBPNet we hit a puzzle: rs6733839 is the fine-mapped **causal** variant (posterior 0.998) yet its predicted *microglial accessibility* effect was tiny (log2FC +0.026, 54th percentile) and pointed at an adjacent element rather than the variant base. AlphaGenome, looking at more modalities, gives a coherent explanation:

| Modality | AlphaGenome peak |effect| | Interpretation |
|---|---|---|
| Chromatin accessibility (ATAC) | 0.237 log2FC | modest; **in brain tracks only 0.056** — agrees with ChromBPNet |
| DNase sensitivity | 0.263 log2FC | modest, same story |
| **TF binding (ChIP)** | **0.315 log2FC (MEF2A, quantile 0.99)** | **largest effect — the variant changes TF occupancy** |
| Gene expression (BIN1) | 0.041 log2FC, **quantile 1.00** | small magnitude but top-of-distribution for BIN1 |

**The mechanism the accessibility model couldn't see is transcription-factor binding.** rs6733839's strongest predicted consequence is not opening/closing chromatin — it is changing how strongly transcription factors bind. That is exactly the kind of effect a pure accessibility model (ChromBPNet) is blind to, and it explains why the causal variant looked "quiet" on accessibility.

## The two models independently agree on the TF

This is the important corroboration. ChromBPNet's in-silico mutagenesis + JASPAR scan flagged that the risk allele T **strengthens a MEF2 motif** spanning the variant. AlphaGenome — a completely independent model, trained separately — predicts that the risk allele T **increases MEF2A binding** (log2FC +0.315, quantile 0.99), and also increases SPI1/PU.1 binding (+0.168, quantile 0.97), the other motif ChromBPNet's attribution pointed at. Two independent SOTA models converge on the same transcription factors. That convergence is far stronger evidence than either model alone.

## Honest caveats

- **Cell-type mismatch on the peak tracks.** AlphaGenome's largest accessibility and TF-binding effects are in **lymphoblastoid / immune-lineage lines (GM12878, GM19463)**, not brain or microglia. AlphaGenome does not have a microglia-specific track the way our ChromBPNet model does. So the *magnitude* of the brain-specific effect is best read from ChromBPNet; AlphaGenome's contribution is the *modality* insight (it's TF binding) and the *direction* (risk T increases MEF2A/SPI1 binding). BIN1 is broadly expressed including in immune cells, so an immune-line signal is biologically plausible but is not microglia.
- **Expression magnitude is small.** The BIN1 expression effect is modest in absolute log2FC (0.041) even though its quantile is ~1.0. AlphaGenome flags it as unusually high *for BIN1*, not as a large absolute change.
- **AlphaGenome is a black box.** Unlike ChromBPNet we cannot run attribution on it; we take its track scores at face value.
- These are model predictions, not measurements. The convergence is a strong hypothesis for wet-lab follow-up (e.g. a MEF2A allele-specific ChIP or reporter assay), not proof.

## Where this leaves the hybrid method (design doc Layer 2/3)

The consensus/confidence logic now has a real worked example:
- **Accessibility:** both models agree the effect is small in brain -> low-confidence accessibility call. (Consensus: agree/small.)
- **TF binding:** ChromBPNet motif + AlphaGenome ChIP agree the risk allele **increases MEF2A/SPI1 binding** -> this is the high-confidence, mechanistically-specific call. (Consensus: agree/directional.)
- **Classification:** rs6733839 lands in the "multimodal-only / TF-occupancy" tier — a variant whose mechanism is TF binding, not accessibility. That is precisely the tier the hybrid was designed to surface.

**Next:** score the full 25-variant credible set through AlphaGenome the same way, so we can ask whether rs6733839's TF-binding effect is *distinctive within its credible set* (unlike its accessibility effect, which was mid-pack). If the causal variant is the top TF-binding hit in the set, that closes the loop the accessibility model left open.

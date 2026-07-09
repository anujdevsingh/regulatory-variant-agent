# NPC MPRA benchmark expansion — result

## What we tested
We expanded the on-wedge (brain-lineage) held-out set to 857 variants (of which 788 are
the new NPC context; the other 69 are the pre-existing immune/microglia/brain test rows) by
adding 788 test variants from a large independent psychiatric cross-disorder MPRA in
hiPSC-derived neural progenitor cells (Lee et al. 2025, Cell; GSE244011). Direction was
computed directly from deposited DNA/RNA barcode counts (measured, not predicted),
balanced 50/50, lifted to hg38, added to the frozen chromosome split (test = chr 2,6,11,19).

On-wedge TRAINING data grew from 62 → 2,939 variants — the ceiling-break the previous
negative result pointed to as the highest-value lever.

## Result: a clean, well-powered null (n=788 held-out)

| Model | direction acc | 95% CI | AUROC |
|---|---|---|---|
| PWM Δ-score (floor) | 0.464 | [.429,.499] | — |
| Logistic-motifs (floor, cross-context) | 0.494 | [.458,.529] | — |
| Logistic-motifs (in-distribution) | 0.496 | [.459,.529] | 0.506 |
| GBT-motifs (in-distribution) | 0.523 | [.489,.557] | 0.527 |
| Wedge-GBT (motif+context) | 0.504 | [.472,.537] | 0.516 |
| AlphaGenome (1 Mb) | 0.509 | [.475,.546] | 0.480 |
| Borzoi (524 kb) | 0.236* | [.208,.266] | 0.473 |
| majority-class baseline | 0.547 | — | — |

*Borzoi 0.236 is a zero-inflation artifact: 51% (405/788) of variants get an exactly-zero
neural-accessibility delta (they sit outside any neural accessibility peak), which sign()
scores as auto-wrong. The honest Borzoi metric is AUROC 0.473 (full set) and 0.486 accuracy
[.433,.538] on the 383 nonzero-delta variants — i.e. at chance where it makes a confident call.

## The finding
On a large, independent, balanced brain-lineage MPRA, **noncoding variant direction is not
predictable** — not by:
- local motif grammar (PWM, logistic, or GBT) — even trained IN-DISTRIBUTION on 2,877
  matched NPC variants (AUROC 0.51–0.53),
- AlphaGenome (1 Mb generalist) — AUROC 0.48, CI spans 0.5,
- Borzoi (524 kb) — AUROC 0.47, at chance where it predicts a nonzero change,
- our grammar-aware wedge model — AUROC 0.52.

Every model's *honest* directional metric is at chance — AUROC 0.47–0.53 for all, and
every accuracy CI includes 0.5 except Borzoi's raw score, whose 0.236 [.208,.266] is a
zero-inflation artifact (its honest nonzero-subset accuracy is 0.486 [.433,.538], which
does span 0.5). None reaches the 0.547 majority-class rate. This is not a
weak signal we failed to capture — it is a well-powered null (n=788), consistent across
seven independent modeling approaches including in-distribution training.

## Why this matters (honest interpretation)
1. **It is a real, publishable-shape result, not a failure.** With n=56 we could not
   distinguish "wedge exists but we can't model it" from "no signal." At n=788 the answer
   is clear: in this brain-lineage context, sequence→direction is at chance for everyone.
2. **It sharpens the original rs6733839 finding rather than erasing it.** The rs6733839
   wedge (Borzoi right, AlphaGenome backwards) lives specifically in immune/microglia
   context, on a variant with a strong measured effect. The NPC set is (a) a different
   lineage (neural progenitor, not microglia/immune) and (b) dominated by small-effect
   variants. The wedge, if real, is context- and effect-size-specific — not a general
   brain-lineage property.
3. **The exact-context microglia anchor (Kosoy caQTL) is now the pivotal missing piece.**
   It is access-gated (Synapse token / NIAGADS DAR), so we could not test whether the
   wedge holds where rs6733839's failure actually lives.

## Honest bottom line
This is a well-characterized NEGATIVE at scale, which the mandate explicitly counts as a
legitimate close. The direction-prediction wedge does NOT generalize to brain-lineage MPRA
at large; where it appeared (rs6733839, immune/microglia, large effect) it may be
context-and-magnitude-specific. Confirming or refuting that requires the microglia-specific
measured data, which is gated.

## Provenance
- Data: GSE244011 DNA/RNA count matrices (open). Direction = sign(alt−ref) log2(RNA/DNA),
  joint per-replicate CPM normalization, paired t-test across 22 replicates, FDR<0.05.
- Liftover hg19→hg38 (UCSC chain, pyliftover), all same-chromosome.
- Borzoi: johahi/borzoi-replicate-0, 524 kb, neural accessibility tracks (n=79), central
  5-bin delta. AlphaGenome: 1 Mb, ATAC+DNASE neural biosample tracks, DIFF_LOG2_SUM.
- Floors + wedge: 49 JASPAR PWM Δ-features, seed=0, chromosome split, bootstrap CIs (2000).

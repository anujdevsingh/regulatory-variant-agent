# Kosoy microglia caQTL — the pivotal on-target test

## What this is
The one dataset that tests the directional wedge in its NATIVE context: microglia,
chromatin-accessibility layer, exactly where rs6733839's failure was documented.
Source: Kosoy et al. 2022 Nature Genetics (PMC9388367), meta-caQTL summary result
(Synapse syn30308248, AD Knowledge Portal open tier; downloaded by user 2026-07-10).
45.8M variant×peak rows; per-variant signed effect on chromatin accessibility from
95-donor microglia ATAC-seq.

## Harmonization
- direction convention: effect on the ALT allele (our benchmark standard).
- Kosoy gives effect_allele + Beta + Z_score_fixed per variant×peak; collapsed to one
  direction per variant = the peak with largest |Z_score_fixed| (strongest local caQTL).
- aligned Kosoy effect_allele to our (ref,alt); dropped 158 allele mismatches (strand/indel).
- 1,478 of our benchmark variants have microglia caQTL data; balance 48.8% alt-opens.
- added to the frozen chromosome split (test = chr 2,6,11,19): 361 test / 1,117 train.
- new context label: "microglia (caQTL chromatin)".

## Result (361 held-out variants, 95% bootstrap CI, seed 0)
| Model | Direction acc | 95% CI | AUROC |
|---|---|---|---|
| Motif PWM (floor) | 0.493 | [.443,.543] | — |
| Logistic-motifs (in-dist) | 0.529 | [.479,.579] | 0.544 |
| Boosted trees (in-dist) | 0.499 | [.446,.549] | 0.501 |
| **AlphaGenome (incumbent)** | **0.537** | **[.485,.587]** | **0.547** |
| *(majority class)* | *0.565* | — | — |

**Every model is at chance.** All CIs span 0.5; none reaches the 0.565 majority-class
rate. This is AlphaGenome's NATIVE task (chromatin accessibility) in the NATIVE cell
type (microglia) — the fairest possible test — and it still cannot predict direction
better than chance across 361 variants. The well-powered null now holds on the on-target
dataset, not just the NPC/3'-UTR proxies.

Borzoi row is GPU-gated (instance deleted after prior runs); caQTL is a native ATAC/DNase
task for Borzoi too and can be added if a GPU is reconnected.

## The rs6733839 reconciliation (the real scientific payoff)
rs6733839 IS in this dataset with a strong signal (effect_allele=T, Beta=+0.147, Z=3.34):
the risk-T allele OPENS chromatin in microglia.

| Layer | Measured (risk-T) | AlphaGenome |
|---|---|---|
| Chromatin accessibility (caQTL, this data) | OPENS (+, Z=3.3) | predicts OPENS → **CORRECT** |
| Enhancer output (MPRA, THP-1/HMC3) | REPRESSES (−) | assumed activates → **WRONG** |

(Which TF drives the MPRA repression is not settled here: the 2025 AD-MPRA source models it
as SPI1-mediated, whereas our own JASPAR analysis found the risk-T allele creates a strong
new MEF2A site (+7.56 bits) while SPI1 is essentially unchanged (+0.18). The caQTL result
below is independent of that TF question — it concerns the accessibility direction, not the
responsible factor.)

The variant OPENS chromatin while REPRESSING transcriptional output. These are different
molecular layers. AlphaGenome reads the accessibility layer correctly — its MPRA
"backwards" call was reading accessibility right and mistaking open-chromatin for
activation. This is not a model bug fixable by more sequence context; it is the
accessibility↔activity decoupling itself. That decoupling — a variant whose chromatin and
transcriptional signs disagree — is the precise, mechanistically-grounded statement of the
"wedge."

## Honest status of the wedge
- Direction-from-sequence is at chance for everyone across every context we assembled
  (NPC n=788, microglia/SH 3'-UTR, and now native microglia caQTL n=361) — a robust,
  well-powered NEGATIVE for the general task.
- The rs6733839 story is real but is a SINGLE-VARIANT, CROSS-LAYER phenomenon: chromatin
  and activity signs disagree, and which layer you measure determines whether a given model
  looks right or wrong. It is not a generalizable sequence-direction signal we can train on.
- This closes the data-gathering thread honestly: the on-target dataset was obtained and
  tested; the wedge does not generalize, and we can state precisely why.

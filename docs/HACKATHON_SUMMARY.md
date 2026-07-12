# Hackathon submission — plain-language summary + demo script

## 150-word summary

**Can AI models predict which way a disease variant changes gene regulation?**

Sequence-to-function models like AlphaGenome and Borzoi predict genomic signals
accurately, and are used to interpret the noncoding DNA variants behind most disease
risk. We tested the harder question that actually matters: can they predict the
*direction* of a variant's effect — does it turn regulation up or down — in the right
cell type? Using a chromosome-split benchmark of variants with lab-measured direction,
including a native human-microglia dataset, we found every model sits at chance —
even models trained on the test data itself. We explain why: in the same 95 donors, a
variant's effect on chromatin openness and its effect on gene expression are
statistically *independent* (concordance 0.506). A model reading one layer cannot
recover the other. The Alzheimer's variant rs6733839 anchors this — it opens chromatin,
raises BIN1 expression, yet represses an isolated enhancer — with a structural co-fold
showing a tighter MEF2A grip at the risk allele.

## 60-second demo script

**[0:00–0:10] The hook.**
"Everyone's excited that AI can read DNA. But if you ask these models the one question a
doctor needs — does this variant turn a gene UP or DOWN — they're basically flipping a
coin. We show that, and we show why."

**[0:10–0:25] The benchmark (Figure 1).**
"We built a fair test: real variants, real measured directions, in microglia — the exact
cell type and exact task these models are trained for. AlphaGenome: 54%. Borzoi: 55%.
Chance is 56%. Even a model we trained directly on this data: chance. It's not a model
problem — the answer isn't in the sequence."

**[0:25–0:45] The explanation (Figures 2–3).**
"Here's why. In the same 95 people, we asked: if a variant opens chromatin, does it raise
expression? Answer: no relationship — 50/50, a coin flip. The two layers are independent.
So a model that predicts chromatin literally cannot tell you the direction of expression.
That's the wall."

**[0:45–0:60] The anchor (Figure 4) + close.**
"One variant makes it concrete: rs6733839, an Alzheimer's risk variant. It opens chromatin,
raises BIN1, but represses an isolated enhancer — three layers, different answers. Our
structural co-fold shows the risk allele grips the MEF2A factor tighter. The takeaway:
don't trust a single-layer model's direction call on the variants that matter most. And
here's the benchmark to prove it — open, reproducible, ready to use."

## One-line pitch
We show frontier genomics models can't predict regulatory-variant *direction* — and prove
it's because chromatin and expression effects are statistically independent, not a model
flaw — with an open benchmark and an Alzheimer's-variant structural anchor.

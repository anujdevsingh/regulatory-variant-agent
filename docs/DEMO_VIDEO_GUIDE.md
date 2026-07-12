# Demo video — shot list (what to SAY + what to SHOW)

Target length ~90 seconds. Screen recording with voiceover. Read the "SAY" lines
naturally — they're written for speaking, not reading. Each beat = one screen + one line.

---

## BEAT 1 — The problem (0:00–0:12)
SHOW: GitHub repo README, or the paper title (MANUSCRIPT_bioRxiv.pdf, page 1).
SAY:  "Everyone's excited that AI models like AlphaGenome and Borzoi can read DNA. But if
       you ask them the one question a doctor actually needs — does this disease variant
       turn a gene UP or DOWN — they're basically flipping a coin. I set out to test that,
       and to show why."

## BEAT 2 — The benchmark result (0:12–0:30)
SHOW: Figure 1 — fig_caqtl_result.png (bars, everyone at chance vs the 0.565 line).
SAY:  "I built a fair test: real variants with lab-measured direction, in human microglia —
       the exact cell type and exact task these models are trained for. AlphaGenome: 54%.
       Borzoi: 55%. Chance is 56%. Even a model I trained directly on this data lands at
       chance. So it's not a model-size problem — the directional answer just isn't in the
       sequence."

## BEAT 3 — The explanation (0:30–0:52)
SHOW: Figure 3 — fig_caqtl_eqtl_clean.png (same-donor caQTL vs eQTL scatter + forest plot).
SAY:  "Here's why. In the same 95 people, I asked: if a variant opens chromatin, does it
       raise gene expression? The answer is no relationship — 0.506, a coin flip. Chromatin
       accessibility and expression are statistically independent. So a model that predicts
       one layer literally cannot tell you the direction of the other. That's the wall these
       models hit."

## BEAT 4 — The anchor + structure (0:52–1:15)
SHOW: Figure 4 — fig_boltz_cofold.png; then rotate a 3D structure live
      (MEF2A_BIN1_ALT_cofold.pdb in the viewer, spinning) if you can screen-record it.
SAY:  "One variant makes it concrete: rs6733839, a top Alzheimer's risk variant near BIN1.
       It opens chromatin, raises BIN1 expression, but represses an isolated enhancer —
       three layers, different answers. My Boltz-2 co-fold shows the risk allele grips the
       MEF2A transcription factor tighter — twelve percent more contacts — consistent with
       it creating a new binding site."

## BEAT 5 — Close (1:15–1:30)
SHOW: repo file tree (results/ and bench/ folders), or the paper's data-availability section.
SAY:  "The takeaway: don't trust a single-layer model's direction call on the variants that
       matter most for disease. And it's all here — an open benchmark, every score,
       reproducible, with the paper. That's the contribution: not that I beat the models,
       but that I show WHY they fail, and give the field a clean way to measure it."

---

## Recording tips
- Have all four figures open in tabs BEFORE you start, in order (1 → 3 → 4). Skip Fig 2 in
  the video; it's detail for the paper, not the pitch.
- The single most memorable number is 0.506 = coin flip. Land on it slowly in Beat 3.
- If you can spin one 3D structure for ~3 seconds, do it in Beat 4 — it's the visual that
  makes judges remember the entry.
- Don't over-claim. The honest framing ("I show WHY they fail") is stronger than any
  "I beat the SOTA" line — and it's what your data actually supports.
- End on the repo, not your face — leave the reproducibility on screen.

## The three numbers you must get right if asked
- Benchmark: AlphaGenome 0.537, Borzoi 0.551, majority-class 0.565 (all at chance).
- Decoupling: same-donor caQTL vs eQTL concordance 0.506 (95% CI 0.455–0.556, p=0.87).
- Structure: both alleles high-confidence (interface pTM 0.978); risk allele +12.5% contacts.

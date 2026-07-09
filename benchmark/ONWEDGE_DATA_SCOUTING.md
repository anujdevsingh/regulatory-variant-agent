# On-wedge data scouting — candidates to lift the n=56 ceiling

**Why this matters:** the wedge benchmark is capped by 62 on-wedge training +
56 on-wedge test variants. No model architecture beats that few examples
(confirmed: on-wedge-only training = 0.464, chance). The single highest-value
next step is *more measured-direction data in microglia/brain/immune*. This memo
scouts what's publicly available, assessed on the three things that actually
matter: (1) is it an on-wedge context, (2) does it give per-variant measured
direction we can harmonize, (3) is the per-variant table openly downloadable.

## Candidates (ranked)

### HIGH priority

**1. Cell 2024 cross-disorder psychiatric MPRA** — PMC11890967 (DOI 10.1016/j.cell.2024.12.022)
- Context: human neural progenitor cells (brain-adjacent). ~17,841 variants tested,
  emVar (expression-modulating) subset called with direction.
- Direction: YES — allele-specific MPRA activity, standard emVar effect sign.
- Access: open (PMC). Largest single potential addition by far.
- Caveat: NPCs, not adult microglia — a brain-lineage context, not brain-identical.
  Would enter the benchmark as its own named context ("neural progenitor MPRA"),
  not merged into existing brain/microglia rows.

**2. Peripheral-immune CNN + MPRA (AD)** — PMC11389932 (2024)
- Context: peripheral immune cells. AD-associated variant set (hundreds).
- Direction: YES — MPRA used to refine their CNN; per-variant activity available.
- Access: open package (zip). Directly on the immune wedge and the *same research
  family* as our documented failure mode (AD immune-cell regulatory variants).
- Caveat: peripheral immune ≠ microglia; verify per-variant table granularity.

**3. Kosoy 2022 microglia caQTL (regulome)** — PMC9388367 / Nat Genet 2022 / NIAGADS NG00105
- Context: primary human microglia, 95 donors. 5,468 significant caQTLs (FDR 5%).
- Direction: YES — sign of the caQTL effect on chromatin accessibility (same
  direction axis as our SuRE/AD-MPRA convention: does alt raise or lower activity).
- Access: NOT in PMC OA package; data via NIAGADS (NG00105) or the paper's supp
  tables — a heavier access path (possible registration).
- Caveat: caQTL (population accessibility) vs MPRA (episomal activity) — measures
  the same ref/alt direction but by a different assay; worth a separate context row.
  This is the most on-target microglia source and the largest real-microglia option.

### MEDIUM priority

**4. Chen microglia + neuroblastoma 3'-UTR MPRA** — PMC8827855 (abstract) / Chen et al. 2024
- 13,515 3'-UTR SNPs; 400 (SH-SY5Y) + 657 (microglia) significant; direction
  concordant in 81/84 shared. On microglia + neuronal.
- Caveat: 3'-UTR variants act post-transcriptionally (mRNA stability/translation),
  a different regulatory layer than the enhancer/promoter MPRA our set is built on.
  Usable but should be flagged as a distinct mechanism, not pooled naively.

**5. MiGA microglia eQTL/sQTL atlas** — NIAGADS NG00105 (Lopes 2022)
- Primary microglia, 4 regions, 100 donors; thousands of eGenes.
- Caveat: eQTL direction is *downstream gene expression*, not the *local ref/alt
  regulatory activity* our benchmark measures. Indirect — a variant can be an
  eQTL via distal mechanisms. Lower fidelity to our exact task.

### BLOCKED

**6. Cooper 2022 AD/PSP MPRA** — DOI 10.1126/science.abi8654
- The ideal on-wedge source (320 frVars in neurons + microglia, 5,706 screened),
  but closed-access (not in PMC; per-variant supplement not freely retrievable) —
  a constraint recorded in prior sessions. Would need institutional/author access.

## Recommended harvest order
1. **Peripheral-immune MPRA (PMC11389932)** — smallest lift, open, directly immune-wedge, on-theme. Start here.
2. **Cell 2024 psychiatric MPRA (PMC11890967)** — biggest payoff (adds brain-lineage variants at scale), open, but large — needs parsing the emVar supplement.
3. **Kosoy 2022 microglia caQTL** — the real-microglia anchor; heavier access path, tackle after the two open MPRAs land.

Each new source enters as its **own named context row** in the benchmark (never
merged into an existing context), harmonized with the same direction convention
(sign of alt−ref activity), hg38-resolved, and added to the frozen split by
chromosome. Re-running the incumbent + floor + wedge scoreboard on the enlarged
on-wedge set is then the test of whether Borzoi's borderline edge (0.625, CI
lower bound at 0.500) becomes significant — and whether a model can finally
separate from it.

## Honest expectation
Even doubling or tripling on-wedge N will not guarantee a win — it will *resolve*
whether the wedge is winnable at all. If Borzoi's edge sharpens and stays
unbeaten, the honest story becomes "Borzoi is the on-wedge SOTA and the gap is
real"; if a model separates, that's the narrow win. Either is a genuine result
the current n=56 cannot deliver.

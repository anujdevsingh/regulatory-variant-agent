# Phase 3.1 — Boltz-2 co-fold of MEF2A + BIN1 enhancer DNA (ref vs alt, rs6733839)

*Structural illustration of the rs6733839 variant effect. NOT a benchmark result —
a confident co-folded complex showing how the risk allele changes the MEF2A–DNA
interface. Run on L40S (female-jade-owl), Boltz-2, 5 diffusion samples, 3 recycling steps.*

## Inputs
MEF2A MADS-box dimer (chains A,B; residues from PDB 1EGW sequence) + 17-bp BIN1 enhancer
DNA duplex (chains E,F) centered on rs6733839.
- REF (non-risk C): DNA …AAAGGT**G**TTTTTAACTT…
- ALT (risk T):     DNA …AAAGGT**A**TTTTTAACTT…  (the +7.56-bit MEF2A site-creating allele)

## Confidence (both high — the complexes are well-defined)
| | confidence | complex pLDDT | ipTM | pTM |
|---|---|---|---|---|
| REF | 0.983 | 0.984 | 0.978 | 0.980 |
| ALT | 0.981 | 0.982 | 0.978 | 0.980 |
Both clear the interface pass line (ipTM>0.5) and fold pass line (pLDDT>0.7) by a wide margin.

## Interface difference (the structural signal)
Protein–DNA atom contacts within 4 Å:
- REF: 255 contacts
- **ALT (risk-T): 287 contacts (+12.5%)**
The MEF2A dimer makes MORE contacts with the risk-allele DNA — structurally consistent
with the JASPAR prediction (risk-T creates a stronger MEF2A motif) and with the measured
microglia chromatin-opening (caQTL) and BIN1 up-regulation (eQTL). The co-fold does not
by itself prove causation, but it provides a concrete, high-confidence structural picture
of a tighter MEF2A–DNA interface at the risk allele.

## Honest scope
- This is a de novo co-fold of a consensus MEF2A dimer onto the local BIN1 enhancer
  sequence, NOT an experimental structure of the endogenous locus.
- The +12.5% contact difference is a single-model geometric readout, not a free-energy
  calculation; it agrees in DIRECTION with the sequence and functional evidence.
- Files: MEF2A_BIN1_REF_cofold.pdb, MEF2A_BIN1_ALT_cofold.pdb (+ confidence JSONs).

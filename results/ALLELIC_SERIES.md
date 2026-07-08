# BIN1 credible set — is rs6733839 the functional variant?

*The highest-value question after single-variant scoring: GWAS gives a locus, not a variant. This scores the **published statistical fine-mapping credible set** for the BIN1 locus through the microglia model, to ask whether rs6733839 — the fine-mapped causal variant — is also the one with the largest predicted molecular effect.*

## Credible set — from published fine-mapping
- **Source:** Schwartzentruber et al. 2021, *Nature Genetics* (DOI 10.1038/s41588-020-00776-w), Supplementary Table 8 — an AD GWAS meta-analysis fine-mapped with **three SNP-level methods** (mean causal probability across FINEMAP / PAINTOR / GCTA-COJO), using open-chromatin annotations. This is the real posterior-probability credible set, not a proxy.
- **25 variants** at the BIN1 locus with mean causal probability ≥ 0.01, scored ref→alt through the **microglia ChromBPNet** model (each aligned to the hg38 reference base; effect allele from the fine-mapping table).
- The set is **overwhelmingly dominated by rs6733839 (posterior 0.998)** — the fine-mapping essentially names it as *the* causal variant, with rs7584040 (0.338) a distant second and the rest < 0.04.

## Result — the fine-mapped causal variant is NOT the largest predicted effect

| Variant | Position | ref>alt | fine-map PP | log2FC | \|effect\| rank |
|---|---|---|---|---|---|
| rs6733839 | chr2:127135234 | C>T | 0.998 | +0.0264 | 11/25 |
| rs7584040 | chr2:127105648 | C>T | 0.338 | -0.0480 | 4/25 |
| rs34997561 | chr2:127147966 | T>C | 0.031 | -0.0128 | 17/25 |
| rs28434131 | chr2:127092716 | A>G | 0.022 | +0.0360 | 7/25 |
| rs72845977 | chr2:127333304 | A>C | 0.017 | +0.0133 | 16/25 |
| rs66837244 | chr2:127144896 | A>C | 0.016 | +0.0037 | 23/25 |

- **rs6733839 is the fine-mapped causal variant (PP = 0.998)** — but ranks only **11th of 25** by predicted microglial accessibility effect.
- The **largest predicted effects** come from low-posterior variants:

| Variant | \|log2FC\| | fine-map PP |
|---|---|---|
| rs12475915 | 0.173 | 0.012 |
| rs7583814 | 0.100 | 0.010 |
| rs11675014 | 0.085 | 0.015 |

- Across the credible set, fine-mapping posterior and predicted effect are **uncorrelated** (Spearman ρ = +0.16, p = 0.46).

![credible set](bin1_susie_figure.png)

## Interpretation (honest)
The statistical evidence that rs6733839 is *the* causal variant is about as strong as fine-mapping ever gets (PP 0.998). Yet the microglia accessibility model does **not** rank it as the largest-effect variant in its own credible set. Three legitimate readings, none of which one model resolves:
1. **The causal mechanism isn't bulk accessibility.** rs6733839's effect may be on TF occupancy or BIN1 promoter looping (invisible to a chromatin-accessibility model) — consistent with its near-median effect and near-zero attribution at the variant base.
2. **This microglia model has real limits.** A single scATAC-pseudobulk model won't capture every regulatory grammar.
3. **The high-effect low-PP variants are model artifacts** — plausible, since they carry little statistical support.

The rigorous takeaway: **statistical causality and predicted molecular effect are decoupled here.** rs6733839 is almost certainly the causal variant, but *this model* doesn't explain why via accessibility — an honest, non-obvious result, and exactly the kind of discrepancy that motivates orthogonal assays (reporter, CRISPR, footprinting).

## Caveats
- 13/25 variants used the fine-mapping effect allele directly; for 12, the effect allele equalled the reference base, so the alternate allele was scored (magnitude meaningful, sign not disease-oriented). rs6733839 uses its true risk allele (C>T).
- Single microglia model, bias-corrected head. Bulk-brain-derived, not experimentally validated.
- "Credible set" here = mean fine-mapping probability ≥ 0.01 (25 variants); the 0.95-mass set is even more rs6733839-dominated.

## Files
- `bin1_susie_figure.png` — fine-mapping posterior vs predicted effect, rs6733839 highlighted.
- `bin1_susie_series.json`, `susie_series_stats.json` — full ranked table + summary stats.

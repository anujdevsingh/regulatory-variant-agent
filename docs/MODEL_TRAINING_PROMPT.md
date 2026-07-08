# Exact kickoff prompt — "train a model to beat the current best"

Paste this to the agent (or the specialist) to start Route #2. It is written to
force the discipline that separates a real result from a fake one.

---

> **You are working on the `regulatory-variant-agent` project. Read
> `docs/MODEL_TRAINING_BRIEF.md` and `results/MPRA_VALIDATION.md` first, then work
> the staged plan in the brief.**
>
> **Goal:** beat the current best model (AlphaGenome; and open-weight Borzoi/
> Flashzoi) on ONE narrow, grounded task — predicting the *direction* of a
> noncoding regulatory variant's effect in a specified cell context, where
> single-window sequence models are known to fail (see the rs6733839 immune-cell
> direction miss). Do NOT attempt to beat AlphaGenome as a generalist.
>
> **Start with the benchmark, not the model.** Before training anything:
> 1. Assemble a held-out variant test set from public MPRA/raQTL with measured
>    ref/alt direction (Cooper 2022; Kircher saturation-MPRA; SuRE raQTL). Split by
>    locus/chromosome, never by variant. Document the split.
> 2. Run Borzoi/Flashzoi (open weights) and AlphaGenome (API) ref−alt scoring on
>    that exact set. Record their direction accuracy and, specifically, their
>    directional errors. This is the bar and the proof the wedge is real.
> 3. Produce a baseline comparison table + figure before writing model code.
>
> **Then** build the motif-grammar-aware directional head (strategy 2 in the
> brief), evaluate on the identical held-out set, and add your model as a new row
> in the same table. Only move to fine-tuning Borzoi (strategy 1) after that.
>
> **Rules (non-negotiable):**
> - Compare on the same task/metric as the incumbents, on the identical held-out
>   set. Report where you LOSE as prominently as where you win.
> - Treat any apparent SOTA win as a leakage bug until you've ruled out test
>   contamination, an easier test set, and metric cherry-picking.
> - No compute target is connected yet — if training needs a GPU, tell me to
>   connect one (Compute panel) rather than faking a run.
> - Commit each stage to the repo and log it in `ROADMAP.md`; present the plan and
>   let me choose the direction at each fork (project workflow).
> - Honesty mandate: a well-characterized negative or a narrow, real win both beat
>   an overclaimed result.

---

## Notes on scope
- This prompt encodes the *benchmark-first* discipline deliberately — the easiest
  way to fool yourself here is to train first and benchmark loosely.
- Swap the task (T1/T2/T3 in the brief) only with an explicit reason; the wedge is
  currently T2-direction.

# From Raw Experience to Skill Consumption: A Systematic Study of Model-Generated Agent Skills

**Authors:** Zisu Huang, Jingwen Xu, Yifan Yang, Ziyang Gong, Qihao Yang, Muzhao Tian, Xiaohua Wang, Changze Lv, Xuemei Gao, Qi Dai, Bei Liu, Kai Qiu, Xue Yang, Dongdong Chen, Xiaoqing Zheng, Chong Luo  
**Affiliations:** Fudan University, Microsoft Research, Shanghai Jiao Tong University  
**Date:** May 2026  
**Source:** https://arxiv.org/abs/2605.23899

---

## Abstract

Language agents increasingly improve by reusing knowledge distilled from past trajectories: _skills_—short, structured procedural artifacts—can be loaded at inference time without retraining and have become a defining mechanism for accumulating experience in modern agent stacks. In particular, _domain-level skills_ package a domain's recurring procedures into a single reusable artifact or a coordinated set of them, enabling fast adaptation to new tasks within the domain rather than per-task optimization.

This paper conducts a comprehensive, utility-grounded study of model-generated, domain-level skills that analyzes all three stages of the skill lifecycle: **experience generation → skill extraction → skill consumption**. The study spans five domains, six target models, and five extractor models.

---

## Key Research Questions

- **RQ1** Do model-generated, domain-level skills reliably benefit downstream agents across targets, extractors, and domains?
- **RQ2** What actually drives a skill's downstream utility across the three lifecycle stages?
- **RQ3** Can empirical findings be transformed into a concrete, drop-in improvement to skill extraction itself?

---

## Evaluation Framework

### Skill Lifecycle

**Stage 1 — Experience generation:** Target model M executes training tasks, producing an experience pool of (task, trajectory, outcome) triples with both successful and failed trajectories.

**Stage 2 — Skill extraction:** Extractor E distills the pool into a skill set using a two-stage framework:
- _Per-trajectory analysis_: each trajectory is independently processed to extract up to K success or failure patterns.
- _Hierarchical consolidation_: pattern sets are merged in groups (configurable size G) until a single consolidated pattern set remains, then converted to schema-conformant skills via tool calls.

**Stage 3 — Skill consumption:** The same target M is provided with the extracted skills (in the system prompt) and evaluated on held-out tasks.

### Skill Representation

Each skill follows the **Agent Skills open standard** (https://github.com/agentskills/agentskills) with fields: `name`, `description`, `body` (Markdown procedural instructions), and optional `references` and `scripts`.

### Metrics

**Performance delta:**  
Δ(E, M, D) = Perf(M | skills, test) − Perf(M | test)

**Extraction Efficacy (EE):** For a fixed extractor, how reliably it produces helpful skills across different target models.

**Target Evolvability (TE):** For a fixed target, how much it benefits from skills extracted by different extractors.

---

## Main Results (RQ1)

Evaluated across five domains: ALFWorld (embodied), SpreadsheetBench (productivity), SWE-bench-Verified (software engineering), SEAL-0 (web search), BFCL-v4 (tool calling).

### Skills are generally beneficial, but not guaranteed

- Positive gains in **75% of entries**
- **25% negative transfer** (skills degrade performance)
- Domain-dependent risk: SpreadsheetBench and SWE-bench lowest negative rate (13%); ALFWorld most fragile (47%)

### Better executor ≠ better extractor

On SpreadsheetBench, the lightweight Gemini-3.1-Flash-Lite achieves the highest EE, while GPT-5.4 ranks last despite having the strongest baseline. Skill extraction is a **distinct capability** from task execution.

### Skill utility is target-dependent

The same extractors can produce very different gains across targets in the same domain. Skill benefit is shaped both by extractor quality and by what the target's own experience makes extractable.

---

## Diving Deeper into the Lifecycle (RQ2)

### Experience Generation: Success or Failure?

Success/failure pool composition strongly affects skill quality:
- **All-failure pools perform worst** — successful trajectories are essential as they provide positive procedural signals.
- Optimal ratio is **domain-specific**: SpreadsheetBench favors success-heavy pools; ALFWorld performs best with failure-heavy pools (failed attempts reveal invalid actions and dead-end states).

### Skill Extraction: What Makes a Good Skill?

**Format does not matter.** Four formats tested (ordered list, unordered list, checklist, prose) — the format effect is statistically non-significant on every target (all p > 0.34). Variance is driven by **what** a skill says, not how it looks.

**Textual plausibility does not predict utility.** Without evaluation criteria, an LLM judge picks the better skill only **46.4% of the time** (random). On pairs with large gaps (δ ≥ 5%), accuracy drops to **15.8%** — the skill that reads better is often the one that performs worse.

**Qualitative pattern:** High-utility skills name **concrete failure mechanisms with executable remedies** (e.g., "formulas are not evaluated in headless environments; always precompute static values in Python"). Low-utility skills offer only generic process-level advice (e.g., "resolve the contract before coding").

### Skill Consumption: Benefit Varies Across Targets

- With the same skill, per-target gains differ sharply.
- Skills distilled from strong-baseline experience pools consistently improve all targets.
- Skills from weak pools cause negative transfer on some targets.
- Skill consumption **reshapes the default policy** rather than triggering explicit skill calls.

---

## From Diagnosis to Intervention: Validated Rubric (RQ3)

### Three Dimensions That Predict Utility

Discovered through automated contrastive analysis of high-gap skill pairs. Better-rates (proportion where higher-Δ skill scores better) in parentheses:

| Dimension | Description | Better-rate |
|---|---|---|
| **Failure Mechanism Encoding** | Names specific domain failure modes with executable remedies | 64–66% |
| **Actionable Specificity** | Concrete, executable instructions rather than generic advice | 64–66% |
| **High-Risk Action Blacklist** | Explicit list of actions to avoid | 64–66% |

### What Does NOT Predict Utility (plausibility rubric, 7 naive dimensions)

Clarity, completeness, conciseness, logical structure, formatting, tone, generality — these are what an LLM believes distinguishes good skills, but they **do not align with actual downstream performance**.

### Impact of the Validated Rubric

Adding the 3-dimension rubric to the extractor's system prompt:
- Improves **all 9 evaluated cells** (+1.55 pp average)
- Largest gains on SpreadsheetBench (+2.3 to +3.7 pp)

Adding the naive 7-dimension plausibility rubric:
- **Hurts** average performance (−0.59 pp), reducing accuracy in 6 of 9 cells

### Judge Accuracy with Rubric Guidance

| Condition | Overall accuracy | On hardest pairs (δ ≥ 5%) |
|---|---|---|
| Unguided LLM judge | 46.4% | 15.8% |
| With validated rubric | **73.8%** | majority correct |

---

## Conclusion

Model-generated skills are beneficial on average (75% of cases) but exhibit substantial variance and non-trivial negative transfer (25% of cases). Neither model scale nor textual plausibility reliably predicts downstream utility.

Key practical takeaways:
1. **Format is irrelevant** — focus on content.
2. **Encode failure mechanisms** — name what goes wrong and how to fix it.
3. **Be specific** — generic process advice provides no actionable leverage.
4. **Include blacklists** — explicit "never do X" improves performance.
5. **Use the validated rubric** when evaluating or generating skills; ignore plausibility-based criteria.

---

## Appendix: Contrastive Skill Examples

### SpreadsheetBench (Δ gap = 10.3 pp)

**Higher-Δ skill** (Gemini-3.1-FL, Δ = +14.7): Encodes three domain-specific failure mechanisms:
1. Formula injection fallacy — formulas not evaluated in headless execution; always precompute static values in Python.
2. Index-shifting errors during deletion — use reverse iteration.
3. Dynamic addressing — never use hardcoded cell references.

**Lower-Δ skill** (GPT-5.4, Δ = +4.3): Only process-level directives ("resolve the contract," "edit minimally") — reasonable but too abstract to prevent the concrete failure modes.

### ALFWorld (Δ gap = 6.0 pp)

**Higher-Δ skill** (Gemini-3.1-Pro, Δ = +7.5): Provides executable action patterns tailored to ALFWorld's mechanics:
1. Deep inspection — explicitly open closed containers; don't assume visibility equals absence.
2. Active state transformations — concrete locate-acquire-transport-invoke pipeline.
3. Prerequisite resolution — navigate and open destinations _before_ attempting placement.

**Lower-Δ skill** (GPT-5.4, Δ = +1.5): Same high-level logic ("ground the goal," "manage preconditions") but at a level of abstraction that doesn't map onto ALFWorld's action vocabulary.

---

## Note on Agent Skills Standard

This study uses the Agent Skills open standard as its skill schema — the same format used by this repository. The skill fields (name, description, body, references, scripts) are the experimental unit throughout the paper.

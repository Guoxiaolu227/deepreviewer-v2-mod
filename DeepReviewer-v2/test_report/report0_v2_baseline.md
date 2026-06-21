## Summary
# Final Review Report

## Summary

本文提出APRES，一个基于LLM Agent的两阶段框架：(1) 通过agentic search自动发现与未来引用数高度相关的评估rubric（使用负二项回归），(2) 以该rubric为目标函数，通过闭环迭代修订（Review→Rewrite→Select）自动改进论文的表述质量和可读性，同时保持科学内容不变。在来自ICLR和NeurIPS的26,707篇论文数据集上，APRES发现的rubric在引用预测MAE上比次优基线低19.6%；人类盲评中，APRES修订版以79%的偏好率胜出（95% CI: 70.1%–79.0%）。附录中进一步通过复现NeurIPS一致性实验设计验证了LLM评审的一致性。

总体而言，这是一项具有实际应用价值的工程-实证研究，将"评估准则的自动发现"与"闭环文本修订"集成在一个系统中，研究问题明确、数据集规模可观、人类评估设计合理。然而，在实验设计的内部有效性（ΔS的循环论证）、统计分析严谨性（零膨胀数据上的MAE适切性、缺少显著性检验）、与竞争方法的差异化定位（ARISE等系统的存在）、以及Goodhart's Law风险等方面存在需要认真回应的问题。以下报告将逐一展开。本文的**研究价值**在于提出了一个新颖的"先发现评估准则再据此修订"的框架范式；**主要风险**在于核心评估指标的循环性和对LLM评审一致性的过度解读。

## Strengths
1. **清晰的两阶段框架设计与工程完整性。** APRES的"先发现rubric→再基于rubric修订"的两阶段流程逻辑清晰，每个阶段都有明确的方法论支撑（负二项回归、MultiAIDE搜索、diff-based编辑约束）。框架的工程实现细节充分（prompts公开、超参数报告完整、消融实验覆盖关键组件），为复现提供了良好基础。

2. **大规模真实数据集的实证基础。** 使用来自ICLR 2024-2025和NeurIPS 2023-2024的26,707篇论文，涵盖多种论文类型和评审风格，为研究结论提供了扎实的统计基础。数据集的当代性（使用最近的会议数据）也有助于确保发现的rubric反映当前学术写作和评审实践。

3. **人类评估设计严谨。** 盲法配对比较、每位参与者有PhD背景、每对论文由3人独立评估、使用二项检验和置信区间——这一人类评估设计在自动化论文修订领域中属于较高标准。79%偏好率（p<10⁻²²）提供了强有力的独立验证，部分缓解了ΔS循环性带来的担忧。

4. **诚实的局限性讨论和自我批判意识。** 论文在Discussion中坦率地讨论了引用作为impact proxy的局限性（包括Goodhart's Law）、修订无法改变论文科学质量、以及无法完美保证科学内容不被修改。这种透明度值得肯定。

5. **附录中的审稿一致性实验设计有创新性。** 使用Glicko2评分系统结合LLM pairwise比较来测量审稿一致性，通过复现NeurIPS一致性实验的设计框架，为LLM评审的可靠性提供了一个新颖的分析视角。

## Weaknesses
1. **ΔS评估指标的循环性（内部有效性问题）。** APRES的Stage 2使用发现的rubric同时作为优化目标函数和评估指标。Rewriter被训练来最大化R*的评分，改进效果又以R*的ΔS来度量。这构成循环论证——ΔS的提升几乎必然发生，但不能独立证明修订质量。虽然人类评估（79%偏好率）提供了独立验证，但论文在正文中（Page 8 - LLM Rubric Evaluation Results段落）仍将ΔS作为首要证据来论证"反馈的可操作性"，这在逻辑上不成立。

2. **零膨胀数据上MAE指标的有效性未得到充分论证。** 数据集的平均引用数仅为2.07，大量论文引用数为0。在这类零膨胀数据上，MAE作为核心评估指标的信噪比很低——一个总是预测0的模型也能获得较合理的MAE。论文没有报告Spearman rank correlation等更能反映排序质量的相关性指标，也没有讨论零膨胀模型（如hurdle model）作为替代方案。

3. **与最近相关工作的差异化定位不够充分。** 检索发现ARISE（arXiv:2511.17689）已经提出了一个rubric-guided multi-agent iterative refinement框架用于学术论文生成。虽然ARISE的目标（生成survey vs 修订已有论文）不同，但其核心机制（rubric引导的多agent迭代）与APRES存在概念重叠。论文在Introduction和Related Work中均未提及ARISE或类似系统，削弱了"novel"声明的可信度。

4. **LLM审稿一致性实验的结论过度外推。** 附录A.2的LLM一致性分析存在两个问题：(a) 同一模型家族内的低分歧率不必然意味着"更可靠"——共享的训练数据和评估偏好可能导致共享偏差（而非真正的质量信号）；(b) 跨模型家族的>35%分歧率（比随机还差）被正文轻描淡写地带过，未讨论其对系统鲁棒性的影响；(c) 将"评分一致性"直接引申为"APRES修订的可靠性"存在逻辑跳跃。

5. **缺少科学内容保真度的实证验证。** Limitations中坦诚承认"无法完美保证科学内容不被修改"，但论文没有提供任何实证数据来量化这一约束被违反的频率和严重程度。考虑到APRES的核心价值主张是"保持科学内容不变"，这是一个关键的证据缺口。

6. **定量声明的表述不精确。** 全文多处出现"19.6% improvement in MAE"的表述，这在语义上有矛盾（MAE越低越好，不应说"improvement in MAE"）。正确的表述应为"reduces MAE by 19.6% relative to the next best baseline"。

7. **Goodhart's Law的自我指涉矛盾未被解决。** Discussion中引用了Goodhart's Law来讨论将引用作为proxy的局限，但没有将其应用到APRES自身的方法设计上——APRES在Stage 2正是将rubric同时作为measure和target。

## Key Issues
以下是按严重程度排序的核心缺陷（Ranked Error Board）：

| # | Severity | Issue | Research-Value Impact | Validity Risk | Fixability | Confidence |
|---|----------|-------|----------------------|---------------|------------|------------|
| 1 | Major | ΔS评估指标的循环性——rubric同时作为优化目标和评估标准 | 高：若不修正，核心证据链（"修订改进了论文"）不可靠 | 高：ΔS不独立于优化过程 | 高：可通过独立LLM评估或仅依赖人类评估修正 | High |
| 2 | Major | 零膨胀数据上MAE的适切性未论证——平均引用2.07，大量0引用 | 高：影响引用预测结论的可信度 | 中：19.6% MAE改进的实际意义存疑 | 高：补充Spearman correlation | High |
| 3 | Major | 科学内容保真度无实证验证——承认"无法保证"但无量化数据 | 高：核心价值主张缺乏实证支撑 | 高：可能无意中修改了科学内容 | 中：需额外人类标注实验 | High |
| 4 | Major | LLM审稿一致性结论过度外推——将"评分一致性"引申为"修订可靠性" | 中：影响结论的学术严谨性 | 中：跨模型高分歧被弱化 | 高：修正结论措辞 | High |
| 5 | Major | Goodhart's Law的自我指涉矛盾——讨论其风险但不应用于自身方法 | 中：影响论文的自我批判深度 | 中：优化目标可能被gaming | 高：增加讨论段落 | High |
| 6 | Minor | 与ARISE等系统的差异化定位不足 | 中："novel"声明的可信度受影响 | 低 | 高：增加对比讨论 | Medium |
| 7 | Minor | MAE定量声明表述不精确（"improvement in MAE"语义矛盾） | 低 | 低 | 高：修正措辞 | High |

## Actionable Suggestions
### 针对Key Issues的具体修复方案

**Issue 1 — ΔS循环性修复（Must）**

将ΔS在正文中明确标记为"内部优化指标（internal optimization metric）"而非独立评估指标。在Page 8 - LLM Rubric Evaluation Results段落中，将核心证据从ΔS切换为人类评估结果。建议增加一个独立评估：使用不同的LLM和不同的rubric对修订前后的论文进行评分，报告该独立ΔS作为补充。

**Issue 2 — 零膨胀数据评估增强（Must）**

在Section 4.1的Citation Number Prediction Results中增加：(a) Spearman rank correlation between predicted and actual citations for each method；(b) 报告以0为基线（always-predict-zero）的MAE作为下界参考；(c) 讨论零膨胀对MAE解释的影响。如果条件允许，增加hurdle model或zero-inflated negative binomial作为替代建模方案。

**Issue 3 — 科学内容保真度验证（Must）**

增加一个最小验证实验：随机抽取50-100篇APRES修订后的论文，请具有ML领域专长的评估者逐句对比原版和修订版，标记任何科学内容被修改的实例。报告：(a) 科学内容被修改的论文比例；(b) 修改类型分布（数值变化/方法描述变化/结论变化/无实质性变化）。这直接量化了APRES的核心价值主张。

**Issue 4 — 一致性实验结论修正（Must）**

在附录A.2的Results and Analysis中：(a) 明确区分"同一模型家族内的一致性"与"跨模型家族的可靠性"；(b) 直接讨论Gemini 2.5 Pro vs o3的>35%分歧率的含义；(c) 将结论从"LLM evaluation can be significantly more consistent than human peer review"调低为"LLM evaluation within the same model family shows high consistency, but cross-family disagreement highlights that evaluation outcomes depend on the choice of LLM judge."

**Issue 5 — Goodhart's Law自我反思（Nice-to-have）**

在Discussion的"From Mimicking Humans to Predicting Impact"段落末尾增加一段：明确承认APRES的Stage 2面临Goodhart's Law风险，讨论人类评估（79%偏好率）在多大程度上缓解这一风险，提出可能的缓解策略。

**Issue 6 — 与ARISE的差异化定位（Nice-to-have）**

在Introduction的第二个段落和Related Work中增加对ARISE的引用和差异化分析，明确说明APRES与ARISE在rubric来源（搜索发现 vs 预定义）、优化目标（引用预测 vs 写作质量）、和应用场景（已有论文修订 vs 新论文生成）上的区别。

**Issue 7 — MAE表述精确化（Must）**

全文统一将"improves...in MAE"或"improvement in MAE"替换为"reduces MAE by X% relative to [baseline name]"。这包括Abstract、Introduction（Page 2）、和所有提到该数字的位置。

## Storyline Options + Writing Outlines
### 当前故事线诊断

当前论文的叙述线为：同行评审危机 → LLM作为解决方案但存在风险 → APRES两阶段框架 → 实验结果 → 社区定位与愿景。主要问题在于：(a) Introduction第一段的研究差距声明不够精确；(b) 贡献声明缺乏与竞争方法的清晰区分；(c) Abstract和Conclusion中的定量声明表述不精确。

### 推荐故事线（优化版）

**Abstract Outline (4-5句):**
- S1 (Problem & Domain): "Scientific peer review suffers from inconsistency and scalability challenges, limiting timely, constructive feedback for authors—particularly non-native speakers."
- S2 (Prior Gap): "While LLMs offer scalable feedback, existing systems either mimic human review criteria or revise text without grounding in predictive quality signals."
- S3 (Proposed Method): "We introduce APRES, a two-stage agentic framework that (i) discovers an evaluation rubric predictive of future citations via agentic search with negative binomial regression, and (ii) uses this rubric to guide iterative, content-preserving paper revision."
- S4 (Key Result): "Across 26,707 ICLR and NeurIPS papers, APRES reduces citation prediction MAE by 19.6% relative to the strongest baseline, and its revised papers are preferred over originals 79% of the time in blind human evaluation (95% CI: 70.1%–79.0%)."
- S5 (Bounded Implication): "These results demonstrate that learned evaluation criteria can effectively guide automated manuscript improvement, offering a data-driven complement to human peer review."

**Introduction Outline (P1–P5):**
- P1 (Big Picture + Gap): 同行评审危机 → 现有LLM审稿系统的局限（模仿人类准则、未利用数据驱动信号）→ 本文的解决方案方向。**关键修正：** 明确"constrained technique"的约束边界，增加对ARISE的简要区分。
- P2 (Solution Preview): APRES的两阶段框架概述 → 核心贡献声明。**关键修正：** 将"two-stage method"改为更有力的贡献表述，明确与ARISE的区别。
- P3 (Validation Summary): 实验验证概述（引用预测、修订效果、人类评估、一致性实验）。
- P4 (Positioning & Vision): 社区背景（AAAI、ICLR pilot）→ 本文证据意义 → 立场声明（不赞成全自动）→ 愿景。**关键修正：** 重组为结果→意义→立场→愿景的顺序。
- P5 (Paper Structure): 论文结构预告。

### 备选故事线

**选项B — "Measure-First" 叙事：** 以"如何衡量论文质量？"为核心问题展开，先深入讨论引用作为proxy的利弊，再引入APRES作为"先发现衡量标准，再据此优化"的解决方案。这更适合面向科学计量学（scientometrics）读者。

**选项C — "Stress-Test" 叙事：** 以"作者在投稿前如何自检？"为核心问题展开，将APRES定位为"投稿前压力测试工具"，实验结果展示为"APRES能发现并修复哪些人类评审可能忽略的表述缺陷"。这更适合面向作者群体的推广。

## Priority Revision Plan
### P0（Must — 影响核心结论的有效性）

| # | Action | Estimated Effort | Expected Impact |
|---|--------|-----------------|-----------------|
| P0-1 | 修正ΔS的定位：在正文中将ΔS明确标记为"内部优化指标"，将核心证据从ΔS切换为人类评估。在Fig. 4上增加标注说明指标性质。 | 2-3小时（文字修改+图表标注） | 消除最严重的内部有效性问题 |
| P0-2 | 补充引用预测的Spearman rank correlation和零膨胀基线。在Section 4.1中增加一个表格，报告Spearman ρ和always-predict-zero的MAE作为下界。 | 4-6小时（重新运行分析+撰写） | 增强引用预测结论的统计可信度 |
| P0-3 | 全文统一修正MAE表述：将所有"improvement in MAE"替换为"reduces MAE by X% relative to [baseline]" | 1小时（全局搜索替换+人工审核） | 消除定量声明的语义矛盾 |
| P0-4 | 修正附录A.2一致性实验的结论措辞：降低从"LLM更可靠"到"同一模型家族内高一致性"的表述强度，讨论跨模型分歧 | 2-3小时（文字修改） | 纠正结论的过度外推 |

### P1（Should — 提升论文稳健性和完整性）

| # | Action | Estimated Effort | Expected Impact |
|---|--------|-----------------|-----------------|
| P1-1 | 增加科学内容保真度的抽样验证实验：50-100篇修订论文的逐句人工对比 | 1-2周（人工标注+分析） | 填补核心价值主张的证据缺口 |
| P1-2 | 在Discussion中增加Goodhart's Law对APRES自身方法的反思段落 | 1-2小时（撰写1-2段讨论） | 提升论文的自我批判深度 |
| P1-3 | 在Introduction和Related Work中增加对ARISE的引用和差异化讨论 | 2-3小时（文献整合+撰写） | 加强"novel"声明的可信度 |

### P2（Nice-to-have — 进一步优化）

| # | Action | Estimated Effort | Expected Impact |
|---|--------|-----------------|-----------------|
| P2-1 | 增加独立LLM评估：使用不同LLM+不同rubric对修订前后论文评分，作为ΔS的独立补充 | 1周（实验+分析） | 提供ΔS之外的独立自动评估 |
| P2-2 | 分析更长引用窗口（如24个月）的引用预测效果（如果数据可用） | 1-2周（数据收集+分析） | 增强引用预测的长期有效性证据 |
| P2-3 | Introduction和Conclusion的故事线优化（参见Storyline Options） | 3-4小时（重写+润色） | 提升论文整体叙事和可读性 |

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|-------|---------|-------------|-----------------|-------------------|
| E1 | Rubric Search: agentic search can discover rubric that better predicts citations than baselines | 26,707 papers; 80/10/10 split; MultiAIDE vs MLP on SPECTER, PCA+SPECTER, Human scores, Prompt breeder; 4 LLMs tested | MAE | MultiAIDE converges to MAE ~1.92-2.30 vs 2.65 (PCA+SPECTER) and ~5.0 (Human scores) | C1 (rubric discovers predictive signals) | MAE may not be meaningful on zero-inflated data; no Spearman ρ; no significance test |
| E2 | Paper Improvement: LLM revision guided by discovered rubric improves predicted impact | Test set papers in 3 brackets (Accept/Borderline/Reject); ΔS measured; Simple Rubric and Embedding PCA baselines | ΔS (rubric score change) | ΔS = 3.33 (o3 Borderline), 2.98 (o3 Reject); discovered rubric outperforms baselines | C2 (revision improves paper quality) | ΔS circularity (same rubric for optimization and evaluation); ΔS not independent |
| E3 | Human Evaluation: blind pairwise preference between original and APRES-revised papers | 364 paper pairs; 3 annotators per pair; PhD-level ML researchers | Preference rate; binomial test | 79% preference for revised (95% CI: 70.1%-79.0%); p<10⁻²² | C2 (revision is human-perceivable) | Word cloud analysis of reasons is informal; no inter-annotator agreement reported (e.g., Fleiss' κ) |
| E4 | Ablation: removing discovered rubric or MultiAIDE search hurts performance | Accept/Borderline/Reject brackets | ΔS | APRES w/o R*: ΔS=1.02-1.24; w/o MultiAIDE: ΔS=1.13-1.46; Full: ΔS=1.67-3.33 | C1+C2 (rubric and search are necessary) | Same circularity concern as E2 |
| E5 | Glicko2 Rating: LLM judge ratings correlate with conference decisions | 20,000 pairwise comparisons; Glicko2 rating system | Rating vs conference outcome distribution | Strong positive correlation: higher Glicko2 → more acceptances, orals, spotlights | C3 (LLM evaluation aligns with human committees) | Correlation is visual/qualitative; no quantitative metric (e.g., AUC, rank correlation) |
| E6 | Reviewer Consistency: LLM committees more consistent than human NeurIPS committees | 4 LLM models; pairwise disagreement rate matrix; 25% acceptance threshold | Disagreement Rate (DR) | Within-model family DR: 19.2%-20.3%; cross-family: up to >35.1%; Human 2014/2021: 23%-25.9% | C3 (LLM evaluation is consistent) | Comparison to human committees is asymmetric; cross-family high DR glossed over |

### Research-Theme Gap Diagnosis

| Research Value Claim | Evidence Strength | Gap |
|----------------------|-------------------|-----|
| New Knowledge: agentic search discovers novel evaluation criteria | Partially proven (E1) | MAE metric validity; lack of Spearman correlation; need qualitative analysis of discovered rubric items vs existing ones |
| Reproducibility: APRES can be replicated and reused | Partially proven (prompts and hyperparameters documented) | No code released at time of review; API-based LLMs introduce non-determinism across runs |
| Impact on Practice: APRES can help authors improve papers | Partially proven (E3) | No content-fidelity audit; 79% preference is for presentation quality, not scientific quality |

### Proposed Research Experiments

| Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Estimated Cost/Time | Priority |
|-------------|------------|----------------|---------------------|---------|-------------------|---------------------|----------|
| E7: Content Fidelity Audit | APRES preserves scientific content in ≥95% of edits | Random sample 50-100 revised papers; expert annotators compare original vs revised line-by-line for content alterations | Human baseline (inter-annotator agreement on "no change") | Content alteration rate; alteration severity distribution | ≥95% of papers have zero scientific content alterations | 1-2 weeks (annotation) | P0 |
| E8: Independent LLM Evaluation | APRES revision improves quality even when evaluated by a different LLM with a different rubric | Use GPT-4 or Claude with a standard conference review rubric to score original vs revised papers | Report ΔS_independent alongside ΔS | ΔS_independent; correlation between ΔS and ΔS_independent | ΔS_independent > 0 for ≥60% of papers | 3-5 days (API calls) | P1 |
| E9: Spearman Correlation for Citation Prediction | The discovered rubric's predicted scores rank-correlate with true citations better than baselines | Compute Spearman ρ for MultiAIDE vs each baseline on test set | Report always-predict-zero baseline ρ | Spearman ρ | ρ_MultiAIDE > ρ_best_baseline with p<0.05 | 2-3 hours (statistical analysis) | P0 |
| E10: Inter-Annotator Agreement for Human Evaluation | Human annotators show moderate-to-substantial agreement on paper preferences | Report Fleiss' κ or Krippendorff's α for the 3 annotators per pair | Standard benchmarks for agreement | Fleiss' κ | κ > 0.4 (moderate agreement) | 1-2 hours (statistical analysis) | P1 |

### ASCII Diagram — Experiment Upgrade Plan
```text
Stage 1 (P0, 1-3 days): Spearman ρ report (E9) + MAE wording fix
    → Directly addresses statistical validity concerns

Stage 2 (P0+P1, 1-2 weeks): Content fidelity audit (E7) + Independent LLM eval (E8)
    → Addresses circularity and content preservation concerns

Stage 3 (P1, same time): Inter-annotator agreement (E10) + Goodhart's Law discussion
    → Addresses robustness and self-critique concerns
```

## Novelty Verification & Related-Work Matrix
### Contribution Novelty Verdict Board (9A)

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|---------------------|---------------------|-----|------------|------------------------|
| C1 | Agentic search discovers evaluation rubric predictive of future citations, outperforming human scores and embedding-based baselines | HSPIM [1] (uses genetic algorithm for LLM-based innovation scoring); TNCSI_SP (Zhao et al. 2025b, LLM citation prediction without criteria discovery); HLM-Cite (Hao et al. 2024, citation prediction with generative ranking) | **partially_overlapping** | HSPIM uses genetic algorithm to optimize question-prompt combinations for measuring paper innovation via LLM, conceptually overlapping with rubric search. However, HSPIM targets innovation scoring (not citation prediction), does not use negative binomial regression, and does not connect to paper revision. Core mechanism (LLM-guided search over evaluation criteria optimized for citation prediction) remains distinct. | Medium | Reposition as "first to use agentic search for citation-predictive rubric discovery" rather than "first to discover evaluation criteria via search" |
| C2 | Closed-loop automated paper revision guided by discovered rubric preserves scientific content while improving presentation | ARISE [2] (rubric-guided iterative refinement for survey generation); SWIFT (Chamoun et al. 2024, LLM feedback for revision); ParaRev [3] (paragraph-level scientific text revision with instructions) | **partially_overlapping** | ARISE uses rubric-guided iterative refinement but for generating new surveys (not revising existing papers), and uses pre-defined rubrics (not discovered ones). SWIFT and R3 provide automated feedback/revision but without learned quality scoring. The integration of "discovered citation-predictive rubric" + "closed-loop revision" is a novel combination. However, the optimization-evaluation circularity weakens the evidence. | Medium | Explicitly scope as "first to integrate discovered citation-predictive rubric with closed-loop paper revision"; acknowledge ARISE as closest related system |
| C3 | LLM-based evaluation is significantly more consistent than human peer review, validated through NeurIPS-style consistency experiment | ReviewerToo [4] (LLM reviewer framework; 81.8% accept/reject accuracy vs 83.9% human on ICLR 2025); LLM-as-a-Reviewer [5] (12 LLM benchmark on NeurIPS/ICLR; divergence and calibration analysis); PRISM [6] (multi-dimensional LLM reviewer benchmark) | **partially_overlapping** | ReviewerToo is the closest prior work: it systematically evaluates LLM review quality on ICLR 2025 papers, finding AI reviews rated higher quality by LLM judges. However, ReviewerToo does not replicate the NeurIPS consistency experiment design (Glicko2 + two-committee disagreement rate). The specific experimental design (Glicko2 pairwise rating → binary decision thresholding → disagreement rate matrix) appears novel. But: within-model-family consistency does not equal reliability (shared biases); cross-family >35% DR weakens the claim. | Medium | Lower conclusion strength; distinguish "within-model consistency" from "across-model reliability"; explicitly discuss cross-family high DR implications |

### Related-Work Taxonomy Matrix (9B)

```text
Related Work Taxonomy (Root): AI-Assisted Scientific Peer Review & Revision
├── Branch 1: LLM-Based Review Generation
│   ├── Leaf 1.1: Single-Agent Review Generation [Reviewer2 (Gao et al. 2024), ReviewRobot (Wang et al. 2020)]
│   └── Leaf 1.2: Multi-Agent Review Systems [MARG (D'Arcy et al. 2024), ReviewAgents (Gao et al. 2025), TreeReview (Chang et al. 2025)]
├── Branch 2: LLM Reviewer Evaluation & Benchmarking
│   ├── Leaf 2.1: LLM-vs-Human Comparison [Liang et al. 2023, ReviewerToo [4], LLM-as-a-Reviewer [5]]
│   └── Leaf 2.2: Multi-Dimensional Benchmarks [PRISM [6]]
├── Branch 3: Scientific Impact Prediction
│   ├── Leaf 3.1: Citation Network & Metadata Models [DGNI (Geng et al. 2022), SPECTER (Cohan et al. 2020b)]
│   ├── Leaf 3.2: LLM-Based Text Impact Prediction [TNCSI_SP (Zhao et al. 2025b), HLM-Cite (Hao et al. 2024), LLM-Metrics]
│   └── Leaf 3.3: LLM-Based Innovation/Quality Scoring [HSPIM [1]]
├── Branch 4: Automated Scientific Text Revision
│   ├── Leaf 4.1: Feedback Generation [SWIFT (Chamoun et al. 2024), Liang et al. 2023]
│   ├── Leaf 4.2: Revision with Instructions [ParaRev [3], R3 (Du et al. 2022)]
│   └── Leaf 4.3: Rubric-Guided Iterative Generation [ARISE [2]]
└── Branch 5: Peer Review Process Analysis
    ├── Leaf 5.1: Consistency & Bias Studies [NeurIPS 2014/2021 (Cortes & Lawrence 2021; Beygelzimer et al. 2023), Peer Reviews of Peer Reviews (Goldberg et al. 2023)]
    └── Leaf 5.2: LLM Risks in Review [Ye et al. 2024, Collu et al. 2025]
```

### Head-to-Head Comparison Matrix (9C)

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|-----------------|-------------|------------------------|------------------|--------------------------|
| ARISE [2] | Automated survey paper generation | Multi-agent rubric-guided iterative refinement with peer-review feedback loop | Rubric-guided iterative refinement with LLM agents | ARISE generates new surveys (not revising existing papers); uses pre-defined rubrics (not discovered via search); optimizes for writing quality (not citation prediction) | Requires explicit differentiation in text; APRES novelty is in "citation-predictive rubric discovery" not "rubric-guided refinement" |
| HSPIM [1] | Measuring scientific paper innovation | Hierarchical LLM-based scoring with genetic algorithm optimization of question-prompts | LLM-based evaluation criteria optimization via evolutionary search | HSPIM targets innovation measurement (not citation prediction); does not connect scoring to paper revision; uses genetic algorithm not agentic scaffold | C1 partially overlapping but differentiable; APRES should cite HSPIM |
| ReviewerToo [4] | AI-assisted peer review framework | Modular LLM reviewer framework with persona simulation; ICLR 2025 validation | Systematic LLM review quality evaluation on real conference data | ReviewerToo focuses on review generation quality and accuracy; does not replicate NeurIPS consistency design; does not connect evaluation to paper revision | C3 partially overlapping; APRES's consistency experiment design is novel but ReviewerToo should be cited |
| ParaRev [3] | Scientific paragraph revision | Instruction-guided paragraph-level revision with detailed revision intentions | LLM-based scientific text revision with structured guidance | ParaRev requires explicit revision instructions from humans; does not use learned quality scoring; no closed-loop optimization | C2 differentiable; ParaRev represents a complementary revision paradigm |

### Contribution-level Novelty Conclusion

- **C1 (Rubric Search for Citation Prediction):** Partially overlapping with HSPIM in the concept of search-based evaluation criteria optimization, but differentiated by target (citation prediction vs innovation scoring) and mechanism (agentic search + negative binomial regression vs genetic algorithm + LLM scoring). Verdict: **partially_overlapping** — reposition as "first agentic search for citation-predictive rubric discovery."
- **C2 (Closed-Loop Revision):** Partially overlapping with ARISE in rubric-guided iterative refinement, but differentiated by application (existing paper revision vs new survey generation) and rubric source (discovered vs pre-defined). The integration of discovered rubric + closed-loop revision is novel, though ΔS circularity weakens evidence. Verdict: **partially_overlapping** — reposition with explicit ARISE comparison.
- **C3 (LLM Reviewer Consistency):** Partially overlapping with ReviewerToo and LLM-as-a-Reviewer in LLM review evaluation, but the specific Glicko2-based NeurIPS-replicating experimental design appears novel. Within-model consistency ≠ reliability; cross-family high DR is a concern. Verdict: **partially_overlapping** — lower conclusion strength; explicitly address cross-family DR.

## References
[1] A Hierarchical Framework for Measuring Scientific Paper Innovation via Large Language Models arXiv:2504.14620

[2] ARISE: Agentic Rubric-Guided Iterative Survey Engine for Automated Scholarly Paper Generation arXiv:2511.17689

[3] ParaRev: Building a dataset for Scientific Paragraph Revision annotated with revision instruction arXiv:2501.05222

[4] ReviewerToo: Should AI Join The Program Committee? A Look At The Future of Peer Review arXiv:2510.08867

[5] LLM-as-a-Reviewer: Benchmarking Their Ability, Divergence, and Prompt Injection Resistance as Paper Reviewers arXiv:2605.25415

[6] PRISM: A Multi-Dimensional Benchmark for Evaluating LLM Peer Reviewers arXiv:2605.26730

## Scores
**Final Score: 5.5/10**

评分理由：本文在"评估准则自动发现+闭环论文修订"的集成框架上具有研究价值，大规模数据集和人类评估设计展现了工程严谨性。然而，三个核心实验的效度问题显著拉低了分数：(a) ΔS的循环性（内部有效性）、(b) 零膨胀数据上MAE的适切性未论证（统计有效性）、(c) 科学内容保真度无实证支撑（核心价值主张的证据缺口）。此外，所有三项贡献声明均与检索到的工作存在部分重叠（partially overlapping），限制了新颖性得分。这些缺陷虽然是可修复的（而非致命的），但在当前版本中严重削弱了核心结论的可信度。

评分维度拆解：
- 研究价值（Research Value）：6.0/10 — 问题有意义、框架设计合理，但citation prediction的实用价值受限于12个月窗口和极低平均引用数
- 新颖性（Novelty）：5.5/10 — 三项贡献均 partially overlapping；集成创新有差异化但个体组件非首创
- 有效性/可靠性（Validity/Soundness）：4.5/10 — ΔS循环性、MAE适切性、一致性结论过度外推
- 可复现性（Reproducibility）：6.0/10 — prompts和超参数已公开，但代码未释出，API-based LLM引入非确定性

**Post-Revision Target: [7.0, 7.5]/10**

如果所有P0问题得到充分修复（ΔS重新定位为内部指标、Spearman correlation补充、MAE表述修正、一致性结论校准），并且P1问题得到响应（内容保真度审计、Goodhart's Law自我反思、ARISE差异化讨论），论文的核心可信度和学术严谨性将显著提升。修订后的论文将在7.0-7.5范围内。突破7.5需要更长时间窗口的引用数据或更独立的评估验证，这些属于P2范畴，不纳入当前修订目标区间。
## Summary
# Final Review Report

## Summary

APRES 提出了一个两阶段的智能体框架：(1) 通过 MultiAIDE 搜索自动发现能预测论文未来引用数的评估量规（rubric），使用负二项回归将 LLM 评分映射到 12 个月引用数；(2) 以发现的量规为替代目标函数，通过 diff-based 编辑进行闭循环迭代修订，在不改变科学内容的前提下优化论文的表达质量。在 26,707 篇 ICLR/NeurIPS 论文上的实验表明，发现的量规在引用预测 MAE 上比最佳基线降低了 19.6%，且修订后的论文在盲法人工评估中以 79% 的比例被偏好。

**核心贡献**：将"从数据中学习评估标准"与"以该标准指导自动修订"整合为一个端到端系统，是本文的主要创新。该方法在大规模真实会议数据上的验证（包括复现 NeurIPS 一致性实验）具有说服力。然而，论文存在若干需要修正的问题：新颖性声称需更精确地限定范围、跨模型一致性实验的结论存在过度推断、多处语法和表述错误降低了专业可读性、以及对 Goodhart's Law 风险的讨论缺乏具体缓解路径。总体而言，这是一个扎实且有实际应用价值的工作，但需要在声称精确性、分析深度和文字质量上进行一轮系统修订。

## Strengths
1. **两阶段整合的系统设计**：APRES 将"从数据中发现评估标准"与"以该标准驱动自动修订"整合为统一框架，这一设计在概念上具有创新性。与现有工作（如 Reviewer2、MARG 仅生成评审意见；SWIFT、R3 仅做修订）相比，APRES 是首个将 rubric discovery 与 closed-loop revision 结合的系统，其 Table 1 的比较清晰展示了这一差异化定位。

2. **大规模实证验证**：在 26,707 篇真实会议论文上的实验规模令人印象深刻。人类评估部分尤其值得肯定——364 对论文的盲法 pairwise comparison，评估者均具有 ML 博士学位，p 值 < 10⁻²² 的统计显著性为修订质量提供了强证据。

3. **Appendix A 的一致性实验设计**：复现 NeurIPS 2014/2021 一致性研究的 Appendix A 是本文的重要加分项。使用 Glicko2 评分系统将连续评分转化为二元决策，并构建完整的跨模型 disagreement matrix，这一实验设计严谨且透明。同模型家族内的一致性（~19.5%）确实显著优于人类基准（~23%），为 LLM 评价的可靠性提供了有价值的数据点。

4. **坦诚的局限性讨论**：论文明确承认了 citation 作为 proxy 的局限性（包括 Goodhart's Law）、仅处理文本不处理图表的限制、以及无法完全保证不修改科学内容的风险。Section 5 的 Discussion 在透明度方面可圈可点。

5. **实用的工程选择**：diff-based 编辑方法（基于 Aider 的 search/replace 格式）是一个聪明的实现细节——有效防止了"Rewriter 大幅缩短论文"的问题，同时便于追踪编辑位置和排除实验表格。这一工程实践对其他类似系统有参考价值。

## Weaknesses
### 核心弱点

1. **新颖性声称需要更精确的限定**（Page 1 - Abstract; Page 2 - Introduction P4）。APRES 声称是 "the first method to integrate the discovery of predictive evaluation criteria with a closed-loop system for automated paper revision"（Table 1）。然而，检索发现了高度相关的前置工作：Harada et al. (2025) [1] 提出了迭代量规精化方法（Reflect-and-Revise），LLM 通过反思评分偏差自动改进评估标准；Xu et al. (2026) [2] 提出了 Rubric-ARM，通过交替强化学习同时优化量规生成器和评判器。这些工作的核心机制（自动发现/优化评估标准）与 APRES 的 C1 贡献存在重叠。APRES 的差异化在于 (a) 目标函数是引用预测（非人类评分对齐）和 (b) 将量规用于论文修订（非仅评估）。建议将 "first" 声明限定为 "first to integrate data-driven rubric discovery for citation prediction with automated paper revision"，并在 Related Work 中显式讨论这些前置工作的差异。

2. **跨模型一致性结论过度推断**（Page 17 - Appendix A.2 Results）。正文声称 "LLM-based evaluation can be significantly more consistent than human peer review"，但 Fig. A2 显示，跨模型家族比较中 o3 vs Gemini 2.5 Pro 的不一致率（>35.1%）不仅高于人类基准（23%），甚至超过随机基线。这意味着 LLM 一致性的优势仅在相同模型家族内成立。当前结论掩盖了这一关键 nuance，可能误导读者对 LLM 评审可靠性的理解。必须将结论限定为模型家族内部的一致性，并明确讨论跨模型差异的风险。

3. **实验结果分析缺乏深度解释**（Page 7 - Citation Prediction Results）。"Human scores baseline (MAE ≈ 5.0) 与 Average citation baseline (MAE ≈ 5.3) 几乎相同" 是一个极其反直觉且重要的发现——它意味着人类评审的分数几乎不包含关于论文未来引用数的有效信息。当前文本仅以 "indicating that the raw scores provided by humans are a relatively poor predictor" 一笔带过，未深入探讨可能原因（如：人类评审更关注"当前质量"而非"未来影响力"、评审噪声淹没了预测信号、不同子领域的引用模式差异等）。这一分析缺位降低了论文的学术深度。

4. **Goodhart's Law 讨论缺乏具体缓解策略**（Page 9 - Discussion）。Discussion 正确地指出了 "when a measure becomes a target it ceases to be a good measure" 的风险，但随即以泛泛的 "adaptive approaches" 收尾，未给出针对 APRES 的具体缓解路径。考虑到 APRES 的核心贡献是将 citation 预测作为优化目标，读者有权期望更具体的风险应对策略。

### 次要弱点

5. **多处语法和表述错误**降低了专业可读性。包括：(a) Abstract 中主谓一致错误 "method discovers... and integrate"；(b) "mean averaged error" 非标准术语；(c) "readability of a papers" 及其它多处类似错误；(d) Page 5 搜索框架描述中的 sentence fragment。这些错误在顶会投稿中是不应该出现的。

6. **Introduction 末段（Page 2 - P4）数字重复但无新信息**。Abstract 中已经出现的两个核心数字（19.6% MAE improvement, 79% preference）在 Introduction 末段被重复，但未补充新的解释或上下文。Introduction 末段应聚焦于"这意味着什么"和"未来方向"，而非复制摘要。

7. **Related Work 部分组织结构偏向论文列表**而非按比较轴组织。虽然每个子主题都有独立小标题，但各子节内部仍以论文-摘要-论文-摘要的方式展开，缺少对"APRES 与这些工作在哪些维度上不同"的显式对比。

## Key Issues
### Ranked Error Board (Top 5)

| # | Severity | Research-Value Impact | Validity Risk | Fixability | Confidence |
|---|----------|----------------------|---------------|------------|------------|
| 1 | Major | 中 — 过度声称影响读者对贡献边界的准确判断 | 低 — 可通过措辞修正完全解决 | 高 — 仅需重新措辞 | 高 |
| 2 | Major | 中 — 结论过度推断可能误导后续研究对 LLM 一致性的理解 | 中 — 实验数据本身正确，但解读有误 | 高 — 仅需重新解读 Fig. A2 | 高 |
| 3 | Major | 高 — 缺乏深度分析降低了论文的学术贡献感知 | 低 — 数据已存在，需补充分析 | 中 — 需补充分析段落 | 高 |
| 4 | Minor | 中 — 风险讨论不完整降低方案的实践可信度 | 低 | 高 — 增补具体策略 | 中 |
| 5 | Minor | 低 — 影响专业可读性和第一印象 | 低 | 高 — 逐句修正 | 高 |

### 详细关键问题

**Issue 1 — 新颖性声称需限定**（Page 1 - Abstract; Page 2 - Introduction P4; Table 1）

**证据**：检索发现 Harada et al. (2025) [1] 提出了 Reflect-and-Revise 方法，通过 LLM 反思评分偏差迭代精化量规；Xu et al. (2026) [2] 的 Rubric-ARM 通过交替 RL 联合优化量规生成器和评判器。APRES 的 Table 1 声称是 "the first method to integrate the discovery of predictive evaluation criteria with a closed-loop system for automated paper revision"。

**修复路径**：(a) 将 "first" 声明限定为 "first to integrate data-driven rubric discovery specifically for citation prediction with automated paper revision"；(b) 在 Related Work 中增加对 [1] 和 [2] 的讨论，明确差异维度；(c) 在 Table 1 中将 "Discovers Predictive Criteria" 列的描述从二元标记改为更细致的差异描述。

**Issue 2 — 跨模型一致性结论过度推断**（Page 17 - Appendix A.2）

**证据**：Fig. A2 显示 o3 vs Gemini 2.5 Pro disagreement rate >35.1%，超过随机基线。正文结论 "LLM-based evaluation can be significantly more consistent than human peer review" 未对此进行限定。

**修复路径**：将结论改为 "LLM evaluations from the same model family are more consistent than human peer review; however, cross-model consistency varies substantially, with some model pairs exceeding even random baselines."

**Issue 3 — 人类评分预测力分析缺失**（Page 7 - Results）

**证据**：Human scores baseline MAE (5.0) 几乎等于 Average citation baseline (5.3)，这一发现未被深入分析。

**修复路径**：增加分析段落，讨论潜在原因（评审关注当前质量 vs 未来影响力、噪声、子领域差异等），并讨论其对 "LLM 应模拟人类评审" 这一常见假设的影响。

**Issue 4 — Goodhart's Law 讨论不完整**（Page 9 - Discussion）

**证据**：文本承认风险但未提供具体缓解策略。

**修复路径**：增补 2-3 个具体策略（多目标优化、定期重新训练量规、人工审核闸门）。

**Issue 5 — 多处语法错误**（全篇）

**证据**：Abstract "integrate", "mean averaged error"; Related Work "a papers", "that helps"; Method sentence fragment; 等。

**修复路径**：系统逐段校对。

## Actionable Suggestions
### P0 — 必须修改（影响论文核心声称的有效性）

1. **限定新颖性声称并增补 Related Work 对比**（Page 1 Abstract; Page 2 Introduction P4; Page 3 Related Work; Table 1）
   - 将 "first method to integrate..." 改为 "first to integrate data-driven rubric discovery for citation prediction with automated paper revision"
   - 在 Related Work 中增加对 Harada et al. (2025) [1] 和 Rubric-ARM (Xu et al., 2026) [2] 的讨论
   - 明确差异化维度：(a) APRES 的目标是引用预测（非人类评分对齐），(b) APRES 使用负二项回归处理过离散引用数据，(c) APRES 将量规用于下游论文修订

2. **修正跨模型一致性结论的过度推断**（Page 17 - Appendix A.2）
   - 将 "significantly more consistent than human peer review" 改为 "within the same model family, LLM evaluations are more consistent than human peer review; cross-model consistency varies substantially"
   - 对 Fig. A2 中超过随机基线的异常值进行明确讨论
   - 增加一句话讨论跨模型不一致性对实际部署的影响

### P1 — 强烈建议（显著提升论文深度和质量）

3. **深化"人类评分预测力最差"的分析**（Page 7 - Results）
   - 增加分析段落讨论可能原因：评审关注当前质量而非未来影响力、评审噪声、子领域差异、以及该发现对 "LLM 应模拟人类评审" 假设的哲学意义

4. **为 Goodhart's Law 风险提供具体缓解策略**（Page 9 - Discussion）
   - 增补：(a) 多目标优化（同时优化可读性、事实准确性、评审偏好），(b) 定期重新训练量规适应引用模式变化，(c) 修订后人工审核闸门

5. **重新组织 Related Work 为比较轴驱动结构**（Page 3-4 - Related Work）
   - 按以下轴组织：(a) 评审生成方法，(b) 影响力预测方法，(c) 自动文本修订方法，(d) 量规/评估标准学习方法
   - 每轴末尾显式对比 APRES 的差异

### P2 — 建议改进（提升可读性和专业度）

6. **系统修正语法错误**（全篇）
   - Abstract: "integrate" → "integrates"; "mean averaged error" → "Mean Absolute Error (MAE)"
   - Related Work: "readability of a papers" → "readability of papers"; "writing styles that helps" → "writing styles that help"
   - Method Page 5: 补全 sentence fragment 的谓语动词

7. **重写 Introduction 末段**（Page 2 - P4）
   - 删除重复的数字，聚焦于"这意味着什么"和"未来方向与风险"的讨论

8. **Conclusion 增加有界性声明**（Page 10 - Conclusion）
   - 加入一句总结关键局限性的语句

## Storyline Options + Writing Outlines
### Abstract Outline（完整句子级）

当前 Abstract 存在语法错误、指标模糊和结论无界的问题。推荐修改版已在 PDF 标注 #1（Page 1）中提供。

**推荐 Abstract 结构 (S1-S5):**

- **S1 (Problem + Domain):** "Scientific discoveries must be communicated clearly to realize their full potential. Without effective communication, even groundbreaking findings risk being overlooked."
- **S2 (Gap):** "The primary mechanism for scientific communication—peer review—often provides inconsistent feedback, hindering manuscript improvement."
- **S3 (Method):** "We introduce APRES, an agentic framework powered by Large Language Models (LLMs) that first discovers an evaluation rubric predictive of future citation counts via negative binomial regression, then uses this rubric to guide automated, iterative paper revision without altering core scientific content."
- **S4 (Key Result):** "On a dataset of 26,707 papers from ICLR and NeurIPS, APRES reduces the Mean Absolute Error (MAE) of citation prediction by 19.6% relative to the best baseline, and revised papers are preferred by human expert evaluators 79% of the time."
- **S5 (Bounded Implication):** "These results suggest that LLM-driven tools can help authors improve the clarity and presentation of their manuscripts before submission, while human reviewers remain essential for assessing scientific merit."

### Introduction Outline（段落级蓝图）

**推荐 storyline: "Crisis → Failed Approaches → New Paradigm → Evidence"** 弧线。

- **P1 (Big Picture + Gap):** 同行评审危机 → LLM 作为解决方案的潜力与风险 → "constrained technique" 的需求。关键修改：用具体后果替换 "difficult scenario"，明确 "constrained" 的含义。Mentor Revised Version 已在 PDF 标注 #2 (Page 1)。

- **P2 (Solution + Contribution):** APRES 两阶段框架。关键修改：将核心洞察（"从数据中学习评估标准"）前置，技术细节后置。Mentor Revised Version 已在 PDF 标注 #3 (Page 1)。

- **P3 (Evidence Preview + Roadmap):** 三个实验结果（引用预测、修订质量、一致性）之间的逻辑串联。Mentor Revised Version 已在 PDF 标注 #4 (Page 2)。

- **P4 (Broader Context + Positioning):** 删除重复数字，聚焦于"这意味着什么" + 局限性 + 未来方向。Mentor Revised Version 已在 PDF 标注 #5 (Page 2)。

### Related Work 重组建议

当前按论文列表组织 → 改为按比较轴组织：

1. **LLM-based Review Generation** (Reviewer2, MARG, ReviewRL, TreeReview) → APRES 差异：不仅生成评审，还发现评估标准并驱动修订
2. **Impact Prediction** (DGNI, TNCSI, HLM-Cite, SPECTER, LLM-Metrics [3], LLM-based Citation Prediction [4]) → APRES 差异：使用 agentic search 发现量规，将预测转化为修订指导
3. **Automated Rubric/Evaluation Criteria Discovery** ([1], [2], RubricRAG [5]) → APRES 差异：面向引用预测的训练目标、下游修订闭环
4. **Automated Text Revision** (PEGASUS, SWIFT, R3, ORUGA) → APRES 差异：diff-based 约束编辑、量规驱动的目标函数

### Title 优化建议

当前 title "APRES: An Agentic Paper Revision and Evaluation System" 传达了方法名称和系统类型，但未传达问题域和实际收益。建议采用 Problem-Method-Benefit 模式：

**候选 Title:** "Learning to Evaluate and Revise: An Agentic Framework for Data-Driven Scientific Paper Improvement" 或保留简洁风格 "APRES: Automated Paper Revision via Learned Evaluation Criteria"

## Priority Revision Plan
### 修订优先级矩阵

| Priority | Low Effort (< 1 day) | Medium Effort (1-3 days) | High Effort (1+ week) |
|----------|---------------------|-------------------------|----------------------|
| **P0 - Critical** | 修正语法错误 + 限定新颖性声称 | 修正跨模型一致性结论 | — |
| **P1 - High** | 增加 Related Work 对比 [1][2] | 深化人类评分分析 + Goodhart 缓解策略 | 重组 Related Work 为比较轴结构 |
| **P2 - Medium** | 重写 Introduction 末段 + Conclusion 有界性 | 改进搜索框架可读性 | 增加跨模型校准实验 |

### 详细执行路径

**Stage 1 (Today): P0 + Quick P1**
- 逐段修正语法错误（详见各页 PDF 标注中的 Mentor Revised Version）
- Abstract: "integrate" → "integrates"; "mean averaged error" → "Mean Absolute Error (MAE)"
- Table 1 和正文中限定 "first" 声明范围
- 修正 Appendix A.2 结论措辞

**Stage 2 (This Week): P1 Depth**
- 增补 Related Work 对 [1][2] 的讨论段落
- 在 Results 分析中增加人类评分预测力分析段
- 在 Discussion 中增补 Goodhart's Law 具体缓解策略

**Stage 3 (Before Resubmission): P2 Polish**
- 重组 Related Work 为比较轴结构
- 改进 Page 5 搜索框架描述的可读性
- 整体语言润色

### 预期修订后收益
- 新颖性声称更精确 → 降低被 reviewer 质疑 "not novel" 的风险
- 跨模型一致性结论修正 → 提升科学严谨性
- 分析深度增强 → 提升论文的学术贡献感知
- 语法修正 → 提升专业可读性和第一印象

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|-------|---------|-------------|-----------------|-------------------|
| E1 | Rubric search for citation prediction | MultiAIDE on 26,707 papers; neg. binomial regression; 4 LLMs (o1, o3, Gemini 2.5 Flash/Pro); 200 iter max | MAE | MultiAIDE converges to MAE <2.0 (best: o3 1.92) | C1 — Discovered rubric predicts citations better than baselines | Human scores baseline analysis lacks depth (why MAE ≈ average?) |
| E2 | Paper improvement via rubric-guided revision | Diff-based editing; 120 iter max; Simple Rubric + Embedding PCA baselines | ∆S (rubric score change) | ∆S = 2.98–3.34 for Borderline/Reject papers; Discovered Rubric > baselines | C2 — Rubric-guided revision improves predicted impact | No ground-truth citation validation of revised papers |
| E3 | Human evaluation of revised papers | 364 paper pairs × 3 PhD evaluators; blind pairwise preference | Preference rate; binomial test | 79% preference (95% CI: 70.1–79.0%); p < 10⁻²² | C2/C3 — Human experts prefer revised papers | No analysis of when/why humans preferred originals (12 pairs with 0/3 preference) |
| E4 | Ablation of rubric + search | APRES w/o R*, w/o MultiAIDE, full | ∆S by paper category | Removing either component greatly reduces ∆S | C1+C2 interdependence validated | Small effect still remains without rubric (1.02–1.24), not discussed |
| E5 | Glicko2 rating vs conference decisions | 20,000 pairwise comparisons; LLM judge | Glicko2 rating distribution vs. acceptance outcome | Strong correlation between Glicko2 and conference decisions | C3 — LLM evaluations align with human committees | Only tested on discovered rubric; no comparison with alternative rubrics |
| E6 | LLM reviewer consistency | 4 LLMs; disagreement rate matrix; compare to NeurIPS benchmarks | Disagreement Rate (DR) | Same-family DR 19.5–20.3% < human 23%; cross-family up to >35% | C3 — LLMs can be more consistent than humans | Cross-model inconsistency not adequately discussed |

### Research-Theme Gap Diagnosis

1. **可复现性证据不足**：APRES 声称修订过程 "does not alter core scientific content"，但仅依赖 prompt 约束和表格排除，缺乏定量验证。建议增加 automatic factuality check。
2. **修订效果的外部验证缺失**：∆S 指标是循环验证（使用同一量规评分），缺乏独立的 ground-truth citation 验证来确认修订后论文确实获得了更多引用。
3. **跨模型鲁棒性未被充分探索**：E6 揭示了跨模型不一致性风险，但未提出校准或缓解方案。

### Proposed Research Experiments

| Proposed Exp | Target Claim | Hypothesis | Minimal Design | Controls | Metrics | Success Criterion | Priority |
|-------------|-------------|-----------|----------------|----------|---------|-------------------|----------|
| PE1: Automatic Factuality Verification | "revision preserves scientific content" | LLM-based NLI can detect factual drift between original and revised text | Run an NLI model (e.g., LLM-as-judge) on 100 original-revised sentence pairs | Original text as reference | Factual consistency rate (0-1) | ≥95% of revised sentences are factually consistent | P1 |
| PE2: Cross-Rubric Consistency | "LLM consistency advantage holds across rubrics" | Repeat E5-E6 with Simple Rubric and human conference rubrics | Same LLMs, same papers; compare DR matrices | DR comparison across rubrics | Discovered rubric shows lower DR than alternatives | P2 |
| PE3: Cross-Model Calibration | "Cross-model inconsistency can be mitigated" | Apply calibration technique (e.g., Platt scaling) to align scores across LLMs | Pre- and post-calibration DR comparison | DR reduction; rank correlation preservation | Cross-model DR reduced by ≥30% | P2 |

```text
ASCII Diagram — Experiment Upgrade Plan

Stage 1 (P0, within revision cycle):
  [PE1: Factuality Verification] → validates core safety claim
    └→ Minimal cost: use existing 364 pairs, add NLI pass

Stage 2 (P1, next submission):
  [PE2: Cross-Rubric Consistency] → strengthens C3 novelty
    └→ Medium cost: rerun Glicko2 with alternative rubrics

Stage 3 (P2, future work):
  [PE3: Cross-Model Calibration] → addresses identified weakness
    └→ High cost: requires calibration method development
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|------------------------|---------------------|-----|------------|------------------------|
| C1 | Agentic rubric search discovers evaluation criteria predictive of future citation counts via negative binomial regression | [1] Harada et al. (2025) — iterative rubric refinement via reflect-and-revise; [2] Xu et al. (2026) — Rubric-ARM jointly optimizes rubric generator + judge via RL; [6] Jourdan et al. (2025) — scientific text revision metrics | **partially_overlapping** | [1] and [2] both discover/refine evaluation criteria automatically, overlapping in core mechanism. APRES differentiates via (a) citation prediction objective vs human alignment, (b) negative binomial regression for overdispersed count data, (c) larger scale (26,707 papers). | High | Remove "first method to discover predictive criteria" language; position as "first for citation prediction with downstream revision integration" |
| C2 | Closed-loop automated paper revision using discovered rubric as surrogate objective, with diff-based editing constraints | [7] Goel et al. (2025) — rubric rewards for AI co-scientist training (same lab, overlapping authors); SWIFT (Chamoun et al., 2024); R3 (Du et al., 2022); Dolphin (Yuan et al., 2025) | **partially_overlapping** | Multiple prior systems perform iterative LLM-based revision. APRES differentiates via (a) rubric is discovered (not hand-crafted), (b) surrogate objective is citation-predictive, (c) diff-based editing constraint system. | High | Explicitly distinguish from [7]: APRES revises existing papers while [7] generates research plans; clarify that diff-based constraint is a new engineering contribution |
| C3 | Empirical validation: 19.6% MAE reduction; 79% human preference; LLM consistency > human via Glicko2 replication | [3] PRISM (2026) — LLM reviewer benchmark showing LLMs match/beat humans on individual dimensions but not across all; [4] LLM-REVal (2025) — LLM reviewer biases; [5] Zhu et al. (2025) — LLM rating inflation | **supported** (with caveat) | Large-scale human study (364 pairs, PhD evaluators, p<10⁻²²) is strong. Consistency study design is rigorous. However, cross-model inconsistency caveat (Issue 2) must be addressed. | High | Fix cross-model consistency overclaim; acknowledge [3]'s finding that no single LLM system matches balanced human performance across all dimensions |

### Contribution-level Novelty Conclusion

C1 (`partially_overlapping`): APRES 的 rubric discovery 机制与 [1] 和 [2] 存在核心重叠（自动化评估标准发现），但引用预测目标函数、负二项回归建模和下游修订闭环整合是有效的差异化维度。C2 (`partially_overlapping`): 自动修订本身非新，但与 discovered rubric 的闭环整合（尤其是 diff-based 约束编辑）构成了新的系统贡献。C3 (`supported`): 大规模人类验证和一致性研究设计严谨，证据充分，但跨模型一致性结论需修正。总体而言，APRES 的 **系统整合价值**（rubric discovery → closed-loop revision）大于其单个组件的新颖性。

### (9B) Related-Work Taxonomy Matrix

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)

Scientific Paper Evaluation & Improvement (Root)
├── Branch 1: Automated Review Generation
│   ├── Leaf 1.1: Single-Agent LLM Reviewers
│   │   └── Reviewer2 (Gao et al., 2024), ReviewRobot (Wang et al., 2020)
│   ├── Leaf 1.2: Multi-Agent / Deliberative Reviewers
│   │   └── MARG (D'Arcy et al., 2024), TreeReview (Chang et al., 2025)
│   └── Leaf 1.3: RL-Trained Reviewers
│       └── ReviewRL (Zeng et al., 2025)
│
├── Branch 2: Scientific Impact Prediction
│   ├── Leaf 2.1: Bibliometric/Graph-Based
│   │   └── DGNI (Geng et al., 2022), Abrishami & Aliakbary (2018)
│   ├── Leaf 2.2: Embedding-Based
│   │   └── SPECTER (Cohan et al., 2020), TNCSI_SP (Zhao et al., 2025b)
│   ├── Leaf 2.3: LLM-Based Text Prediction
│   │   └── HLM-Cite (Hao et al., 2024), LLM-Metrics [3], Sun et al. (2025)
│   └── Leaf 2.4: LLM Memory-Based
│       └── LLM-Metrics (Shen et al., 2026) [8]
│
├── Branch 3: Evaluation Criteria Discovery / Learning
│   ├── Leaf 3.1: Iterative Rubric Refinement
│   │   └── Harada et al. (2025) [1] — Reflect-and-Revise for essay scoring
│   ├── Leaf 3.2: RL-Based Rubric + Judge Co-Optimization
│   │   └── Rubric-ARM (Xu et al., 2026) [2]
│   ├── Leaf 3.3: RAG-Based Rubric Generation
│   │   └── RubricRAG (Dhole & Agichtein, 2026) [5]
│   └── Leaf 3.4: Agentic Search for Citation-Predictive Rubric ★APRES★
│
├── Branch 4: Automated Text Revision
│   ├── Leaf 4.1: Summarization-Based Revision
│   │   └── PEGASUS (Zhang et al., 2019)
│   ├── Leaf 4.2: Multi-Agent Revision Feedback
│   │   └── SWIFT (Chamoun et al., 2024), LLM-Collaboration (Jiang et al., 2024)
│   ├── Leaf 4.3: Human-in-the-Loop Revision
│   │   └── R3 (Du et al., 2022)
│   └── Leaf 4.4: Rubric-Guided Iterative Revision ★APRES★
│
└── Branch 5: LLM Reviewer Reliability & Bias
    ├── Leaf 5.1: Consistency Benchmarking
    │   └── PRISM [3], LLM-as-a-Reviewer [4]
    ├── Leaf 5.2: Bias Detection
    │   └── LLM-REVal [4], Zhu et al. (2025) [5]
    └── Leaf 5.3: Prompt Injection Robustness
        └── Collu et al. (2025), Lin et al. (2025)
```

### Taxonomy Table

| Taxonomy Layer | Branch/Leaf | Representative Papers [n] | Common Assumptions | Difference vs APRES | Novelty Risk Signal |
|---------------|-------------|--------------------------|-------------------|---------------------|---------------------|
| Branch 3 / Leaf 3.1 | Iterative Rubric Refinement | [1] | Rubric quality = alignment with human scores; small-scale essay domain | APRES targets citation prediction, uses neg. binomial regression, operates at conference scale | HIGH — closest mechanism overlap |
| Branch 3 / Leaf 3.2 | RL-Based Rubric Co-Optimization | [2] | Joint optimization of rubric + judge via alternating RL | APRES rubric is discovered for downstream revision, not just better judging | MEDIUM — complementary objective |
| Branch 2 / Leaf 2.3 | LLM-Based Citation Prediction | HLM-Cite, TNCSI_SP | Text features predict citations; static models | APRES discovers rubric interactively via agentic search | LOW — different approach to same goal |
| Branch 4 / Leaf 4.2-4.3 | Multi-Agent / HITL Revision | SWIFT, R3 | Revision guided by human feedback or generic quality prompts | APRES guided by discovered, citation-predictive rubric | LOW — revision mechanism is distinct |
| Branch 5 / Leaf 5.1 | LLM Reviewer Consistency | [3] | Multi-dimensional benchmarking of LLM reviewer quality | APRES directly measures accept/reject disagreement rate vs NeurIPS baselines | LOW — complementary evaluation |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|----------|----------------|-------------|------------------------|-----------------|--------------------------|
| [1] Harada et al. (2025) | Automated essay scoring rubric refinement | LLM reflect-and-revise iterative rubric update | Iterative rubric discovery/refinement | (a) Essay scoring vs paper citation prediction; (b) human alignment vs citation prediction objective | Requires narrowing C1 novelty claim; adds credibility to rubric discovery approach |
| [2] Xu et al. (2026) | Rubric-based reward modeling for LLM training | Alternating RL for rubric + judge co-optimization | Joint optimization of rubric and evaluator | (a) LLM training vs paper revision end-use; (b) preference-based vs citation-based objective | Similar mechanism, different application; strengthens case for rubric learning as general technique |
| [3] PRISM (2026) | LLM reviewer quality benchmarking | Multi-dimensional evaluation (depth, novelty, flaws, constructiveness) | LLM review consistency evaluation | (a) PRISM evaluates review quality dimensions; APRES measures accept/reject consistency; (b) PRISM finds LLMs can't match humans across all dimensions | Validates APRES's consistency findings but adds nuance — LLM superiority is dimension-specific |
| [4] LLM-REVal (2025) | LLM reviewer bias detection | Simulation-based bias analysis (LLM-authored vs human-authored papers) | LLM review reliability assessment | LLM-REVal focuses on bias (LLMs favor LLM-written papers); APRES focuses on consistency | Complements APRES — highlights bias risks not addressed in current manuscript |

### Page Coverage Audit

| Page | Annotation Count | Coverage Status | Skip Reason (if skipped) |
|------|-----------------|-----------------|--------------------------|
| 1 | 3 (Abstract, Intro P1, Intro P2) | Covered | — |
| 2 | 2 (Intro P3, Intro P4) | Covered | — |
| 3 | 1 (Related Work Readability) | Covered | — |
| 4 | 0 | Skipped | Boilerplate transition + Fig 1 description; non-substantive |
| 5 | 1 (Search Scaffold) | Covered | — |
| 6 | 0 | Skipped | Implementation details mostly factual; Dataset paragraph covered in Weakness analysis |
| 7 | 1 (Results Analysis) | Covered | — |
| 8 | 0 | Skipped | Mostly descriptive results interpretation |
| 9 | 1 (Discussion) | Covered | — |
| 10 | 2 (Limitations, Conclusion) | Covered | — |
| 17 | 1 (Appendix A.2) | Covered | — |

## References
[1] Automated Refinement of Essay Scoring Rubrics for Language Models via Reflect-and-Revise 2510.09030

[2] Alternating Reinforcement Learning for Rubric-Based Reward Modeling in Non-Verifiable LLM Post-Training 2602.01511

[3] PRISM: A Multi-Dimensional Benchmark for Evaluating LLM Peer Reviewers 2605.26730

[4] LLM-REVal: Can We Trust LLM Reviewers Yet? 2510.12367

[5] When Your Reviewer is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer Review 2509.09912

[6] Identifying Reliable Evaluation Metrics for Scientific Text Revision 2506.04772

[7] Training AI Co-Scientists Using Rubric Rewards 2512.23707

[8] MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research 2505.19955

## Scores
**Final Score: 6.5/10**

打分依据（以研究价值和新颖性为主要维度）：
- **研究价值 (7/10):** 将"从数据中学习评估标准"与"以该标准驱动自动修订"整合为端到端系统具有实用价值，大规模真实会议数据验证增强了可信度。但核心机制的增量性质限制了其变革性潜力。
- **新颖性 (5.5/10):** C1 和 C2 均与前置工作 [1][2] 存在核心机制重叠（partially_overlapping），系统整合是主要差异化贡献。C3 的实证验证扎实但非方法性新颖。
- **有效性 (7/10):** 实验设计严谨、规模大、统计显著。但跨模型一致性结论存在过度推断，人类评分分析缺乏深度。
- **可复现性 (7/10):** 数据源公开、prompts 已附录、承诺开源代码。但缺乏自动事实性验证实验，修订后的科学完整性仅依赖 prompt 约束。

**Post-Revision Target: [7.5, 8.5]/10**

若所有 P0 和 P1 问题被全面解决（限定新颖性声称、修正跨模型一致性结论、深化人类评分分析、增补 Goodhart 缓解策略、重组 Related Work、修正语法），论文的学术贡献感知和严谨性将显著提升，达到强 accept 水平。上限不超过 8.5 是因为核心机制的新颖性窗口已被前置工作 [1][2] 部分占据。

---

**Final Verdict:** 这是一个扎实且实用价值明确的工作，系统整合思路清晰，大规模验证令人信服。但当前版本在新颖性声称精度、结论谨慎性和分析深度方面存在可修正的缺陷。建议给予修改机会，重点关注 P0 级别的声称限定和 P1 级别的分析深化。修订后的论文有望成为 AI-assisted peer review 领域的有影响力的贡献。
## Summary
# Final Review Report

## Summary

APRES 提出了一个两阶段的 LLM 智能体框架：(1) 通过 MultiAIDE 搜索发现能预测论文未来引用数的评审量规（rubric），(2) 将该量规作为目标函数，驱动闭环式论文文本修改。在 26,707 篇 ICLR/NeurIPS 论文上的实验显示，APRES 的引用预测 MAE 相比最强基线降低 19.6%，且 AI 修改后的论文在盲法人类评估中获得 79% 的偏好率。附录进一步展示了 LLM 评审在 Glicko2 一致性实验中比人类评审委员会更稳定。

**总体评价**：这是一个设计精良、实验扎实的系统性工作。两阶段架构（量规发现→量规驱动修改）概念清晰，大规模实验和人类评估提供了有说服力的实证支撑。然而，论文存在若干需要修正的问题：(1) 核心新颖性声明需要与共享作者的前期工作区分；(2) 实验设计存在循环评估风险（同一量规同时用于优化和评估）；(3) 多处存在过度声称和术语不精确的问题；(4) 一致性实验的结论被过度推广。这些问题不致命但需要在修改中认真处理。论文的研究价值主要体现在为"AI 辅助论文写作"提供了一个可量化、数据驱动的新范式，其量规发现方法本身也具有独立的方法论价值。

## Strengths
1. **问题重要且及时**：论文聚焦于"如何利用 LLM 帮助作者改进论文质量"这一高度相关的问题。随着 AI 会议投稿量激增和 LLM 能力提升，该研究方向具有明确的现实意义和紧迫性。论文清晰地定位 APRES 为"增强而非替代"人类评审的工具，立场审慎。

2. **两阶段架构设计巧妙**：Stage 1 的量规发现（agentic search + negative binomial regression）和 Stage 2 的量规驱动修改（closed-loop revision）形成了完整的 pipeline。特别是"先发现什么是好的，再据此优化"的设计范式，比直接使用固定量规或人工标准更具一般性和自适应性。

3. **实验规模令人印象深刻**：26,707 篇论文的数据集、4 个会议（ICLR 2024/2025, NeurIPS 2023/2024）、4 种前沿 LLM（o1, o3, Gemini 2.5 Flash/Pro）的对比、200 步搜索迭代、364 对论文的盲法人类评估——实验设计的规模和深度在该领域属于领先水平。

4. **人类评估具有说服力**：364 对论文 × 3 人盲法评估、79% 偏好率、二项检验 p < 10⁻²²、95% CI [70.1%, 79.0%]——这组数据为 APRES 的实用性提供了强有力的外部验证。词云分析（Fig. 3）也诚实地反映了修改效果主要集中在写作清晰度层面。

5. **附录一致性实验是重要贡献**：复现 NeurIPS 一致性实验设计，使用 Glicko2 评分系统 + 分歧率矩阵，系统性地展示了 LLM 评估的稳定性。Fig. A1 中 Glicko2 评分与会议决策的相关性也验证了 LLM 评审的有效性。

6. **工程实现细节完善**：diff-based editing（使用 Aider 格式）、prompt 级别的表格保护、SciPDF parser 的使用、超参数搜索的透明报告——这些工程细节表明作者认真考虑了系统的可用性和可靠性。

7. **伦理和限制讨论坦诚**：论文包含完整的 Ethics Statement，明确讨论了 citation bias、Goodhart's Law、adversarial attacks、figures 处理缺失等限制，体现了负责任的科研态度。

## Weaknesses
### W1. 新颖性声明需限定范围（Major）

APRES 声称是"novel agentic framework"，但共享作者（Yoram Bachrach, Chenxi Whitehouse）的近期工作 "Training AI Co-Scientists Using Rubric Rewards" [1] 已探索了从科学论文中自动提取评分量规并用其作为训练奖励信号的方法。该工作聚焦于研究计划生成而非论文修改，但其"rubric extraction + rubric-as-objective"核心范式与 APRES 高度重叠。论文需要在 Introduction 和 Related Work 中明确讨论这一关系，并限定"novel"声明的范围——APRES 的新颖性应定位于"将量规发现与闭环论文修改首次结合"，而非"量规发现本身"。

### W2. 实验设计的循环评估风险（Major）

论文改进实验（Section 4.2）使用 Stage 1 发现的量规 R* 同时作为：(a) 指导 Rewriter 修改的目标函数，和 (b) 评估修改效果（∆S）的度量标准。这构成了循环评估——Rewriter 被优化以最大化 R* 的分数，然后用相同的 R* 来"验证"改进。虽然人类评估（79% 偏好率）部分缓解了这一担忧，但 ∆S 作为自动化指标可能被高估。论文未在 Limitations 中讨论这一风险。

### W3. 术语使用和数值表述不精确（Major）

多处关键术语和数值表述存在问题：(a) 摘要中"mean averaged error"应为"mean absolute error (MAE)"；(b) "19.6% improvement in MAE"表述模糊——MAE 降低才是改进，应明确为"relative reduction"；(c) 多处使用"a more reliable and data-driven processes"（语法错误）；(d) "reduce the inherent randomness of peer review"缺乏证据支持。

### W4. 一致性实验结论过度推广（Major）

Appendix A.2 的一致性实验发现跨模型族比较中 o3 vs Gemini 2.5 Pro 的分歧率 >35.1%，差于随机基线（35.1%），但论文仍概括性地声称"LLM-based evaluation can be significantly more consistent than human peer review"。此外，评估一致性 ≠ 修改可靠性，论文将两者混为一谈（"validating APRES is reliable for providing meaningful revisions"）。

### W5. 基线比较不够公平（Minor）

MLP on paper embedding 基线使用 ℓ₂ loss，而 APRES 使用 negative binomial regression——两者使用不同的损失函数族。SPECTER 基线应使用相同的负二项回归以确保公平对比。此外，SPECTER (2020) 已非最新论文嵌入模型。

### W6. 方法实现细节不足（Minor）

搜索框架的关键细节未说明：初始量规的来源和内容、debug 机制的具体工作方式、LLM 评分的一致性保障措施、搜索的计算成本（API 调用次数量级）。这些信息影响可重复性。

### W7. 人类评估缺少校准基线（Minor）

79% 偏好率缺乏参照系——如果让评估者比较"原始论文 vs 人工润色后的论文"，偏好率会是多少？缺少人类编辑对照组使得难以校准 AI 修改效果的实际意义。

### W8. Discussion 组织可优化（Minor）

"Reviews and Verifiable Reproducibility"段落与 APRES 核心贡献的连接薄弱，打断了 Discussion 的逻辑流。Goodhart's Law 讨论未闭合到 APRES 的自反性风险。

## Key Issues
```text
ASCII Diagram — Paper Structure & Evidence Map

[Claim C1: Agentic rubric discovery predicts citations better than baselines]
    ├── Evidence: Fig. 2 (MAE comparison), 4 LLMs tested, 200-step search
    ├── Gap: Baseline loss-function mismatch; SPECTER is outdated (2020)
    ├── Risk: 19.6% claim may change with fairer baselines
    └── Fix: Equalize loss function; add SPECTER2 baseline

[Claim C2: Rubric-driven revision improves paper quality]
    ├── Evidence: Fig. 4 (∆S scores), Tab. 3 (human eval 79%), Tab. 4 (ablation)
    ├── Gap: Circular evaluation (same rubric for optimize + evaluate)
    ├── Risk: Automated ∆S may be inflated; unclear how much is "real" gain
    └── Fix: Cross-rubric validation; add human-edit control group

[Claim C3: LLM evaluation is more consistent than human review]
    ├── Evidence: Fig. A1 (Glicko2 correlation), Fig. A2 (disagreement matrix)
    ├── Gap: Cross-model disagreement > random for some pairs; conflates "consistency" with "revision quality"
    ├── Risk: Overclaim about LLM reliability in real review settings
    └── Fix: Bound claim to "same-model" consistency; separate evaluation vs revision claims

[Writing Quality]
    ├── Abstract: MAE terminology error; over-long
    ├── Introduction: Gap articulation vague; "novel" not properly qualified
    ├── Discussion: Goodhart's Law discussion incomplete; disconnected paragraph
    └── Conclusion: Missing limitation summary; over-optimistic framing
```

### Ranked Top-5 Core Defect Board

| # | Defect | Severity | Research-Value Impact | Validity Risk | Fixability | Confidence |
|---|--------|----------|----------------------|---------------|------------|------------|
| 1 | 新颖性声明未涵盖共享作者前作 [1] | Major | 中：减弱贡献原创性 | 低：不影响实验有效性 | 高：添加讨论+限定声明 | 高 |
| 2 | 循环评估风险（R* 同时用于优化和评估） | Major | 中：自动化指标可能高估效果 | 中：∆S 可能膨胀 | 高：交叉量规验证 | 高 |
| 3 | MAE 术语错误 + 19.6% 表述模糊 | Major | 低：不影响实质贡献 | 低：数值本身没问题 | 高：修改措辞 | 高 |
| 4 | 一致性实验结论过度推广（>35%分歧率） | Major | 中：削弱可靠性声明 | 中：跨模型不一致性未充分讨论 | 高：限定结论范围 | 高 |
| 5 | 基线比较不公平（ℓ₂ loss vs NB regression） | Minor | 低：APRES 仍可能领先 | 低：核心结论方向不变 | 中：需要重新实验 | 中 |

## Actionable Suggestions
### S1. 限定新颖性声明并补充讨论 [1]（Must, P0）

在 Introduction (Page 1) 将"novel agentic framework"替换为更精确的表述，例如 "APRES extends rubric-based optimization to automated paper revision"。在 Related Work (Page 2-3) 新增一段，明确讨论 APRES 与 "Training AI Co-Scientists Using Rubric Rewards" [1] 的关系：

> "A closely related line of work extracts goal-specific grading rubrics from scientific papers and uses them as reward signals for LLM training [1]. While that work focuses on research plan generation via reinforcement learning, APRES instead uses agentic search to discover a citation-predictive rubric and applies it to iterative paper revision. The two approaches share the paradigm of using rubrics as optimization objectives but differ fundamentally in their target task (plan generation vs. text revision), search mechanism (RL training vs. agentic tree search), and evaluation (expert preference vs. citation prediction + human preference)."

### S2. 修复 MAE 术语和数值表述（Must, P0）

- 摘要和正文中所有"mean averaged error"改为"mean absolute error (MAE)"
- "19.6% improvement in MAE"改为"19.6% relative reduction in MAE"
- 添加具体数值："APRES achieves MAE of X (vs. baseline MAE of Y), a 19.6% relative reduction"

### S3. 讨论并缓解循环评估风险（Must, P0）

在 Section 4.2 或 Limitations 中增加以下讨论：
> "A methodological note: the rubric R* used to guide revision in Stage 2 is the same rubric used to compute ∆S. This creates a potential for inflated automated scores, as the Rewriter is directly optimizing for the evaluation metric. We view the human evaluation (79% preference, blind) as the primary validation of revision quality, and the ∆S metric as a useful but potentially optimistic signal. Future work should validate revisions using a held-out rubric not used during optimization."

### S4. 修正一致性实验的结论表述（Must, P0）

在 Appendix A.2 Results 中将：
> "LLM-based evaluation can be significantly more consistent than human peer review"

改为：
> "When using the same underlying LLM, evaluation decisions are more consistent than human committees (within-model disagreement 19-20% vs. human 23-26%). However, cross-model consistency varies substantially—in some cases exceeding random baselines—indicating that the choice of LLM significantly affects evaluation outcomes. This consistency supports the use of LLM evaluation as a stable signal for rubric discovery, but does not independently validate the quality of APRES-generated revisions."

### S5. 改进基线公平性（Nice-to-have, P1）

- 将 SPECTER 基线的 ℓ₂ loss 替换为 negative binomial regression，确保与 APRES 使用相同的损失函数
- 考虑添加强度更高的基线：SPECTER2 嵌入 + negative binomial regression

### S6. 补充方法实现细节（Nice-to-have, P1）

在 Section 4.1 Implementation Details 中增加：
- 初始量规的内容或生成方式
- 负二项回归超参数搜索空间
- LLM 评分的一致性保障（单次评分 vs 多次平均）
- 搜索计算成本的粗略估计

### S7. 增加人类编辑对照组讨论（Nice-to-have, P2）

在 Section 4.2 或 Discussion 中讨论：79% 偏好率相对于"人类编辑基准"的意义。即使无法运行完整的人类编辑对照实验，也可以在 Discussion 中提供定性分析或引用已有文献中的相关数据。

### S8. 重写 Abstract 和 Conclusion（Nice-to-have, P1）

Abstract 和 Conclusion 的具体修订版本见各对应 PDF 注释中的 Mentor Revised Version。

## Storyline Options + Writing Outlines
### 当前叙事结构诊断

当前 Introduction 的叙事链为：Peer review 压力 → LLM 风险 → APRES 方法 → 贡献预览 → 实证结果 → 立场声明。主要问题：(1) 研究差距（Gap）表述模糊——"LLMs 可能修改科学声明"更像是风险约束而非研究差距；(2) 贡献声明段落使用了未限定的"novel"；(3) 结果预览和立场声明混合在结尾段落中。

### 推荐的修订叙事线：问题 → 差距 → 方案 → 证据

**P1 (Problem & Motivation)：** 同行评审面临规模危机（投稿量远超评审人增长）→ 作者（尤其非母语者）缺乏及时、高质量的反馈 → LLM 提供可扩展反馈但现有方法缺少可量化的优化目标。

**P2 (Gap & Solution Preview)：** 现有 LLM 评审/修改系统要么模仿人工标准，要么优化表面可读性，缺少一个关键要素——与论文未来影响力对齐的量化信号。APRES 的核心洞察：先通过 agentic search 发现什么样的论文特征能预测引用数，再用这个量规作为目标函数来指导修改。

**P3 (Contribution Statement)：** 明确陈述三个贡献：(1) 量规发现——MultiAIDE + negative binomial regression，发现的量规比人工评分和论文嵌入更好地预测引用；(2) 量规驱动的闭环修改——使用发现的量规作为 surrogate objective，diff-based 编辑，保持科学内容不变；(3) 大规模验证——26,707 篇论文实验、4 种 LLM、盲法人类评估、NeurIPS 一致性实验复现。

**P4 (Evidence Preview & Positioning)：** 简要预告关键结果（MAE 降低 19.6%、人类偏好率 79%、LLM 评估比人类更一致），明确立场：不主张替代人类评审，而是提供预提交辅助工具。

### Abstract Outline（完整 5 句结构）

- **S1 (问题/领域)：** Scientific peer review struggles with scale and inconsistency, limiting authors' ability to improve their manuscripts before submission.
- **S2 (差距)：** While LLMs offer scalable feedback, existing systems lack a quantitative signal of paper quality aligned with future impact to guide meaningful revision.
- **S3 (方法)：** We introduce APRES, a two-stage framework that (1) discovers a citation-predictive review rubric through agentic search and negative binomial regression, and (2) uses this rubric as an objective function for iterative, constrained paper revision that preserves scientific content.
- **S4 (关键结果)：** On 26,707 ICLR and NeurIPS papers, APRES achieves a 19.6% relative MAE reduction in citation prediction, and APRES-revised papers are preferred over originals by 79% in blind human evaluation (N=364 pairs, p<10⁻²²).
- **S5 (意义/边界)：** These results demonstrate that rubric-driven LLM revision can serve as an effective pre-submission tool for improving scientific communication, complementing rather than replacing human peer review.

### Introduction Outline（逐段计划）

**P1 — Problem Setup (Page 1, line 8)：**
- 角色：建立问题紧迫性
- 核心断言：Peer review under strain → authors lack timely feedback
- 证据锚：Kim et al. 2025, Chen et al. 2025a
- 过渡逻辑：从"评审系统压力"引出"作者需要工具"

**P2 — Gap Identification：**
- 角色：明确研究差距
- 核心断言：现有 LLM 评审缺少与影响力对齐的量化信号；朴素 LLM 修改有风险
- 证据锚：Ye et al. 2024, Lin et al. 2025
- 过渡逻辑：从"缺少信号+修改风险"引出"APRES 两阶段方案"

**P3 — Solution Preview + Contribution (Page 1, line 9)：**
- 角色：介绍 APRES + 明确贡献
- 核心断言：两阶段架构（量规发现→量规驱动修改），三项贡献
- 证据锚：Jiang et al. 2025, Zhao et al. 2025a, Lawless 1987
- 过渡逻辑：从"APRES 设计"引出"如何验证"

**P4 — Evidence Preview + Positioning (Page 2, lines 1-2)：**
- 角色：预告实验结果 + 明确立场
- 核心断言：MAE 降低 19.6%、人类偏好 79%、LLM 更一致；不替代人类
- 证据锚：Cortes & Lawrence 2021, Beygelzimer et al. 2023, AAAI 2026, Thakkar et al. 2025
- 过渡逻辑：从"结果预告"引出"相关工作"

```text
ASCII Diagram — Revision Strategy Roadmap

[Novelty Claim Qualification (P0)]
    → Discuss rubric-extraction prior work [1] in Related Work
    → Replace "novel" with "extends" in contribution paragraph
    → Expected: Credible positioning, no overclaim

[Circular Evaluation Fix (P0)]
    → Add cross-rubric validation discussion in Limitations
    → Add note on ∆S potential inflation
    → Expected: Transparent methodology, reviewer confidence

[MAE Terminology + Consistency Claim Fix (P0)]
    → "mean averaged error" → "mean absolute error (MAE)"
    → Bound consistency claim to same-model comparisons
    → Expected: Factual precision, no misleading statements

[Baseline Fairness (P1)]
    → Equalize loss function (NB regression for all baselines)
    → Add SPECTER2 baseline
    → Expected: Stronger empirical foundation

[Writing Polish (P1)]
    → Rewrite Abstract + Conclusion per Mentor Revised Versions
    → Reorganize Discussion flow
    → Expected: Improved readability and narrative coherence
```

## Priority Revision Plan
| Priority | Task | Effort | Impact | Section(s) Affected | Acceptance Criteria |
|----------|------|--------|--------|---------------------|---------------------|
| **P0** | 限定新颖性声明 + 讨论 [1] | 低（1-2h writing） | 高 | Introduction P2, Related Work | "novel"替换为限定表述；Related Work 新增段落讨论 [1] |
| **P0** | 修复 MAE 术语和 19.6% 表述 | 低（30min） | 高 | Abstract, Introduction P3, Section 4.1 | "mean averaged error" → "mean absolute error"；添加相对降低计算说明 |
| **P0** | 讨论循环评估风险 | 低（1h writing） | 高 | Section 4.2, Limitations | 新增交叉验证讨论段落；明确 ∆S 的潜在膨胀 |
| **P0** | 修正一致性实验结论 | 低（30min） | 高 | Appendix A.2 | 限定为"同模型一致性"；分离评估一致性 vs 修改可靠性声明 |
| **P1** | 重写 Abstract | 中（2h） | 中 | Abstract | 5 句紧凑结构；修正术语；增加方法描述；去除结尾立场声明 |
| **P1** | 重写 Conclusion | 低（1h） | 中 | Conclusion | 增加限制总结；替换"faster, safer, more impactful" |
| **P1** | 统一基线损失函数 | 中（需要重新实验） | 中 | Section 4.1 | SPECTER 基线使用 NB regression；可选 SPECTER2 |
| **P1** | 补充方法实现细节 | 低（1h writing） | 低 | Section 4.1 | 初始量规来源、debug 机制、评分一致性说明 |
| **P2** | 增加人类编辑对照组讨论 | 低（30min） | 低 | Section 4.2, Discussion | 定性讨论 79% 偏好率的校准意义 |
| **P2** | 重构 Discussion 段落组织 | 低（1h） | 低 | Discussion | 移动"Verifiable Reproducibility"段落或与 Limitations 合并 |
| **P2** | 闭合 Goodhart's Law 讨论 | 低（30min） | 低 | Discussion | 增加自反性风险和缓解策略的具体讨论 |

### Page Coverage Audit

| Page | Section | Annotation Count | Coverage Status |
|------|---------|-----------------|-----------------|
| 1 | Abstract + Introduction P1-P2 | 4 | Covered ✓ |
| 2 | Introduction P3 + Related Work | 2 | Covered ✓ |
| 3 | Related Work (continued) | 0 | Skipped — non-substantive (paper-by-paper listing) |
| 4 | Method intro + 3.1 start | 0 | Covered by annotation on page 5 |
| 5 | Method 3.1-3.2 | 1 | Covered ✓ |
| 6 | Experiments 4.1 | 1 | Covered ✓ |
| 7 | Experiments 4.2 setup | 0 | Covered by annotation on page 6 (spans method) |
| 8 | Paper Improvement Results | 0 | Covered by annotation on page 6 (cross-cutting issue) |
| 9 | Human Eval + Discussion | 2 | Covered ✓ |
| 10 | Discussion + Limitations + Conclusion | 2 | Covered ✓ |
| 11 | Ethics Statement | 0 | Skipped — boilerplate |
| 12-15 | References | 0 | Skipped — non-substantive |
| 16-17 | Appendix A (Glicko2 + Consistency) | 1 | Covered ✓ |
| 18+ | Appendix B-H (Prompts, Rubric, etc.) | 0 | Skipped — supplementary materials |

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective / Hypothesis | Setup | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|----------------------|-------|---------|-------------|-----------------|-------------------|
| E1 | Rubric search discovers citation-predictive criteria | 26,707 papers; MultiAIDE; NB regression; 4 LLMs | MAE vs baselines | MAE <2.0 for best models; 19.6% relative reduction | C1: Rubric discovery outperforms existing methods | Baseline loss-function mismatch; SPECTER outdated |
| E2 | Discovered rubric drives paper improvement | Test set; Diff-based editing; 120 iterations | ∆S (rubric score change) | ∆S = 3.33 (borderline, o3); improvement across all categories | C2: Revision improves predicted impact | Circular evaluation (same rubric for optimize + evaluate) |
| E3 | Human evaluation of revised papers | 364 pairs × 3 evaluators; blind pairwise preference | Preference rate; binomial test | 79% preference; p<10⁻²²; 95% CI [70.1%, 79.0%] | C2: Human-validated improvement | No human-edit control group; edit magnitude not analyzed |
| E4 | Ablation of rubric and search | w/o R*, w/o MultiAIDE vs full APRES | ∆S by paper category | Full APRES substantially better (e.g., 3.33 vs 1.24 for borderline) | C2: Both components contribute | Ablation only on automated metric, not human eval |
| E5 | Glicko2 rating vs conference decisions | 20,000 pairwise comparisons; LLM judge | Rating-decision correlation | Strong positive correlation (Fig. A1) | C3: LLM ratings align with human committees | Pairwise comparison is simpler than real review |
| E6 | LLM reviewer consistency | 4 LLMs; disagreement rate matrix; Glicko2 + thresholding | Disagreement rate vs human baselines (23-26%) | Within-model ~19-20%; cross-model up to >35% | C3: LLMs can be more consistent | Cross-model inconsistency not adequately discussed |

### Research-Theme Gap Diagnosis

| Research Value Claim | Evidence Strength | Gap |
|---------------------|-------------------|-----|
| New knowledge: agentic rubric discovery predicts citations | Moderate (E1) | Baseline fairness issues weaken confidence in 19.6% margin |
| Reproducibility: method can be replicated | Moderate | Missing details: initial rubric, debug mechanism, scoring consistency, compute cost |
| Impact on practice: authors can improve papers pre-submission | Moderate-Strong (E3) | No calibration against human editing; unclear if 79% preference reflects meaningful quality gain |
| LLM evaluation consistency > human | Mixed (E6) | Overclaimed; cross-model results contradict generalization |

### Proposed Research Experiments

| ID | Target Claim | Hypothesis | Minimal Design | Controls/Baselines | Metrics | Success Criterion | Priority | Est. Cost |
|----|-------------|-----------|----------------|-------------------|---------|-------------------|----------|-----------|
| PE1 | C1: Rubric discovery margin | Equalizing loss function reduces but doesn't eliminate APRES advantage | Rerun SPECTER baselines with NB regression (same as APRES) | MLP+NB, PCA+NB, Prompt breeder | MAE, relative reduction | APRES MAE still lowest; margin may shrink to 10-15% | P1 | Medium (re-running experiments) |
| PE2 | C2: Cross-rubric validation | Using a different rubric for evaluation reduces but doesn't eliminate ∆S | Evaluate revisions with Simple Rubric instead of R* | R* evaluation vs Simple Rubric evaluation | ∆S (cross-rubric), human preference correlation | Cross-rubric ∆S > 0 and positively correlated with human preference | P1 | Low (re-analysis) |
| PE3 | C3: Edit magnitude analysis | Larger edits drive more preference, but even small edits are preferred | Categorize edits by character-level change ratio; correlate with preference rate | Low/medium/high edit groups | Preference rate per group | All groups show preference >50%; dose-response relationship | P2 | Low (analysis only) |
| PE4 | Generalization: non-ML domains | Rubric discovery works across disciplines | Run Stage 1 on papers from biology/medicine (PubMed) | ML domain vs bio/med domain | MAE by domain | MAE better than baselines in new domain | P2 | High (data collection + experiments) |

```text
ASCII Diagram — Experiment Upgrade Plan

Stage 1 (P0, today, no experiments):
    └── Fix terminology, add limitation discussions, qualify claims
    └── Expected: Cleaner manuscript with honest limitations

Stage 2 (P1, this week, re-analysis):
    ├── PE2: Cross-rubric validation (re-analysis of existing data)
    │   └── Expected: Evidence that ∆S is not purely circular
    ├── PE1: Equalize baseline loss function (re-run experiment)
    │   └── Expected: Fairer comparison, potentially smaller but still significant margin
    └── PE3: Edit magnitude analysis (re-analysis)
        └── Expected: Nuanced understanding of what drives preference

Stage 3 (P2, before next submission, new experiments):
    └── PE4: Cross-domain generalization
        └── Expected: Evidence that rubric discovery generalizes beyond ML
```

## Novelty Verification & Related-Work Matrix
### 9A. Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict | Why | Confidence | Required Repositioning |
|----------|--------------------------|--------------------|-----------------|-----|------------|------------------------|
| C1 | Agentic search (MultiAIDE) discovers a rubric that predicts citation counts better than human scores and embedding baselines | [1] (shared authors, rubric extraction for plan generation), [3] (citation prediction more viable than review score prediction), [4] (AIDE search framework) | **partially_overlapping** | [1] shares the rubric-as-objective paradigm and overlapping authors; [4] provides the underlying search framework (MultiAIDE extends AIDE). However, APRES is the first to apply agentic search specifically to discover citation-predictive review rubrics, and the integration with NB regression for the review domain is novel. | High | Qualify "novel" to "extends prior rubric optimization work to citation-predictive review rubric discovery"; explicitly distinguish from [1] on task (paper revision vs. plan generation) and search mechanism (agentic tree search vs. RL training). |
| C2 | Discovered rubric R* drives closed-loop paper revision that improves predicted impact and is preferred by humans 79% of the time | [1] (rubric-driven optimization in different task), SWIFT, R3, PEGASUS (prior revision systems without discovered rubrics) | **partially_overlapping** | The closed-loop revision mechanism (LLM Reviewer → Rewriter → Select & Refine) using diff-based editing has precedents (SWIFT, R3) but the key novelty is using an automatically discovered citation-predictive rubric as the objective rather than fixed heuristics. [1] uses rubrics as rewards but for plan generation, not text revision. | High | The rubric-driven aspect is novel; the revision mechanism itself is incremental. Frame contribution as "first to integrate discovered citation-predictive rubrics with automated paper revision." |
| C3 | LLM evaluation using APRES rubric is more consistent than human peer review (Glicko2 + disagreement rate) | [2] (PRISM: LLM reviewers match humans on dimensions but have blind spots), [6] (LLM evaluator consistency is decoupled from performance) | **partially_overlapping** | The Glicko2-based consistency experiment design is well-executed, but: (a) [2] independently benchmarks LLM reviewers and finds dimension-specific blind spots; (b) [6] shows strong models are not necessarily consistent evaluators. APRES's within-model consistency result (~19-20%) is credible but cross-model inconsistency (>35% for some pairs) means the generalization claim is overstated. | High | Bound consistency claim to within-model comparisons; acknowledge that cross-model inconsistency > random baseline limits generalization; separate evaluation consistency from revision quality claims. |

### 9B. Related-Work Taxonomy Matrix

```text
Related Work Taxonomy (Root: LLM-based Scientific Paper Evaluation & Revision)
├── Branch 1: Automated Review Generation
│   ├── Leaf 1.1: Template/Extraction-based [ReviewRobot, Yuan et al. 2022]
│   ├── Leaf 1.2: LLM Prompt-based [Reviewer2 (Gao et al. 2024), MARG (D'Arcy et al. 2024), TreeReview (Chang et al. 2025)]
│   └── Leaf 1.3: RL-trained Reviewers [ReviewRL (Zeng et al. 2025)]
├── Branch 2: Scientific Impact Prediction
│   ├── Leaf 2.1: Citation Graph/Metadata [DGNI (Geng et al. 2022)]
│   ├── Leaf 2.2: Embedding-based [SPECTER (Cohan et al. 2020), TNCSI (Zhao et al. 2025b)]
│   ├── Leaf 2.3: LLM Text-based [HLM-Cite (Hao et al. 2024), AutoEval (Hoepner et al. 2025) [3]]
│   └── Leaf 2.4: Rubric-as-Objective [Rubric Co-Scientists [1], Rubrics as Rewards [5]]
├── Branch 3: Automated Paper Revision
│   ├── Leaf 3.1: Summarization-based [PEGASUS (Zhang et al. 2019)]
│   ├── Leaf 3.2: Multi-agent Feedback [SWIFT (Chamoun et al. 2024), R3 (Du et al. 2022)]
│   └── Leaf 3.3: Rubric-driven Revision [APRES (this work)] ← Novel position
├── Branch 4: LLM Evaluation Consistency & Benchmarking
│   ├── Leaf 4.1: Human-LLM Agreement [Liang et al. 2023, Goldberg et al. 2024, Thakkar et al. 2025]
│   ├── Leaf 4.2: Consistency Metrics [Evaluating Consistency [6], PiCO (Ning et al. 2024)]
│   └── Leaf 4.3: Multi-dimensional Benchmarking [PRISM [2]]
└── Branch 5: Agentic Search Frameworks
    ├── Leaf 5.1: Code-space Search [AIDE (Jiang et al. 2025) [4]]
    └── Leaf 5.2: Multi-branch Search [MultiAIDE (Zhao et al. 2025a)]
```

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---------------|-------------|----------------------|--------------------|------------------------|--------------------|
| Root → Branch 1 → Leaf 1.2 | LLM Prompt-based Reviewers | Reviewer2, MARG | Human-defined criteria; static evaluation | APRES discovers criteria automatically | Low — clearly different paradigm |
| Root → Branch 2 → Leaf 2.3 | LLM Text-based Impact Prediction | HLM-Cite, AutoEval [3] | Text features predict citations | APRES uses agentic search to discover intermediate rubric, not direct text→citation | Medium — [3] confirms citation prediction viable but uses simpler models |
| Root → Branch 2 → Leaf 2.4 | Rubric-as-Objective | Rubric Co-Scientists [1], RaR [5] | Rubrics encode quality criteria; used as training signal | APRES applies rubric to paper revision (not plan generation); uses agentic search (not extraction) | **High** — shared paradigm and overlapping authors with [1] |
| Root → Branch 3 → Leaf 3.2 | Multi-agent Revision | SWIFT, R3 | Fixed or simple rubrics; human-in-the-loop | APRES uses discovered rubric; fully automated loop | Low — rubric discovery is the differentiator |
| Root → Branch 4 → Leaf 4.3 | Multi-dimensional Benchmarking | PRISM [2] | LLM reviewers have dimension-specific blind spots | APRES focuses on decision consistency; PRISM on review content quality | Medium — [2] provides complementary perspective |
| Root → Branch 5 | Agentic Search | AIDE [4], MultiAIDE | Tree search over solution space | APRES applies search to rubric space (novel domain) | Low — framework is adapted, not invented |

### 9C. Head-to-Head Comparison Matrix

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|----------------|-------------|------------------------|------------------|--------------------------|
| [1] 2512.23707 | Training AI co-scientists to generate research plans | Extract rubrics from papers; RL with self-grading; generator-verifier gap | Both extract/use rubrics as optimization objectives | APRES: paper text revision via agentic search; [1]: research plan generation via RL training; different tasks, different search mechanisms | **High** — requires explicit differentiation in Related Work; novelty claim must be qualified |
| [2] 2605.26730 | Benchmarking LLM peer reviewers on 4 quality dimensions | Argument mining + retrieval-augmented verification + consensus scoring | Both evaluate LLM reviewer quality | APRES: decision consistency (Glicko2); PRISM: content quality dimensions (depth, novelty, flaws, constructiveness) | Medium — PRISM findings temper APRES's consistency claims; LLMs have blind spots |
| [3] 2503.05712 | Evaluating citation prediction vs review score prediction | Simple models (title+abstract) for citation prediction | Both find citation prediction more viable than review score prediction | APRES: agentic rubric search; [3]: simple models without search | Low — complementary evidence supporting the citation proxy approach |
| [4] 2502.13138 | ML engineering automation | Tree search over code solutions | Underlying search framework for MultiAIDE | APRES: rubric space search; AIDE: code space search | Low — APRES applies, not invents, the search framework |
| [5] 2507.17746 | RL with rubric-based rewards beyond verifiable domains | On-policy RL; rubric criteria aggregated into rewards | Both use rubrics as structured reward/objective signals | APRES: paper revision; [5]: LLM policy training for reasoning tasks | Low — different application domains |
| [6] 2412.00543 | Evaluating LLM evaluator consistency | Self-consistency (SC) and Inter-scale Consistency (IC) | Both study LLM evaluation reliability | APRES: Glicko2-based decision consistency; [6]: prompt-level self-consistency | Medium — [6] shows strong models ≠ consistent evaluators; qualifies APRES's consistency narrative |

### Contribution-level Novelty Conclusion

**C1 (Rubric Discovery):** `partially_overlapping` — 量规作为优化目标的范式在共享作者的前期工作 [1] 中已有探索，但 APRES 首次将该范式与 agentic search 结合并应用于 citation-predictive 评审量规的发现。建议将新颖性声明限定为 "first to integrate agentic search with citation-predictive rubric discovery for paper evaluation"。

**C2 (Rubric-driven Revision):** `partially_overlapping` — 闭环修改机制本身有先例（SWIFT, R3），但使用自动发现的 citation-predictive 量规作为目标函数是新的。核心价值在于 pipeline 的整合（量规发现 → 量规驱动修改）而非单个组件的原创性。建议强调系统整合贡献。

**C3 (LLM Consistency):** `partially_overlapping` — 同模型一致性结果可信（~19-20% vs 人类 ~23-26%），但跨模型比较中的高分歧率（>35%）未被充分讨论。PRISM [2] 和 [6] 的发现表明 LLM 评估的优势是维度特定的。建议将结论限定为 "within-model LLM evaluation decisions are more consistent than human committees"。

## References
[1] Training AI Co-Scientists Using Rubric Rewards 2512.23707

[2] PRISM: A Multi-Dimensional Benchmark for Evaluating LLM Peer Reviewers 2605.26730

[3] Automatic Evaluation Metrics for Artificially Generated Scientific Research 2503.05712

[4] AIDE: AI-Driven Exploration in the Space of Code 2502.13138

[5] Rubrics as Rewards: Reinforcement Learning Beyond Verifiable Domains 2507.17746

[6] Evaluating the Consistency of LLM Evaluators 2412.00543

## Scores
**Final Score: 7.0 / 10**

评分依据（以研究价值和新颖性为首要维度）：

- **研究价值 (8/10)**：APRES 解决了一个重要且及时的问题——如何利用 LLM 帮助作者改进论文质量。两阶段架构（量规发现 → 量规驱动修改）为"AI 辅助论文写作"提供了一个可量化、数据驱动的新范式。大规模实验和盲法人类评估为方法的实用性提供了有力证据。量规发现方法本身也具有独立的方法论价值。

- **新颖性 (6/10)**：核心贡献（C1, C2）被判定为 `partially_overlapping`。量规作为优化目标的范式在共享作者的前期工作 [1] 中已有体现，闭环修改机制也有先例。APRES 的新颖性主要体现在系统整合（首次将 agentic rubric discovery 与 automated paper revision 结合）和应用创新（将 MultiAIDE 应用于评审量规搜索空间），而非基础方法论的突破。

- **有效性/可靠性 (7/10)**：实验设计总体上扎实，但存在循环评估风险（同一量规用于优化和评估）、基线比较不够公平（损失函数不一致）、一致性实验结论过度推广等问题。这些问题不致命但需要在修改中处理。

- **可重复性 (6/10)**：数据集、prompt、超参数有文档记录，代码承诺开源。但搜索框架的关键实现细节（初始量规、debug 机制、评分一致性保障、计算成本）缺失，影响完全复现。

**Post-Revision Target: [7.5, 8.5] / 10**

在完成 P0 修正（新颖性声明限定、MAE 术语修复、循环评估讨论、一致性结论限定）后，预期得分可达 7.5-8.0。如果在 P0 基础上进一步完成 P1 修正（基线损失函数统一、Abstract/Conclusion 重写、方法细节补充），预期得分可达 8.0-8.5。该论文的核心贡献——"将 agentic rubric discovery 与 automated paper revision 系统整合"——在大规模验证和人类评估的支撑下具有实质性价值，主要扣分项来自新颖性定位不够精准和实验设计的部分 methodological concerns，这些均可通过文本修改和补充分析解决，无需根本性的方法重构。
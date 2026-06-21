## Summary
# Final Review Report

## Summary

本文提出了APRES，一个两阶段的agentic框架，旨在自动改进科学论文的文本呈现质量。第一阶段（Rubric Search）通过MultiAIDE agentic搜索发现一个能预测未来引用数的评审rubric；第二阶段（Paper Improvement）使用发现的rubric作为代理目标函数，驱动LLM在闭环中迭代修订论文文本。在26,707篇ICLR和NeurIPS论文上的实验表明：(1) 发现的rubric在引用预测MAE上比最强基线降低19.6%，(2) 79%的人类评估者偏好修订后的论文，(3) 使用APRES rubric的LLM评审比人类评审更一致。

本文在AI辅助科学写作的交叉领域做出了有意义的贡献。将agentic search与rubric发现结合用于引用预测是一个新颖的组合，闭环修订pipeline的设计也较为完整。然而，论文在多个维度存在需要修正的问题：核心数值声明缺少可追溯的计算来源；人类评估缺少关键方法学细节（评估者独立性、inter-rater agreement）；内容不变性这一关键约束未被量化验证；结论部分存在overclaim。总体而言，这是一项有潜力的工作，但在科学严谨性和声明边界方面需要进行实质性修订。

## Strengths
1. **问题选择具有现实意义。** 论文聚焦于同行评审中的不一致性问题和科学写作质量的改进，这是当前ML社区高度关注的实际问题。将LLM定位于"投稿前stress-test工具"而非"替代审稿人"的框架设计是合理且有价值的。

2. **两阶段pipeline设计完整。** 从rubric发现到闭环修订的端到端设计思路清晰，两个阶段共享agentic search scaffold（MultiAIDE）的设计具有优雅性。diff-based编辑方法有效防止了LLM在修订中过度缩短论文的问题。

3. **实验规模可观。** 在26,707篇论文、四个顶级会议（ICLR 2024/2025, NeurIPS 2023/2024）上的实验提供了较强的统计基础。364对论文的人类盲法评估设计合理，统计检验（binomial test, p < 10^-22）提供了有力的显著性证据。

4. **附录中的一致性实验是重要的补充验证。** 通过复现NeurIPS一致性研究设计，论文证明了LLM评审可以比人类审稿委员会更一致——这一发现本身具有独立的研究价值，也为rubric作为可靠修订信号提供了必要的可信度基础。

5. **透明度和可复现性承诺良好。** 论文提供了完整的prompts（附录F）、发现的rubric（附录E）、详细的超参数设置，并承诺发布代码和数据。伦理声明也较为全面。

## Weaknesses
**W1 — 核心数值声明缺少可追溯的计算来源 (Major, Validity Risk)。** 论文多次强调"19.6% improvement in MAE over the next best baseline"，但在Page 6 - Citation Number Prediction Results中仅报告了近似MAE值（"approximately 2.8 and 2.65"），未给出19.6%的精确计算过程。读者无法独立验证这一核心数字。此外，三次重复实验的方差未被量化报告，图2也未显示error bars。

**W2 — 人类评估缺少关键方法学细节 (Major, Validity Risk)。** Page 9 - Human Evaluation of Revised Papers段落未披露评估者与作者团队的关系（是否来自同一机构Meta？是否知晓研究假设？），未报告inter-rater agreement（Fleiss' kappa），也未对偏好原因进行分维度分析。这些缺失使79%偏好率的稳健性无法被完整评估。

**W3 — 内容不变性约束未被量化验证 (Major, Validity Risk)。** Page 10 - Limitations段落承认"we cannot perfectly guarantee this constraint was met"，但未提供任何抽查或验证数据来估计科学内容被意外修改的频率。考虑到"不改动科学内容"是APRES的核心设计原则，缺少对这一约束的实证验证是一个显著缺陷。

**W4 — 结论存在overclaim (Major)。** Page 10 - Conclusion中的"unlocking faster, safer, and more impactful scientific progress"超出了实验证据的边界。APRES仅在ML会议论文上验证了修订效果，将其推广为"加速科学进步"的催化剂缺乏证据支持。

**W5 — 引用作为唯一impact proxy的局限性讨论不够充分 (Minor)。** Page 9 - From Mimicking Humans to Predicting Impact段落承认了citation的偏差（子领域差异、社交媒体效应、Goodhart's Law），但未通过实验量化这些偏差对rubric公平性的具体影响。

**W6 — Related Work缺少对最接近相邻工作的讨论 (Minor)。** Page 2 - Related Work段落未讨论"Training AI Co-Scientists Using Rubric Rewards" [1]，该工作同样来自Meta团队，使用自动提取的rubrics作为RL训练的奖励信号——在概念上与APRES的rubric-as-objective高度相关，但任务不同（research plan generation vs. paper revision）。明确区分这两者对于确立APRES的差异化贡献至关重要。

**W7 — 写作质量问题 (Minor)。** 摘要过长且缺少紧凑结构；Introduction各段角色不够清晰；多处存在语法错误（"a...processes"）和指代不清（"constrained technique"在首段未获解释）。

## Key Issues
```text
ASCII Diagram — Paper Structure & Evidence Map

[Claim: APRES rubric reduces citation prediction MAE by 19.6%]
    ├── Evidence: Fig. 2 shows MultiAIDE converges to MAE < 2.0, baselines at ~2.65
    │   └── GAP: 19.6% calculation source not explicitly traced in text
    │       └── RISK: Core quantitative claim not independently verifiable
    ├── Evidence: Three repeat runs "to generate confidence intervals"
    │   └── GAP: Variance/CI not shown in Fig. 2
    │       └── RISK: Statistical reliability unknown

[Claim: 79% human preference for APRES-revised papers]
    ├── Evidence: 287/364 pairs preferred by majority, binomial test p < 10^-22
    │   └── GAP: Evaluator independence not disclosed; no inter-rater agreement (Fleiss' kappa)
    │       └── RISK: Preference rate may conflate presentation bias with quality improvement
    └── Evidence: Word cloud (Fig. 3) shows "clearly, logically, novelty"
        └── GAP: No structured decomposition by revision dimension
            └── RISK: Cannot distinguish clarity improvement from novelty inflation

[Claim: APRES preserves core scientific content]
    └── Evidence: Prompt instructs Rewriter to not alter results/tables
        └── GAP: No empirical verification (no manual spot-check data)
            └── RISK: Key design principle unvalidated

[Claim: LLM evaluations are "more consistent than human committees"]
    ├── Evidence: Fig. A2 shows within-model-family disagreement < human benchmark (23%)
    │   └── GAP: 25% acceptance threshold sensitivity not analyzed
    │       └── RISK: Consistency advantage may be threshold-dependent
    └── Evidence: 20,000 pairwise comparisons on 26,707 papers
        └── GAP: Only 0.006% of total pairwise space sampled
            └── RISK: Glicko2 rating stability at this sampling rate unclear
```

### Ranked Top-5 Core Defect Board

| # | Severity | Research-Value Impact | Validity Risk | Defect | Fixability | Confidence |
|---|----------|----------------------|---------------|--------|------------|------------|
| 1 | Major | High | Medium | 19.6% MAE声明缺少可追溯计算和方差报告 (W1) | High: 补充精确数值和CI即可 | High |
| 2 | Major | High | High | 内容不变性约束未经验证 (W3) | Medium: 需要人工抽查50+篇论文 | High |
| 3 | Major | Medium | Medium | 人类评估缺少独立性披露和inter-rater agreement (W2) | High: 补充方法论细节即可 | High |
| 4 | Major | Medium | Low | 结论overclaim "accelerating scientific progress" (W4) | High: 精炼措辞即可 | High |
| 5 | Minor | Low | Low | Related Work缺少Rubric Rewards [1]的讨论 (W6) | High: 添加1段讨论即可 | High |

## Actionable Suggestions
### S1 — 补充19.6% MAE改善的精确计算和方差报告 (Must, 对应W1)
在Page 6 - Citation Number Prediction Results段落末尾添加：(a) 精确的MAE数值表（含均值和标准差，而非"approximately"），(b) 19.6%的具体计算（"from baseline MAE 2.65 to APRES MAE 2.13, (2.65-2.13)/2.65 = 19.6%"），(c) 三次重复的标准差，并在Fig. 2中添加error bars或shaded CI区域。

### S2 — 添加内容不变性的抽查验证 (Must, 对应W3)
随机抽取50篇修订论文，由人工检查：(a) 数值结果是否被修改，(b) 方法论声明是否被扭曲，(c) 技术描述是否仍然准确。在Limitations段落中报告错误率（如"2/50 cases had minor factual inaccuracies"）。这一数据可以显著提升读者对"preserving scientific content"声明的信任。

### S3 — 完善人类评估的方法学报告 (Must, 对应W2)
在Page 9 - Human Evaluation段落中补充：(a) 评估者是否来自作者所在机构（是否Meta员工），(b) 评估者是否知晓研究假设，(c) Fleiss' kappa值衡量评估者间一致性，(d) 按修订维度（清晰度、论证逻辑、贡献框架、风格）分解偏好原因。

### S4 — 降低Conclusion中的overclaim (Must, 对应W4)
将"unlocking faster, safer, and more impactful scientific progress"替换为更受证据支持的表述，例如："providing a data-driven baseline for improving the clarity of scientific writing, with demonstrated effectiveness on ML conference papers."同时补充已发现的核心限制和下一步工作方向。

### S5 — 讨论Rubric Rewards [1]并明确差异化 (Nice-to-have, 对应W6)
在Page 2 - Related Work中添加一段讨论"Training AI Co-Scientists Using Rubric Rewards" [1]，明确区分：(i) rubric发现方式（agentic search vs. extraction from existing papers），(ii) 优化目标（paper revision vs. research plan generation），(iii) 是否需要模型微调（inference-time loop vs. RL fine-tuning）。

### S6 — 添加一致性实验的敏感度分析 (Nice-to-have)
在附录A.2中报告使用20%和30%接受阈值时的disagreement rate变化，以及Glicko2 rating在最后5,000次比较中的收敛性证据（均值绝对变化量）。

### S7 — 按子领域分解rubric预测性能 (Nice-to-have)
考虑到不同ML子领域的引用率差异（NLP vs. 理论ML vs. CV），按子领域报告rubric的MAE有助于评估其公平性和泛化能力。

## Storyline Options + Writing Outlines
### 当前Introduction问题诊断

当前Introduction由4段组成：P1（评审危机+LLM机遇+风险）、P2（APRES方法概述）、P3（验证策略预览）、P4（研究意义+定位）。主要问题：(1) P1信息过载，缺少明确的gap statement，(2) P2贡献声明缺少操作方法预览，(3) P3过于简略，(4) P4的human-in-the-loop讨论与APRES自动化设计存在张力。

### 推荐Storyline

**Option A（推荐）："从发现问题到解决问题"的叙事弧线**

P1 - Big Picture & Crisis：同行评审的规模危机 → 不一致性问题 → 作者缺乏可靠反馈。
P2 - Gap & Opportunity：现有LLM审稿工具使用固定标准 → 无法自动发现影响力信号 → APRES的两阶段创新。
P3 - Method Preview：Stage 1如何发现rubric → Stage 2如何驱动修订 → 核心约束（不改科学内容）。
P4 - Evidence Roadmap：三个实验的预览（rubric预测力、修订效果、一致性验证）→ 关键数值结果预览。
P5 - Positioning：贡献总结 + 定位为投稿前工具 + 非替代人工审稿。

### Abstract Outline (推荐)

- **S1 (Problem):** 科学写作质量影响研究影响力，但同行评审反馈不一致，LLM辅助工具使用固定人工标准。
- **S2 (Gap):** 现有系统无法自动发现与论文实际影响力相关的评估维度。
- **S3 (Method):** APRES通过agentic搜索自动发现预测引用数的评分rubric，并用其驱动闭环论文修订。
- **S4 (Results):** 发现的rubric在引用预测MAE上比最强基线降低19.6%；79%人类评估者偏好修订论文；LLM评审比人类委员会更一致。
- **S5 (Scope):** 仅修改文本呈现、不改动科学内容；定位为投稿前辅助工具。

### Introduction Paragraph-by-Paragraph Plan

**P1 — Big Picture & Crisis (当前P1前半部分)**
- Role: 建立问题的重要性和紧迫性
- Claim: 同行评审面临规模和质量双重危机，作者缺少可靠的改进反馈
- Evidence: 引用Kim et al. 2025, Chen et al. 2025a
- Transition: "LLMs offer a scalable alternative, but..."

**P2 — Gap & Opportunity (当前P1后半部分 + 新内容)**
- Role: 明确现有LLM工具的缺口
- Claim: 现有LLM审稿工具使用固定的、人工定义的评估标准，无法自动发现与论文实际影响力相关的信号
- Evidence: LLM审稿研究（Gao 2024, D'Arcy 2024等）+ 人类审稿分数预测引用数不佳（MAE ~5.0）
- Transition: "APRES addresses this by..."

**P3 — Method Preview**
- Role: 概述APRES的两阶段设计
- Claim: Stage 1通过agentic search发现预测引用数的rubric；Stage 2使用rubric作为目标函数驱动闭环修订
- Key detail: 显式说明"revises only presentation, not scientific content"
- Transition: "We validate APRES through three experiments..."

**P4 — Evidence Roadmap**
- Role: 预览实验结构和关键结果
- Claim: 三个实验分别验证rubric预测力、修订效果和评审一致性
- Key numbers: 19.6% MAE reduction, 79% human preference
- Transition: "These results position APRES as..."

**P5 — Positioning & Contributions**
- Role: 总结贡献并定位研究
- Claim: 三项贡献：(1) agentic rubric discovery, (2) closed-loop revision, (3) empirical validation
- Positioning: pre-submission stress-test tool, not reviewer replacement

## Priority Revision Plan
```text
ASCII Diagram — Revision Strategy Roadmap

P0 (Must, Before Resubmission)
├── [Fix W1] 补充19.6% MAE计算来源 + 方差报告
│   └── Action: 在Page 6添加精确MAE表格（含mean±std）；Fig. 2添加error bars
├── [Fix W3] 添加内容不变性抽查验证
│   └── Action: 抽查50篇修订论文，报告错误率；补充到Limitations段
├── [Fix W2] 完善人类评估方法学报告
│   └── Action: 补充评估者独立性声明、Fleiss' kappa、分维度偏好分析
└── [Fix W4] 降低Conclusion overclaim
    └── Action: 精炼措辞，添加限制条件和下一步方向

P1 (Nice-to-have, Strengthens Paper)
├── [Fix W6] Related Work添加Rubric Rewards [1]讨论
│   └── Action: 在Page 2添加1段差异化比较
├── [S6] 一致性实验敏感度分析
│   └── Action: 附录A.2添加threshold sensitivity + 收敛性证据
└── [S7] 子领域rubric性能分解
    └── Action: 按NLP/CV/Theory等子领域报告MAE

P2 (Optional, Additional Polish)
├── 重写Abstract为5句紧凑结构（见Storyline Options）
├── 重写Introduction为5段结构（见Storyline Options）
└── 修复语法错误（"a...processes"等）
```

### 各修订任务详情

| Priority | Task | Effort | Expected Impact | Page(s) Affected |
|----------|------|--------|-----------------|------------------|
| P0 | 补充MAE数值精确计算和方差 | 2-4h | 核心声明可信度显著提升 | Page 6, Fig. 2 |
| P0 | 内容不变性抽查验证 | 8-16h (需人工) | 核心设计原则获实证支撑 | Page 10 |
| P0 | 人类评估方法学补充 | 2-4h | 79%偏好率稳健性可被完整评估 | Page 9 |
| P0 | Conclusion overclaim修正 | 1h | 声明边界恢复诚实性 | Page 10 |
| P1 | Related Work补充 | 2h | 差异化定位更清晰 | Page 2 |
| P1 | 一致性实验敏感度分析 | 4-8h (需重跑实验) | 附录结论更稳健 | Appendix A.2 |
| P1 | 子领域性能分解 | 4-8h | 公平性和泛化能力获评估 | Page 6-7 |

## Experiment Inventory & Research Experiment Plan
### Completed Experiment Inventory

| Exp ID | Objective/Hypothesis | Setup | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|-------|---------|-------------|-----------------|-------------------|
| E1 | Rubric search能发现比固定标准更预测引用数的rubric | 26,707 papers; MultiAIDE search; NB regression | MAE | MultiAIDE MAE ~1.92-2.30 vs. baselines 2.65-5.0 | C1: rubric发现有效 | 19.6%计算来源不明确; 方差未报告 |
| E2 | 发现的rubric能有效指导论文修订 | Test set; 120 iterations; Discovered/Simple/Embedding PCA rubrics | ΔS (rubric score improvement) | ΔS = 3.33 (borderline), 2.98 (reject) for o3 | C2: 修订有效 | 仅报告rubric score改善, 未报告实际引用预测改善 |
| E3 | 修订论文被人类评估者偏好 | 364论文对; 3评估者/对; blind pairwise | Preference rate; binomial test | 79%偏好修订论文; p < 10^-22 | C3: 人类验证 | 评估者独立性未披露; 无inter-rater agreement |
| E4 | Rubric + MultiAIDE的消融 | Ablation: w/o R*, w/o MultiAIDE | ΔS | Full APRES ΔS=3.33 vs. w/o R* ΔS=1.24 | C2: 两个组件都必要 | 仅在o3上测试 |
| E5 | LLM评审一致性 vs. 人类 | Glicko2 rating; 20K pairwise comparisons; 4 LLM judges | Disagreement rate | 同模型族内 ~19-20% vs. 人类~23% | 一致性验证 | 阈值敏感度未分析; 收敛性未验证 |
| E6 | Glicko2 rating与会议决策的相关性 | Pairwise LLM judge; official outcomes | Rating-outcome correlation | 高rating与oral/spotlight正相关 | 验证LLM评审信号有效性 | 相关性未量化(如Spearman ρ) |

### Research-Theme Gap Diagnosis

1. **新知识 (New Knowledge):** APRES的核心新知识是"agentic search可以发现比人工标准更预测引用数的rubric维度"。当前E1已证明这一点，但缺少对该rubric具体内容的分析——哪些维度最预测引用数？是否有反直觉的发现？
2. **可复现性 (Reproducibility):** 论文承诺发布代码和数据，但当前报告中对超参数搜索空间、prompt工程细节、以及LLM API调用成本的信息不足以确保完全复现。
3. **实践影响 (Impact on Practice):** APRES声称可作为"投稿前stress-test工具"，但缺少用户研究来验证作者是否真的从APRES反馈中受益（仅验证了修订论文被偏好，未验证作者使用APRES后论文质量是否提升）。

### Proposed Research Experiments

```text
ASCII Diagram — Experiment Upgrade Plan

Stage 1 (P0, Before Resubmission)
├── EE1: 内容不变性验证 [S2]
│   └── 抽查50篇修订论文, 报告科学内容被意外修改的错误率
├── EE2: 人类评估方法学补全 [S3]
│   └── 报告Fleiss' kappa; 分维度偏好分解
└── EE3: MAE方差与统计检验 [S1]
    └── 报告三次重复的mean±std; Fig. 2添加CI

Stage 2 (P1, Strengthens Paper)
├── EE4: 子领域rubric性能分解 [S7]
│   └── 按NLP/CV/Theory子领域报告MAE
├── EE5: 一致性实验敏感度分析 [S6]
│   └── 不同阈值(20%/25%/30%)下的disagreement rate
└── EE6: Rubric内容分析
    └── 报告哪些rubric维度对引用预测贡献最大

Stage 3 (P2, Future Work)
├── EE7: 用户研究 - 作者使用APRES后论文质量变化
└── EE8: 跨领域泛化 - 在非ML论文上测试rubric
```

### 详细实验设计

| ID | Target Claim | Hypothesis | Minimal Design | Controls | Metrics | Success Criterion | Priority |
|----|-------------|------------|----------------|----------|---------|-------------------|----------|
| EE1 | "preserves core scientific content" | 修订错误率 < 5% | 随机抽样50篇修订论文，人工审查：(a)数值变化，(b)方法论声明扭曲，(c)技术描述失实 | 原始论文作为ground truth | 错误率（按类型分解） | 任一类型错误率 < 5% | P0 |
| EE2 | "79% human preference" | Inter-rater agreement moderate (κ > 0.3) | 计算现有364对数据的Fleiss' kappa；对偏好理由进行主题编码 | 随机偏好作为baseline | Fleiss' κ; 分维度偏好率 | κ > 0.3 且分维度偏好一致 | P0 |
| EE4 | Rubric公平性 | 子领域间MAE差异 < 30% | 按论文的主要methodology标签分类（如NLP/CV/Theory/RL），分别计算MAE | 全局MAE | 子领域MAE; 相对差异 | 最大差异 < 30% | P1 |

## Novelty Verification & Related-Work Matrix
### 9A — Contribution Novelty Verdict Board

| Claim ID | Author Contribution Claim | Key Evidence Papers [n] | Novelty Verdict Tag | Why | Confidence | Required Repositioning |
|----------|--------------------------|------------------------|---------------------|-----|------------|------------------------|
| C1 | Agentic search discovers review rubric predictive of future citations via negative binomial regression | [2] Prompt breeder (prompt evolution); [3] SPECTER (citation-informed embeddings); [4] Auto. Evaluation Metrics (citation vs. review score prediction) | **partially_overlapping** | Agentic search for rubric discovery is novel in the citation prediction context, but individual components (iterative prompt optimization [2], paper embeddings for citation prediction [3], and the observation that human scores are poor citation predictors [4]) are established. The specific combination of MultiAIDE + NB regression is original. | High | Add explicit comparison with Prompt breeder's prompt evolution mechanism; clarify why MultiAIDE search outperforms simpler prompt optimization approaches. |
| C2 | Closed-loop paper revision guided by discovered rubric as surrogate objective | [1] Rubric Rewards (rubric-as-objective for plan generation); [5] R3 (iterative human-in-the-loop revision); [6] SWIF²T (multi-agent feedback for revision) | **partially_overlapping** | The closed-loop revision concept is shared with R3 [5] and SWIF²T [6], though these use fixed or human-defined criteria, not discovered rubrics. Rubric Rewards [1] uses rubrics as objectives but for research plan generation, not paper revision. The combination of (discovered rubric + diff-based editing + iterative revision) is novel within scope. | High | Discuss Rubric Rewards [1] explicitly in Related Work; clarify task difference (revision vs. plan generation) and mechanism difference (search-based discovery vs. extraction). |
| C3 | Empirical validation: 19.6% MAE improvement, 79% human preference, LLM consistency > human | — | **supported** | The empirical evidence is substantial in scale (26,707 papers, 364 paper pairs, 4 LLMs). While methodological gaps exist (W1-W3), the overall evidence direction supports the claims. No contradictory evidence found. | Medium | Supplement methodological details (variance, inter-rater agreement, content-integrity check) to elevate confidence from Medium to High. |

### 9B — Related-Work Taxonomy Matrix

```text
ASCII Diagram — Related-Work Taxonomy Tree (Layered)

Automated Scientific Peer Review & Revision (Root)
├── Branch A: LLM Review Generation
│   ├── Leaf A1: Single-agent review generation [7][8]
│   │   └── Reviewer2, ReviewRobot — template/prompt-based review generation
│   ├── Leaf A2: Multi-agent review generation [9][10]
│   │   └── MARG, TreeReview — deliberative committees via multi-agent LLMs
│   └── Leaf A3: RL-trained reviewers
│       └── ReviewRL — RL for useful review generation
│
├── Branch B: Scientific Impact Prediction
│   ├── Leaf B1: Citation network/graph methods
│   │   └── DGNI, HLM-Cite — metadata + graph-based citation prediction
│   ├── Leaf B2: Text-embedding-based methods [3]
│   │   └── SPECTER, TNCSI_SP — document embeddings for impact prediction
│   └── Leaf B3: Rubric/prompt optimization methods [2][4]
│       └── Prompt breeder, Auto. Eval. Metrics — iteratively refined evaluation criteria
│
├── Branch C: Automated Text Revision
│   ├── Leaf C1: Summarization-based revision
│   │   └── PEGASUS — abstractive summarization with remove/mask strategy
│   ├── Leaf C2: Iterative human-in-the-loop revision [5]
│   │   └── R3 — human accepts/rejects model edits iteratively
│   └── Leaf C3: Multi-agent feedback revision [6]
│       └── SWIF²T — multi-agent LLM constructive feedback for revision
│
└── Branch D: Rubric-Guided Generation (Emerging)
    ├── Leaf D1: Rubric extraction + RL training [1]
    │   └── Rubric Rewards — extracted rubrics for RL-based plan generation
    └── Leaf D2: Agentic rubric discovery + revision (APRES) ★
        └── This paper — discovered rubrics for closed-loop paper revision
```

### 9C — Head-to-Head Comparison Matrix

| Ref [n] | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|----------|----------------|-------------|------------------------|------------------|--------------------------|
| [1] Rubric Rewards | Research plan generation from goals | Extract rubrics from papers; RL with self-grading | Uses rubric as objective function for LLM generation | Task (plan generation vs. paper revision); rubric source (extraction vs. agentic search); training (RL fine-tuning vs. inference-time loop) | Closest conceptual neighbor; needs explicit differentiation in Related Work |
| [2] Prompt breeder | Prompt optimization via evolution | Self-referential prompt improvement through mutation | Iterative search for better evaluation prompts | Target is prompts, not rubrics; no regression model for citation prediction | Direct baseline in experiments; APRES outperforms it |
| [5] R3 | Human-in-the-loop text revision | Iterative model edits + human accept/reject | Iterative revision loop | Human-in-the-loop vs. fully automated; no discovered rubric or citation objective | Shares iteration concept but different paradigm |
| [3] SPECTER | Document representation for citation prediction | Citation-informed transformer embeddings | Citation prediction from paper content | Fixed embedding model vs. discovered interpretable rubric; no revision component | Key baseline; APRES outperforms by combining LLM scoring with search |

### Contribution-level Novelty Conclusion

- **C1 (Rubric Discovery): partially_overlapping.** APRES首次将agentic search用于发现预测引用数的评审rubric，这一特定组合在现有文献中未被报道。但核心组件（prompt evolution [2]、paper embeddings [3]、citation prediction [4]）分别存在于先前工作中。建议在论文中更明确地区分"first to combine"与"first to propose"的表述。
- **C2 (Closed-loop Revision): partially_overlapping.** Rubric-as-objective的概念与Rubric Rewards [1]重叠，但APRES将其应用于不同的任务（论文修订而非研究计划生成）并使用不同的rubric获取方式（搜索而非提取）。与R3 [5]共享迭代修订框架但自动化程度和目标函数不同。建议在Related Work中与[1]进行详细的差异化讨论。
- **C3 (Empirical Validation): supported.** 实验规模和统计显著性充足。需补充方法学细节（W1-W3）以提升证据完整性。

## References
[1] Training AI Co-Scientists Using Rubric Rewards 2512.23707

[2] Promptbreeder: Self-referential self-improvement via prompt evolution (Fernando et al., 2024)

[3] SPECTER: Document-level Representation Learning using Citation-informed Transformers 2004.07180

[4] Automatic Evaluation Metrics for Artificially Generated Scientific Research 2503.05712

[5] Read, Revise, Repeat: A System Demonstration for Human-in-the-loop Iterative Text Revision 2204.03685

[6] Automated focused feedback generation for scientific writing assistance (Chamoun et al., 2024)

[7] Reviewer2: Optimizing review generation through prompt generation 2402.10886

[8] ReviewRobot: Explainable paper review generation based on knowledge synthesis (Wang et al., 2020)

[9] MARG: Multi-agent review generation for scientific papers 2401.04259

[10] TreeReview: A dynamic tree of questions framework for deep and efficient llm-based scientific peer review 2506.07642

## Scores
**Final Score: 6.5/10**

评分依据（按优先级排列）：

1. **研究价值 (Research Value): 7/10。** APRES在AI辅助科学写作这一高价值方向上做出了有意义的贡献。将agentic search与rubric发现结合用于引用预测是一个新颖的组合，闭环修订pipeline的设计也较为完整。但论文未充分展示rubric发现带来了哪些超越直觉的新知识（例如哪些非常规维度最预测引用数？），这限制了其研究洞察的深度。

2. **新颖性 (Novelty): 6.5/10。** C1（rubric发现）和C2（闭环修订）的核心组件在先前工作中分别存在（[1]-[6]），但APRES的组合方式——特别是将discovered rubric作为revision的objective——在现有文献中未见直接匹配。C3的实证验证规模充足但方法学细节有缺失。

3. **有效性 (Validity/Soundness): 5.5/10。** 实验设计整体合理，但存在若干影响核心声明可信度的问题：19.6%数值缺少可追溯计算（W1）、人类评估缺少关键方法学细节（W2）、内容不变性约束未经实证验证（W3）。这些问题的修正预计可将有效性评分提升至7-7.5。

4. **可复现性 (Reproducibility): 7/10。** 论文提供了详细的prompts、超参数和rubric，并承诺发布代码和数据。但LLM API调用成本、prompt工程迭代细节、以及搜索空间中未探索的因素使得完全复现需要大量资源。

5. **写作质量 (Presentation): 5.5/10。** 摘要和Introduction结构需要改进（W7）。多处语法错误和指代不清降低了阅读流畅度。但Method和Experiment部分的描述总体清晰。

**Post-Revision Target: [7.0, 8.0]/10**

如果所有P0和P1修订任务完成（特别是S1-S4），预计：
- 有效性提升至7-7.5（W1-W3修正）
- 新颖性提升至7-7.5（W6修正，差异化更清晰）
- 研究价值维持或小幅提升（rubric内容分析增加新知识）
- 写作质量提升至6.5-7

最终得分预计在7.0-8.0区间，取决于修订执行的彻底程度。达到8.0需要额外完成S6（一致性实验敏感度分析）和S7（子领域分解）。
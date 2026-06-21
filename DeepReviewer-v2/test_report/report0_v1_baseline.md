## Summary
APRES提出了一个两阶段的LLM智能体框架：(1) 通过智能体搜索（MultiAIDE）发现能够预测未来引用计数的评审rubric；(2) 以该rubric为目标函数，闭环迭代修订论文文本以提升其清晰度和可读性。在26,707篇ICLR/NeurIPS论文上，APRES的引用预测MAE比次优基线低19.6%，修订后的论文在79%的情况下被人类专家评审者偏好。附录进一步通过NeurIPS一致性实验的复制验证了LLM评审管道的稳定性。

本文定位清晰，写作坦率（多处承认引用计数的局限性和Goodhart's Law），人类评估设计严谨（364对盲法比较，p<10⁻²²），且工程实现扎实（diff-based editing、多LLM对比）。然而，核心方法论中存在一个未被充分讨论的风险：LLM Reviewer评分→负二项回归→LLM Rewriter修订→LLM Reviewer再评分的闭环存在自增强偏差（self-reinforcing bias），且∆S指标的循环验证性质削弱了定量评估的独立性。此外，LLM评审系统性偏差（已有文献表明LLM评审高估低质量论文、识别弱点能力不足）对rubric质量的影响未被评估。论文的价值在于首次将智能体rubric搜索与闭环论文修订整合，但需要在方法论上对这些风险进行更严格的界定和缓解。

## Strengths
1. **问题选择具有现实意义。** 同行评审面临可扩展性危机（Kim et al., 2025），LLM辅助论文修订是学术界迫切需要探索的方向。APRES定位为「增强而非替代」人类评审，立场合理。

2. **研究设计完整且有层次。** 论文包含两个相互关联的阶段（rubric发现→论文修订），并配有自动化评估（MAE/∆S）、人类评估（364对盲法偏好测试，p<10⁻²²）和一致性验证（附录A Glicko2/NeurIPS实验复制）。多维度验证设计值得肯定。

3. **工程实现扎实。** diff-based editing（使用Aider格式）有效防止了Rewriter过度缩短论文的问题；通过prompt约束和表格排除机制保护实验结果不被动修改；对比了4种前沿LLM（o1/o3/Gemini 2.5 Flash/Pro）。

4. **坦诚的局限性讨论。** 正文和Discussion多处承认引用计数的局限性、Goodhart's Law的风险、APRES仅处理文本的限制、以及对抗攻击（prompt injection）的威胁。这种坦诚增强了论文的科学可信度。

5. **人类评估结果具有较强的说服力。** 79%的偏好率（95% CI: 70.1%-79.0%），364对论文、3位评审者/对的盲法设计，以及二项检验的极低p值，使修订效果的人类验证具有统计学可信度。

## Weaknesses
1. **循环自增强偏差未充分讨论（W1-核心风险）。** APRES的架构存在一个闭合环路：LLM Reviewer根据rubric评分→负二项回归学习评分→引用预测→LLM Rewriter优化论文以最大化rubric分数→LLM Reviewer再次评估。如果LLM Reviewer存在系统性偏差（已有文献[2][3][4][6]表明LLM评审倾向于高估低质量论文、偏好LLM生成文本），整个优化可能收敛于「LLM认为好」而非「真正有科学影响力」的局部最优。检索文献[5]将此称为LLM评估的「circularity trope」。当前论文在Limitations中未讨论这一风险。

2. **∆S指标的循环验证问题（W2-方法论缺陷）。** Section 4.2的核心定量指标∆S定义为修订后论文的rubric评分减原始评分，而该rubric正是APRES Stage 1自身发现的。这构成「出题人即评分人」的循环验证。尽管人类评估（79%偏好率）提供了一定程度的独立验证，但∆S的提升有多少来自真实质量改善、多少来自LLM Rewriter对LLM Reviewer评分偏好的适应（同模型家族的风格偏好），未被量化区分。

3. **LLM评审偏差对rubric质量的潜在影响未被评估（W3-有效性风险）。** 检索文献[7]发现LLM评审在识别弱点方面比人类评审少生成59.42%的相关内容，对论文质量的敏感度远低于人类（从好论文到差论文仅增加5.7%的节点数，而人类增加50%）。如果APRES的Reviewer agent表现出类似偏差，发现的rubric可能系统性地低估科学严谨性维度，过度强调表面呈现特征。当前缺乏对发现rubric的内容效度分析。

4. **Introduction和Abstract中存在若干过度声明（W4-写作精确性）。** 摘要中「improves future citation prediction by 19.6% in MAE」措辞有歧义（MAE降低是improvement但表述不够直观）；Introduction P3中「strong empirical evidence that LLMs can serve as a reliable tool」的reliable一词超越了实验证据的范围（实验仅在ML会议论文上验证，且仅限于文本修订任务）。

5. **Related Work缺乏结构化分类框架（W5-写作质量）。** 当前Related Work以论文逐一列举的方式组织（「paper-by-paper summary」），而非按比较轴（如：审稿生成 vs 论文修订、单智能体 vs 多智能体、预定义标准 vs 自动发现标准）进行分类。Tab. 1提供了比较矩阵但段落实体未围绕这些维度展开讨论。

6. **跨模型族一致性差于随机基线的事实被低估（W6-结果解读准确性）。** Appendix Fig. A2显示o3与Gemini 2.5 Pro之间的不一致率>35.1%，差于随机基线（35.1%）。正文声称「LLM-based evaluation can be significantly more consistent than human peer review」虽在同模型族内成立，但跨模型族的不一致性是一个重要的使用限制，应被更明确地讨论。

## Key Issues
### KI-1 [Critical] LLM评分→回归→修订→再评分的自增强偏差循环

**位置**: Page 4 - Section 3.1; Page 7 - Section 4.2 Evaluation Metrics

**问题**: APRES的核心架构形成了一个闭合环路：LLM Reviewer用rubric评分论文→负二项回归从评分预测引用→LLM Rewriter优化论文以最大化rubric分数→LLM Reviewer再次评分修订版。此环路未经过偏差审计。已有文献表明LLM评审者存在系统性偏差：高估低质量论文[2][3]、偏好LLM生成文本[4][6]、识别弱点的能力远低于人类[7]。如果这些偏差存在于APRES的Reviewer agent中，整个优化过程可能收敛于LLM的局部偏好而非真正的科学质量提升。

**修复路径**: (Must) 在Limitations或Discussion中增加「Self-Reinforcing Bias Risk」小节，明确讨论此风险。(Must) 增加交叉模型评估实验：用LLM A修订的论文由LLM B评估∆S，以部分排除模型家族自偏好。(Nice-to-have) 进行rubric内容的定性审计，邀请领域专家评估发现的rubric是否合理覆盖了科学质量的多维度。

### KI-2 [Major] ∆S指标的循环验证性质

**位置**: Page 7 - Section 4.2 Evaluation Metrics

**问题**: 核心定量指标∆S使用的是APRES自身发现的rubric来计算改善幅度。这构成了「用自己的标准衡量自己的产出」的循环验证。虽然人类评估（79%偏好率）提供了独立验证，但∆S提升与人类偏好之间的一致性未被量化报告（例如，∆S与人类偏好率之间的相关性）。

**修复路径**: (Must) 报告∆S与人类偏好投票结果之间的相关性（Spearman/Kendall），以验证自动化指标与人类判断的一致性。(Must) 增加一个独立的评估指标，例如使用不同的LLM或不同的rubric来评估修订效果。

### KI-3 [Major] 发现rubric的内容效度未被验证

**位置**: Page 4 - Section 3.1; Appendix E

**问题**: 论文声称发现的rubric「捕捉了现有方法未捕获的未来影响力信号」，但未对rubric本身进行内容效度分析。Rubric包含60+条目（Appendix E），覆盖Problem Formulation、Literature Review、Methodology等8个维度。但没有分析这些条目中哪些对引用预测贡献最大、哪些可能仅反映表面文本特征而非科学质量信号。检索文献[8]指出LLM评估指标可能激励作者撰写误导性摘要和过度推销工作。

**修复路径**: (Must) 进行特征重要性分析（如SHAP值或消融研究），识别对引用预测最有贡献的rubric条目，并对这些条目进行定性讨论。(Must) 在Discussion中讨论发现的rubric可能编码了哪些与科学质量无关的文本特征（如特定写作风格、英语语言特征）。

### KI-4 [Major] 「consistent → reliable → meaningful revisions」推理链的逻辑跳跃

**位置**: Page 17 - Appendix A.2 Results

**问题**: 附录一致性实验的结论断言「LLMs can provide a stable signal, therefore validating APRES is reliable for providing meaningful revisions」。这一推理存在逻辑跳跃：(a) 一致性（两次运行产生相似结果）≠ 准确性（结果反映真实质量）；(b) Fig. A2显示跨模型族不一致率在某些情况下差于随机基线（>35.1%），暗示一致性高度依赖模型选择；(c) 二元Accept/Reject决策的一致性不等同于多维度rubric评分的稳定性。

**修复路径**: (Must) 修改结论措辞为更保守的表述，明确区分「within-model consistency」和「cross-model agreement」，并澄清consistency是修订可靠性的必要非充分条件。

### KI-5 [Minor] 写作精确性问题

**位置**: Page 1 - Abstract; Page 2 - Introduction P3; Page 10 - Conclusion

**问题**: 多处存在措辞不够精确：(a) 摘要「improves MAE by 19.6%」表述有歧义；(b) 「strong evidence that LLMs can serve as a reliable tool」中的reliable过度声明；(c) 结论中「unlocking faster, safer, and more impactful scientific progress」是超出实验验证范围的推测性声明。

**修复路径**: (必须) 按各PDF标注中提供的Mentor Revised Version进行修订。

## Actionable Suggestions
### S1 [Must] 增加自增强偏差分析并实施交叉模型验证

在Limitations中增加「Self-Reinforcing Bias」小节（约5-8句），明确讨论LLM Reviewer→回归→LLM Rewriter→LLM Reviewer闭环中的自增强风险。同时进行交叉模型验证实验：使用GPT模型修订的论文由Gemini模型评估∆S，反之亦然，报告∆S在交叉模型条件下的变化。如果∆S在交叉模型条件下显著下降，这将直接量化自偏好偏差的大小。

### S2 [Must] 报告∆S与人类偏好的相关性

计算并报告∆S与人类偏好投票结果之间的Spearman或Kendall秩相关系数。这为∆S作为自动化评估指标的有效性提供了关键的效度证据。

### S3 [Must] 进行rubric特征重要性分析

对发现的60+条目rubric进行SHAP分析或消融研究，识别对引用预测最有贡献的rubric维度。报告Top-10特征并讨论：(a) 它们是否捕捉了有意义的科学质量信号；(b) 它们是否可能仅反映表面文本特征（如抽象长度、特定连接词使用频率等）。

### S4 [Must] 修正写作中的过度声明

按PDF标注中的Mentor Revised Version修订：(a) Abstract中MAE措辞精确化；(b) Introduction P3中弱化reliable工具声明；(c) Conclusion中区分已验证发现与推测性声明；(d) Appendix A.2中修正一致性→可靠性的逻辑链条。

### S5 [Must] 重组Related Work

按比较轴组织Related Work，而非paper-by-paper列举。推荐结构：(a) LLM-based Review Generation（单智能体 vs 多智能体）；(b) LLM-based Paper Revision（静态标准 vs 自动发现标准）；(c) Citation Prediction and Impact Forecasting；(d) Reviewer Consistency and Evaluation Reliability。每个小节末尾明确APRES在该维度的差异化定位。

### S6 [Nice-to-have] 增加修订效果的领域内vs领域外分析

APRES的rubric是在ML会议论文上训练的。建议在至少一个非ML学科（如计算生物学或NLP子领域）的论文子集上测试修订效果，以初步评估跨领域泛化性。

### S7 [Nice-to-have] 人类评估中报告评分者间信度

在Tab. 3基础上，补充报告Fleiss' Kappa或Krippendorff's Alpha，以量化三位评审者之间的一致性程度。

## Storyline Options + Writing Outlines
## 当前叙事诊断

当前Introduction的叙事结构为：
- P1: 同行评审危机 → LLM机会与风险 → 本文应对（缺口定义模糊）
- P2: APRES框架介绍 → 两阶段贡献
- P3: 实验验证预览 → 社会背景 → 结果复述 → 立场声明

主要问题：(1) P1的gap定义不够精确；(2) P2中两阶段间的因果连接弱；(3) P3叙事顺序混乱。

## 推荐叙事结构（选项A — 首选）

**Arc**: Big Picture（评审危机）→ Concrete Gap（缺少约束性LLM修订方法）→ Solution Intuition（为什么rubric发现+闭环修订是合适路径）→ Evidence Preview → Contribution Summary

## Abstract Outline（完整）

- **S1 (Problem)**: 科学发现需要清晰沟通才能发挥影响，但同行评审面临可扩展性危机和不一致性挑战。
- **S2 (Gap)**: LLM可提供规模化反馈，但直接应用于论文修订存在修改科学内容、偏离学术规范等风险；缺少在保持科学内容完整的前提下自动改进论文呈现的方法。
- **S3 (Method)**: 我们提出APRES——一个两阶段智能体框架：(1)智能体搜索发现能预测未来引用计数的评审rubric；(2)以该rubric为目标函数的闭环论文修订。
- **S4 (Result)**: 在26,707篇ICLR/NeurIPS论文上，APRES的引用预测MAE比最优基线降低19.6%；修订论文在79%的情况下被人类专家偏好（364对盲法测试，p<10⁻²²）。
- **S5 (Scope)**: APRES仅处理文本不处理图表，依赖引用计数作为影响力的代理指标；定位为增强而非替代人类评审。

## Introduction Outline（完整 — 段落级别）

**P1 — Big Picture + Gap**: 同行评审是科学交流的基石，但顶级会议每年数万份投稿远超合格评审者的增长速度（Kim et al., 2025; Chen et al., 2025a），导致评审不一致和反馈质量下降。LLM提供了规模化反馈的可能，但其直接用于论文评审和修订存在风险：可能无意中修改科学声明或偏离学术规范（Ye et al., 2024; Lin et al., 2025）。核心缺口：目前缺少一种原则性方法，能够在可靠保持论文核心科学内容不变的前提下，利用LLM系统性地改进论文的呈现和可读性。

**P2 — Solution Intuition**: 我们提出APRES——一个将LLM从单纯的「人类评审模仿者」升级为「影响力信号发现者」的两阶段框架。核心洞察：与其让LLM模拟人类评审标准，不如让LLM通过智能体搜索自动发现哪些评估维度最能够预测论文的未来影响力（以引用计数衡量）。这个发现的rubric随后可作为闭环修订系统的优化目标——LLM Rewriter迭代改进论文文本，LLM Reviewer评估改进效果，搜索框架选择最优修订版本——整个过程约束在「不修改实验数据和科学结论」的范围内。

**P3 — Key Results Preview**: 在26,707篇来自ICLR 2024-2025和NeurIPS 2023-2024的论文上：(a) APRES发现的rubric在引用预测MAE上比SPECTER嵌入+PCA基线低19.6%；(b) APRES修订的论文在79%的盲法人类比较中被偏好（364对，3评审者/对，p<10⁻²²）；(c) 附录验证了LLM评审管道在一致性上优于人类评审委员会。

**P4 — Positioning + Roadmap**: 我们的工作与AAAI 2026的AI辅助评审试点和ICLR 2025的LLM评审反馈研究相呼应。重要的是，我们提倡的是AI增强而非替代人类评审——本文的方法旨在为作者提供投稿前的「压力测试」工具，帮助改进论文的清晰度和呈现，而非进行自主的科学价值判断。下文组织：Section 2回顾相关工作，Section 3详述方法，Section 4报告实验，Section 5讨论意义与局限。

## Priority Revision Plan
## P0 — 阻断性问题（必须在下一版投稿前解决）

| 优先级 | 任务 | 对应Issue | 预期工作量 | 对论文质量的影响 |
|--------|------|-----------|-----------|-----------------|
| P0 | 增加「Self-Reinforcing Bias」讨论至Limitations | KI-1 | 1-2小时 | 高：关闭方法论核心风险敞口 |
| P0 | 实施交叉模型∆S评估实验 | KI-1, KI-2 | 1-2天计算 | 高：提供循环偏差的定量证据 |
| P0 | 报告∆S与人类偏好的相关性 | KI-2 | 2-4小时 | 高：验证自动化指标的效度 |
| P0 | 修正Abstract/Introduction/Conclusion中的过度声明 | KI-5 | 2-3小时 | 中：提升科学可信度 |

## P1 — 高优先级修订（应在下一版中完成）

| 优先级 | 任务 | 对应Issue | 预期工作量 | 对论文质量的影响 |
|--------|------|-----------|-----------|-----------------|
| P1 | 进行rubric特征重要性分析（SHAP/消融） | KI-3 | 1-2天 | 高：揭示rubric的内在结构 |
| P1 | 修正Appendix A.2的结论措辞（consistency≠reliability） | KI-4 | 1小时 | 中：消除逻辑误解 |
| P1 | 重组Related Work为分类框架 | KI-5/W5 | 3-5小时 | 中：提升文献综述的学术质量 |
| P1 | 在Limitations中增加rubric跨领域泛化性讨论 | KI-3 | 1小时 | 中：明确适用范围 |

## P2 — 建议性修订（如时间允许）

| 优先级 | 任务 | 对应Issue | 预期工作量 | 对论文质量的影响 |
|--------|------|-----------|-----------|-----------------|
| P2 | 人类评估报告Fleiss' Kappa评分者间信度 | S7 | 1小时 | 低：增强方法论的透明度 |
| P2 | 至少一个非ML领域的修订效果初步测试 | S6 | 1-2天 | 低-中：探索泛化性 |
| P2 | 按论文质量分层报告人类偏好率（Accept/Borderline/Reject） | S7 | 2小时 | 低：提升分析的粒度 |

## 修订预计总时间：4-7天（取决于计算资源可用性）

## ASCII Diagram — Revision Strategy Roadmap

```text
[当前状态: 科学贡献坚实但方法论风险敞口未关闭]
    │
    ├── P0 (1-3天) ──→ 关闭自增强偏差讨论 + 交叉模型验证 + 声明修正
    │                        │
    │                        └──→ [状态: 方法论风险得到承认和量化]
    │
    ├── P1 (2-4天) ──→ rubric特征分析 + Related Work重组 + 结论修正
    │                        │
    │                        └──→ [状态: 文献定位清晰，rubric可解释]
    │
    └── P2 (1-3天) ──→ 评分者信度 + 跨领域测试 + 分层分析
                                     │
                                     └──→ [最终状态: 方法论透明，结论稳健]
```

## Experiment Inventory & Research Experiment Plan
| Exp ID | Objective/Hypothesis | Setup | Metrics | Main Outcome | Claim Supported | Current Limitation |
|--------|---------------------|-------|---------|-------------|-----------------|-------------------|
| E1 | MultiAIDE rubric search预测引用 | 26,707 papers (ICLR/NeurIPS), 80/10/10 split, neg-binomial regression, 4 LLMs | MAE | MAE 1.92-2.30; 比SPECTER+PCA改善19.6% | C1: rubric搜索有效 | 未分析rubric内容效度 |
| E2 | Ablation: Human scores baseline | 同E1, 使用人类评审原始分数 | MAE | MAE ~5.0 (与平均值基线接近) | C1: 人类分数预测力弱 | 可能因score scale与citation distribution不匹配 |
| E3 | Ablation: SPECTER embedding baselines | MLP + PCA variants on SPECTER embeddings | MAE | MAE 2.65-2.80 | C1: rubric优于文本嵌入 | 未比较其他SOTA embedding方法 |
| E4 | Ablation: Prompt breeder | 200步迭代演化prompt-based rubric | MAE | 收敛到比MultiAIDE更差的MAE | C1: MultiAIDE优于简单prompt演化 | 仅比较了一种prompt优化方法 |
| E5 | Paper Improvement with discovered rubric | 120步迭代修订, diff-based editing, 3 paper categories | ∆S (rubric score change) | Accept: ∆S=1.67, Borderline: ∆S=3.33, Reject: ∆S=2.98 | C2: 修订有效 | ∆S为循环验证 |
| E6 | Ablation: Simple Rubric vs Embedding PCA | 同E5但用不同目标函数 | ∆S | Discovered Rubric明显优于两个baseline | C2: 发现rubric更有效 | 同E5的循环验证问题 |
| E7 | Ablation: w/o R* and w/o MultiAIDE | Tab. 4 | ∆S | 移除任一组件大幅降低∆S | C2: 两组件的必要性 | 小规模消融 |
| E8 | Human evaluation | 364对论文, 3评审者/对, blind, binomial test | Preference rate | 79%偏好修订版 (95% CI: 70.1-79.0%), p<10⁻²² | C3: 人类验证 | 未按论文类别分层报告偏好率 |
| E9 | Glicko2 rating consistency | 20,000 pairwise comparisons, LLM judge | Disagreement rate | Within-model: 19.2-20.3%; 优于人类23% | C3: LLM一致性 | Cross-model >35%差于随机 |
| E10 | NeurIPS consistency replication | Fig. A2 heatmap, 4 LLMs | Disagreement rate | 多数比较优于NeurIPS人类基准 | C3: 附录验证 | 一致性≠准确性 |

## Research-Theme Gap Diagnosis

**未充分验证的核心研究价值声明**:

1. **「发现rubric捕捉了人类评审未捕获的影响力信号」**（Page 7, E1结论）：虽然MAE改善显著，但未证明rubric条目捕捉的是实质性科学质量（而非表面文本特征）。需要在特征级别分析rubric的内容效度。

2. **「LLM修订工具可作为投稿前压力测试」**（Abstract, Conclusion）：压力测试通常暗示对抗性/边界条件测试，但APRES实际执行的是文本清晰度提升。需要更精确地界定APRES的实际功能边界。

3. **「APRES augmentation of peer review ecosystem」**（Conclusion）：该声明未经验证，因为论文未在实际审稿流程中测试APRES。

## Proposed Research Experiments

### P0 Experiments

**PE1: Cross-Model ∆S Validation**
- **Target Claim**: ∆S的提升反映了真实质量改善而非LLM自偏好
- **Hypothesis**: 同模型家族的∆S > 跨模型家族的∆S（如果存在自偏好偏差）
- **Minimal Design**: 用o3修订论文→Gemini 2.5 Pro评估∆S；反之亦然。计算cross-model ∆S与same-model ∆S的比值。
- **Controls/Baselines**: Same-model ∆S (已有)
- **Metrics**: ∆S ratio (cross/same); 如果ratio >0.7则自偏好偏差可接受
- **Success Criterion**: 证明cross-model ∆S仍然为正且与人类偏好相关
- **Estimated Cost**: 1-2天GPU时间
- **Expected Gain**: 高——关闭KI-1和KI-2

**PE2: Rubric Feature Importance Analysis**
- **Target Claim**: 发现的rubric捕捉了有意义的科学质量信号
- **Hypothesis**: Top贡献特征包含实质性科学维度（methodology, novelty）而非仅表面特征（writing style）
- **Minimal Design**: SHAP分析或leave-one-dimension-out消融
- **Controls/Baselines**: Random feature baseline
- **Metrics**: SHAP值; feature排名
- **Success Criterion**: Top-5贡献特征中包含≥2个实质性科学维度
- **Estimated Cost**: 1-2天计算
- **Expected Gain**: 高——关闭KI-3

### P1 Experiments

**PE3: ∆S-Human Preference Correlation**
- **Target Claim**: ∆S与人类判断一致
- **Hypothesis**: ∆S与人类偏好投票率正相关
- **Minimal Design**: 对E8中的364对论文计算∆S，与人类偏好率做Spearman相关
- **Controls/Baselines**: Random score baseline
- **Metrics**: Spearman ρ
- **Success Criterion**: ρ > 0.3, p < 0.05
- **Estimated Cost**: 2-4小时
- **Expected Gain**: 高——关闭KI-2

**PE4: Within-Model vs Cross-Model Consistency Audit**
- **Target Claim**: LLM评审一致性支持APRES修订可靠性
- **Hypothesis**: Within-model consistency的效应量远大于cross-model agreement
- **Minimal Design**: 扩展现有Fig. A2，明确报告并讨论两者差异
- **Controls/Baselines**: 人类评审不一致率23%
- **Metrics**: Within-model DR vs Cross-model DR
- **Success Criterion**: 清晰展示consistency的两个维度及其对修订的不同含义
- **Estimated Cost**: <1小时（现有数据）
- **Expected Gain**: 中——关闭KI-4

## ASCII Diagram — Experiment Upgrade Plan

```text
当前实验体系
    │
    ├── PE2 (P0): Rubric特征重要性 ──→ 揭示rubric内在结构
    │                                        │
    ├── PE1 (P0): 交叉模型∆S ──→ 量化自偏好偏差
    │                                        │
    ├── PE3 (P1): ∆S-人类相关性 ──→ 验证自动化指标
    │                                        │
    └── PE4 (P1): 一致性审计 ──→ 澄清consistency≠reliability
                                                     │
                                                     └──→ [实验体系完备: 方法论风险被系统量化]
```

## Novelty Verification & Related-Work Matrix
## Contribution Novelty Verdict Board (9A)

| Claim ID | Author Contribution Claim | Key Evidence Papers | Novelty Verdict | Why | Confidence | Required Repositioning |
|----------|--------------------------|---------------------|-----------------|-----|------------|------------------------|
| C1 | Agentic search (MultiAIDE) discovers evaluation rubrics predictive of future citation counts | TNCSI (Zhao et al., 2025b), HLM-Cite (Hao et al., 2024), Rubric Refinement for Essay Scoring [10], CritiQ [12] | **partially_overlapping** | Citation prediction via LLM exists (TNCSI, HLM-Cite) but uses fixed criteria. Automated rubric refinement exists (essay scoring [10], data quality [12]) but targets different domains. The combination of agentic search + rubric discovery + citation optimization is novel, but core mechanism (iterative search for evaluation criteria) is not unprecedented. | Medium-High | Differentiate from prompt optimization literature; add comparison to [10][12] in Related Work |
| C2 | Closed-loop paper revision using discovered rubric as objective function | XtraGPT [1], ARISE [11], SWIFT² (Chamoun et al., 2024), R3 (Du et al., 2022) | **partially_overlapping** | LLM-based paper revision exists (XtraGPT [1], SWIFT²). Rubric-guided iterative refinement exists for surveys (ARISE [11]). The novelty is in coupling discovered rubric (from citation prediction) with closed-loop search-based revision—a specific integration not present in prior work. | Medium | Position APRES as a new integration rather than a new category; explicitly compare with XtraGPT [1] (closest competitor in paper revision) |
| C3 | LLM-based evaluation is more consistent than human peer review; revised papers preferred 79% by humans | LLM-as-Reviewer [2], LLM Peer Review Biases [3], LLM-REVal [6], NeurIPS consistency studies (Cortes & Lawrence, 2021; Beygelzimer et al., 2023) | **supported** | The consistency finding (within-model) is robust and well-benchmarked against NeurIPS studies. The 79% human preference is statistically strong (p<10⁻²²). However, cross-model inconsistency (>35%) limits generality. The "reliability for meaningful revisions" inference needs qualification. | High | Qualify the consistency claim: separate within-model consistency from cross-model agreement; add disclaimer about consistency ≠ accuracy |

## Related-Work Taxonomy Matrix (9B)

| Taxonomy Layer | Branch/Leaf | Representative Papers | Common Assumptions | Difference vs This Paper | Novelty Risk Signal |
|---------------|-------------|----------------------|-------------------|--------------------------|---------------------|
| **Root: LLM-based Scientific Paper Evaluation & Revision** | | | | | |
| ├── **Branch 1: Review Generation** | | | | | |
| │   ├── Leaf 1.1: Single-LLM Review | Reviewer2 (Gao et al., 2024), ReviewRobot (Wang et al., 2020) | Predefined review criteria | APRES discovers criteria, not just generates reviews | Low |
| │   ├── Leaf 1.2: Multi-Agent Review | MARG (D'Arcy et al., 2024), TreeReview (Chang et al., 2025), ReviewAgents | Human-like deliberation simulation | APRES uses agents for search/optimization, not deliberation simulation | Low |
| │   └── Leaf 1.3: RL-Trained Reviewers | ReviewRL (Zeng et al., 2025) | RL for review quality | APRES uses search, not RL | Low |
| ├── **Branch 2: Impact Prediction** | | | | | |
| │   ├── Leaf 2.1: Metadata/Graph-based | DGNI (Geng et al., 2022) | Citation graph features | APRES is text-only via rubric | Low |
| │   ├── Leaf 2.2: LLM Text-based | TNCSI (Zhao et al., 2025b), HLM-Cite (Hao et al., 2024), LLM-Metrics | LLM can capture impact signals | APRES discovers rubric for impact; others use fixed features | **Medium** |
| │   └── Leaf 2.3: LLM-as-Judge for Quality | LLM Post-Pub Evaluation (2604.16387), LLM Research Quality [8] | LLM scores correlate with quality | APRES optimizes rubric for citation, not quality per se | Medium |
| ├── **Branch 3: Automated Revision** | | | | | |
| │   ├── Leaf 3.1: Criteria-Guided Revision | XtraGPT [1], SWIFT² (Chamoun et al., 2024) | Predefined writing guidelines | APRES discovers its own criteria | **High** |
| │   ├── Leaf 3.2: Human-in-the-Loop Revision | R3 (Du et al., 2022) | Human feedback needed | APRES is fully automated (closed-loop) | Medium |
| │   └── Leaf 3.3: Iterative Refinement with Rubric | ARISE [11] | Rubric-guided multi-agent refinement | ARISE targets survey generation; APRES targets paper revision | Medium |
| ├── **Branch 4: Evaluation Criteria Discovery** | | | | | |
| │   ├── Leaf 4.1: Prompt Optimization | Prompt Optimization Survey (2502.18746), Prompt breeder (Fernando et al., 2024) | Search for optimal prompts | APRES searches for rubrics (structured criteria), not free-form prompts | Medium |
| │   ├── Leaf 4.2: Rubric Refinement | Essay Rubric Refinement [10], RefGrader (2510.09021) | Iterative rubric improvement | APRES targets scientific impact (citation); others target essay grading / math proofs | Medium |
| │   └── Leaf 4.3: Criteria Mining from Preferences | CritiQ [12] | Agent-mined quality criteria from human pairs | APRES mines from citation data; CritiQ mines from human preferences for data quality | Medium |
| └── **Branch 5: LLM Peer Review Consistency & Bias** | | | | | |
|     ├── Leaf 5.1: LLM-Human Agreement | LLM-as-Reviewer [2], LLM Peer Review Biases [3], LLM-REVal [6] | LLM reviews diverge from human in specific ways | APRES contributes additional consistency evidence (Glicko2) | Low |
|     └── Leaf 5.2: Evaluation Circularity Risks | LLM-Evaluation Tropes [5] | LLM evaluation can be self-reinforcing | APRES's closed-loop design is directly vulnerable to this risk | **High** |

## Head-to-Head Comparison Matrix (9C)

| Ref | Problem/Setting | Method Core | Strongest Overlap Point | Clear Difference | Impact on Final Judgment |
|-----|----------------|-------------|------------------------|------------------|--------------------------|
| [1] XtraGPT | Academic paper revision with criteria-guided intent | Fine-tuned LLM on 140K revision pairs from predefined guidelines | Both do criteria-guided paper revision | APRES discovers criteria autonomously; XtraGPT uses predefined guidelines and requires training data | **High**: Direct competitor in revision; APRES's discovered-rubric approach is a distinct advantage |
| [10] Essay Rubric Refinement | Automated essay scoring rubric optimization | LLM reflect-and-revise on scoring rationales | Both do iterative rubric refinement for scoring | APRES optimizes for citation prediction; [10] optimizes for human score alignment in education | Medium: Shows rubric refinement is a broader technique |
| [11] ARISE | Automated survey generation | Rubric-guided multi-agent iterative refinement | Both use rubric + agent iteration for text improvement | ARISE generates surveys from scratch; APRES revises existing papers | Medium: Same pattern, different task |
| [9] AIDE | ML code optimization via agentic search | Tree-search over code solutions | APRES builds on AIDE's search scaffold | AIDE optimizes code; APRES applies same scaffold to rubric search and paper revision | Low: APRES acknowledges this dependency |
| [5] LLM-Evaluation Tropes | LLM-based IR evaluation validity | Taxonomy of evaluation risks including circularity | Circularity risk is directly applicable to APRES | [5] addresses IR evaluation; APRES faces the same structural risk in paper evaluation | **High**: This is the strongest external risk signal for APRES's methodology |

## ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
LLM-based Scientific Paper Evaluation & Revision (Root)
│
├── Branch 1: Review Generation
│   ├── Leaf 1.1: Single-LLM Review ── Reviewer2, ReviewRobot
│   ├── Leaf 1.2: Multi-Agent Review ── MARG, TreeReview, ReviewAgents
│   └── Leaf 1.3: RL-Trained Reviewers ── ReviewRL
│
├── Branch 2: Impact Prediction
│   ├── Leaf 2.1: Metadata/Graph-based ── DGNI
│   ├── Leaf 2.2: LLM Text-based ── TNCSI, HLM-Cite, LLM-Metrics [★APRES sits here with rubric discovery]
│   └── Leaf 2.3: LLM-as-Judge ── Post-Pub Eval [8]
│
├── Branch 3: Automated Revision
│   ├── Leaf 3.1: Criteria-Guided ── XtraGPT [1], SWIFT² [★APRES competes here]
│   ├── Leaf 3.2: Human-in-the-Loop ── R3
│   └── Leaf 3.3: Rubric-Iterative ── ARISE [11]
│
├── Branch 4: Evaluation Criteria Discovery
│   ├── Leaf 4.1: Prompt Optimization ── PromptBreeder, PromptOpt Survey
│   ├── Leaf 4.2: Rubric Refinement ── Essay Rubric [10], RefGrader [★APRES pioneered in scientific impact domain]
│   └── Leaf 4.3: Criteria Mining ── CritiQ [12]
│
└── Branch 5: LLM Review Consistency & Bias
    ├── Leaf 5.1: LLM-Human Agreement ── LLM-as-Reviewer [2], Biases [3], LLM-REVal [6]
    └── Leaf 5.2: Circularity Risks ── LLM-Evaluation Tropes [5] [⚠APRES is vulnerable]

★ = APRES's primary positioning    ⚠ = Identified risk
```

## Contribution-Level Novelty Conclusion

**C1 (Rubric Search for Citation Prediction): PARTIALLY OVERLAPPING** — LLM-based citation prediction is an established area (TNCSI, HLM-Cite), and iterative rubric/prompt refinement is a known technique (essay scoring [10], CritiQ [12]). APRES's contribution is the specific integration: applying agentic search (MultiAIDE) to discover evaluation rubrics optimized for citation prediction on scientific papers. This is a novel application of existing techniques rather than a new technique.

**C2 (Closed-Loop Paper Revision): PARTIALLY OVERLAPPING** — LLM-based paper revision is well-established (XtraGPT [1], SWIFT²), and rubric-guided iterative refinement exists (ARISE [11]). APRES's novelty lies in the coupling: using a *discovered* (not predefined) rubric from citation prediction as the objective function for revision. This integration is not present in prior work but the individual components are.

**C3 (Empirical Validation): SUPPORTED** — The human evaluation (79% preference, p<10⁻²², blind, 364 pairs) is methodologically strong. The consistency replication of NeurIPS experiments is a valuable contribution. However, the inference from consistency to revision reliability requires qualification (consistency ≠ accuracy), and the cross-model inconsistency (>35%) limits the generality claim.

## References
[1] XtraGPT: Context-Aware and Controllable Academic Paper Revision 2505.11336

[2] LLM-as-a-Reviewer: Benchmarking Their Ability, Divergence, and Prompt Injection Resistance as Paper Reviewers 2605.25415

[3] When Your Reviewer is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer Review 2509.09912

[4] Do LLMs Favor LLMs? Quantifying Interaction Effects in Peer Review 2601.20920

[5] LLM-Evaluation Tropes: Perspectives on the Validity of LLM-Evaluations 2504.19076

[6] LLM-REVal: Can We Trust LLM Reviewers Yet? 2510.12367

[7] Unveiling the Merits and Defects of LLMs in Automatic Review Generation for Scientific Papers 2509.19326

[8] Research quality evaluation by AI in the era of Large Language Models: Advantages, disadvantages, and systemic effects 2506.07748

[9] AIDE: AI-Driven Exploration in the Space of Code 2502.13138

[10] Automated Refinement of Essay Scoring Rubrics for Language Models via Reflect-and-Revise 2510.09030

[11] ARISE: Agentic Rubric-Guided Iterative Survey Engine for Automated Scholarly Paper Generation 2511.17689

[12] CritiQ: Mining Data Quality Criteria from Human Preferences 2502.19279

## Scores
**评分理由（优先考虑研究价值+新颖性）**:

本文的研究价值在于首次将智能体rubric搜索与闭环论文修订整合到一个统一框架中，并对其实证效果进行了多维度验证（自动化指标+人类偏好+一致性分析）。人类评估（79%偏好率，p<10⁻²²）的设计和执行质量较高。

扣分主要来自：
- **新颖性**（C1/C2均为partially_overlapping）：核心组件（智能体搜索、rubric优化、LLM修订）在各自领域已有先例，APRES的创新在于整合而非发明新机制。这本身不是致命缺陷，但限制了研究的突破性。
- **方法论风险敞口**（KI-1至KI-4）：循环自增强偏差未讨论、∆S指标存在循环验证、rubric内容效度未验证、一致性→可靠性的逻辑跳跃——这些风险在检索文献中已有明确警示，但本文未能充分应对。这些问题的存在降低了核心结论的可信度。
- **声明精确性**（KI-5）：多处措辞的声明强度超出了实验证据的边界。

**正向因素**: 工程实现扎实、人类评估方法严谨、局限性讨论坦诚（尽管不完整）、对Goodhart's Law的自我意识。

## Post-Revision Target: [7.5, 8.5]/10

**上限假设**: 所有P0/P1问题得到充分解决后：
- 自增强偏差被系统讨论和定量评估（交叉模型∆S实验）
- Rubric特征重要性分析揭示了其内在结构
- ∆S与人类偏好的相关性得到验证
- 写作声明精确化到与实验证据一致的水平
- 在此基础上，研究的整合创新价值得到更准确的定位

**下限假设**: 仅解决P0问题但P1不完整的情况下，核心方法论风险得到缓解但rubric可解释性和文献定位仍可改进。

## Score Breakdown

| 维度 | 当前评分 | 修订后目标 | 说明 |
|------|---------|-----------|------|
| 研究价值/贡献 | 7.0 | 8.0 | 将LLM辅助论文修订推进了有意义的一步 |
| 新颖性强度 | 5.5 | 7.0 | C1/C2为partially overlapping；整合新颖但非突破性 |
| 方法论严谨性 | 6.0 | 8.0 | 循环验证风险为主要减分项 |
| 实证验证充分性 | 7.5 | 8.5 | 人类评估设计优秀；rubric内容效度待补 |
| 写作/可复现性 | 6.5 | 8.0 | 声明精确性需提升；工程细节充足 |
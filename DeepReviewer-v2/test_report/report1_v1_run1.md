## Summary
# Final Review Report

## Summary

本文提出APRES，一个利用LLM Agent自动发现论文评审量规（rubric）并据此进行闭环论文修订的两阶段框架。Stage 1通过MultiAIDE agentic search发现一个能通过负二项回归预测论文未来引用数的rubric（R*）；Stage 2将该rubric作为优化目标，驱动"Rewriter" LLM迭代修订论文文本以提升预测影响力分数，约束为仅修改表达层面而不改变科学内容。在26,707篇ICLR/NeurIPS论文上的实验表明：(a) 发现的rubric在引用预测MAE上优于embedding-based baseline；(b) APRES修订的论文在盲评中以79%的比率被人类专家偏好；(c) 基于Glicko2的LLM评估一致性优于人类审稿人。

**核心贡献：** (C1) 首次将agentic search用于发现预测引用影响力的评审rubric；(C2) 将被发现的rubric作为闭环修订系统的优化目标；(C3) 大规模实证验证，包括human preference study和reviewer consistency实验。

**总体评价：** 这是一个设计良好的系统工程论文，在AI辅助学术写作这一重要方向上做出了有价值的探索。论文的核心洞见——LLM不应仅模仿人类评审，而应发现人类未察觉的评估信号——具有启发性。然而，论文在novelty声称的精确性、关键数字的透明度、以及Goodhart's Law等根本性风险的讨论深度方面存在明显不足。修订后预期可达到7.5-8.5/10的水平。

## Strengths
1. **问题选择具有现实意义。** 论文瞄准了学术出版的痛点——同行评审的不一致性和可扩展性危机——并提出了一个务实的解决方案：用AI辅助作者在投稿前改进论文表达质量。这一方向与AAAI 2026和ICLR 2025等会议的AI辅助审稿试点项目高度契合，时效性强。

2. **两阶段设计的工程完整性。** Stage 1（rubric发现）和Stage 2（闭环修订）之间的逻辑衔接紧密：Stage 1产出的R*直接作为Stage 2的优化目标，形成了从"发现什么重要"到"据此改进"的完整pipeline。这种设计比单纯的LLM prompt engineering或one-shot revision更加系统化。

3. **大规模实证验证。** 在26,707篇论文上的实验规模令人印象深刻。特别是human evaluation（364对盲评，79%偏好率，p<10^-22）和Glicko2一致性实验（Appendix A）为论文的核心声称提供了有力的经验支撑。

4. **透明的局限性讨论。** 论文在Discussion中坦诚承认了引用计数的偏差、Goodhart's Law风险、文本-only的输入限制以及无法保证科学内容完全不被修改。这种诚实态度提升了论文的科学可信度。

5. **附录内容丰富。** 附录中的discovered rubric、prompt模板、数据集描述和consistency实验提供了较高的可复现性。尤其是60+条目的discovered rubric本身就是一个有价值的研究产出。

6. **diff-based editing机制。** 使用Aider的search/replace块而非全文重写的技术选择具有工程实用性——避免了模型过度缩短论文的问题，同时可追踪每次编辑。

## Weaknesses
**W1 — Novelty声称过于宽泛（严重性：高）。** 论文多处使用"novel agentic framework"和"novel method"等未加限定的声称（Page 1 - Abstract；Page 1 - Introduction P2）。事实上，已有多个LLM-based review系统存在（ReviewerToo [1]同时使用structured evaluation criteria测量review consistency；MLR-Bench [2]使用LLM reviewers和rubrics进行论文评估；MARG [3]使用multi-agent框架生成review feedback）。APRES的独特贡献在于"将rubric发现与闭环修订集成"，而非agentic框架本身。建议将novelty声称限定为"first to integrate automated rubric discovery with closed-loop revision"。

**W2 — 核心数字"19.6% MAE improvement"的计算方式不透明（严重性：高）。** 论文在Abstract、Introduction和Discussion中多次引用19.6%这一数字，但从未明确其计算方式（Page 6 - Citation Number Prediction Results）。从Figure 2数据推算，不同LLM配置下的MAE差异显著（o3: 1.92；Gemini 2.5 Pro: 1.96；o1: 2.25），且对比的baseline不明确（"next best baseline"究竟指Paper embedding+PCA的2.65？还是Prompt breeder的最佳值？）。这违反了可复现性要求——读者无法独立验证该数字。

**W3 — Goodhart's Law风险的讨论深度不足（严重性：高）。** 论文的核心设计——用citation-predictive rubric作为优化目标驱动revision——与Goodhart's Law存在根本性张力。Discussion中对此的讨论仅一段（Page 9 - From Mimicking Humans to Predicting Impact），且仅将Goodhart's Law作为外部风险提及，未分析APRES设计中哪些机制缓解了风险、哪些可能加剧风险。形式化研究（El-Mhamdi & Hoang, 2024 [4]）提供了strong vs weak Goodhart的分析框架，论文完全可以借鉴。

**W4 — Human evaluation的方法论细节缺失（严重性：中）。** 364对论文的采样策略未报告（是否跨类别均衡？Page 9 - Human Evaluation of Revised Papers），偏好原因的呈现停留在word cloud层面缺乏定量统计。此外，79%这个数字表述为"majority preference"但3/3一致性偏好仅47.8%——两种口径的差距应当被透明呈现。

**W5 — Introduction与实验之间的alignment不足（严重性：中）。** Introduction声称APRES可"reduce the inherent randomness of peer review"（Page 2 - Introduction P4），但实验仅测量了LLM内部的Glicko2一致性，未直接测试APRES修订是否在真实审稿中降低了随机性。"human-in-the-loop systems"的愿景（Page 2 - Introduction P4）也缺乏实验支撑。

**W6 — Related Work组织方式为paper-by-paper列表（严重性：低）。** 第2节的"LLMs for review generation and author assistance"以时间顺序罗列论文（Page 2 - Related Work），而非按方法类别/比较维度组织，读者难以快速把握领域全景和APRES的独特定位。

## Key Issues
### Issue 1 — 19.6% MAE improvement的可验证性（严重性：高）

**证据锚点：** Page 6 - Citation Number Prediction Results；Page 1 - Abstract。

**问题：** 论文声称"19.6% improvement in MAE over the next best baseline"，但未提供：
- 计算公式（relative reduction? absolute? 跨模型平均方式?）
- 与哪个baseline比较（PCA的2.65? Prompt breeder的最佳值?）
- 使用哪种LLM配置的结果（o3? 四模型平均?）

**科学风险：** 如果19.6%的计算方式不透明，读者无法独立验证论文的核心结论之一，影响可复现性和可信度。

**修复路径：** 在Section 4.1中明确写出：
- 公式：$\text{improvement} = (\text{MAE}_\text{baseline} - \text{MAE}_\text{APRES}) / \text{MAE}_\text{baseline} \times 100\%$
- baseline选择依据：选择best non-agentic baseline（Paper embedding+PCA, MAE=2.65）
- 汇报四模型分别的improvement以及平均
- 在Figure 2 caption中注明initial rubric和iteration计数方式

### Issue 2 — Novelty声称缺乏限定（严重性：高）

**证据锚点：** Page 1 - Abstract ("novel method")；Page 1 - Introduction P2 ("novel agentic framework")。

**问题：** 外部证据（ReviewerToo [1]、MLR-Bench [2]、MARG [3]）表明LLM-based review generation、rubric-guided evaluation和paper revision系统已存在。APRES的true novelty在于集成，而非单一组件。

**科学风险：** 过度声称可能被审稿人直接质疑novelty不足，掩盖论文真正的集成创新价值。

**修复路径：** 将"novel method"替换为"first method to integrate automated rubric discovery with closed-loop paper revision"，在Introduction中明确指出集成novelty所在，并引用最接近的工作进行差异化分析。

### Issue 3 — Goodhart's Law与优化闭环的根本张力（严重性：高）

**证据锚点：** Page 9 - Discussion "From Mimicking Humans to Predicting Impact"。

**问题：** APRES使用citation-predictive rubric作为revision优化目标，形成closed-loop optimization。根据Goodhart's Law形式化理论（El-Mhamdi & Hoang, 2024 [4]），当proxy与true goal的差异呈重尾分布时，过度优化proxy会损害true goal。APRES缺乏对这一风险的定量分析。

**科学风险：** 如果rubric score与实际科学质量的discrepancy是重尾的，closed-loop优化可能导致"style over substance"——论文表面分数提高但科学贡献未增强。

**修复路径：** (a) 扩展Discussion中Goodhart分析，借鉴形式化框架讨论APRES的风险等级；(b) 建议未来实验：测量rubric score提升与independent quality rating之间的correlation，评估是否存在divergence。

### Issue 4 — LLM reviewer偏差对rubric质量的影响未讨论（严重性：中）

**证据锚点：** Page 5 - Section 3.1 rubric search procedure；外部证据[5][6]。

**问题：** 外部研究[5]表明LLM review存在systematic blind spots——偏向technical validity而忽视novelty assessment。如果LLM reviewer自身有偏差，那么通过其评分训练的rubric也可能继承这些偏差。论文未讨论这一风险。

**科学风险：** 发现的rubric可能系统性地低估某些论文类型（如高度novel但技术上不polished的工作），从而在revision阶段误导优化方向。

**修复路径：** 在Discussion中增加"rubric bias audit"段落，建议按paper quality strata和research domain分析rubric分数的分布，评估是否存在系统性偏差。

## Actionable Suggestions
### S1 — 透明化核心数字的计算方式（Must, P0）

在Section 4.1的开头或"Citation Number Prediction Results"段落中增加一个显式的计算方法说明段落：

> **建议插入文本：** "We report improvement as the relative reduction in MAE: $\text{Improvement} = (\text{MAE}_{\text{best baseline}} - \text{MAE}_{\text{APRES}}) / \text{MAE}_{\text{best baseline}}$. The best non-agentic baseline is Paper embedding + PCA (MAE=2.65, averaged across four LLMs). With MultiAIDE achieving mean MAE=2.13 across o1/o3/Gemini Flash/Gemini Pro, this yields a 19.6% improvement. Per-model improvements are: o3 27.5%, Gemini 2.5 Pro 26.0%, o1 15.1%, Gemini 2.5 Flash 13.2%."

### S2 — 限定novelty声称（Must, P0）

在Abstract和Introduction中，将"novel method/agentic framework"替换为精确的差异化表述：

> **建议替换（Abstract）：** "In this paper, we introduce APRES, a method that integrates automated rubric discovery with closed-loop paper revision—to our knowledge, the first system to combine these two components for improving scientific manuscripts."

> **建议替换（Introduction P2, Page 1 - line 9）：** 参见PDF注释f0554f26中的导师修订版本。

### S3 — 深化Goodhart's Law讨论（Must, P0）

在Section 5 "Discussion"中扩展Goodhart's Law分析（Page 9 - line 6），参见PDF注释cdae780b中的导师修订版本。核心要点：(a) 分析APRES设计中缓解和加剧Goodhart风险的机制；(b) 引用形式化分析框架（El-Mhamdi & Hoang, 2024 [4]）；(c) 提出未来验证方案。

### S4 — 补充Human evaluation方法论细节（Must, P0）

在Section 4.2 "Human Evaluation of Revised Papers"（Page 9 - line 2）中补充：
- 364对论文的采样策略（跨Clear Accept/Borderline/Clear Reject的分布）
- 同时报告3/3一致性偏好率（47.8%）和majority偏好率（78.8%）
- 偏好原因的定量统计（clarity/narrative/contribution framing各占比）

参见PDF注释37a15e08中的具体修改建议。

### S5 — 讨论LLM reviewer偏差对rubric质量的影响（Nice-to-have, P1）

在Discussion中增加一段（约150词），讨论LLM reviewer的已知偏差（如[5][6]所记录的）如何可能影响discovered rubric的质量，并提出audit方案（按paper category/domain分析rubric分数的系统性差异）。

### S6 — 重组Related Work为类别结构（Nice-to-have, P1）

将Section 2的"LLMs for review generation and author assistance"重组为三类：
(a) Review generation methods (template → multi-agent → RL)
(b) Impact prediction methods (bibliometric → embedding → LLM-based)
(c) Automated revision methods (summarization → feedback → closed-loop)

参见PDF注释c2473b1c中的具体重组建议。

### S7 — 修正Introduction P4中的过度声称（Must, P0）

将"LLMs can serve as a reliable tool to reduce the inherent randomness of peer review"替换为"LLM-based evaluation can yield more consistent assessments than individual human reviewers (Appendix A)"。删除或限定"human-in-the-loop systems"的表述以匹配实际实验设计。参见PDF注释69fa9c5f。

### S8 — 结论收紧（Must, P0）

重写Conclusion（Page 10 - line 4），明确区分已验证发现与愿景声明。参见PDF注释ced60da2中的导师修订版本。

## Storyline Options + Writing Outlines
### 当前Storyline诊断

当前Introduction的叙事结构为：
- P1：同行评审危机 → LLM机遇 → LLM风险 → 研究空白 → 方法约束
- P2：APRES框架介绍 → 两阶段方法 → 技术细节
- P3：验证预览 → 贡献暗示
- P4：领域定位 → 工作愿景

**主要问题：** (1) P1承载过多功能（危机+机遇+风险+空白+方法），读者在进入P2前已被信息淹没；(2) P3和P4之间缺乏清晰的"贡献列表"，读者在Introduction末尾仍不确定C1/C2/C3是什么；(3) "novel"声称过于宽泛；(4) Introduction结尾的"human-in-the-loop"愿景与实验内容不匹配。

### 推荐Storyline：从"审稿危机"到"可操作的修订工具"

**核心叙事弧：** 审稿系统不可靠 → LLM可以提供一致反馈但存在风险 → 我们需要的不仅是模仿人类评审，而是发现新的评估信号 → APRES通过两阶段设计实现：先发现什么预测影响力，再据此修订 → 实验表明修订有效且被人类偏好。

### Abstract Outline（4-5句结构）

- **S1 (Problem+Domain):** 同行评审不一致性阻碍科学传播质量提升。
- **S2 (Significance/Challenge):** LLMs提供可扩展反馈但直接使用存在风险（修改科学内容、风格偏差）。
- **S3 (Prior Gap):** 缺少一种能在保护科学内容的前提下，利用LLM系统化改进论文表达的方法。
- **S4 (Proposed Method):** APRES通过两阶段agentic pipeline——先发现预测引用影响力的评审rubric，再将其作为闭环修订的优化目标——实现约束性论文改进。
- **S5 (Key Result+Bounded Claim):** 在26,707篇论文上，APRES发现rubric的引用预测MAE比最佳embedding baseline低19.6%；APRES修订的论文在79%的盲评中被人类专家偏好（3/3一致性47.8%）。结果表明LLM可作为投稿前"压力测试"工具，但引用计数是影响力不完全代理。

### Introduction Outline（逐段计划）

**P1 — 危机与机遇（保持1段落）**
- 角色：建立紧迫感，引入LLM作为解决方案，明确风险
- 目标声称：同行评审面临可扩展性和一致性危机；LLM可提供规模化反馈但需谨慎使用
- 过渡逻辑：以"a critical unresolved challenge is how to harness LLMs for constructive feedback while preserving scientific content"结尾，桥接P2

**P2 — APRES方案与贡献（保持1段落）**
- 角色：介绍APRES的两阶段设计，明确贡献列表
- 目标声称：(C1) rubric discovery via agentic search，(C2) closed-loop revision with content constraints，(C3) large-scale empirical validation
- 过渡逻辑：以"Figure 1 provides an overview of the framework"结尾

**P3 — 验证预览与结果摘要（保持1段落）**
- 角色：预览三项实验（rubric search, paper improvement, reviewer consistency）的核心结果
- 目标声称：定量呈现19.6%、79%等关键数字（附带计算方式说明）
- 过渡逻辑：以结果的意义总结结尾

**P4 — 领域定位与谨慎展望（保持1段落）**
- 角色：将APRES定位于AI辅助审稿的讨论中，明确不是替代人类审稿人
- 目标声称：LLM可以提供一致性baseline，但最终判断应由人类专家做出
- 注意：不宣称"reduces randomness of peer review"，不引入未实验的"human-in-the-loop"概念

### 标题建议

当前标题："APRES: An Agentic Paper Revision and Evaluation System"

建议修改为更信息丰富的版本：
> **"APRES: Discovering Predictive Rubrics for Automated Scientific Paper Revision"**

理由：(1) 保留系统名称APRES；(2) "Discovering Predictive Rubrics"突出Stage 1的创新性；(3) "Automated Scientific Paper Revision"明确任务域；(4) 避免空洞的"Agentic...System"表述。

## Priority Revision Plan
### P0（投稿前必须完成）

| 项目 | 对应Issue | 工作量 | 预期收益 |
|------|----------|--------|---------|
| 透明化19.6%计算方式（Section 4.1） | Issue 1 | 低（约1小时） | 消除核心数字的不可验证性，提升可信度 |
| 限定novelty声称（Abstract + Introduction P2） | Issue 2 | 低（约30分钟） | 减少审稿人对overclaim的质疑，精准呈现贡献 |
| 深化Goodhart's Law讨论（Discussion） | Issue 3 | 中（约2小时+文献阅读） | 展示对根本性风险的理解深度，提升论文成熟度 |
| 补充Human evaluation采样策略与定量统计（Section 4.2） | W4 | 低（约1小时） | 提升实验严谨性，消除方法论疑虑 |
| 修正Introduction P4过度声称 | W5 | 低（约30分钟） | 确保声称与实验证据对齐 |
| 重写Conclusion（Page 10） | S8 | 低（约30分钟） | 区分验证发现与愿景，保持科学严谨 |

### P1（强烈建议，提升论文竞争力）

| 项目 | 对应Issue | 工作量 | 预期收益 |
|------|----------|--------|---------|
| 重组Related Work为类别结构 | W6 | 中（约2小时） | 提升可读性，清晰展示APRES定位 |
| 增加LLM reviewer偏差讨论（Discussion） | Issue 4 | 中（约3小时+文献阅读） | 展示对方法局限性的深度反思 |
| 重组Introduction段落结构 | Storyline建议 | 中（约3小时） | 提升叙事流畅度，增强读者留存 |

### P2（可选，提升长远影响力）

| 项目 | 对应Issue | 工作量 | 预期收益 |
|------|----------|--------|---------|
| 增加rubric bias audit实验 | Issue 4 | 高（需额外实验） | 增强方法的可信度和公平性 |
| 增加post-hoc content preservation验证 | Limitations | 高（需额外实验） | 消除科学内容意外修改的担忧 |
| 补充跨domain泛化性实验 | W5 | 高（需额外实验） | 验证APRES在非ML领域的适用性 |

## Experiment Inventory & Research Experiment Plan
### A. 已完成实验清单

| Exp ID | 目标/假设 | 设置 | 指标 | 主要结果 | 支撑声明 | 当前局限 |
|--------|----------|------|------|---------|---------|---------|
| E1 | Rubric search discovers criteria predictive of future citations | 26,707篇ICLR/NeurIPS论文；负二项回归；MultiAIDE search | MAE | MultiAIDE MAE≈1.92-2.30 vs PCA 2.65 | C1（rubric发现） | 19.6%计算不透明；rubric bias未审计 |
| E2 | Prompt breeder baseline对比 | 与E1相同设置 | MAE | MultiAIDE优于Prompt breeder | C1 | 公平性存疑（代码级search vs prompt演化） |
| E3 | Paper improvement via discovered rubric | Test set；diff-based editing；120 iterations | ΔS（rubric score change） | Borderline ΔS=3.33；Reject ΔS≈3.0 | C2（闭环修订） | ΔS是自评指标，非独立评估 |
| E4 | Human preference evaluation | 364对论文；3人/对盲评 | 偏好率 | 79% majority；47.8% 3/3一致 | C2+C3 | 采样策略未报告；偏好原因仅word cloud |
| E5 | Glicko2 rating与conference decision相关性 | Test set；20,000次pairwise比较 | Rating vs decision分布 | 高rating对应高acceptance | C3（LLM评估可靠性） | 仅相关性证据，非因果 |
| E6 | LLM reviewer consistency vs human | 四模型两两比较；disagreement rate | DR（%） | LLM 19.2-35.1% vs Human 23-25.9% | C3 | 跨模型family差异大；random baseline 35.1% |
| E7 | Ablation of rubric & search | w/o R*, w/o MultiAIDE | ΔS | 移除任一组件显著降低ΔS | C1+C2 | 仅ablation，未做controlled experiment |

### B. 研究主题差距诊断

1. **新知识主张（rubric发现）：** E1验证了discovered rubric优于embedding baseline，但未分析rubric本身的内容质量——哪些维度最predictive？rubric是否引入了LLM reviewer的systematic bias [5]？
2. **可复现性/可重用性：** 论文提供了prompt和rubric（Appendix E/F），但缺少对revision质量的post-hoc验证机制。无法保证科学内容未被意外修改。
3. **对实践/理解的潜在影响：** E4展示了人类偏好，但未测试APRES修订是否在真实审稿流程中改善论文命运。"stress-test"工具的实际效用需要通过field study验证。

### C. 建议补充实验

#### P0实验（投稿前建议完成）

**PE1 — Rubric Bias Audit**
- 目标声明：验证discovered rubric是否存在对特定paper type的系统性偏差
- 假设：LLM reviewer的已知偏差（重technical validity轻novelty [5][6]）可能传播至discovered rubric
- 最小设计：按paper category（Clear Accept/Borderline/Clear Reject）和research domain（CV/NLP/Theory/Systems）分组，报告各组rubric分数分布；检验是否存在统计显著差异
- 对照：human reviewer scores作为ground-truth参考
- 指标：按组的rubric分数均值±std；ANOVA或Kruskal-Wallis检验
- 成功标准：各组的rubric分数排序与human scores排序一致（Spearman ρ>0.5）
- 预估工作量：2-3天（数据分析，无需额外LLM调用）
- 预期收益：消除rubric bias担忧，提升方法可信度

#### P1实验（建议补充以增强论文竞争力）

**PE2 — Goodhart Divergence Measurement**
- 目标声明：量化rubric score优化与实际paper quality之间的divergence
- 假设：过度优化rubric score可能导致"style over substance"
- 最小设计：选取20篇修订后的论文，邀请3位独立评审人进行blind quality rating（1-10），计算人类评分与rubric score之间的Spearman correlation；按revision iteration绘制两条曲线
- 指标：Spearman ρ, 两条曲线的divergence trend
- 成功标准：ρ>0.4且无显著下降趋势
- 预估工作量：1周（human study）
- 预期收益：直接回应Goodhart's Law担忧，显著提升论文成熟度

**PE3 — Post-hoc Content Preservation Audit**
- 目标声明：量化修订过程中科学内容的保持率
- 假设：diff-based editing和prompt约束能有效防止科学内容修改
- 最小设计：随机抽取50篇修订论文，自动提取original和revised版本中的数值型结果（表格中数字），计算一致率
- 指标：数值一致率（%）
- 成功标准：一致率>99%
- 预估工作量：1-2天（自动化脚本）
- 预期收益：消除内容修改担忧，增强方法实用性论证

#### P2实验（可选，提升长远影响力）

**PE4 — Cross-Domain Generalization**
- 目标声明：验证APRES在非ML领域的适用性
- 最小设计：在小规模非ML论文数据集（如生物信息学或材料科学，约500篇）上测试rubric search和revision
- 预估工作量：1-2周

### D. ASCII Diagram — Experiment Upgrade Plan

```text
当前证据链
├── E1-E2: Rubric预测 → C1 ✓（但计算透明度需改进）
├── E3-E4: 修订效果 → C2 ✓（但Goodhart风险未量化）
├── E5-E6: 评估一致性 → C3 ✓（但跨模型family差异大）
└── E7: Ablation → C1+C2 ✓

建议升级路径
Stage 1（投稿前P0）: PE1 Rubric Bias Audit ─→ 消除偏差担忧
Stage 2（投稿前P0）: 透明化计算 + 修正声称 ─→ 消除可复现性障碍
Stage 3（如时间允许P1）: PE2 Goodhart测量 + PE3 Content Audit ─→ 解决两大根本风险
Stage 4（未来P2）: PE4 Cross-Domain ─→ 扩展影响力
```

## Novelty Verification & Related-Work Matrix
### 9A. Contribution Novelty Verdict Board

| Claim ID | 作者贡献声明 | 关键证据论文 | Novelty裁决 | 理由 | 置信度 | 需重新定位 |
|----------|------------|-------------|------------|------|--------|-----------|
| C1 | Agentic search discovers review rubric predictive of future citations | ReviewerToo [1]（使用structured criteria评估但不发现rubric）；MLR-Bench [2]（使用LLM reviewers+rubrics但不自动发现）；TNCSI_SP（LLM预测引用但不搜索rubric） | **partially_overlapping** | Rubric搜索的agentic方法本身是novel的，但"LLM评估预测引用"这一概念已有TNCSI_SP [7]和HLM-Cite [8]等先行工作。APRES的增量在于用搜索替代直接text-to-citation映射 | 中 | 将C1精确定位为"first to use agentic search to discover evaluation dimensions predictive of citations, rather than learning a direct text-to-impact mapping" |
| C2 | Closed-loop revision system using discovered rubric as optimization target | R3 [9]（human-in-the-loop迭代修订）；XtraGPT [10]（context-aware academic revision）；PROF [11]（feedback generation via simulated revisions） | **partially_overlapping** | 闭环修订的概念在R3和PROF中已有探索。APRES的增量在于：(a) rubric自动发现作为优化目标（而非人工定义），(b) 完全自动化（无human-in-the-loop），(c) diff-based editing约束 | 中 | 强调three-way differentiation：自动发现rubric + 全自动闭环 + content-preservation constraint |
| C3 | Large-scale empirical validation: 79% human preference, LLM consistency > human | Thakkar et al. [12]（ICLR 2025 feedback study）；ReviewerToo [1]（81.8% accuracy vs 83.9% human） | **supported** | 79% human preference和Glicko2 consistency实验的规模和方法论在该领域中较为突出。ReviewerToo [1]虽报告了类似的accept/reject accuracy，但未涉及human preference for revised papers | 高 | 无需重新定位，但建议在Discussion中主动对比ReviewerToo的findings |

### 9B. Related-Work Taxonomy Matrix

| 分类层级 | 分支/叶子 | 代表论文 | 共同假设 | 与本文差异 | Novelty风险信号 |
|---------|----------|---------|---------|-----------|---------------|
| Root: AI辅助学术出版 | | | | | |
| ├─ Branch 1: 审稿生成 | | | LLM可生成类人审稿意见 | APRES不生成传统审稿，而是发现rubric并用于修订 | 低 |
| │  ├─ Leaf 1.1: Template-based | ReviewRobot, Yuan et al. | 审稿有固定结构 | 非LLM驱动的早期方法 | 无风险 |
| │  ├─ Leaf 1.2: Multi-agent deliberation | MARG [3], TreeReview | 多Agent讨论可提高审稿质量 | APRES使用agentic search但目标不同 | 低 |
| │  └─ Leaf 1.3: RL-based reviewer | ReviewRL | RL可学习审稿策略 | APRES不使用RL | 低 |
| ├─ Branch 2: 影响力预测 | | | 论文内容/元数据可预测影响力 | APRES通过rubric间接预测而非直接映射 | 中 |
| │  ├─ Leaf 2.1: Bibliometric | DGNI, Thelwall et al. | 引用图和元数据信号 | APRES使用文本+LLM而非引用网络 | 无风险 |
| │  ├─ Leaf 2.2: LLM text-to-impact | TNCSI_SP [7], HLM-Cite [8] | LLM可从标题/摘要预测引用 | APRES通过rubric scores作为中间表示 | 需差异化 |
| │  └─ Leaf 2.3: LLM parametric memory | LLM-Metrics | LLM训练数据中编码了论文影响力 | APRES实时评估而非依赖预训练记忆 | 低 |
| ├─ Branch 3: 论文修订 | | | LLM可改进论文文本质量 | APRES使用发现的rubric作为优化信号 | 中 |
| │  ├─ Leaf 3.1: Summarization-based | PEGASUS | 修订≈摘要重写 | APRES使用diff-based local editing | 无风险 |
| │  ├─ Leaf 3.2: Multi-agent feedback | SWIFT, LLM-collaboration | 多Agent反馈→修订 | APRES是closed-loop optimization而非open-loop feedback | 低 |
| │  └─ Leaf 3.3: Human-in-the-loop iterative | R3 [9], PROF [11] | 人类参与迭代修订 | APRES是全自动闭环，无人干预 | 需差异化 |
| └─ Branch 4: 审稿一致性评估 | | | 审稿随机性是已知问题 | APRES提供LLM一致性作为baseline | 低 |
|    ├─ Leaf 4.1: Human consistency studies | NeurIPS 2014/2021 | 人类审稿有~23%分歧 | APRES提供LLM对比数据 | 无风险 |
|    └─ Leaf 4.2: LLM reviewer benchmarking | ReviewerToo [1], PRISM [13], Mind the Blind Spots [5] | LLM审稿有系统偏差 | APRES未深入分析LLM reviewer偏差 | 需补充分析 |

### 9C. Head-to-Head Comparison Matrix

| Ref | 问题/设置 | 方法核心 | 最强重叠点 | 明确差异 | 对最终判断的影响 |
|-----|----------|---------|-----------|---------|----------------|
| [1] ReviewerToo | LLM辅助审稿；ICLR 2025；1,963篇 | Modular framework；specialized reviewer personas；structured criteria | 使用structured evaluation criteria评估论文；测量LLM-human agreement | 不发现rubric；不进行论文修订；使用predefined criteria | 限制C3中"LLM一致性"声称的novelty——需承认ReviewerToo已有类似发现 |
| [2] MLR-Bench | LLM agents做ML research；201 tasks | LLM reviewers + rubrics for paper evaluation | 使用LLM reviewers结合rubrics进行论文评估 | 用于benchmarking AI agents而非author assistance；rubrics是human-designed而非discovered | 限制C1——rubric-guided LLM evaluation概念已有先行工作 |
| [7] TNCSI_SP | 新生儿论文引用预测 | LLM fine-tuned on title+abstract→TNCSI score | 使用LLM从论文文本预测影响力 | 直接text-to-score，不经过rubric中间表示 | 限制C1——LLM-based citation prediction概念不new |
| [10] XtraGPT | 学术论文修订 | Fine-tuned LLMs；context-aware；140K instruction-response pairs | 自动化学术论文修订 | human-AI collaboration范式；不涉及rubric discovery或closed-loop optimization | 限制C2——学术论文自动修订领域已活跃 |
| [5] Mind the Blind Spots | LLM审稿的focus分布分析 | 676篇ICLR reviews；facet-level evaluation | 分析LLM review quality | 发现LLM偏向technical validity而忽视novelty——APRES未讨论此偏差的影响 | 影响C1/C3的可靠性讨论 |

### Contribution-level Novelty Conclusion

- **C1 (Rubric Discovery):** **partially_overlapping** — 将LLM用于citation prediction的概念（TNCSI_SP, HLM-Cite）和rubric-guided LLM evaluation（MLR-Bench）已有先行工作；APRES的增量在于使用agentic search发现rubric而非直接text-to-impact mapping或human-designed rubric。建议将声称限定为"first to use agentic search to automatically discover predictive evaluation dimensions"。
- **C2 (Closed-Loop Revision):** **partially_overlapping** — 闭环修订（R3, PROF）和自动论文修订（XtraGPT）领域活跃；APRES的增量在于(a) discovered rubric作为优化目标、(b)完全自动化、(c) content-preservation constraint。这三者组合尚未在先前的系统中同时出现。
- **C3 (Empirical Validation):** **supported** — 79% human preference和Glicko2 consistency实验的规模和方法论较为突出，但需主动对比ReviewerToo的类似发现并承认LLM review可能存在systematic bias（如[5]所记录）。

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
AI辅助学术出版 (Root)
│
├── Branch 1: 审稿生成 (Review Generation)
│   ├── Leaf 1.1: Template-based [ReviewRobot, Yuan+]
│   ├── Leaf 1.2: Multi-agent deliberation [MARG, TreeReview]
│   └── Leaf 1.3: RL-based reviewer [ReviewRL]
│
├── Branch 2: 影响力预测 (Impact Prediction)
│   ├── Leaf 2.1: Bibliometric [DGNI, Thelwall+]
│   ├── Leaf 2.2: LLM text-to-impact [TNCSI_SP, HLM-Cite]  ← APRES在此有overlap
│   └── Leaf 2.3: LLM parametric memory [LLM-Metrics]
│
├── Branch 3: 论文修订 (Paper Revision)
│   ├── Leaf 3.1: Summarization-based [PEGASUS]
│   ├── Leaf 3.2: Multi-agent feedback [SWIFT, LLM-collab]
│   └── Leaf 3.3: Human-in-the-loop iterative [R3, PROF]  ← APRES在此有overlap
│
├── Branch 4: 审稿一致性评估 (Review Consistency)
│   ├── Leaf 4.1: Human consistency studies [NeurIPS 2014/2021]
│   └── Leaf 4.2: LLM reviewer benchmarking [ReviewerToo, PRISM, Blind Spots]
│
└── APRES独特贡献空间
    ├── 自动发现预测性rubric (vs 人工设计rubric)
    ├── Rubric→闭环修订的集成 (vs 独立使用)
    └── Content-preservation约束下的全自动迭代 (vs human-in-the-loop)
```

## References
[1] ReviewerToo: Should AI Join The Program Committee? A Look At The Future of Peer Review 2510.08867

[2] MLR-Bench: Evaluating AI Agents on Open-Ended Machine Learning Research 2505.19955

[3] MARG: Multi-Agent Review Generation for Scientific Papers 2401.04259

[4] On Goodhart's law, with an application to value alignment 2410.09638

[5] Mind the Blind Spots: A Focus-Level Evaluation Framework for LLM Reviews 2502.17086

[6] Unveiling the Merits and Defects of LLMs in Automatic Review Generation for Scientific Papers 2509.19326

[7] From Words to Worth: Newborn Article Impact Prediction with LLM 2408.03934

[8] HLM-Cite: Hybrid Language Model Workflow for Text-Based Scientific Citation Prediction (cited in manuscript; retrieved via paper_search)

[9] Read, Revise, Repeat: A System Demonstration for Human-in-the-loop Iterative Text Revision 2204.03685

[10] XtraGPT: Context-Aware and Controllable Academic Paper Revision 2505.11336

[11] Closing the Loop: Learning to Generate Writing Feedback via Language Model Simulated Student Revisions 2410.08058

[12] Can LLM feedback enhance review quality? A randomized study of 20K reviews at ICLR 2025 2504.09737

[13] PRISM: A Multi-Dimensional Benchmark for Evaluating LLM Peer Reviewers 2605.26730

## Scores
**Final Score: 7.0/10**

**评分依据（研究价值 + novelty 优先）：**

- **研究价值 (7.5/10):** 论文瞄准了学术出版的真实痛点，提出的两阶段pipeline（rubric发现→闭环修订）具有实际应用潜力。大规模human evaluation (79% preference) 和Glicko2 consistency实验为方法的有效性提供了有说服力的证据。然而，Goodhart's Law风险未充分解决降低了长期实用价值。

- **Novelty (6.5/10):** APRES在三方面的增量创新（rubric发现、闭环修订、大规模验证）都是有价值的，但每个单独维度都有明显的先行工作。C1的rubric discovery与TNCSI_SP/HLM-Cite等LLM citation prediction工作构成partial overlap；C2的closed-loop revision与R3/PROF的迭代修订范式部分重叠。论文的真正novelty在于三者的集成，而非任何单一组件。

- **有效性/可靠性 (7.0/10):** 核心数字"19.6%"的计算方式不透明是一个显著的可靠性问题。实验设计整体良好，但human evaluation的采样策略和偏好原因分析缺乏透明度。

- **可复现性 (7.5/10):** 论文在Appendix中提供了prompts、rubric和超参数，数据来源公开（OpenReview + Semantic Scholar），可复现性较好。但缺少post-hoc content preservation验证是一个缺口。

- **写作质量 (6.5/10):** 整体清晰但存在多处overclaim。Related Work组织方式（paper-by-paper列表）和Introduction的段落结构需要改进。

**Post-Revision Target: [7.5, 8.5]/10**

如果所有P0问题（透明化19.6%计算、限定novelty声称、深化Goodhart讨论、补充human evaluation细节、修正过度声称、重写结论）得到充分解决，并且至少完成PE1（Rubric Bias Audit），论文可以达到7.5-8.5的水平。剩余差距主要来自C1/C2的partial overlap性质——这需要通过claim repositioning而非额外实验来解决。

### ASCII Diagram — Paper Structure & Evidence Map

```text
[Claim C1: Rubric Discovery]
    ├── E1: MultiAIDE vs baselines → MAE 1.92-2.30 ✓
    │   ⚠ 19.6%计算不透明
    │   ⚠ Rubric bias未审计
    └── E7: Ablation w/o R* → ΔS drop ✓

[Claim C2: Closed-Loop Revision]
    ├── E3: Rubric score improvement ΔS=3.33 ✓
    │   ⚠ ΔS是自评指标
    │   ⚠ Goodhart风险未量化
    ├── E4: Human preference 79% ✓
    │   ⚠ 采样策略不透明
    └── E7: Ablation w/o MultiAIDE → ΔS drop ✓

[Claim C3: Empirical Validation]
    ├── E5: Glicko2 vs conference decisions ✓
    ├── E6: LLM consistency vs human ✓
    │   ⚠ 跨模型family差异大
    └── E4: Human evaluation + word cloud ✓
        ⚠ 缺乏定量原因分析

[Key Gaps → Fixes]
    G1: 19.6%透明度 → S1
    G2: Novelty overclaim → S2
    G3: Goodhart风险 → S3 + PE2
    G4: Rubric bias → PE1
    G5: Content preservation → PE3
```

### ASCII Diagram — Revision Strategy Roadmap

```text
Priority   Effort    Action
────────────────────────────────────────────
P0 (Must)  Low      透明化19.6%计算 (S1)
P0 (Must)  Low      限定novelty声称 (S2)
P0 (Must)  Low      修正Introduction过度声称 (S7)
P0 (Must)  Low      补充Human eval细节 (S4)
P0 (Must)  Low      重写Conclusion (S8)
P0 (Must)  Medium   深化Goodhart讨论 (S3)
P1 (Nice)  Medium   重组Related Work (S6)
P1 (Nice)  Medium   Rubric bias audit实验 (PE1)
P1 (Nice)  High     Goodhart divergence测量 (PE2)
P1 (Nice)  Medium   Content preservation audit (PE3)
P2 (Opt)   High     Cross-domain generalization (PE4)
```
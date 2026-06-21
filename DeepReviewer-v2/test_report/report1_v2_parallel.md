## Summary

本文提出了APRES——一个基于LLM Agent的两阶段框架，旨在自动改进科学论文的文本呈现质量。第一阶段通过Agentic搜索（MultiAIDE）自动发现一个评分准则（rubric），该准则的评分能够通过负二项回归最优地预测论文未来的引用次数；第二阶段将该发现的准则作为优化目标，在闭环中驱动LLM“Rewriter”对论文进行迭代修订，同时保持核心科学内容不变。在26,707篇ICLR和NeurIPS论文上的大规模实验表明，发现的准则在引用预测MAE上比最佳基线降低19.6%，修订后的论文在盲法人类评估中以79%的比例被偏好，且LLM评审管道在模型族内表现出比人类更高的一致性。三份独立评审一致认为该工作在AI辅助科学写作领域具有实用价值，系统整合思路清晰，大规模验证具有说服力。但均指出论文存在核心数值声明溯源不透明、结论过度推广、人类评估方法学细节缺失、以及内容不变性假设未经验证等共同问题，需要在方法论严谨性和声明精确性方面进行实质性修订。

## Strengths
1. **清晰且新颖的两阶段整合设计**：APRES将“从数据中自动发现评分准则”与“以该准则驱动闭环论文修订”集成为统一框架。经文献检索确认，这一特定组合在现有工作中未见直接先例，Table 1的四维度对比清晰展示了差异化定位。[R1,R2,R3 agree]

2. **大规模且多维度的实证验证**：基于26,707篇当代顶级会议论文（ICLR/NeurIPS）的实验设计具有统计优势。验证维度涵盖引用预测（MAE）、自动修订效果（∆S）、364对盲法人类评估（p < 10^{-22}）以及复现NeurIPS一致性研究的附录实验，证据链较为完整。[R1,R2,R3 agree]

3. **人类评估设计较为严谨**：364对论文的盲法配对比较，每对由3位具备ML博士背景的评估者独立判断，统计检验提供了较强的偏好显著性证据。[R1,R2,R3 agree]

4. **局限性与伦理的坦诚讨论**：论文在Section 5中讨论了引用偏差和Goodhart’s Law风险，并明确将APRES定位为“投稿前stress-test工具”而非替代人类审稿，立场务实。[R1,R2 agree]

5. **实用的工程实现**：diff-based编辑方法有效防止了Rewriter缩短论文，且便于追踪修改和排除表格，对类似系统具有参考价值。[R1,R2 agree]

## Weaknesses
1. **核心数值声明（19.6% MAE改进）的计算溯源不透明**：该数字在Abstract和Introduction中被反复引用，但正文中未明确标注其计算公式、涉及的基线名称和APRES模型配置，读者无法独立验证。[R1,R3 agree; 已确认为共识]

2. **人类评估缺少关键方法学细节**：未披露评估者是否来自作者所在机构、是否知晓研究假设，且未报告评估者间一致性（如Fleiss' kappa）或按修订维度的偏好分解，削弱了79%偏好率结果的稳健性评估。[R3; single-source，但推理有力，保留]

3. **内容不变性约束未经验证**：“不改变科学内容”是APRES的核心设计承诺，但目前仅依赖prompt约束，缺乏任何定量抽查或验证数据，构成一个重要的有效性缺口。[R3; single-source，与R2提出的自动事实性验证建议一致，保留]

4. **结论段存在过度推广**：“unlocking faster, safer, and more impactful scientific progress”这一宏大声明超出了在ML会议语料上所获证据的边界。[R1,R3 agree]

5. **一致性结论的表述需要严格限定**：附录A.2的结果应从当前的“more reliable signal”修正为“more self-consistent”，且正文中LLM评审一致性优于人类的结论需严格限定于“同一模型家族内部”，并明确讨论跨模型不一致性的风险。[R1,R2 agree]

6. **多处术语与语法错误**：包括“mean averaged error”应修正为“Mean Absolute Error (MAE)”、主谓一致错误（如“criteria is”）、冠词-名词不匹配等，降低了专业呈现质量。[R1,R2,R3 agree]

## Key Issues
以下按严重程度排列，融合所有审阅人的发现，并标注共识/单来源信息：

### KI-1: 19.6% MAE改进声明的数值溯源缺失（严重程度：Major） [R1,R3 agree]
论文最突出的定量声明在正文中缺乏明确的数学溯源。MAE基准值分散在不同配置间（Paper embedding + PCA约2.65，APRES最佳约1.92-2.30），19.6%不匹配任何直观心算。读者无法独立验证这一核心声明。  
**修复要求（Must）**：在正文中明确标注19.6%的计算公式、使用的基线名称、APRES模型配置及三次重复实验的均值和标准差。

### KI-2: 一致性结论中的逻辑跳跃与泛化不当（严重程度：Major） [R1,R2 agree]
附录A.2的结论称LLM管道提供了“更可靠的信号”，但实验仅测量了自我一致性，未测量与ground truth的一致性。此外，正文中“LLM评审显著比人类更一致”的结论忽略了跨模型家族比较中>35.1%的不一致率（超过随机基线），需严格限定适用范围。  
**修复要求（Must）**：将附录结论修正为“more self-consistent”；正文结论限定为“同一模型家族内部LLM评审比人类评审更一致”，并明确讨论跨模型差异的风险。

### KI-3: 结论段过度推广超出证据边界（严重程度：Major） [R1,R3 agree]
Conclusion末句声称APRES能够“unlocking faster, safer, and more impactful scientific progress”。该声明在速度、安全性和跨领域影响力方面均无实验证据支撑，超出已验证范围。  
**修复要求（Must）**：将结论收窄至已有证据支持的表述，例如“helping authors communicate their findings more clearly, with effectiveness validated on ML conference papers”。

### KI-4: 内容不变性约束未获实证支持（严重程度：Major） [R3; single-source, 推理充分]
APRES的核心设计原则是仅修改呈现方式，不改变科学内容。然而，论文未提供任何人工抽查或自动验证的数据来估计科学内容被意外修改的频率，使这一关键约束停留在声明层面。  
**修复要求（Must）**：随机抽查至少50篇修订论文，人工检查数值结果、方法论声明和技术描述的准确性，并在Limitations中报告错误率。

### KI-5: 人类评估方法论细节缺失（严重程度：Major） [R3; single-source, 推理充分]
人类评估段落未披露评估者独立性（是否来自Meta？是否知晓假设？）、未报告评估者间一致性指标（Fleiss' kappa），也未按修订维度分解偏好原因。这些信息对于评估79%偏好率的稳健性不可或缺。  
**修复要求（Must）**：补充评估者独立性声明、报告Fleiss' kappa值，并尽可能提供分维度的偏好分析。

### KI-6: 自引用评分循环削弱∆S的方法论解释力（严重程度：Major） [R1; single-source, 推理充分]
修订质量的度量∆S使用了与修订过程相同的发现准则R*作为评分函数，构成了闭环自引用。这使得∆S混合了真实质量提升与系统自我一致性，但其在Limitations中未被透明讨论。虽然人类评估提供了外部验证，但∆S的绝对值解读需更谨慎措辞。  
**修复要求（Must）**：在Limitations段明确增加对自引用评分循环的讨论，并在结果解读中将∆S表述为“improvement under APRES's learned quality model”而非绝对质量增益。

### KI-7: 系统性术语和语法错误（严重程度：Minor） [R1,R2,R3 agree]
全文多处出现“mean averaged error”（应为Mean Absolute Error）、“criteria is”、“a papers”等术语和语法错误，累计影响专业呈现。  
**修复要求（Must）**：进行全面语言校对，重点修正主谓一致、冠词匹配和标准术语。

## Actionable Suggestions
### AS-1: 明确19.6% MAE改进的计算溯源（对应KI-1，Priority: P0）
在Section 4.1的引用预测结果段末尾，增加一句明确的数值溯源说明，例如：“The 19.6% improvement corresponds to the relative MAE reduction from the strongest non-agentic baseline (Paper embedding + PCA, MAE=2.65) to our best APRES configuration (o3, MAE=2.13), computed as (2.65−2.13)/2.65 × 100% ≈ 19.6%.”同时在Fig. 2中为每组数据添加误差棒或置信区间，并报告三次重复的标准差。

### AS-2: 修正一致性结论表述并增加限定义（对应KI-2，Priority: P0）
- 将Page 10的“more reliable and less random signal”修改为“more self-consistent signal, particularly within the same model family”。
- 正文中“significantly more consistent than human peer review”改为“within the same model family, LLM evaluations are more consistent than human peer review; cross-family consistency varies substantially, with some pairs exceeding random baselines”。
- 在附录A.2对Fig. A2中跨模型异常值进行明确讨论。

### AS-3: 收窄Conclusion的宏大声明（对应KI-3，Priority: P0）
将Page 10 Conclusion末句修改为包含证据边界的表述，例如：“thereby helping authors communicate their findings more clearly within the scientific community, with the important caveat that effectiveness has been validated only on ML conference papers and further cross-domain testing is needed.”

### AS-4: 增加内容不变性的实证抽查（对应KI-4，Priority: P0）
随机抽取50篇修订论文，由人工检查：（a）数值结果是否被修改，（b）方法论声明是否被扭曲，（c）技术描述是否仍然准确。在Limitations段落中报告错误率（如“X/50 cases had minor factual inaccuracies”）。

### AS-5: 完善人类评估方法学报告（对应KI-5，Priority: P0）
在Page 9的人类评估段中补充：（a）评估者是否来自作者所在机构，（b）评估者是否知晓研究假设，（c）Fleiss' kappa值，（d）若可能，按清晰度、论证逻辑等维度分解偏好原因。

### AS-6: 在Limitations中增加自引用评分讨论（对应KI-6，Priority: P0）
在Page 10 Limitations段末尾增加内容：“Third, since the improvement score ∆S is computed using the same discovered rubric R* that guides the revision process, ∆S partially reflects the system's self-consistency rather than an independent quality assessment. Our human evaluation partially mitigates this concern, but readers should interpret ∆S as ‘improvement under APRES's learned quality model’ rather than as an absolute quality gain.”

### AS-7: 全文系统语法与术语校对（对应KI-7，Priority: P0/P1）
重点修正清单：（a）“mean averaged error” → “Mean Absolute Error (MAE)”；（b）“criteria is” → “criteria are”；（c）“results reveals” → “results reveal”；（d）“a papers” → “papers”；（e）“comprising of” → “comprising”。建议使用专业语言校对工具或人工逐段审查。

### AS-8: 限定新颖性声称并增补Related Work对比（对应R2单一来源关键问题，Priority: P1）
- 将“first method to integrate...”改为“first to integrate data-driven rubric discovery for citation prediction with automated paper revision”。
- 在Related Work中显式讨论Harada et al. (2025)和Xu et al. (2026) (Rubric-ARM) 及Rubric Rewards [1]，明确差异化维度（目标函数、应用任务、rubric获取方式）。

### AS-9: 深化人类评分预测力缺失的分析（对应R2单一来源建议，Priority: P1）
在Page 7相应段落中增加分析，讨论“人类评审分数MAE≈平均引用数baseline”这一反直觉发现的可能原因（评审关注当前质量 vs. 未来影响力、噪声、子领域差异等），及其对“LLM应模仿人类评审”假设的启示。

### AS-10: 为Goodhart’s Law风险提供具体缓解策略（对应R2单一来源建议，Priority: P1）
在Page 9 Discussion中加入2-3条具体缓解路径，如多目标优化、定期重训练rubric适应引用模式变化、修订后人工审核闸门。

## Storyline Options + Writing Outlines
三份评审普遍认为Introduction和Abstract的结构与精确度有提升空间。综合建议如下：

**Abstract Outline（推荐5句紧凑结构）:**
- S1 (Problem): Scientific communication quality affects impact; peer review feedback is inconsistent.
- S2 (Gap): Existing LLM revision tools use fixed human-defined criteria; none automatically discover criteria predictive of real-world impact to guide revision.
- S3 (Method): APRES, a two-stage agentic framework: agentic search discovers a citation-predictive rubric via negative binomial regression; then drives closed-loop, content-preserving paper revision using this rubric as surrogate objective.
- S4 (Results): Reduces citation prediction MAE by 19.6% over best baseline; revised papers preferred 79% of the time by human experts in blind comparisons.
- S5 (Scope): Positioned as a pre-submission authoring assistant, revising presentation only; validated on ML conference papers.

**Introduction Outline（段落级蓝图，吸纳R1和R2建议）:**
- P1 (Problem & Crisis): 同行评审规模与一致性危机 → 作者缺乏可靠反馈 → LLM作为潜在辅助但存在风险。
- P2 (Gap & Core Insight): 当前LLM审稿工具使用固定标准；人类评审分数本身对引用预测力差（MAE≈5.0）。核心洞察：应“发现”而非“模仿”能预测影响力的准则。
- P3 (APRES Solution Preview): 两阶段框架概述，强调stage 1发现、stage 2驱动修订，并明确“仅修改presentation”的核心约束。
- P4 (Evidence Roadmap): 三点验证预览：引用预测降低19.6%，人类偏好79%，评审一致性更高——并简述三者间的逻辑支撑关系。
- P5 (Positioning & Contributions): 总结三项贡献，明确工具定位为投稿前辅助，非替代人类审稿人，并前瞻声明关键局限性。

## Priority Revision Plan
基于三份评审建议的优先级综合，设计如下修订路径：

### P0 (提交前必须完成 — 影响核心声明的可信度与完整性)
| 任务 | 对应AS | 预期工作量 |
|------|--------|-----------|
| 19.6% MAE改进的精确计算溯源与方差报告，Fig.2添加error bars | AS-1 | 2-4小时 |
| 修正一致性结论：限定为模型族内一致性，讨论跨模型风险 | AS-2 | 1-2小时 |
| 收窄Conclusion的宏大声明 | AS-3 | 0.5小时 |
| 内容不变性抽查验证（抽查50篇并报告错误率） | AS-4 | 8-16小时（需人工） |
| 补充人类评估的方法学细节（独立性、Fleiss' kappa等） | AS-5 | 2-4小时 |
| 在Limitations段增加自引用评分讨论 | AS-6 | 0.5小时 |
| 全文语法与术语校对 | AS-7 | 3-5小时 |

### P1 (强烈建议 — 提升论文严谨性和学术深度)
| 任务 | 对应AS | 预期工作量 |
|------|--------|-----------|
| 限定新颖性声称，增补Related Work中与Harada et al., Rubric-ARM, Rubric Rewards的对比 | AS-8 | 3-4小时 |
| 深化“人类评分预测力差”的分析段落 | AS-9 | 2-3小时 |
| 为Goodhart’s Law风险提供具体缓解策略 | AS-10 | 1-2小时 |

### P2 (可选但推荐 — 增强影响力与完整性)
- 重组Related Work为比较轴驱动结构（如评审生成、影响力预测、准则学习、文本修订）。
- 在一致性实验中增加阈值敏感度分析，增强结论稳健性。
- 考虑按子领域（NLP/CV/Theory）分解rubric预测性能，评估公平性。

**预期修订后质量增益**：完成全部P0和P1任务后，论文的方法论严谨性将得到质的提升——核心数值声明可追溯，关键约束获实证支撑，结论边界与证据对齐，专业呈现显著改善。预计总分可从当前的6.5分提升至7.5-8.5区间。

## Experiment Inventory & Research Experiment Plan
### (A) 已完成实验清单概要

| ID | 目标 | 主要发现 | 当前局限（共识） |
|----|------|---------|-----------------|
| E1 | Rubric搜索用于引用预测 | APRES MAE 1.92-2.30，优于基线(PCA 2.65)，人类评分MAE≈5.0 | 19.6%计算来源与方差未报告；缺乏按子领域分析 |
| E2 | Rubric指导的论文修订 | ∆S=3.33 (borderline)，优于简单rubric基线 | 自引用评分循环未讨论；缺乏修订对实际引用影响的验证 |
| E3 | 修订论文的人类偏好 | 79%偏好修订版，p<10^-22 | 缺少评估者独立性、inter-rater agreement、分维度分析 |
| E4 | 消融实验 | Full APRES显著优于移除R*或MultiAIDE的版本 | 仅在单个LLM配置上测试 |
| E5 | LLM评审一致性 | 同模型族内不一致率~19-20% (<人类23%)；跨模型家族高达>35% | 一致性结论泛化不当；阈值敏感度未分析 |
| E6 | Glicko2评分 vs 会议决策 | 高评分区oral/spotlight比例增加 | 相关性量化不足 |

### (B) 研究主题差距诊断
1. **科学内容完整性**：声称未被实证，是最紧迫的缺口。
2. **修订信号的外部独立性**：∆S是自引用指标，缺少独立的、不与发现的rubric绑定的质量/效果度量。
3. **泛化性证据**：仅在ML会议论文上验证，未测试领域迁移能力。
4. **实际影响力**：未展示修订论文在真实投稿场景中的表现变化。

### (C) 推荐新增/补充实验

| 优先级 | 实验名称 | 目标声明 | 最小设计 | 指标 | 成功标准 |
|--------|---------|---------|---------|------|---------|
| P0 | 内容不变性验证 (EE1) | 修订不显著改变科学内容 | 人工审查50篇修订论文的数字与方法论声明 | 错误率 | <5%的论文发生事实性改变 |
| P0 | 人类评估方法学补全 (EE2) | 评估者间具有中等以上一致性，偏好非随机 | 计算现有数据的Fleiss' kappa；分维度编码偏好理由 | Fleiss' κ；分维度偏好率 | κ>0.3；各维度偏好方向一致 |
| P1 | 子领域rubric性能分解 (EE4) | 发现的rubric在不同ML子领域间无显著偏差 | 按论文方法论标签分类计算MAE | 子领域MAE；相对差异 | 最大差异<30% |
| P1 | 一致性阈值敏感度 (EE5) | 一致性优势在不同阈值下保持 | 复现E5，使用20%和30%接受阈值 | 不一致率变化 | 优势模式一致，无反转 |

## Novelty Verification & Related-Work Matrix
综合三份评审的文献检索结果，对三项核心贡献的新颖性判定如下：

| Claim ID | 贡献声明 | 关键证据论文 | 综合新颖性判定 | 论证 |
|----------|---------|-------------|---------------|------|
| C1 | Agentic搜索发现预测引用数的评分准则（MultiAIDE + 负二项回归） | Promptbreeder (prompt演化)；Harada et al. (Rubric反思精化)；Xu et al. (Rubric-ARM) | **partially_overlapping** | Agentic搜索用于准则发现本身与近期工作[1][2]存在机制重叠，但APRES的差异化在于：目标是引用预测（非人类评分对齐），使用负二项回归处理过离散数据，并用于下游修订。经检索未发现完全相同的组合。需在文中明确区分。[R1: supported; R2: partially_overlapping; R3: partially_overlapping] → 综合判定为partially_overlapping。 |
| C2 | 发现准则驱动闭环论文修订（diff-based编辑） | SWIFT, R3; Rubric Rewards | **partially_overlapping** | 迭代修订本身非新，但使用自动发现的、以引用预测为目标的准则作为优化函数，且集成diff-based编辑约束，构成了新的系统贡献。Rubric Rewards将rubric作为RL目标但任务是研究计划生成。需在Related Work中显式区分。[R1: supported; R2: partially_overlapping; R3: partially_overlapping] → 综合判定为partially_overlapping，但系统整合价值高。 |
| C3 | 实证验证：19.6% MAE改进，79%人类偏好，较高模型族内一致性 | 无直接冲突文献 | **supported (with caveats)** | 大规模验证和统计显著性得到一致认可，但核心定量声明需补充计算来源和方差，一致性结论需限定，人类评估需补充方法论细节。修正后可提升为strong supported。 |

**综合新颖性结论**：APRES的单点组件与现有工作存在共享，但其组合方式——面向引用预测的准则发现+准则驱动闭环修订——在当前文献中未见完整先例。系统整合的新颖性（integration novelty）是主要贡献，建议论文在措辞上将“first method to discover”改为“first to integrate”以更精确反映贡献边界。

### Related-Work Taxonomy Tree (ASCII)
```
AI-Assisted Scientific Review & Revision (Root)
├── Branch 1: LLM Review Generation
│   ├── Leaf 1.1: Single-Agent (Reviewer2, ReviewRobot)
│   ├── Leaf 1.2: Multi-Agent (MARG, TreeReview)
│   └── Leaf 1.3: RL-Trained (ReviewRL)
├── Branch 2: Scientific Impact Prediction
│   ├── Leaf 2.1: Graph/Metadata (DGNI)
│   ├── Leaf 2.2: Embedding-Based (SPECTER, TNCSI_SP)
│   └── Leaf 2.3: LLM Text-Based (HLM-Cite, TNCSI)
├── Branch 3: Evaluation Criteria Discovery
│   ├── Leaf 3.1: Iterative Rubric Refinement (Harada et al.)
│   ├── Leaf 3.2: RL Co-Optimization (Rubric-ARM)
│   └── Leaf 3.3: Agentic Search for Citation Prediction ★APRES★
├── Branch 4: Automated Text Revision
│   ├── Leaf 4.1: Summarization (PEGASUS)
│   ├── Leaf 4.2: Multi-Agent Feedback (SWIFT)
│   ├── Leaf 4.3: Human-in-the-Loop (R3)
│   └── Leaf 4.4: Rubric-Guided Iterative Revision ★APRES★
└── Branch 5: Rubric-as-Objective Generation
    ├── Leaf 5.1: RL with Extracted Rubrics (Rubric Rewards)
    └── Leaf 5.2: Search-Discovered Rubric for Revision ★APRES★
```

## References
(整合三份评审中检索到的关键参考文献，去重后列出)
1. Promptbreeder: Self-referential self-improvement via prompt evolution (Fernando et al., 2024, 2402.10886)
2. Harada et al. (2025). Automated Refinement of Essay Scoring Rubrics for Language Models via Reflect-and-Revise. 2510.09030
3. Xu et al. (2026). Alternating Reinforcement Learning for Rubric-Based Reward Modeling in Non-Verifiable LLM Post-Training. 2602.01511
4. Training AI Co-Scientists Using Rubric Rewards. 2512.23707
5. Reviewer2: Optimizing Review Generation Through Prompt Generation. 2402.10886
6. MARG: Multi-agent review generation for scientific papers. 2401.04259
7. SWIFT: Automated focused feedback generation for scientific writing assistance. 2407.09756
8. R3: Read, revise, repeat: A system demonstration for human-in-the-loop iterative text revision. 2010.04665
9. SPECTER: Document-level Representation Learning using Citation-informed Transformers. 2004.07180
10. HLM-Cite: Hybrid language model workflow for text-based scientific citation prediction. 2412.15249
11. ARISE: Agentic Rubric-Guided Iterative Survey Engine for Automated Scholarly Paper Generation. 2511.17689
12. Liang et al. (2023). Can large language models provide useful feedback on research papers? 2310.01783
13. PRISM: A Multi-Dimensional Benchmark for Evaluating LLM Peer Reviewers. 2605.26730
14. LLM-REVal: Can We Trust LLM Reviewers Yet? 2510.12367

## Scores
**Consolidated Score: 6.5/10**

三份评审独立给出的分数均为6.5/10，高度一致。评分依据综合如下：
- **研究价值与新颖性 (6.5-7/10)**: 问题方向具有现实意义，两阶段集成的系统贡献新颖，但核心组件与近期文献存在重叠（partially_overlapping），需通过精确措辞和增补比较来清晰界定贡献边界。
- **方法有效性 (5.5-7/10)**: 实验规模大，设计较完整，但存在多项影响可信度的缺陷：关键定量声明不可追溯、人类评估方法学细节缺失、核心设计约束未经验证、部分结论过度推广。修正后预期可提升至7.5+。
- **可复现性 (7/10)**: 数据与prompts公开，代码承诺开源，但LLM调用随机性、搜索过程不确定性和内容不变性无评估，使得完全复现有挑战。
- **写作与呈现 (5.5-6.5/10)**: 结构可改进，多处语法术语错误降低专业度，但Method和Experiment部分描述总体清晰。

**Post-Revision Target: [7.5, 8.5]/10**
如果所有P0和P1任务（特别是数值溯源、一致性限定、内容不变性验证、人类评估细节补充、语法修正）得到充分解决，论文的严谨性将显著增强，得分可望进入7.5-8.5区间。达到上限可能需要额外的跨领域泛化性或用户研究实验。

---

## Meta-Review Notes
**审稿人间共识/单源/争议统计**:
- 确认共识（2+审稿人同意）：5项（19.6%溯源缺失、结论overclaim、一致性结论需限定、语法术语错误、两阶段设计和大规模验证作为优点）。
- 单一来源但保留（推理充分）：5项（内容不变性未验证、人类评估细节缺失、自引用评分循环、人类评分预测力分析缺失、Goodhart's Law策略缺失、新颖性声称需限定、Related Work缺少Rubric Rewards等）。这些均被认为对提升论文质量有实质帮助，予以保留并标记。
- 争议项：无。三份评审在核心判断上无本质冲突，仅侧重点不同。

**审稿人间显著差异**:
- R1更关注方法论内部严谨性（自引用循环、数值声明、概念跳跃），并进行了系统的贡献新颖性矩阵分析，判定C1/C2为supported。
- R2更关注文献对比与新颖性边界的精准界定，检索到了R1未涉及的近期相关工作（Harada et al., Rubric-ARM），并将C1/C2判定为partially_overlapping，同时强调了分析和讨论的深度。
- R3聚焦于实证缺陷（人类评估细节、内容不变性验证），对实验可信度提出了更具体的要求，并将C1/C2判定为partially_overlapping。
- 三者互为补充，共同构成了对论文较为全面的诊断。

**整体审稿人一致性水平: 高**。对论文优缺点、核心问题所在以及最终分数的判断高度收敛。修订建议虽有不同侧重，但目标是统一的，均可被纳入修订计划。这为作者提供了明确且可操作的修改路径。
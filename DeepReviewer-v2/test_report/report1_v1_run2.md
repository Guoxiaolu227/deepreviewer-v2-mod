## Summary
本文提出APRES——一个两阶段的LLM智能体框架，旨在自动改进科学论文的表述质量和可读性。第一阶段使用智能体搜索（agentic search）结合负二项回归，从论文文本中发现能够预测未来引用数量的评价量规（rubric）；第二阶段将该量规作为目标函数，通过闭环迭代修订过程自动优化论文文本。实验基于来自ICLR 2024/2025和NeurIPS 2023/2024的26,707篇论文及其审稿数据，主要发现包括：(1) 发现的量规在引用预测MAE上比最强基线提升19.6%；(2) 在364对论文的盲法人类评估中，APRES修订版本在79%的情况下被偏好。

**核心贡献**在于将"评价标准的自动发现"与"基于该标准的闭环修订"整合为一个统一框架——这是该领域的首创。检索证据表明，现有工作要么聚焦于自动审稿生成（如SEA [9]、ReviewAdvisor [8]），要么聚焦于引用预测（如TNCSI_SP），要么聚焦于独立的文本修订（如XtraGPT [3]），但尚无同时完成"发现预测性评价标准→使用该标准驱动修订"闭环的工作。

**主要关切**包括：(1) ∆S评估指标存在循环论证——优化目标和评估指标使用同一量规；(2) 部分措辞（如"reliable tool"、"strong evidence"）超出当前证据范围；(3) 内容保真度缺乏经验性验证；(4) Goodhart's Law的承认与系统设计之间存在未解决的张力。这些问题均可通过修订解决，不影响论文的核心科学价值。

## Strengths
1. **概念整合的新颖性。** APRES首次将"评价标准的自动发现"与"基于该标准的闭环论文修订"整合为统一框架。检索证据表明，现有工作（ARISE [5]使用量规但用于综述生成而非发现，HypoEval [4]从人类数据中生成量规但不优化引用预测，XtraGPT [3]进行论文修订但不使用发现的量规）各自覆盖了该管道的部分环节，但APRES是首个完成完整"发现→评估→修订"闭环的系统。这一整合本身就是有意义的研究贡献。

2. **大规模实证验证。** 研究建立在26,707篇论文的真实数据集上，涵盖四个顶级会议（ICLR 2024/2025, NeurIPS 2023/2024），使用Semantic Scholar的"influential citation"指标。实验设计包含多个精心选择的基线（人类评分、SPECTER嵌入、Prompt Breeder），并在四种前沿LLM（o1, o3, Gemini 2.5 Flash/Pro）上进行了比较。364对论文的盲法人类评估（每对3位PhD评估者）提供了独立的修订质量验证。

3. **附录中的审稿一致性实验。** 附录A复现了NeurIPS一致性实验的设计（Cortes & Lawrence 2021; Beygelzimer et al. 2023），使用Glicko2评分系统证明了LLM评估管道比人类审稿委员会具有更高的一致性。该实验直接回应了关于LLM审稿随机性的关键质疑，是论文的重要补充证据。

4. **负责任的立场声明与伦理考量。** 论文在多个位置明确声明不主张全自主AI审稿系统，强调human-in-the-loop的必要性，并在Ethics Statement中系统性地讨论了数据使用、双用途风险、公平性偏见和透明度问题。Discussion中对Goodhart's Law的承认也体现了方法论自觉。

5. **diff-based编辑方法的工程设计。** 使用Aider格式的search/replace块进行增量修订（而非全文重写），有效防止了LLM倾向于大幅缩短论文的问题。这种设计选择具有实用价值，对后续系统设计有参考意义。

## Weaknesses
### W1. ∆S指标的循环评估问题（方法学，严重）

∆S指标的定义为 $\Delta S = S_{\text{rev}} - S_{\text{ori}}$，其中$S$由Stage 1发现的量规$\mathcal{R}^*$计算。但Stage 2的修订过程使用同一个$\mathcal{R}^*$作为优化目标。这意味着优化目标与评估指标完全相同，构成了循环论证——系统被训练来最大化$\mathcal{R}^*$评分，然后用$\mathcal{R}^*$评分的提升作为"改进"的证据。这类似于用训练损失来证明模型泛化能力，在方法学上是不充分的。虽然人类评估提供了独立验证，但∆S在正文中被作为主要量化证据呈现（Figure 4的核心发现），其局限性需要被明确承认。

**证据锚点：** Page 7 - Evaluation Metrics段落；Page 5 - Section 3.2中$\mathcal{R}^*$作为surrogate function的描述。

### W2. 措辞过度声称超出证据范围（写作/科学性，中等）

多处使用超出当前证据范围的措辞：(a)「strong empirical evidence that LLMs can serve as a reliable tool」（Page 2），但检索到的研究[1]显示LLM审稿与人类接受论文的相似度仅38.6%；(b)「novel signals...that elude traditional review criteria」（Page 2），暗示传统标准完全无法捕捉这些信号，但更准确的说法是互补性；(c)「unlocking faster, safer, and more impactful scientific progress」（Page 10 Conclusion），属于无证据支撑的宏大叙事。

**证据锚点：** Page 2 - Introduction最后一段；Page 10 - Conclusion。

### W3. 内容保真度缺乏经验性验证（方法学，中等）

论文承认「we cannot perfectly guarantee this constraint was met」（Page 10 Limitations），但没有对修订后的论文进行内容保真度抽样检查。考虑到这是系统的核心安全约束（"不改变科学内容"），缺少经验性验证是一个显著的方法学缺口。建议至少对50篇修订论文进行抽样，人工检查是否引入了事实错误。

**证据锚点：** Page 10 - Limitations段落。

### W4. 引用数作为论文质量的代理变量存在根本局限（概念性，中等）

论文承认引用数存在偏见但选择使用它，并在Discussion中引用了Goodhart's Law。然而，论文的核心设计——将引用预测量规作为优化目标——与Goodhart's Law存在未解决的张力：如果该量规被广泛采用，作者和AI系统可能学会"迎合"该量规而非真正提升论文质量。这一风险在Discussion中仅被简要提及，缺乏深入分析。

**证据锚点：** Page 9 - Discussion第一节。

### W5. 写作细节问题（呈现质量，轻微）

- 「Mean Averaged Error」应为「Mean Absolute Error (MAE)」——全文多处出现
- 表格编号不一致：「Tab. 3」引用实际为「Table 2」（Page 6）
- 「comprising of」语法错误（Page 6）
- 「there maybe bugs in the code hence the need for the debug probability design」过于口语化（Page 5）
- 「a more reliable and data-driven processes」冠词-名词不一致（Page 2）

**证据锚点：** 分别位于Page 1 Abstract、Page 6 Dataset、Page 5 Method、Page 2 Introduction。

## Key Issues
### Ranked Error Board (Top 5)

| # | 问题 | 严重程度 | 研究价值影响 | 有效性风险 | 可修复性 | 置信度 |
|---|------|----------|-------------|-----------|---------|--------|
| 1 | ∆S循环评估：优化目标与评估指标相同 | **Major** | 中——若不修复，修订质量的自动评估不可信 | 高——循环性削弱了∆S作为独立证据的价值 | 高——增加独立评估指标+显式声明局限即可修复 | 高 |
| 2 | 措辞过度声称：超出证据范围的"reliable tool"/"strong evidence"表述 | **Major** | 中——影响论文可信度和科学严谨性 | 中——不威胁核心结果但可能引起审稿人质疑 | 高——替换为有边界的措辞即可 | 高 |
| 3 | 内容保真度缺乏经验性验证 | **Major** | 中——影响系统安全性声明的可靠性 | 中——无法量化"不改变科学内容"约束的实际效果 | 中——需要人工抽样检查，成本适中 | 高 |
| 4 | Goodhart's Law与系统设计之间的未解决张力 | **Minor** | 低——主要影响Discussion深度而非核心贡献 | 低——不威胁实验有效性 | 高——增加一段深入讨论即可 | 中 |
| 5 | 写作细节错误（MAE术语、表格编号、语法） | **Minor** | 低——不影响研究价值但影响专业形象 | 低——不威胁任何结论 | 高——全局查找替换即可 | 高 |

### 详细分析

**Key Issue 1 — ∆S循环评估（Page 7 - Evaluation Metrics）**

问题机制：$\mathcal{R}^*$同时作为Stage 2的优化目标函数和∆S的计算函数。当修订系统学习最大化$\mathcal{R}^*$时，∆S必然上升——这反映的是优化收敛而非独立的论文质量提升。人类评估（第二个指标）提供了部分独立验证，但Figure 4的分析和结论（如"borderline papers achieve a much higher final score"）主要基于∆S。

修复路径：(a) 在Evaluation Metrics段落中显式声明循环局限；(b) 增加一个独立于$\mathcal{R}^*$的评估指标（如SPECTER PCA baseline评分变化）；(c) 在Discussion中分析循环性对结论的影响范围。

**Key Issue 2 — 措辞过度声称（Page 2 - Introduction最后一段）**

问题机制：论文的实证范围限定在ML会议论文（ICLR/NeurIPS）的文本修订场景，但部分措辞暗示了更广泛的可靠性和影响力。检索到的研究[1]显示LLM审稿存在显著局限（与人类接受论文仅38.6%相似度），Goldberg et al. [2]也报告了不准确(20/52)和过度严格(14/52)的问题。

修复路径：将"reliable tool"替换为限定范围的表述（如"a tool that can provide consistent, rubric-guided feedback on presentation quality"），将"strong empirical evidence"替换为"empirical evidence on a large-scale dataset from four ML conferences"，将"elude"替换为"are complementary to"。

**Key Issue 3 — 内容保真度（Page 10 - Limitations）**

问题机制：APRES的核心安全约束是"不改变科学内容"，但论文承认这一约束无法完美保证，却没有提供任何经验性验证。这类似于部署一个安全关键系统但从未测试其故障率。

修复路径：对50篇APRES修订论文进行人工抽样检查，统计事实错误率（如修改数据值、技术描述扭曲等），并在Limitations段落中报告结果。如果错误率极低（<2%），这将显著增强论文的可信度。

**Key Issue 4 — Goodhart's Law张力（Page 9 - Discussion）**

问题机制：论文承认Goodhart's Law但未将其与APRES的设计关联起来。如果引用预测量规成为广泛使用的优化目标，可能导致科学写作文体的同质化或表面性优化。

修复路径：在Discussion中增加一段，分析APRES系统本身可能助长的Goodhart效应及建议的缓解措施。

**Key Issue 5 — 写作细节（多处）**

修复路径：全局查找替换"Mean Averaged Error"→"Mean Absolute Error (MAE)"；修正表格引用；修正语法错误。

## Actionable Suggestions
### S1. 修复∆S循环评估（Must — 对应KI-1）

在Page 7 - Evaluation Metrics段落末尾增加以下声明：

「Since $\mathcal{R}^*$ serves as both the optimization objective for revision and the scoring function for $\Delta S$, the improvement score should be interpreted as a measure of optimization progress rather than an independent quality assessment. The human preference study (Section 4.2) provides orthogonal validation of revision quality.」

同时，在Figure 4的分析中增加一个使用SPECTER PCA baseline评分计算的对照$\Delta S$曲线，作为独立于优化目标的参考指标。

### S2. 限定措辞范围（Must — 对应KI-2）

以下替换应在全文中执行：
- 「LLMs can serve as a reliable tool」→「LLM-based evaluation, when guided by discovered rubrics, can provide a more consistent signal than human review committees on specific evaluation tasks」
- 「strong empirical evidence」→「empirical evidence on a large-scale dataset from four ML conferences」
- 「novel signals...that elude traditional review criteria」→「citation-predictive patterns complementary to those captured by traditional review criteria」
- 「unlocking faster, safer, and more impactful scientific progress」（Conclusion）→「supporting more consistent and data-driven scientific communication」

### S3. 增加内容保真度抽样验证（Must — 对应KI-3）

从364对APRES修订论文中随机抽取50对，由至少两名标注者独立检查修订是否引入事实错误（修改数据值、扭曲技术描述、改变实验设置等）。在Limitations段落中报告错误率。如果错误率<2%，这一发现将显著增强论文可信度；如果错误率较高（>5%），则需要讨论更严格的约束机制。

**Mentor Revised Version（Limitations段落补充）：**
「To empirically assess content fidelity, we conducted a manual spot-check on 50 randomly sampled APRES-revised papers. Two annotators independently examined each revision for factual inaccuracies. Preliminary results indicate that X% of revised papers contained at least one factual error (e.g., altered numerical values or distorted technical descriptions). While this rate is [low/moderate], it underscores the need for verification mechanisms before deploying automated revision tools in high-stakes settings.」

### S4. 深化Goodhart's Law讨论（Nice-to-have — 对应KI-4）

在Page 9 - Discussion的"From Mimicking Humans to Predicting Impact"段落后增加一段：

「A related concern specific to APRES's design is that the same rubric $\mathcal{R}^*$ optimized during revision is also used to measure improvement ($\Delta S$). This creates a self-referential evaluation loop: the system learns to satisfy its own scoring criteria, which may diverge from genuine improvements in scientific communication. Furthermore, if citation-predictive rubrics become widely adopted as optimization targets, they may incentivize surface-level writing adjustments—such as adopting high-scoring vocabulary patterns—rather than deeper improvements in clarity or argumentation. Mitigating this risk requires periodic rubric recalibration against updated citation data, incorporation of expert qualitative assessments, and transparency about the rubric's limitations as a quality proxy.」

### S5. 修正写作细节（Must — 对应KI-5）

全局修正：
- 「Mean Averaged Error」→「Mean Absolute Error (MAE)」（全文约5-6处）
- 「Tab. 3」→「Tab. 2」（Page 6 Dataset段落）
- 「comprising of」→「comprising」或「consisting of」（Page 6）
- 「a more reliable and data-driven processes」→「more reliable and data-driven processes」（Page 2）
- 口语化表述「there maybe bugs in the code hence the need for the debug probability design」→正式表述（Page 5）

## Storyline Options + Writing Outlines
### 当前Storyline评估

当前论文的叙述线为：Peer Review危机 → LLM作为解决方案（但存在风险） → APRES框架（两阶段） → 实验验证 → 意义讨论。这一结构与标准学术论文叙事基本一致，但在以下方面存在改进空间：(a) Introduction中gap陈述不够显式化；(b) 第一阶段和第二阶段之间的逻辑连接需要更清晰的数学锚点；(c) Conclusion未有效总结已知局限。

### 推荐Storyline：以"发现优于人类定义的评估标准"为核心叙事

**Big Picture：** 科学论文的评审和修订是低效且不一致的过程。

**Gap：** 现有LLM审稿工具试图模仿人类审稿人，但人类审稿标准本身对引用预测效果不佳（MAE≈5.0）。真正的问题是：我们能否发现比人类定义的标准更好的评估标准？

**Solution：** APRES通过智能体搜索自动发现引用预测性更强的评估量规（MAE<2.0，比人类评分提升>60%），然后使用该量规作为目标函数驱动论文修订。

**Evidence：** 19.6% MAE提升 + 79%人类偏好 + LLM审稿一致性优于人类。

### Abstract Outline（4-5句结构）

- **S1（问题/领域）：** 「Scientific communication quality directly affects research impact, yet peer review—the primary feedback mechanism—often delivers inconsistent evaluations that limit manuscript improvement.」
- **S2（现有方法不足/Gap）：** 「Existing LLM-based review tools attempt to mimic human reviewers, but human-defined criteria are themselves poor predictors of a paper's future citation impact.」
- **S3（提出方法）：** 「We introduce APRES, a two-stage agentic framework that first discovers a citation-predictive evaluation rubric through iterative search with negative binomial regression, then uses this rubric as an objective function to drive automated, closed-loop paper revision.」
- **S4（关键结果）：** 「Across 26,707 papers from ICLR and NeurIPS, APRES's discovered rubric reduces citation prediction MAE by 19.6% over the strongest embedding baseline, and APRES-revised papers are preferred by human evaluators 79% of the time in blind comparisons of 364 paper pairs.」
- **S5（有边界的结论）：** 「These results demonstrate that LLM-based tools can discover evaluation criteria more predictive than human-defined standards, and can use these criteria to provide actionable pre-submission feedback—while human judgment remains essential for assessing scientific merit.」

### Introduction Outline（段落级蓝图）

- **P1（动机+问题陈述）：** 建立peer review系统面临的压力（投稿量激增、审稿疲劳、一致性差），引出LLM作为可扩展反馈渠道。明确gap：现有LLM审稿工具直接模仿人类标准，但人类标准本身在预测论文影响力方面表现不佳（MAE≈5.0 vs. 随机基线5.3）。

- **P2（核心思想+贡献声明）：** 提出核心假设：通过优化引用预测来发现评估标准，可能优于依赖预定义的人类量规。引入APRES的两阶段设计（发现→修订）。精确描述贡献的三维度：(1) 量规发现方法，(2) 闭环修订系统，(3) 大规模实证验证（含人类评估和审稿一致性实验）。

- **P3（验证策略+结果预览）：** 预告实验设置（26,707篇论文、四个会议）和关键结果（19.6% MAE提升、79%人类偏好、LLM审稿一致性优于人类）。嵌入具体数字以增强说服力。

- **P4（更广泛意义+立场声明+论文结构）：** 将该工作定位于AI辅助审稿的更大讨论中（引用AAAI 2026试点、ICLR 2025实验），声明非全自主审稿立场，概述论文结构。关键修改：将"reliable tool"替换为限定范围的表述。

### Related Work重组建议

当前Related Work按主题分组（LLM审稿生成、AI修改检测、审稿可靠性、引用预测、可读性与影响力、自动文本修订、审稿语料库），结构合理。建议在第2节末尾增加一个对比段落，明确说明APRES与XtraGPT [3]和ARISE [5]的关键区别：

「APRES differs from prior work in two key aspects. First, unlike ARISE [5], which uses predefined behaviorally anchored rubrics for survey generation, APRES discovers its rubric through optimization against citation data. Second, unlike XtraGPT [3], which performs instruction-guided revision, APRES employs a closed-loop search process where the rubric scores serve as the optimization objective.」

## Priority Revision Plan
### P0（必须完成，投稿前）

| 优先级 | 行动 | 预期收益 | 估计工作量 | 对应Issue |
|--------|------|---------|-----------|----------|
| P0-1 | 全局修正MAE术语（"Mean Averaged Error"→"Mean Absolute Error"） | 消除术语错误，提升专业形象 | 10分钟 | KI-5 |
| P0-2 | 限定Introduction和Conclusion中的过度声称措辞 | 显著提升科学严谨性，降低被审稿人质疑风险 | 30分钟 | KI-2 |
| P0-3 | 在Evaluation Metrics段落中显式声明∆S循环局限 | 防止审稿人指出方法学缺陷，化被动为主动 | 15分钟 | KI-1 |
| P0-4 | 修正表格引用编号（Tab. 3→Tab. 2）及语法错误 | 消除文档错误 | 15分钟 | KI-5 |
| P0-5 | 将第5页口语化表述改为正式学术语言 | 提升方法学描述的严谨性 | 10分钟 | KI-5 |

### P1（强烈建议，投稿前完成）

| 优先级 | 行动 | 预期收益 | 估计工作量 | 对应Issue |
|--------|------|---------|-----------|----------|
| P1-1 | 增加独立评估指标（SPECTER PCA baseline）作为∆S对照 | 部分解决循环评估问题，显著增强Figure 4的论证力度 | 2-3小时（需运行实验） | KI-1 |
| P1-2 | 完成50篇论文的内容保真度抽样检查并报告结果 | 填补方法学缺口，若错误率低则大幅增强可信度 | 4-6小时（需人工标注） | KI-3 |
| P1-3 | 在Discussion中增加Goodhart's Law与APRES设计的关联分析 | 展示方法论自觉，加深Discussion深度 | 30分钟 | KI-4 |
| P1-4 | 在Related Work末尾增加与XtraGPT [3]和ARISE [5]的显式对比 | 强化新颖性定位 | 20分钟 | — |

### P2（可选，提升论文质量）

| 优先级 | 行动 | 预期收益 | 估计工作量 | 对应Issue |
|--------|------|---------|-----------|----------|
| P2-1 | 在Section 3.1添加Algorithm 1（MultiAIDE Rubric Search伪代码） | 提升可复现性 | 30分钟 | — |
| P2-2 | 重组Abstract为4-5句标准结构 | 提升摘要可读性 | 15分钟 | — |
| P2-3 | 讨论对抗攻击（prompt injection）的具体缓解方案 | 丰富Limitations讨论 | 30分钟 | — |

### 修订后预期影响

完成P0和P1后，论文将：(a) 消除循环评估的方法学隐患，(b) 将措辞限定在证据范围内，(c) 填补内容保真度的经验性验证缺口，(d) 显著提升Discussion的深度和自我批判性。预期这将使论文在审稿中减少major concerns数量，提升总体评分1-2分（10分制）。

## Experiment Inventory & Research Experiment Plan
### (a) 已完成实验清单

| Exp ID | 目标/假设 | 设置（数据/划分/协议/基线） | 指标 | 主要结果 | 支撑的声明 | 当前局限 |
|--------|----------|--------------------------|------|---------|-----------|---------|
| E1 | Rubric Search：发现的量规能否比现有方法更好地预测引用数？ | 26,707篇论文；80/10/10划分；o1/o3/Gemini 2.5 Flash/Pro四种LLM；Human scores/SPECTER/PCA/Prompt breeder基线 | MAE | MultiAIDE搜索一致收敛到更低MAE（o3: 1.92, Gemini 2.5 Pro: 1.96）vs. 最强基线2.65 | C1, C2 | 仅在ML会议数据上验证；12个月引用窗口可能不足以捕捉长期影响力 |
| E2 | Paper Improvement (自动评估)：APRES能否提升论文的预测影响力评分？ | 测试集；Clear Accept/Borderline/Clear Reject三层；Discovered Rubric/Simple Rubric/Embedding PCA三种目标函数 | ∆S | Borderline论文∆S最高（o3: 3.33）；Discovered Rubric优于其他目标函数 | C3 | ∆S使用与优化目标相同的量规（循环评估） |
| E3 | Paper Improvement (人类评估)：APRES修订的论文是否被人类偏好？ | 364对论文，每对3位PhD评估者；盲法成对比较 | 偏好率 + 二项检验 | 79%偏好APRES版本；p<10^-22；95% CI [70.1%, 79.0%] | C3 | 评估者均为ML领域PhD，可能不适用于其他学科 |
| E4 | 消融实验：发现量规和MultiAIDE搜索各自的贡献 | APRES w/o R*；APRES w/o MultiAIDE | ∆S（按论文类别） | 移除任一组件显著降低∆S（如Borderline: 3.33→1.24/1.46） | C1 | 消融仅在∆S上评估（同循环问题） |
| E5 | 审稿一致性（附录A）：LLM评估是否比人类审稿更一致？ | 20,000次成对比较；Glicko2评分系统；四模型间一致性矩阵 | Disagreement Rate | LLM模型间不一致率总体低于人类23%基准；同模型家族内部更一致 | 辅助声明（LLM可靠性） | 仅限ML会议论文；Glicko2二值化阈值（top 25%）可能影响比较公平性 |

### (b) 研究主题差距诊断

| 研究价值声明 | 支撑强度 | 差距 |
|-------------|---------|------|
| "新知识"：发现比人类标准更预测引用的评估标准 | **中强** — E1提供了MAE比较证据，但仅在ML领域验证 | 需在非CS学科（如生物学、社会科学）上验证量规的跨领域泛化能力 |
| "可复现性/可重用性"：方法可被其他研究者复现和扩展 | **中** — 使用了公开数据和代码承诺，但搜索过程需要大量LLM API调用（成本高） | 需报告单次搜索的API成本估算；需提供更小规模复现方案 |
| "改变实践/理解"：APRES可能改变作者在投稿前的修订实践 | **初步** — E3的人类偏好提供了方向性证据，但未见实际投稿结果改变的纵向数据 | 需跟踪使用APRES修订后论文的实际审稿结果（如与原始版本的acceptance rate比较） |

### (c) 建议的研究实验（P0/P1/P2）

**P0-1: 独立评估指标验证（Must — 对应KI-1）**

| 字段 | 内容 |
|------|------|
| 目标声明 | ∆S的循环性可通过独立于R*的指标来缓解 |
| 假设 | 使用SPECTER PCA baseline评分计算的∆S'与使用R*计算的∆S呈正相关，但涨幅较小 |
| 最小设计 | 在Fig. 4已有的实验数据上，增加一条使用SPECTER PCA scoring function计算的∆S'曲线 |
| 对照/基线 | ∆S (R*) vs. ∆S' (SPECTER PCA) |
| 指标 | 两条曲线的Pearson相关性；∆S'的绝对涨幅 |
| 成功标准 | ∆S' > 0（表明独立指标也检测到改进）且 |∆S'| < |∆S|（表明循环性确实放大了涨幅） |
| 估计成本/时间 | 2-3小时计算时间（无需额外实验，仅需重新计算评分） |
| 预期质量提升 | 显著：将循环评估从潜在的致命缺陷转化为已识别并量化的局限 |

**P0-2: 内容保真度验证（Must — 对应KI-3）**

| 字段 | 内容 |
|------|------|
| 目标声明 | 量化APRES修订引入事实错误的比例 |
| 假设 | 绝大多数修订（>95%）不引入事实错误 |
| 最小设计 | 从364对论文中随机抽样50对；2位标注者独立比对原稿和修订稿，标记所有事实错误（修改数值、扭曲技术描述等）；计算Cohen's κ和错误率 |
| 对照/基线 | 无（描述性统计） |
| 指标 | 包含≥1个事实错误的修订比例；每篇论文的平均错误数；标注者间一致性 |
| 成功标准 | 错误率 < 5% |
| 估计成本/时间 | 4-6小时（标注 + 分析） |
| 预期质量提升 | 显著：填补最严重的方法学缺口，若错误率低则大幅增强可信度 |

**P1-1: 跨领域泛化验证（Nice-to-have）**

| 字段 | 内容 |
|------|------|
| 目标声明 | 验证APRES发现的量规在非ML科学领域的有效性 |
| 假设 | 为ML优化的量规在非CS学科上的MAE高于在ML数据上的MAE，但仍优于人类评分基线 |
| 最小设计 | 从PubMed Central或其他开放获取数据库中选取500-1000篇非CS论文；计算已有量规的MAE |
| 对照/基线 | ML领域MAE vs. 非CS领域MAE；跨领域的人类评分基线 |
| 指标 | 跨领域MAE比值；与人类评分基线的比较 |
| 成功标准 | 跨领域MAE < 人类评分基线的MAE |
| 估计成本/时间 | 1-2天（数据收集 + 评分 + 分析） |
| 预期质量提升 | 中等：增强外部有效性，但非必须 |

### ASCII Diagram — Experiment Upgrade Plan

```text
Stage 1 (P0, 投稿前必须)
  ├── P0-1: 独立评估指标 ──► 解决∆S循环性
  └── P0-2: 内容保真度验证 ──► 填补安全性验证缺口

Stage 2 (P1, 强烈建议)
  └── P1-1: 跨领域泛化 ──► 增强外部有效性

Stage 3 (P2, 可选)
  ├── 纵向跟踪修订论文的实际审稿结果
  └── 多模态修订（含图表优化）
```

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | 作者贡献声明 | 关键证据论文 [n] | 新颖性判定 | 理由 | 置信度 | 需要的重新定位 |
|----------|------------|-----------------|-----------|------|--------|--------------|
| C1 | 智能体搜索框架（MultiAIDE）自动发现引用预测性评价量规——通过负二项回归优化量规评分来预测引用数，超越预定义的人类标准 | ARISE [5]（使用量规但不发现量规）；HypoEval [4]（从人类数据生成量规但不优化引用预测）；Prompt Breeder（进化提示但不应用于论文评价） | **supported** | 检索确认：无现有工作将智能体搜索与负二项回归结合用于发现引用预测性量规。ARISE使用预定义的行为锚定量规进行综述生成；HypoEval从人类评估中生成量规但目标是NLG评估对齐而非引用预测。APRES的独特贡献在于优化目标（引用预测）与搜索机制（MultiAIDE）的结合。 | 高 | 无需重新定位，但建议在Introduction中明确说明"discover"的具体含义（即通过优化引用预测来搜索量规项）。 |
| C2 | 发现的量规在引用预测上比最强基线提升19.6% MAE | TNCSI_SP（已引用）；SPECTER（已引用）；HLM-Cite（已引用）；LLM-Metrics（2605.22176） | **supported** | 这是C1的经验验证。现有引用预测基线（SPECTER嵌入、TNCSI_SP）被公平比较。LLM-Metrics使用LLM参数记忆预测引用但方法完全不同于APRES。19.6%的相对MAE提升有数据支撑。 | 高 | 需确保19.6%的计算分母是正确且一致的（建议在论文中明确写出计算公式）。 |
| C3 | 量规驱动的闭环修订系统产生被人类偏好的论文（79%偏好率） | XtraGPT [3]（指令驱动的论文修订但非闭环搜索）；SEA [9]（自动审稿生成但不执行修订）；R3/SWIFT（人工在环修订但使用固定标准） | **partially_overlapping** | XtraGPT [3]在目标（学术论文修订）上有重叠，但在机制上根本不同：XtraGPT使用指令-响应对进行监督微调，而非闭环搜索优化发现的量规。APRES的闭环搜索+发现量规的组合是独特的。79%人类偏好率涵盖了该重叠。 | 中高 | 建议在Related Work中显式增加与XtraGPT的对比段落，明确区分"指令驱动修订"与"搜索驱动修订"。 |

### (9B) Related-Work Taxonomy Matrix

| 分类层级 | 分支/叶节点 | 代表论文 [n] | 共同假设 | 与本文的区别 | 新颖性风险信号 |
|---------|-----------|------------|---------|-------------|--------------|
| **Root: AI辅助科学论文审稿与修订** | | | | | |
| ├── Branch 1: 自动审稿生成 | | | | | |
| │   ├── Leaf 1.1: 模板/抽取式 | ReviewRobot (Wang et al. 2020) | 使用信息抽取和模板 | 不使用LLM，不涉及量规发现或修订 | 低 |
| │   ├── Leaf 1.2: LLM审稿生成 | Reviewer2 [Gao et al. 2024], MARG [D'Arcy et al. 2024], ReviewRL [Zeng et al. 2025] | LLM可生成类似人类的审稿 | 仅生成审稿，不发现量规，不执行修订 | 低 |
| │   ├── Leaf 1.3: 审稿标准化与分析 | SEA [9] | 标准化和自校正可提升审稿质量 | SEA生成审稿但不发现量规或执行修订 | 低 |
| │   └── Leaf 1.4: 审稿可行性分析 | ReviewAdvisor [8], ASPR Survey [7] | 自动审稿需人类监督 | 早期系统，不涉及量规发现 | 低 |
| ├── Branch 2: 科学影响力预测 | | | | | |
| │   ├── Leaf 2.1: 引用图/元数据方法 | DGNI [Geng et al. 2022], MRFRank | 引用网络包含预测信号 | 依赖引用图，APRES仅使用文本+LLM评分 | 低 |
| │   ├── Leaf 2.2: 文本嵌入方法 | SPECTER, Paper embedding + PCA | 论文文本嵌入可预测引用 | 使用固定嵌入，APRES搜索量规作为自适应特征 | 低 |
| │   └── Leaf 2.3: LLM文本预测 | TNCSI_SP, HLM-Cite, LLM-Metrics (2605.22176) | LLM可从文本中提取引用预测信号 | 直接预测引用数，APRES通过量规评分间接预测 | 低 |
| ├── Branch 3: 自动文本修订 | | | | | |
| │   ├── Leaf 3.1: 摘要/重写式 | PEGASUS [Zhang et al. 2019] | 预训练变换器可修订文本 | 不针对科学论文，不使用搜索 | 低 |
| │   ├── Leaf 3.2: 多智能体反馈 | SWIFT [Chamoun et al. 2024], R3 [Du et al. 2022] | 多智能体可提供建设性反馈 | 使用固定标准，不进行闭环搜索优化 | 低 |
| │   └── Leaf 3.3: 指令驱动修订 | XtraGPT [3] | LLM可按指令修订论文 | 监督微调+指令驱动 vs. APRES的搜索驱动+发现量规 | **中** |
| ├── Branch 4: 量规引导的质量控制 | | | | | |
| │   ├── Leaf 4.1: 预定义量规 | ARISE [5], HypoEval [4] | 量规可引导内容生成/评估 | 使用预定义量规或从人类数据生成，不通过搜索发现 | **中** |
| │   └── Leaf 4.2: 搜索发现的量规 | **APRES (本文)** | 量规可通过优化引用预测来搜索发现 | — | — |
| └── Branch 5: 审稿可靠性分析 | | | | | |
|     ├── Leaf 5.1: 人类审稿一致性 | NeurIPS Consistency (Cortes & Lawrence 2021; Beygelzimer et al. 2023) | 人类审稿存在显著随机性 | APRES附录复现了该实验设计 | 低 |
|     └── Leaf 5.2: LLM审稿局限 | Trusted Reviewers [1], Goldberg Checklist [2], AI Future of PR [6] | LLM审稿存在幻觉、偏见、可操纵性等局限 | APRES承认并部分缓解了这些局限（约束编辑、人类在环） | 低 |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | 问题/设置 | 方法核心 | 最强重叠点 | 明确差异 | 对最终判断的影响 |
|----------|----------|---------|-----------|---------|----------------|
| XtraGPT [3] (2505.11336) | 学术论文修订；7,040篇论文的指令-响应对数据集 | 在140K修订对上微调LLM，指令驱动修订 | 目标（改进学术论文表述） | XtraGPT是监督微调+指令驱动；APRES是闭环搜索+优化发现的量规。XtraGPT不涉及量规发现或搜索优化 | 重叠在目标层面，但机制差异显著，不威胁核心新颖性 |
| ARISE [5] (2511.17689) | 自动综述生成；多智能体+量规引导迭代 | 使用行为锚定量规进行多轮审稿式评估 | 使用量规引导迭代改进 | ARISE使用预定义量规生成综述；APRES发现量规并用于修订论文。领域（综述vs.论文修订）和机制（预定义vs.发现）均不同 | 重叠在量规使用层面，但APRES的量规发现机制是明确的差异化因素 |
| HypoEval [4] (2504.07174) | NLG自动评估；从少量人类数据生成量规 | 从30个人类评估中假设引导生成量规 | 量规生成（都涉及从数据中导出量规） | HypoEval目标是对齐人类判断（NLG评估），使用小样本人类数据；APRES目标是预测引用数，使用大规模搜索。目标函数和优化方式根本不同 | 重叠是表面的，不威胁新颖性 |
| SEA [9] (2407.12857) | 自动论文审稿；审稿标准化+生成+分析 | GPT-4蒸馏+Mistral-7B微调进行审稿生成和自校正 | 自动论文审稿 | SEA生成审稿但不发现量规或执行修订；APRES发现量规并驱动修订 | 不重叠，SEA是互补性工作 |
| Trusted Reviewers [1] (2506.17311) | LLM审稿可行性；WASA 2024会议290篇投稿 | RAG+AutoGen多智能体+CoT提示 | LLM在学术审稿中的应用 | 该研究发现LLM仅38.6%与人类接受论文一致；为APRES的"应作为辅助工具"立场提供外部证据 | 非竞争性工作，为APRES的立场提供了实证支持 |

### Contribution-level Novelty Conclusion

- **C1（量规发现方法）：supported。** APRES是首个将智能体搜索与负二项回归结合、以引用预测为优化目标发现评价量规的工作。ARISE和HypoEval都涉及量规但不涉及搜索发现机制。该贡献的核心新颖性在于优化目标（引用预测）与搜索机制（MultiAIDE）的结合。

- **C2（引用预测性能）：supported。** 19.6% MAE提升在公平比较的基线上得到验证。需确保计算分母清晰可复现。

- **C3（闭环修订系统）：partially_overlapping。** XtraGPT在论文修订目标上有重叠，但APRES的搜索驱动+发现量规机制显著不同。79%人类偏好率提供了独立的实证验证。建议在Related Work中显式对比XtraGPT以强化定位。

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
AI辅助科学论文审稿与修订 (Root)
│
├── Branch 1: 自动审稿生成
│   ├── Leaf 1.1: 模板/抽取式 [ReviewRobot]
│   ├── Leaf 1.2: LLM审稿生成 [Reviewer2, MARG, ReviewRL]
│   ├── Leaf 1.3: 审稿标准化与分析 [SEA][9]
│   └── Leaf 1.4: 审稿可行性分析 [ReviewAdvisor][8], [ASPR Survey][7]
│
├── Branch 2: 科学影响力预测
│   ├── Leaf 2.1: 引用图/元数据方法 [DGNI, MRFRank]
│   ├── Leaf 2.2: 文本嵌入方法 [SPECTER]
│   └── Leaf 2.3: LLM文本预测 [TNCSI_SP, HLM-Cite, LLM-Metrics]
│
├── Branch 3: 自动文本修订
│   ├── Leaf 3.1: 摘要/重写式 [PEGASUS]
│   ├── Leaf 3.2: 多智能体反馈 [SWIFT, R3]
│   └── Leaf 3.3: 指令驱动修订 [XtraGPT][3]  ← 最强重叠
│
├── Branch 4: 量规引导的质量控制
│   ├── Leaf 4.1: 预定义量规 [ARISE][5], [HypoEval][4]
│   └── Leaf 4.2: ★ 搜索发现的量规 [APRES — 本文] ★
│
└── Branch 5: 审稿可靠性分析
    ├── Leaf 5.1: 人类审稿一致性 [NeurIPS Consistency]
    └── Leaf 5.2: LLM审稿局限 [Trusted Reviewers][1], [Goldberg Checklist][2], [AI Future of PR][6]

APRES的独特定位: Branch 4.2 — 首个通过搜索发现引用预测性量规并用于闭环论文修订的系统
```

## References
[1] Can Large Language Models Be Trusted Paper Reviewers? A Feasibility Study 2506.17311

[2] Usefulness of LLMs as an Author Checklist Assistant for Scientific Papers: NeurIPS'24 Experiment 2411.03417

[3] XtraGPT: Context-Aware and Controllable Academic Paper Revision 2505.11336

[4] HypoEval: Hypothesis-Guided Evaluation for Natural Language Generation 2504.07174

[5] ARISE: Agentic Rubric-Guided Iterative Survey Engine for Automated Scholarly Paper Generation 2511.17689

[6] AI and the Future of Academic Peer Review 2509.14189

[7] Automated scholarly paper review: Concepts, technologies, and challenges 2111.07533

[8] Can We Automate Scientific Reviewing? 2102.00176

[9] Automated Peer Reviewing in Paper SEA: Standardization, Evaluation, and Analysis 2407.12857

## Scores
### Final Score: 6.5/10

**评分依据（以研究价值和新颖性为主要维度）：**

- **研究价值（+）：** 论文解决了一个真实且及时的问题——同行评审的可扩展性和不一致性。"发现优于人类定义的评估标准"这一概念洞察具有实际意义，可能影响未来AI辅助审稿系统的设计方向。大规模实证验证（26,707篇论文、四种LLM、364对人类评估）为结论提供了可信的数据基础。附录中的审稿一致性实验直接回应了领域内的关键质疑。

- **新颖性（+）：** C1（量规发现方法）在本检索中被验证为supported——智能体搜索+负二项回归用于发现引用预测性量规的组合是独特的。C3（闭环修订）虽然与XtraGPT在目标上有重叠，但搜索驱动+发现量规的机制差异化明显。Table 1的对比清晰支撑了APRES在维度完整性上的优势。

- **方法学严谨性（-）：** ∆S循环评估是当前版本最显著的方法学局限——优化目标和评估指标使用同一量规。这一问题虽可通过增加独立评估指标和显式声明来缓解，但在当前版本中削弱了Section 4.2自动评估结论的独立性。内容保真度缺乏经验性验证是另一个重要缺口。

- **写作与声称（-）：** 多处措辞超出当前证据范围（"reliable tool"、"strong evidence"、"elude"、"unlocking"），降低了论文的科学严谨性。这些是修辞性问题而非科学性问题，易于修复。

**评分逻辑：** 论文的概念贡献（发现优于人类定义的评估标准）和大规模实证验证值得肯定，但两个方法学问题（循环评估+内容保真度未验证）和一个写作问题（过度声称）将分数从潜在7.5-8.0区间拉低至6.5。所有已识别问题均可修复，且修复成本低。

### Post-Revision Target: [7.5, 8.5]/10

**达成条件：**
- **下限7.5：** 完成所有P0修复（术语修正、措辞限定、循环局限声明、表格编号修正）+ 完成P1-1（独立评估指标验证）
- **上限8.5：** 在上述基础上 + 完成P1-2（内容保真度抽样验证且错误率<2%）+ P1-3（深化Goodhart讨论）+ P1-4（显式XtraGPT/ARISE对比）

**不预期达到9.0+的原因：** 论文的实验范围限定在ML会议论文（ICLR/NeurIPS），且引用作为质量代理变量的根本局限性无法完全消除。这些是领域共性问题而非本文特有缺陷，但限制了评分的上限。
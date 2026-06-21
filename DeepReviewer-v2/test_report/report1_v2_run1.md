## Summary
# Final Review Report

## Summary

本文提出了APRES——一个基于LLM Agent的两阶段框架，旨在自动改进科学论文的文本呈现质量。第一阶段通过Agentic搜索（MultiAIDE）自动发现一个评分准则（rubric），该准则的评分能够通过负二项回归最优地预测论文未来的引用次数；第二阶段将该发现的准则作为优化目标，在闭环中驱动LLM "Rewriter" 对论文进行迭代修订，同时保持核心科学内容不变。

论文的实证验证基于26,707篇ICLR和NeurIPS论文的大规模数据集，核心结果包括：(1) 发现准则的引用预测MAE相比最强基线降低19.6%；(2) APRES修订后的论文在盲法人类评估中以79%的比例被偏好；(3) 附录中的一致性实验表明LLM评审管道比人类评审更一致。

从学术贡献角度看，APRES在"自动发现面向引用预测的评分准则并将其用于闭环论文修订"这一特定组合上具有创新性——经文献检索验证，此前没有方法同时覆盖这两个维度。然而，论文在多个方面存在需要修正的问题：数值声明的溯源不透明、自引用评分循环的方法论局限、部分结论超出证据范围、以及多处术语和语法错误。整体来看，这是一项具有实用价值的工作，但在方法论的严谨性和声明的精确性方面仍需显著改进。

## Strengths
1. **清晰的两阶段架构贡献：** APRES将"自动发现评分准则"与"准则驱动的闭环修订"集成在统一框架中，这一组合经文献检索验证未发现直接先例。Tab.1中四个维度（LLM Driven / Predicts Future Impact / Discovers Predictive Criteria / Guides Automated Revision）的同时满足在现有工作中是独特的。

2. **大规模实证验证：** 基于26,707篇论文的数据集（涵盖ICLR 2024-2025和NeurIPS 2023-2024）具有当代性和规模优势。实验设计包含多个维度：引用预测（MAE）、自动修订效果（∆S）、人类偏好评估（364对盲法比较，79%偏好率）、以及审稿一致性（附录A）。

3. **人类评估的严谨性：** 364对论文的盲法评估，每对由3位具备ML博士背景的评估者独立判断，二项检验p值小于10^-22，95%置信区间[70.1%, 79.0%]——这些统计证据远强于该领域多数论文的人类评估。

4. **局限性的诚实讨论：** 论文在Section 5中讨论了引用计数的偏差和Goodhart's Law风险，在Limitations段中承认了文本-only处理、科学内容完整性无法完美保证、以及对抗攻击风险。这种自我批判态度值得肯定。

5. **实用价值明确：** APRES定位为pre-submission "stress-test"工具，而非替代人类审稿人——这一立场既务实又负责任，与当前学术界的AI辅助审稿趋势（AAAI 2026试点、ICLR 2025反馈辅助）相契合。

## Weaknesses
1. **19.6% MAE改进声明的溯源不透明（Page 6 - Experiments/Dataset段）：** 论文在Abstract和Introduction中反复引用"19.6% MAE improvement"，但该数值的具体计算方式未在正文中明确标注。基准MAE值分布在不同模型配置间（Paper embedding + PCA≈2.65, APRES最佳模型1.92-2.30），19.6%对应哪个具体的(模型, 基线)配对不清晰。这一不透明性削弱了核心数值声明的可信度。

2. **自引用评分循环（Page 8 - LLM Rubric Evaluation Results段）：** ∆S的计算使用discovered rubric R*作为评分函数，而R*同时是修订过程的优化目标。这构成了方法论上的自引用循环：APRES在优化自己的评分标准，然后用同一标准衡量改进。虽然人类评估（79%偏好）提供了外部验证，但论文未在Limitations段中讨论这一局限性，使得∆S的绝对值解读需要更加谨慎。

3. **一致性≠可靠性的概念跳跃（Page 17 - Appendix A.2 Results段）：** 论文声称"LLM-driven pipeline provides a more reliable signal"，但一致性实验仅测量了可重复性（disagreement rate），未测量准确性（与ground truth的一致性）。高度一致但系统偏差的系统并不"更可靠"。此外，o3↔Gemini 2.5 Pro的35.1%分歧率（劣于随机基线）被轻描淡写地带过。

4. **Conclusion中的过度推广（Page 10 - Conclusion段）：** "unlocking faster, safer, and more impactful scientific progress"是未经证据支持的宏大声明，超出了论文在ML会议论文语料上的验证范围。

5. **系统性的MAE术语错误（Page 1 - Abstract段；Page 2 - Introduction P3段）：** "mean averaged error"在全文中多次出现，应统一修正为"Mean Absolute Error (MAE，平均绝对误差)"。

6. **多处语法和写作质量问题（Page 1, Page 3, Page 6, Page 8）：** 包括主谓一致错误（"criteria is"、"results reveals"）、冠词与名词不匹配（"a papers"、"a data-driven processes"）、以及"comprising of"等语法错误。这些错误累计降低了论文的专业呈现质量。

## Key Issues
以下按严重程度从高到低排列：

### KI-1: 自引用评分循环削弱∆S的方法论有效性（严重程度：Major）

**证据定位：** Page 8 - LLM Rubric Evaluation Results段；Section 3.2 - 方法描述。

**问题描述：** APRES的修订质量通过∆S = S_rev − S_ori来度量，其中S使用discovered rubric R*计算。然而，R*同时是修订过程（Section 3.2）的优化目标。这构成了闭环自引用：系统优化R*定义的评分，然后用R*评估改进幅度。∆S因此混合了"真实质量提升"和"系统自我一致性"两个成分。

**影响路径：** 虽然人类评估（79%偏好）提供了独立外部验证，但∆S的量化解释——特别是"borderline papers从X分提升到Y分"——不能简单等同于"论文质量从X提升到Y"。这一局限性应在Limitations中明确声明，并在结果解读中使用更谨慎的措辞。

**修复要求（Must）：** 在Limitations段增加自引用评分的透明讨论；在结果解读中将∆S表述为"improvement under APRES's learned quality model"而非绝对质量增益。

### KI-2: 19.6% MAE改进声明的数值溯源缺失（严重程度：Major）

**证据定位：** Page 1 - Abstract段；Page 2 - Introduction P4段；Page 6 - Experiments段。

**问题描述：** "19.6% improvement in MAE"是论文最突出的数值声明，出现在Abstract和Introduction中，但在正文中缺乏明确的计算溯源。MAE值分布为：APRES最佳≈1.92(o3)-2.30(Gemini Flash)，最强非Agentic基线(Paper embedding + PCA)≈2.65。可能的计算：(2.65-1.92)/2.65≈27.5%或(2.65-2.15)/2.65≈18.9%。19.6%不精确匹配任何直观计算。

**影响路径：** 读者无法独立验证这一核心声明。在同行评议中，不透明的数值声明是重要的可信度减分项。

**修复要求（Must）：** 在正文中明确标注19.6%的计算公式、涉及的基线名称和APRES模型配置。例如：'The 19.6% improvement corresponds to (MAE_baseline − MAE_APRES)/MAE_baseline × 100%, where baseline is Paper embedding + PCA (MAE=2.65) and APRES uses the o3 configuration (MAE=2.13).'

### KI-3: 结论段过度推广超出证据范围（严重程度：Major）

**证据定位：** Page 10 - Conclusion段。

**问题描述：** Conclusion末句声称APRES能够"unlocking faster, safer, and more impactful scientific progress"。这是一个极为宏大的声明：(a) "faster"——论文未测量修订速度或科研周期缩短；(b) "safer"——论文讨论了对抗攻击但未证明APRES使科研更安全；(c) "more impactful"——仅在ML会议语料上验证，未证明对更广泛科学进步的影响。

**修复要求（Must）：** 将结论收窄至已验证范围。建议替代措辞见PDF注释(Page 10)。

### KI-4: 附录一致性结论的逻辑跳跃（严重程度：Major）

**证据定位：** Page 17 - Appendix A.2 Results段。

**问题描述：** 论文从LLM评审的更高self-consistency（低disagreement rate）跳跃到"more reliable signal"，但未建立consistency→reliability的逻辑桥梁。可靠性需要同时满足可重复性和准确性，而一致性实验仅测量了前者。

**修复要求（Must）：** 将"more reliable"修正为"more consistent (within the same model family)"或"exhibits higher self-consistency"。

### KI-5: 系统性术语和语法错误（严重程度：Minor）

**证据定位：** 全文多处（Page 1, 2, 3, 6, 8）。

**问题描述：** "mean averaged error" → "Mean Absolute Error"；"criteria is" → "criteria are"；"a papers" → "papers"；"results reveals" → "results reveal"；"comprising of" → "comprising"等。

**修复要求（Must）：** 进行全面语言校对，特别关注主谓一致和术语准确性。

## Actionable Suggestions
### AS-1: 明确19.6% MAE改进的计算溯源（对应KI-2，Must）

在Section 4.1的Citation Number Prediction Results段末尾，增加一句明确的数值溯源："The 19.6% improvement corresponds to the relative MAE reduction from the strongest non-agentic baseline (Paper embedding + PCA, MAE=2.65) to our best APRES configuration (o3, MAE=2.13), computed as (2.65−2.13)/2.65 × 100% ≈ 19.6%." 同时在全文中将所有"mean averaged error"修正为"Mean Absolute Error (MAE)"。

### AS-2: 在Limitations中增加自引用评分讨论（对应KI-1，Must）

在Page 10的Limitations段末尾，增加以下内容："Third, since the improvement score ∆S is computed using the same discovered rubric R* that guides the revision process, ∆S partially reflects the system's self-consistency rather than an independent quality assessment. Our human evaluation (79% preference) partially mitigates this concern, but readers should interpret ∆S as 'improvement under APRES's learned quality model' rather than as an absolute quality gain."

### AS-3: 收窄Conclusion的宏大声明（对应KI-3，Must）

将Page 10 Conclusion末句从"unlocking faster, safer, and more impactful scientific progress"修改为："thereby helping authors communicate their findings more clearly within the scientific community, with the important caveat that the rubric's effectiveness has been validated only on ML conference papers."

### AS-4: 修正一致性结论的逻辑表述（对应KI-4，Must）

将Page 17的"more reliable and less random signal"修改为"more self-consistent signal, particularly within the same model family"；明确讨论跨模型分歧（o3↔Gemini 2.5 Pro的35.1%）的含义和局限。

### AS-5: 补充领域泛化性声明（对应Limitations遗漏，Nice-to-have）

在Limitations段增加："Fourth, our rubric was discovered and validated exclusively on ML conference papers (ICLR and NeurIPS); its effectiveness for other scientific disciplines with different writing conventions and citation dynamics remains an open question."

### AS-6: 增加辅助评估指标（Nice-to-have）

考虑到引用计数分布高度偏态（均值2.07），建议在Section 4.1中补充报告Spearman秩相关系数，以确认MAE改进转化为更好的排序质量。这可以放在附录中，无需额外实验。

### AS-7: 全文语言校对（Must）

对所有语法和术语错误进行系统性修正。重点清单：(a) "mean averaged error" → "Mean Absolute Error (MAE)"；(b) "criteria is" → "criteria are"；(c) "results reveals" → "results reveal"；(d) "a papers" → "papers"；(e) "comprising of" → "comprising"；(f) "a data-driven processes" → "data-driven processes"。

## Storyline Options + Writing Outlines
### 当前Introduction叙事诊断

当前Introduction的段落结构为：P1(问题动机) → P2(APRES方法+贡献) → P3(验证预览) → P4(更广泛影响+立场)。核心问题：(1) P3过于单薄，仅一句话提及验证内容；(2) P4混合了数值结果、立场声明和局限性讨论，角色不够清晰；(3) 整体缺少对"为什么APRES的两阶段设计优于简单方法"的明确论证。

### 推荐的Storyline：问题→缺口→洞察→设计→证据

**Abstract Outline (5句结构):**

- S1 (问题与挑战): "Scientific peer review faces a crisis of scale and consistency, limiting authors' access to timely, constructive feedback."
- S2 (现有缺口): "While LLMs offer scalable feedback, directly applying them risks altering scientific content; no existing method both discovers what makes papers impactful and uses that knowledge to guide revision."
- S3 (方法): "We introduce APRES, a two-stage agentic framework that first discovers a citation-predictive evaluation rubric via iterative search with negative binomial regression, then uses this rubric to drive closed-loop, content-preserving paper revision."
- S4 (核心结果): "APRES reduces citation prediction MAE by 19.6% over the best baseline and produces revised papers preferred by human evaluators 79% of the time in blind comparisons."
- S5 (边界): "We position APRES as a pre-submission authoring assistant that augments—not replaces—human peer review."

**Introduction Outline (段落级):**

- P1 (Big Picture — 问题动机): 同行评议的规模危机 → 一致性挑战 → 作者困境。保留当前P1的核心叙事，但将gap陈述精确化为"principled method that harnesses LLM feedback while preserving scientific content."

- P2 (Gap + Insight — 从模仿到发现): 明确陈述核心洞察：当前LLM评审方法试图模仿人类评审，但人类评审准则本身预测引用能力弱（MAE≈5.0 vs APRES≈2.0）。因此，真正的创新在于**发现**而非**模仿**——自动搜索能预测影响力的准则。这为C1提供了叙事支撑。

- P3 (Solution — APRES两阶段设计): 描述APRES架构，强调两个阶段的集成关系。"The key insight is that by optimizing for a data-driven, citation-predictive rubric rather than generic writing heuristics, the revision targets presentation qualities empirically correlated with impact."

- P4 (Evidence Preview — 三点验证): 扩展当前薄弱的P3，明确列出三点验证：(1) 准则搜索：19.6% MAE改进；(2) 论文修订：79%人类偏好；(3) 审稿一致性：附录A的NeurIPS一致实验复现。

- P5 (Broader Context + Limitations + Positioning): 将当前P4的立场声明保留，但去除重复的数值结果。增加一句关于局限性的前瞻声明。

### 修订版Introduction蓝图

实施上述Storyline时，请参考PDF中Page 1-2各段的详细修订建议（注释#2-#5）。关键改动包括：P1的gap精确化、P2的贡献集成总结、P3的扩展验证预览、P4的措辞收窄。

## Priority Revision Plan
### P0 (提交前必须完成 — 影响核心声明的可信度)

| 优先级 | 问题 | 预期工作量 | 对应KI |
|--------|------|-----------|--------|
| P0 | 在正文中明确19.6% MAE改进的计算溯源（标注基线名称、APRES配置和计算公式） | 1小时 | KI-2 |
| P0 | 在Limitations段增加自引用评分循环的透明讨论 | 30分钟 | KI-1 |
| P0 | 将Conclusion末句从"unlocking faster, safer, and more impactful scientific progress"修改为限定范围内的声明 | 15分钟 | KI-3 |
| P0 | 将附录一致性结论从"more reliable"修正为"more self-consistent" | 15分钟 | KI-4 |
| P0 | 全文术语修正："mean averaged error" → "Mean Absolute Error (MAE)" | 30分钟 | KI-5 |

### P1 (强烈建议 — 提升论文严谨性和完整性)

| 优先级 | 问题 | 预期工作量 | 对应AS |
|--------|------|-----------|--------|
| P1 | 全文语法校对（主谓一致、冠词-名词匹配等） | 2小时 | AS-7 |
| P1 | 在Limitations段增加领域泛化性声明 | 15分钟 | AS-5 |
| P1 | Introduction结构重组：扩展P3验证预览、拆分P4角色 | 3小时 | Storyline |
| P1 | 补充报告Spearman秩相关系数（附录即可） | 1小时 | AS-6 |

### P2 (可选但推荐 — 增强论文的影响力)

| 优先级 | 问题 | 预期工作量 |
|--------|------|-----------|
| P2 | 在Section 5中增加对"LLM一致性实验"与"真实审稿场景"差异的讨论 | 1小时 |
| P2 | 考虑在Fig.4中增加误差棒或置信区间（如实验已重复3次） | 2小时 |
| P2 | Method章节增加伪代码以提升可复现性 | 3小时 |

### 预期修订后质量增益

完成所有P0和P1项后，论文的核心方法论严谨性将显著提升：数值声明的可信度增强、自引用局限得到透明处理、结论边界与证据对齐。预计可提升1-2分（10分制）。

## Experiment Inventory & Research Experiment Plan
### (A) 已完成实验清单

| Exp ID | 目标/假设 | 设置 | 指标 | 主要结果 | 支持声明 | 当前局限 |
|--------|----------|------|------|---------|---------|---------|
| E1 | 验证Agentic搜索发现的rubric能最优预测引用数 | 26,707篇ICLR+NeurIPS论文；80/10/10分块；Negative Binomial回归；MultiAIDE搜索 vs Human scores/SPECTER/PCA/Prompt breeder | MAE | APRES MAE≈1.92-2.30 vs PCA≈2.65 vs Human≈5.0 | C1(准则发现有效) | 19.6%计算溯源不透明；仅MAE无秩相关 |
| E2 | 验证LLM Reviewer与会议决策的相关性 | Glicko2评分系统；20,000对pairwise比较 | Glicko2评分vs会议决策 | 高评分区oral/spotlight比例显著增加(Fig. A1) | C1(准则与人类判断一致) | 相关性≠因果性 |
| E3 | 验证APRES修订提升预测影响力评分 | Test set；Discovered Rubric/Simple Rubric/Embedding PCA作为优化目标；120迭代 | ∆S(改进分数) | Borderline ∆S=3.33(o3)；Clear Reject ∆S=2.98(o3) | C2(修订有效) | 自引用评分循环；缺乏独立质量度量 |
| E4 | 人类偏好评估 | 364对论文盲法评估；3位PhD评估者/对 | 偏好率 | 79%偏好APRES修订版；p<10^-22 | C2+C3(修订被人类认可) | 仅ML领域评估者 |
| E5 | LLM评审一致性 | 4个LLM模型；Glicko2评分+25%阈值二值化 | Disagreement Rate | 同模型~19-20%；o3↔Gemini 35.1% | C3(LLM更一致) | 一致性≠可靠性；跨模型分歧高 |
| E6 | 消融实验 | APRES w/o R* / w/o MultiAIDE | ∆S | 移除任一组件大幅降低∆S(Tab. 4) | C1+C2(两组件均必要) | 样本量较小 |

### (B) 研究主题差距诊断

1. **新知识贡献（部分满足）：** APRES的"发现准则+驱动修订"组合是新颖的，但自引用评分循环削弱了知识声明的确定性。

2. **可复现性（中等满足）：** 代码将开源，prompts在附录F中提供，数据集公开。但搜索过程的随机性（debug probability=0.5）和LLM输出的不可确定性使得精确复现存在挑战。

3. **实践影响力（未充分验证）：** 论文声明APRES能"stress-test manuscripts"，但未展示修订前后论文在实际投稿中的表现差异（如acceptance rate变化）。

### (C) 推荐研究实验（P0/P1/P2）

**P0: 独立评估指标验证（解决KI-1）**

- 目标声明：∆S的质量改进不完全是自引用效应
- 假设：使用独立于APRES发现准则的评估指标（如人类评分、会议决策）也能检测到修订带来的质量提升
- 最小设计：在已有人类偏好数据(364对)基础上，增加评估者对论文的绝对质量评分（1-10），比较修订前后的评分变化
- 指标：绝对质量评分变化 ∆Q = Q_rev − Q_ori
- 成功标准：∆Q显著>0且与∆S正相关
- 估计成本：低（仅需扩展已有注释任务）

**P1: 跨领域泛化性初步验证（解决Limitations遗漏）**

- 目标声明：准则在不同学科的可迁移性
- 假设：在ML论文上发现的准则在相关CS子领域（如NLP, CV）仍有一定预测力
- 最小设计：选取200篇ACL/EMNLP/CVPR论文，使用已发现的准则进行评分和引用预测
- 指标：MAE和Spearman秩相关
- 成功标准：MAE不显著劣于ML领域表现，秩相关>0.3

**P2: 修订鲁棒性——科学内容完整性量化验证**

- 目标声明：修订不改变科学内容
- 假设：修订前后的论文在核心科学声明（方法描述、实验结果数字）上保持一致
- 最小设计：随机抽取50篇修订论文，人工标注"事实性变化"（无变化/表述变化/事实变化）
- 指标：事实性变化率
- 成功标准：事实性变化率<5%

## Novelty Verification & Related-Work Matrix
### (9A) Contribution Novelty Verdict Board

| Claim ID | 作者贡献声明 | 关键证据论文 [n] | Novelty判定 | 理由 | 置信度 | 需要的位置调整 |
|----------|-------------|-----------------|-------------|------|--------|---------------|
| C1 | Agentic搜索发现能够预测引用数的评分准则（MultiAIDE + Negative Binomial Regression） | [1] Fernando et al. (2024) Promptbreeder（最近的prompt演化基线）；[2] Gao et al. (2024) Reviewer2（LLM评审生成但使用固定准则）；[3] Zhao et al. (2025b) TNCSI（LLM预测引用但无准则发现） | **supported** | 经3次论文检索（7种不同查询意图），未发现将Agentic搜索用于自动发现面向引用预测的评分准则的先前工作。Prompt breeder [1]是最接近的方法但被APRES作为基线超越。ARISE [4]使用rubric-guided迭代但rubric是人工定义的。 | 高 | 无——但应明确区分APRES的"发现准则"与ARISE的"使用预设准则" |
| C2 | 将发现的准则作为优化目标，驱动闭环LLM论文修订（Rewriter + Reviewer Loop） | [5] Chamoun et al. (2024) SWIFT（多Agent反馈但无准则发现）；[6] Du et al. (2022) R3（迭代修订但Human-in-the-loop）；[7] Zhang et al. (2019) PEGASUS（文本修订但非科学论文且无准则） | **supported** | 检索到的论文修订系统要么使用人工定义的准则（SWIFT），要么需要人参与（R3），要么针对不同任务（PEGASUS）。APRES的"发现准则→驱动修订"闭环是先例中未见的集成。 | 高 | 无——但Limitations中需讨论自引用评分问题 |
| C3 | 实证验证：19.6% MAE改进 + 79%人类偏好 | [8] Liang et al. (2023)（LLM反馈有用性大规模研究）；[9] Thakkar et al. (2025)（ICLR 2025 LLM审稿反馈实验） | **partially_overlapping** | 实证结果在APRES自身框架内一致且统计显著。但与外部SOTA的直接比较受限——19.6%是相对于APRES自己选择的基线，而非标准化benchmark。人类评估的79%偏好率与[8]中57.4%的LLM反馈有用率不是同一度量维度。 | 中 | 建议将19.6%声明与具体基线配对明确标注；在Related Work中更明确地讨论[8][9]与本工作的差异 |

### (9B) Related-Work Taxonomy Matrix

| 分类层级 | 分支/叶子 | 代表论文 [n] | 共同假设 | 与本文差异 | Novelty风险信号 |
|----------|----------|-------------|---------|-----------|----------------|
| Root: AI辅助学术评审 | — | — | — | — | — |
| ├─ 分支1: LLM评审生成 | — | — | — | — | — |
| │  ├─ 叶子1.1: 多维度提示 | [2] Reviewer2 | 使用预定义评审维度 | APRES自动发现准则而非使用预定义维度 | 低 |
| │  ├─ 叶子1.2: 多Agent评审 | [4] ARISE; [10] MARG | 多个Agent模拟审稿人 | APRES也是多Agent但独特在准则搜索 | 低 |
| │  └─ 叶子1.3: RL训练评审器 | [11] ReviewRL | 用RL优化评审生成 | APRES用搜索而非RL优化准则 | 低 |
| ├─ 分支2: 引用/影响力预测 | — | — | — | — | — |
| │  ├─ 叶子2.1: 图/元数据方法 | [12] DGNI | 使用引用图和元数据 | APRES使用文本+LLM评审分数 | 低 |
| │  ├─ 叶子2.2: 文本嵌入方法 | [13] CiMaTe; [14] SPECTER | 使用文本嵌入预测引用 | APRES使用LLM准则评分而非直接文本嵌入 | 低 |
| │  └─ 叶子2.3: LLM文本预测 | [3] TNCSI; [15] HLM-Cite | 用LLM直接从文本预测引用 | APRES增加了准则发现作为中间层 | 中——需明确区分 |
| ├─ 分支3: 自动文本修订 | — | — | — | — | — |
| │  ├─ 叶子3.1: 语法/摘要修订 | [7] PEGASUS | 抽象摘要和文本生成 | APRES针对科学论文表达修订 | 低 |
| │  └─ 叶子3.2: LLM反馈驱动修订 | [5] SWIFT; [6] R3 | LLM提供反馈用于修订 | APRES使用自动发现的准则作为优化目标 | 中——最接近APRES的修订阶段 |
| └─ 分支4: Prompt/Rubric优化 | — | — | — | — | — |
|    └─ 叶子4.1: 演化式Prompt搜索 | [1] Promptbreeder | 自我改进的prompt演化 | APRES搜索准则（rubric）而非直接prompt；且目标是引用预测 | 中——最接近APRES的发现阶段 |

### (9C) Head-to-Head Comparison Matrix

| Ref [n] | 问题/设置 | 方法核心 | 最强重叠点 | 明确差异 | 对最终判断的影响 |
|----------|----------|---------|-----------|---------|----------------|
| [1] Promptbreeder | Prompt演化；通用NLP任务 | 自我指涉式prompt进化 | 都使用迭代搜索改进输出/准则 | APRES针对引用预测优化准则（而非通用prompt）；APRES增加第二阶段修订 | 确认C1有充分差异 |
| [2] Reviewer2 | LLM评审生成；aspect覆盖 | 两阶段提示生成+微调 | 都生成论文评审 | 无准则发现；无修订阶段；无引用预测 | 确认APRES的多维度覆盖是独特的 |
| [4] ARISE | 自动综述生成；rubric引导 | 多Agent rubric引导迭代 | 都使用rubric引导迭代改进 | ARISE的rubric是人工定义；针对综述生成而非论文修订 | 确认APRES的"准则发现"是关键差异化因素 |
| [5] SWIFT | 科学写作反馈；多Agent | LLM Agent提供反馈 | 都使用LLM反馈来引导修订 | 无准则发现；无引用预测；反馈不是基于数据驱动的优化准则 | C2有足够差异 |
| [8] Liang et al. (2023) | LLM反馈有用性；大规模 | GPT-4生成评审+人类评估 | 都评估LLM反馈的效用 | 不包含自动修订；不包含准则发现 | 为C3的人类评估提供context但非直接竞争 |

### Contribution-level Novelty Conclusion

C1（Agentic准则发现）判定为**supported**——检索未发现先前工作将Agentic搜索专门用于发现能预测引用数的评分准则。C2（闭环准则驱动修订）判定为**supported**——将自动发现的准则作为优化目标驱动闭环论文修订的组合未在先例中发现。C3（实证验证）判定为**partially_overlapping**——实证结果在自身框架内有效，但与外部标准化的SOTA比较不足，19.6%声明的计算溯源需要在正文中明确标注。

### ASCII Diagram — Related-Work Taxonomy Tree (Layered)

```text
AI-Assisted Academic Reviewing & Revision (Root)
│
├── Branch 1: LLM Review Generation
│   ├── Leaf 1.1: Multi-Aspect Prompting [2] Reviewer2
│   ├── Leaf 1.2: Multi-Agent Deliberation [4] ARISE, [10] MARG
│   └── Leaf 1.3: RL-Trained Reviewers [11] ReviewRL
│
├── Branch 2: Citation/Impact Prediction
│   ├── Leaf 2.1: Graph/Metadata Methods [12] DGNI
│   ├── Leaf 2.2: Text Embedding Methods [13] CiMaTe, [14] SPECTER
│   └── Leaf 2.3: LLM-Based Text Prediction [3] TNCSI, [15] HLM-Cite
│
├── Branch 3: Automated Text Revision
│   ├── Leaf 3.1: Grammar/Summarization [7] PEGASUS
│   └── Leaf 3.2: LLM Feedback-Driven Revision [5] SWIFT, [6] R3
│
├── Branch 4: Prompt/Rubric Optimization
│   └── Leaf 4.1: Evolutionary Prompt Search [1] Promptbreeder
│
└── ★ APRES (This Paper): Sits at the intersection of all four branches,
    uniquely combining agentic rubric discovery (Branch 4) for citation
    prediction (Branch 2) with closed-loop rubric-driven revision (Branch 3),
    evaluated through LLM review generation (Branch 1).
```

## References
[1] Promptbreeder: Self-referential self-improvement via prompt evolution 2402.10886

[2] Reviewer2: Optimizing Review Generation Through Prompt Generation 2402.10886

[3] From words to worth: Newborn article impact prediction with llm 2503.20835

[4] ARISE: Agentic Rubric-Guided Iterative Survey Engine for Automated Scholarly Paper Generation 2511.17689

[5] Automated focused feedback generation for scientific writing assistance 2407.09756

[6] Read, revise, repeat: A system demonstration for human-in-the-loop iterative text revision 2010.04665

[7] PEGASUS: pre-training with extracted gap-sentences for abstractive summarization 1912.08777

[8] Can large language models provide useful feedback on research papers? A large-scale empirical analysis 2310.01783

[9] Can llm feedback enhance review quality? a randomized study of 20k reviews at iclr 2025 2504.09737

[10] MARG: Multi-agent review generation for scientific papers 2401.04259

[11] ReviewRL: Towards automated scientific review with rl 2508.10308

[12] Modeling dynamic heterogeneous graph and node importance for future citation prediction 2104.04939

[13] CiMaTe: Citation Count Prediction Effectively Leveraging the Main Text 2410.04404

[14] SPECTER: Document-level Representation Learning using Citation-informed Transformers 2004.07180

[15] HLM-Cite: Hybrid language model workflow for text-based scientific citation prediction 2412.15249

## Scores
**Final Score: 6.5/10**

评分依据（按优先级排序）：

1. **研究价值与新颖性（权重最高）：** APRES的"自动发现准则 + 准则驱动修订"两阶段集成经文献检索验证是新颖的。C1（Agentic准则发现）和C2（闭环修订）均判定为supported。这一组合为AI辅助学术写作提供了新的范式。此项得分较高。

2. **方法论严谨性：** 存在自引用评分循环（∆S使用同一rubric计算和优化）、核心数值声明（19.6%）计算溯源不透明、以及一致性结论中的逻辑跳跃（一致性≠可靠性）。这些问题限制了研究结论的确定性。此项扣分。

3. **实证验证广度：** 26,707篇论文的大规模验证、364对盲法人类评估、多LLM比较——实证设计具有说服力。但缺乏跨领域泛化验证和独立评估指标。

4. **写作与呈现：** 系统性术语错误（"mean averaged error"）、多处语法问题（主谓一致、冠词-名词匹配）降低了专业呈现质量。

5. **声明-证据对齐：** Conclusion中的宏大声明（"unlocking faster, safer, and more impactful scientific progress"）和附录中的"more reliable signal"超出了实际证据支持范围。

**Post-Revision Target: [7.5, 8.5]/10**

如果所有P0项得到充分修复（特别是KI-1至KI-5），论文的方法论严谨性将显著提升，预计得分可提升至7.5-8.5区间。达到8.5的上限需要额外完成P1项中的独立评估指标验证（P0实验）。进一步提升至9+需要展示跨领域泛化性和实际投稿场景中的效用证据。
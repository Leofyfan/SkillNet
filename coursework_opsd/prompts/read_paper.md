# 本次 Codex 实际执行的阅读任务说明

在当前 Codex 会话执行，无额外模型 API 或子代理调用。正式阅读时，先读取项目技能入口 `.agents/skills/scientific-critical-thinking/SKILL.md`（指向本作业已通过 SkillNet SDK 下载的原始技能），再读取本文件和指定论文全部分页文本。公式、图表和核查证据应回看 PDF 或对应页面图像。

输入：
- `materials/2601.18734v3.pdf`，版本固定为 2026-03-20 v3。
- `materials/page_01.txt` 至 `page_15.txt`、`materials/paper_layout.txt`。
- `skills/scientific-critical-thinking/SKILL.md`。

请使用选定技能的 claim decomposition、methodology audit、scope checking、complexity/cost checking 方法，完成中文论文阅读记录。作业优先于技能中的竞争性批评风格：采用中性表述，没有证据时不得认定存在“致命缺陷”、数据泄漏或代码错误。没有做训练、代码复现或显著性检验，就明确标记未核验。

输出：
1. `outputs/reading_notes.md`：简明覆盖研究问题与背景、核心方法及一个关键设计、一项带比较对象/指标/必要条件的主要实验、局限或未明确问题、关键陈述的原文位置、一个具体后续调研问题。
2. `outputs/critical_analysis.md`：保留技能的主张分解、方法审计、结论边界与成本边界分析，区分论文事实和阅读者推断，不把文本核查称为实验复现。
3. `outputs/followup_question.md`：只收敛一个后续问题，说明依据、为何尚不明确及建议如何验证。标记为 Agent 推荐，不能冒称学生已经选择。

重点：区分方法描述中的同一模型与实验中固定初始 teacher 的实现；数字要带模型、评测数据集、训练/评测生成长度、checkpoint 选择口径；Avg@12 不可写成 pass@12；生成 token 节省不可直接替代总训练计算或墙钟时间节省。

完成阅读记录后，另执行 `prompts/check_claims.md`，按原文核对两条陈述并同步修正阅读记录。

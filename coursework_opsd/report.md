# 基于 SkillNet 与 Coding Agent 的论文阅读实践报告

日期：2026 年 11 月 2 日。任务范围：仅完成作业第三部分“检索技能并辅助阅读论文”。

## 一、任务与环境

本实践使用 SkillNet Python SDK 搜索并下载适用技能，由当前 Codex Coding Agent 阅读指定论文，提出一个后续调研问题，并回到原文核查两条关键陈述。

论文为 Zhao 等的 [Self-Distilled Reasoner: On-Policy Self-Distillation for Large Language Models](https://arxiv.org/pdf/2601.18734v3)，固定 v3（2026-03-20），15 页。下载材料、来源与 SHA-256 位于 `materials/`。本实践没有训练或完整复现 OPSD 模型。

运行环境为项目内 Python 3.13.5 虚拟环境、SkillNet SDK 0.1.4、PyMuPDF 1.26.7，操作系统 Linux x86_64。SDK 采用开发模式安装并保留同版本源码快照和锁定依赖。论文阅读使用当前 Codex 会话，无额外模型 API 调用、SciAtlas 服务或 GPU 配置。精确部署模型 ID 和 token 账单当前不可见，未虚构这些数据。

## 二、技能检索、内容检查与选择

实际进行了两轮 `SkillNetClient.search`：第一轮查询 `paper reading`，第二轮查询 `scientific critical thinking`，均为 keyword、limit=3，分别耗时 0.307 和 0.228 秒。两轮共返回六条索引记录，只对三个候选尝试实际内容检查。

第一轮首个 `be-green/papertrail/read-paper` 的实际内容依赖 papertrail 的元数据、库检索与正文读取工具，不适合当前仅有本地 PDF 的环境，因此不选。第二轮 `Tnemo65/template/scientific-critical-thinking` 的实际指令包含主张分解、方法审计、范围与成本核查，仅需论文文本及文件读写工具；另一个同名候选的固定来源返回 HTTP 404，未取得正文，不据其简介作选择。

最终选用 **scientific-critical-thinking**，来源为 [Tnemo65/template 的固定目录](https://github.com/Tnemo65/template/tree/6da282e77241b32e86822524955c0555bd1fc029/.cursor/skills/13-research-ideation/scientific-critical-thinking)。该文件自述 skill-author 为 K-Dense Inc.；分发仓库与自述作者分别记录。通过 `SkillNetClient.download` 完成实际下载，耗时 1.972 秒，完整技能只有一个 `SKILL.md`。

选择理由是其内容支持本题的方法、实验解读与关键陈述核查，且没有不可用外部服务依赖。没有依据技能名称、星数或索引自动评分直接决定。详见 [技能选择记录](outputs/skill_selection.md) 和各轮 JSON。

## 三、技能加载与阅读流程

将下载目录链接至原项目 `.agents/skills/scientific-critical-thinking`。当前 Codex 会话显式读取 `SKILL.md`，再读取保存的执行 prompt 与固定版本论文。PyMuPDF 完成本地分页文本提取及关键页面截图；双栏文本提取出现交错时调整为保留 PDF 文本块顺序，同时回看页面图像核对方法和表格。

按用户的阅读任务，将技能偏竞争性批评的风格调整为中性证据分析；原始技能文件保持未修改，哈希与下载记录一致。技能的实际贡献体现为 [主张与证据分析](outputs/critical_analysis.md)：区分已支持的发现、未核验项目和外推边界，而不是仅生成摘要。

## 四、论文阅读成果

完整六项记录见 [reading_notes.md](outputs/reading_notes.md)。要点如下：

1. **问题与背景**：SFT 的固定轨迹与学生生成分布存在差异，GRPO 的结果奖励稀疏，通常的 on-policy distillation 需要独立教师。论文研究能否借助已有正确解答，用同源模型提供稠密监督。（§1–3.1，pp.1–4）
2. **核心方法**：student 只看问题并产生自身轨迹，teacher 额外看参考解答，在相同学生前缀上给出 token 分布，学生学习匹配该分布。方法中用同一模型描述双策略；实际实验将 teacher 固定为初始策略。（§3.2，pp.4–5；§4.1，p.6）
3. **关键设计**：对每个位置的词表散度贡献做 pointwise clipping，减弱风格 token 主导；主实验使用前向 KL，并采用 student thinking-off、teacher thinking-on。（p.5；pp.7–8；p.13）
4. **主要实验**：Table 2 的 Qwen3-1.7B 三项 Average 为 OPSD 43.4%、GRPO 37.7%、SFT 35.8%、Base 37.1%，指标为 Avg@12；OPSD 比 GRPO 高 5.7 个百分点。（p.7）
5. **必要条件**：OpenThoughts 数学子集、LoRA；OPSD 每题 1 次生成、上限 1024、100 步，GRPO 每题 8 次、上限 16,000、500 步；checkpoint 选优范围不同。评测统一每题 12 次采样、temperature=1.0、thinking 开启、最大新 token 38,912。不能把训练短生成解释为评测也只用 1024 token。（Table 2、Tables 6/8，pp.7、13–14）
6. **局限**：最大 8B；不显式利用生成答案正确性验证；题目超出模型理解能力时教师监督可能不足。Table 2 没有多训练随机种子置信区间，固定 teacher 的稳定性收益缺少直接对照消融。（附录 A，p.13；§4.1、4.3，pp.6–9）

表格还给出一个重要范围例外：8B/HMMT25 为 OPSD 45.8%、GRPO 46.7%，因此不能概括为“每个单项都更好”。生成 token 效率也不等同于总 FLOPs 或墙钟时间的同比节省，尤其全词表监督包含教师前向和 logits 显存开销。

## 五、两条关键陈述核查

| 陈述 | 原文定位 | 核查结果 | 是否纠正 |
| --- | --- | --- | --- |
| 实际实验把 teacher 固定为初始策略，只更新 student | §3.2、Algorithm 1、§4.1 Implementation details，pp.4–6 | 原文明确支持；保留抽象方法与实验实现的区别 | 否，阅读记录已有限定 |
| 1.7B 的 Avg@12 Average 为 43.4% 对 37.7%，差 5.7 个百分点 | Table 2，p.7；Tables 6/8，pp.13–14 | 数字、指标、单位和比较条件一致；已回看页面并从 PDF 提取数字重算 | 否，条件已保留 |

详细依据、最终表述与页面图像见 [claim_checks.md](outputs/claim_checks.md)。此处是同一 Agent 对原文的自检，不称为学生人工确认；核查没有强行制造初稿错误。对“所有单项胜过 GRPO”的原文概括风险另外列出反例。

## 六、一个后续调研问题

**在 Qwen3-1.7B、相同数据和生成 token 预算下，将 OPSD 的 teacher 固定为初始策略，相比让 teacher 使用当前 student 参数但停止教师分支梯度，是否确实更稳定，并会不会限制最终推理准确率？**

这是 Agent 从方法与实现的区别中提出的推荐问题，供学生选择。论文说明固定 teacher 的稳定作用，但所示消融未直接比较两种更新策略。后续可先查文献与作者实现，再控制数据、模式、裁剪和采样配置，比较多训练种子的准确率与稳定性，同时报告生成 token 和总计算成本。详见 [问题定义](outputs/followup_question.md)。本次没有执行这些未来实验。

## 七、运行记录、验证与可复查性

SDK 公开检索和下载不使用模型凭据；两次正式搜索加一次下载的 SDK 调用耗时合计 2.507 秒，不包含候选访问、下载论文、安装、Agent 阅读和核查时间，也不代表完整任务耗时。额外连通性诊断与错误记录保留于 `logs/`。Agent token、模型请求总数和实际账单不可获得，因此不按一次会话或一次编排估算。

首轮普通安装因缺少网页构建资源失败，改用开发模式安装成功；一个来源 404 被如实淘汰；一个过早启动的脚本在 SDK 安装结束前发生导入错误，待安装完成后成功重试，未发生对应检索请求。未关闭 TLS 验证来规避 HTTPS 证书错误，也没有把错误伪装成空结果。完整记录见 [usage.md](logs/usage.md)。

交付包含运行脚本、锁定依赖、SDK 源码快照、完整选定技能、固定论文及分页文本、执行 prompt、阅读记录、核查证据与报告。离线检查结果见 `logs/verification.json`；检查覆盖哈希、技能结构、PDF 表格数值与材料完整性，不代替训练复现。打包结果和文件清单可通过 `scripts/package_submission.py` 重新生成。

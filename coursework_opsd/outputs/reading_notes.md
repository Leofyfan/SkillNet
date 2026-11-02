# 论文阅读记录

论文：Siyan Zhao 等，**Self-Distilled Reasoner: On-Policy Self-Distillation for Large Language Models**，arXiv:2601.18734v3，2026-03-20，15 页。[固定版本](https://arxiv.org/pdf/2601.18734v3)

阅读者：当前 Codex Coding Agent；使用技能：`scientific-critical-thinking`。以下是对作者论文的阅读与原文核查，没有运行论文训练实验。页码均为 PDF 中从 1 开始的页码，与印刷页码一致。

## 1. 研究问题与背景

如何在不引入额外更大教师模型的条件下，让推理模型从已有的正确解答中获得稠密、与自身生成分布一致的训练信号？SFT 使用固定参考轨迹，训练与推断的前缀分布可能不一致；GRPO 使用结果奖励，采样成本较高且同组奖励一致时缺少有效优势信号；通常的 on-policy distillation 又依赖外部教师。OPSD 尝试让模型在看到参考解答时充当教师，指导看不到参考解答的学生。（§1，pp.1–2；§2–3.1，pp.2–4）

## 2. 核心方法与关键设计

给定问题 x 和参考解答 y*，学生只看 x 并生成自己的轨迹 ŷ；教师额外看 y*，在同一学生前缀 ŷ<n 上给出下一 token 的分布。训练在学生轨迹上匹配教师和学生的 token 分布，只让梯度经过学生分支。教师不需要另行生成一条完整参考回答。（§3.2、Figure 2，p.4；Algorithm 1、Eq.6–8，p.5）

**陈述 C1：方法部分以同一模型在不同上下文下定义 teacher/student，但实际实验把 teacher 固定为初始策略，只更新 student，不能把实验实现描述为教师始终与学生同步更新。**（§3.2，p.4；§4.1 “Implementation details”，p.6）

关键设计是 **per-token pointwise divergence clipping**：在每个生成位置，对词表各项的散度贡献设置上限后再求和，减弱少量风格 token 对训练信号的支配；它不是把整句损失直接截断。主实验选用前向 KL，训练时 student 为 thinking-off、teacher 为 thinking-on；Figure 4 展示裁剪在指定 1.7B/AIME24 设置下缓解性能崩塌。（p.5；Table 3，p.7；§4.3.2–3、Figure 4，p.8；Table 5，p.13）

## 3. 一项主要实验结果

Table 2 的 **Qwen3-1.7B** 结果如下，指标为 **Avg@12 准确率（%）**，不是 pass@12：

| 方法 | AIME24 | AIME25 | HMMT25 | 三项 Average |
| --- | ---: | ---: | ---: | ---: |
| Base（Instruct） | 51.5 | 36.7 | 23.1 | 37.1 |
| SFT | 48.4 | 36.3 | 22.7 | 35.8 |
| GRPO | 51.1 | 38.3 | 23.7 | 37.7 |
| OPSD | 57.2 | 43.9 | 29.2 | 43.4 |

**陈述 C2：在上述设置及作者的 checkpoint 选择口径下，OPSD 三项 Average 为 43.4%，GRPO 为 37.7%，差为 5.7 个百分点；相对 Base 提升 6.3 个百分点。**（Table 2，p.7）

解释这一结果所需的条件：

- 训练数据来自 OpenThoughts 数学子集，最多抽取 30K 问题—解答对；模型采用 LoRA，作者使用 A100/H100 GPU。（§4.1，p.6；附录 B，p.13）
- OPSD 每题一次生成，上限 1024 token，训练 100 步；GRPO 每题 8 次生成，每次上限 16,000 token，训练 500 步。双方有效 batch size 都为 32，但采样温度不同：OPSD 1.1，GRPO 1.2。（Table 6，p.13）
- Table 2 表注称 OPSD 每 20 步评估、在 100 步以内选最佳分数；GRPO 报告 500 步内峰值，SFT 使用与 OPSD 相同数量的样本。不能将其视为等训练步数、等总算力下的比较。（Table 2 表注，p.7）
- 评测每题采样 12 次、temperature=1.0、thinking mode 开启，最大新 token 为 **38,912**。训练用的 1024 上限不等于评测长度。（Table 8，p.14）

范围例外：不能说 OPSD 所有单项都胜过 GRPO；8B/HMMT25 为 OPSD 45.8、GRPO 46.7。生成 token 效率也不能直接等同于总训练耗时或 FLOPs 的节省。（Table 2，p.7；§4.3.5，p.8）

## 4. 局限和尚不明确之处

作者明确指出实验最大为 8B；框架未显式利用生成答案的正确性验证；问题超过模型理解能力时，即使给教师正确解答也可能得不到有效监督。（附录 A，p.13）

阅读者进一步观察：§4.1 声称固定初始 teacher 可稳定训练，但 §4.3 展示的消融没有直接量化“固定初始 teacher”相对“同步更新 teacher”的稳定性与性能取舍。Table 2 也未给出多训练随机种子的置信区间，因此小幅差异不能直接称为统计显著。上述是阅读后提出的证据缺口，不等于已经证明算法无效。（§4.1，p.6；§4.3，pp.7–9）

## 5. 关键位置索引

| 内容 | 原文位置 |
| --- | --- |
| 两种上下文、学生轨迹 | §3.2、Figure 2，p.4 |
| 散度目标、梯度和裁剪 | Algorithm 1、Eq.6–8，p.5 |
| 固定初始 teacher | §4.1 Implementation details，p.6 |
| 主要结果和 checkpoint 口径 | Table 2 及表注，p.7 |
| 训练与评测条件 | Tables 6、8，pp.13–14 |
| 作者局限 | 附录 A，p.13 |

## 6. 后续调研问题

**在 Qwen3-1.7B、相同数据和生成 token 预算下，将 OPSD 的 teacher 固定为初始策略，相比让 teacher 使用当前 student 参数但停止教师分支梯度，是否确实更稳定，并会不会限制最终推理准确率？**

这是 Agent 推荐的问题，尚未冒称学生已确认。它把“自蒸馏”收敛为一个可对照的 teacher 更新策略问题；依据与建议验证方法见 `followup_question.md`。

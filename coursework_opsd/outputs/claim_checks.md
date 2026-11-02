# 两条关键陈述核查

核查材料：[固定版本 PDF](../materials/2601.18734v3.pdf)，SHA-256 见 `materials/source.json`；所有页码为从 1 开始的 PDF 页码。本次由同一 Codex Agent 回到原文进行自检，并辅以页面图像与数值检查；没有声称由另一模型或学生独立复核。

## C1：教师的来源、上下文与更新方式

待核查陈述：阅读记录 §2 的 C1——“方法部分以同一模型在不同上下文下定义 teacher/student，但实际实验把 teacher 固定为初始策略，只更新 student，不能把实验实现描述为教师始终与学生同步更新。”

| 核查点 | 原文位置与证据 | 判断 |
| --- | --- | --- |
| 方法以不同上下文定义 teacher/student | p.4，§3.2 与 Figure 2；教师条件为问题、参考解答和学生前缀，学生无参考解答 | 与陈述一致。 |
| 轨迹来自学生，教师分布作为目标 | p.5，Algorithm 1 第 5–6 步、Eq.6–8 及其下方梯度说明 | 与阅读记录一致。 |
| 实验是否把 teacher 固定在初始策略 | p.6，右栏 §4.1 “Implementation details”，定位句：*We fix the teacher policy to be the initial policy, rather than the currently updating learning policy* | 明确支持固定初始 teacher。 |

是否需要纠正：**C1 不需要修改**，原阅读记录已经区分方法抽象与实验实现。核查进一步确认：单次目标计算中 stop-gradient，并不自动意味着 teacher 跨训练步骤的参数一定不变；跨步骤冻结来自 §4.1 的额外实现选择。这个区别应保留。

最终限定表述：OPSD 用同源模型在有、无参考解答的上下文下构造监督；本文实验使用初始策略作为固定 teacher，以当前 student 采样轨迹并更新 student。本文核查的是论文文字，未检查训练代码是否完全对应。

页面证据：[p.4](../evidence/page_04.png)、[p.5](../evidence/page_05.png)、[p.6](../evidence/page_06.png)。

## C2：1.7B 的主要结果及比较条件

待核查陈述：阅读记录 §3 的 C2——“在上述设置及作者的 checkpoint 选择口径下，OPSD 三项 Average 为 43.4%，GRPO 为 37.7%，差为 5.7 个百分点；相对 Base 提升 6.3 个百分点。”

| 核查点 | 原文位置与证据 | 判断 |
| --- | --- | --- |
| OPSD 1.7B 数值 | p.7，Table 2 下方 Qwen3-1.7B 区块，OPSD 行：57.2 / 43.9 / 29.2 / 43.4 | 与记录一致。 |
| GRPO 与 Base | 同一区块，GRPO Average=37.7，Base Average=37.1 | 与记录一致。 |
| 差值单位 | 43.4−37.7=5.7；43.4−37.1=6.3 | 是百分点，不能写成相对百分比提升 5.7%。 |
| 指标和 checkpoint | p.7，Table 2 表注：Avg@12；OPSD 在 100 步内评估选优，GRPO 取 500 步内峰值 | 不可误标 pass@12 或最后一步准确率。 |
| 训练条件 | p.13，Table 6：batch=32；OPSD 1 次、1024 上限、100 步；GRPO 8 次、16,000 上限、500 步，且温度不同 | 不是等采样预算或等计算量实验。 |
| 评测条件 | p.14，Table 8：12 samples、temperature=1.0、thinking enabled、max new tokens=38,912 | 不是“推断最多只用 1024 token”。 |

是否需要纠正：**C2 不需要修改**，数字、单位与条件均与原文一致。

额外发现的范围问题：§4.2 的概括性文字容易让人理解为每个单项都不低于 GRPO，但 Table 2 的 8B/HMMT25 中 OPSD=45.8、GRPO=46.7。阅读记录已使用带模型与指标的限定表述，并列出该反例；如果采用“全面超过 GRPO”的概括，就需要纠正为“表中各规模三项平均分更高，存在单项例外”。这属于原文结论范围核对，不冒称阅读初稿曾经写错。

最终限定表述：在 Table 2 所报的 1.7B、Avg@12、作者 checkpoint 筛选口径下，OPSD Average 43.4%，高于 GRPO 37.7% 共 5.7 个百分点；这不是等算力比较，不能外推为任意模型和单项都更优。

页面证据：[p.7](../evidence/page_07.png)、[p.13](../evidence/page_13.png)、[p.14](../evidence/page_14.png)。

## 核查结论

两条选定陈述均通过原文自检，无需纠正。值得保留的限定是：固定初始 teacher、具体模型和指标、checkpoint 筛选、训练/评测长度的区分、单项例外。自动化检查只验证下载哈希和表格数值等可机械复查内容，不能代替上述语义判断；学生人工复核尚未发生。

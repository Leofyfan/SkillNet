# 技能检索与选择记录

## 检索过程

使用项目本地开发模式安装的 `skillnet-ai==0.1.4`，实际调用 `SkillNetClient.search`：

| 轮次 | 查询 | 模式与上限 | 返回数 | SDK 调用耗时 |
| --- | --- | --- | --- | --- |
| 1 | `paper reading` | keyword，limit=3 | 3 | 0.307 秒 |
| 2 | `scientific critical thinking` | keyword，limit=3 | 3 | 0.228 秒 |

第一轮的首个技能经实际阅读后发现依赖 papertrail 工具，因此第二轮将检索意图收敛为对研究主张、方法和实验的批判性分析。两轮共返回六条索引记录；仅对三个候选尝试获取实际内容，其中两个成功，一个返回 404。未继续扩大候选或调用轮数。另有正式检索前的 HTTP/HTTPS 连通性诊断，见 `logs/connectivity_preflight.md`，不能把诊断漏算为零请求。

`search_round_1.json` 与 `search_round_2.json` 保存 SDK 返回对象的序列化结果及调用参数，并非完整 HTTP 原始响应。没有仅凭索引中的名称、星数或自动评分选择技能。

## 候选实际内容检查

| 候选 | 实际输入要求 | 实际输出形式 | 运行依赖与判断 |
| --- | --- | --- | --- |
| be-green/papertrail 的 `read-paper` | papertrail 库内论文的 BibTeX key 或检索词 | 元数据、摘要、指定章节内容 | 明确调用 `get_paper_metadata`、`search_library`、`read_paper`；当前只有本地 PDF，无此工具与文献库。不选。 |
| Tnemo65/template 的 `scientific-critical-thinking` | 可读取的论文、研究主张、方法和实验材料 | 主张与证据对照、方法审计、局限及已支持结论的结构化分析 | 实际文件只有 `SKILL.md`，只声明 Read/Write，无必需 Python 脚本、MCP 服务或外部 API。可配合本地 PDF 提取工具使用，选用。 |
| jmead/cursor-config 的同名技能 | 无法确认 | 无法确认 | 来源提交查询返回 HTTP 404，实际技能正文未取得。不能将索引简介当作已检查内容，不选。 |

两个成功获取的原始文件位于 `candidates/`，包括各自原始 frontmatter；全部获取状态、固定提交、URL 和哈希位于 `candidate_inspection.json`。其他三个搜索结果未深入检查，因此不对其适用性作最终判断。

## 选定技能与来源

- 名称：`scientific-critical-thinking`。
- 检索来源：[SkillNet](http://skillnet.openkg.cn/)，SDK 第二轮结果第 1 项。
- 下载来源：[Tnemo65/template 固定目录](https://github.com/Tnemo65/template/tree/6da282e77241b32e86822524955c0555bd1fc029/.cursor/skills/13-research-ideation/scientific-critical-thinking)。
- 固定提交：`6da282e77241b32e86822524955c0555bd1fc029`。
- 本地目录：`skills/scientific-critical-thinking/`。
- `SKILL.md` SHA-256：`662e14378fab7b8529ce130d96058d4b371d7333b7f77d96fb639103be481eb7`。
- 实际下载：`SkillNetClient().download(url=固定目录URL, target_dir=作业目录/skills)`；成功，耗时 1.972 秒，目录包含一个文件，详见 `download.json`。
- 文件 metadata 声明 `skill-author: K-Dense Inc.`、`license: MIT license`；这里区分文件自述作者与实际分发仓库，不把分发者说成原创作者，也未取得独立许可证文件。

选择理由：本作业不仅要总结论文，还要核查方法和实验陈述。该技能的主张分解、方法审计、结论范围与成本检查恰好支持这些环节，且不需要当前没有的工具。它不能解析 PDF，因此补充本地 PyMuPDF 提取和截图；这属于输入准备，不是技能原有能力。

## 加载和应用方式

SDK 下载后，在项目 `.agents/skills/scientific-critical-thinking` 建立相对符号链接，指向上述完整技能目录。当前会话不会因写入目录就自动取得其正文，所以 Codex 通过工具显式读取该入口的 `SKILL.md`，随后读取 `prompts/read_paper.md` 与论文材料并执行任务。没有声称重启客户端或自动加载已经发生。

技能使用的具体产物为 `critical_analysis.md`，其中主张分解、方法审计和成本边界分析直接映射到技能步骤。六项阅读记录见 `reading_notes.md`；核查见 `claim_checks.md`。该技能没有必须阅读的引用资源。

实际调整：保留原始技能不改，执行 prompt 将竞争性批评与“致命缺陷”式模板改为中性证据分析；按用户要求仅完成阅读与核查，不开展训练或代码复现。没有使用课程备用技能。

# 第三题提交材料：检索技能并辅助阅读论文

已完成真实 SDK 检索、候选内容检查、一个技能下载与加载、指定论文阅读、一个后续问题和两条关键陈述核查。所有环境与文件均在原 SkillNet 项目目录内；本目录也包含可独立安装的 SDK 源码快照。无需 SciAtlas、模型 API Key 或 GPU。

## 阅读入口与提交内容

| 内容 | 文件 |
| --- | --- |
| 中文项目报告 | [report.md](report.md) |
| SDK 调用代码 | [sdk_workflow.py](scripts/sdk_workflow.py) |
| 技能名称、来源、选择理由 | [skill_selection.md](outputs/skill_selection.md) |
| Agent 生成的六项阅读记录 | [reading_notes.md](outputs/reading_notes.md) |
| 两条陈述的原文核查 | [claim_checks.md](outputs/claim_checks.md) |
| 收敛后的后续问题 | [followup_question.md](outputs/followup_question.md) |
| 技能实际应用分析 | [critical_analysis.md](outputs/critical_analysis.md) |
| 原始选定技能 | [SKILL.md](skills/scientific-critical-thinking/SKILL.md) |
| 实际执行 prompt | [阅读](prompts/read_paper.md)、[核查](prompts/check_claims.md) |
| 运行、错误和调整记录 | [usage.md](logs/usage.md) |

`outputs/search_round_*.json` 是 SDK 返回对象序列化记录；`candidate_inspection.json` 保存实际来源访问结果；`download.json` 保存成功下载及全部文件哈希。`materials/` 保存论文与分页文本；`evidence/` 保存关键页面图像。

## 环境与启动

本次实际环境：Linux x86_64、Python 3.13.5、SkillNet SDK 0.1.4、PyMuPDF 1.26.7。精确环境见 `logs/environment.json`，依赖版本见 `requirements.lock.txt`。

已有环境可直接使用：在原项目根目录运行 `coursework_opsd/.venv/bin/python coursework_opsd/scripts/verify_submission.py`。

提交包解压后也可独立启动，进入解压得到的 `coursework_opsd` 目录：

```bash
bash scripts/bootstrap.sh
.venv/bin/python -m pip check
.venv/bin/python scripts/verify_submission.py
```

bootstrap 使用当前系统的 `python3`，要求 Python 3.10+；本锁文件实际在 Python 3.13/Linux 上验证，其他平台需对应版本的可用 wheel 或编译环境。安装需要访问 Python 包索引；审阅已保存的 Markdown、JSON、PDF 和图像不需要联网。

SDK 从 `vendor/skillnet-ai` 开发模式安装。初次普通安装因为缺少预构建网页资源而失败，开发模式避开不需要的 UI 构建，未修改 SDK 代码。实际完成过该环境安装和 `pip check`；没有另建第二个全新环境重复安装全部依赖。

运行脚本会将临时目录和 SDK 配置路径固定在本目录 `.runtime/`，不读取私人 SkillNet 配置，不使用模型凭据。bootstrap 也将 pip 缓存置于本目录。虚拟环境和缓存不放入提交 ZIP。

## 复查 SDK 流程

以下命令在本目录执行。已保存成功的步骤会返回缓存，不重复请求；要从头重新检索，应先复制一份作业目录、删除该副本内相应结果及下载目录，避免覆盖本次证据。

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/sdk_workflow.py search --round 1 --query 'paper reading'
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/inspect_candidates.py --round 1 --indices 1
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/sdk_workflow.py search --round 2 --query 'scientific critical thinking'
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/inspect_candidates.py --round 2 --indices 1 2
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/sdk_workflow.py download --url 'https://github.com/Tnemo65/template/tree/6da282e77241b32e86822524955c0555bd1fc029/.cursor/skills/13-research-ideation/scientific-critical-thinking'
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/prepare_paper.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/verify_submission.py
```

公开检索端点采用仓库默认 HTTP 地址；HTTPS 诊断有证书主机名错误，没有关闭证书校验。检索无需凭据。GitHub 下载与 arXiv 使用 HTTPS。候选访问失败保留为错误，而非空结果或成功检查。

## 技能加载与 Agent 阅读的复查

原项目中已建立 `.agents/skills/scientific-critical-thinking` 到本目录技能文件夹的相对链接。当前 Codex 会话显式读取入口 `SKILL.md`，再按保存的 prompt 阅读材料。未依赖客户端重启或声称新目录自动在当前会话生效。

在解压包中重做阅读，只需让 Coding Agent 先实际读取 `skills/scientific-critical-thinking/SKILL.md`，再执行 `prompts/read_paper.md` 与 `prompts/check_claims.md`；可按所用客户端文档将该完整文件夹放到项目技能目录。SDK 脚本负责检索和下载，不会在普通 Python 进程中自动调用本聊天模型。Agent 阅读文本可能随模型变化，因此保存了本次实际产物。

## 检查与打包

`verify_submission.py` 离线检查论文/技能哈希、技能结构、检索和候选预算、PDF 表格数字与百分点差、必要产物、链接及 Python 语法；这些检查不等于论文训练复现或独立人工审核。

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/package_submission.py
```

该命令在目录内部生成 `submission.zip` 与 SHA-256，排除 `.venv`、`.runtime`、字节码和自身压缩包，并包含 SDK 源码快照。生成前要求材料检查已通过，并校验全部清单哈希与 ZIP CRC。

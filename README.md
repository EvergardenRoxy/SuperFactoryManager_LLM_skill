# SuperFactoryManager LLM Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![AI Assisted](https://img.shields.io/badge/AI-Claude%20Opus%205.5%20%2B%20Claude%20Code-D97757?style=for-the-badge&logo=anthropic&logoColor=white)](#ai-制作声明)

> 让 Claude（及其他 LLM）正确地编写、审查和调试 Minecraft **Super Factory Manager（SFM）** 程序的 Agent Skill。

[Super Factory Manager](https://github.com/TeamDman/SuperFactoryManager) 是一个用自定义语言 **SFML** 编程的 Minecraft 物流模组。SFML 只有几十个关键字，但语义与常见编程语言差别很大，而且随版本变化频繁——LLM 凭记忆写出的 SFML 经常编译失败，或者能编译但行为不对（例如原料绕过机器直接进产物箱）。

本仓库提供一份**以官方语法文件为准**的 Skill，把 SFML 的语法、执行模型、常见陷阱、效率经验和排错流程整理成 AI 可直接遵循的指南。

[English summary](#english)

<a id="ai-制作声明"></a>

> [!IMPORTANT]
> **AI 制作声明：SuperFactoryManager LLM Skill 采用生成式 AI 参与内容编写、语法校验与文档撰写。** AI 生成或修改的内容由项目维护者审阅、验证并承担最终维护责任。

---

## 能做什么

| 场景 | 示例提问 |
|---|---|
| 编写程序 | "用 SFM 给 64 台熔炉自动补矿石和燃料，产物收进箱子" |
| 审查程序 | "帮我看看这段 SFML 有没有问题" |
| 排查故障 | "管理器不工作 / 机器卡死 / 只有一半机器在干活" |
| 流体 / 能量 / 化学品 | "把 Mekanism 电解分离器的三种气体分别导出" |
| 堆量工厂设计 | "1024 台装配机怎么分配输出口才不会卡" |

每次回答都会给出：**整体思路 + 标签清单（标签 → 方块 → 面）+ 程序 + 搭建步骤 + 风险提示**，并在交付前对照内置自检清单。

## Skill 内容一览

Skill 采用**渐进式加载**：触发时只加载精简的核心文件（约 390 行），细节文件由模型在需要时按索引读取，避免每次占用大量上下文。

**核心文件** [`SKILL.md`](skills/minecraft-sfm-factory/SKILL.md)（每次触发时加载）

| 章节 | 内容 |
|---|---|
| 0. 铁律 | 给 AI 的 13 条硬约束（不发明语法、input/output 语义、side、forget、引号、按需查参考、简单优先……） |
| 1. 参考文件索引 | "遇到什么情况读哪个文件"的路由表 |
| 2. 协助流程 | 需要问清的信息、设计步骤、回答格式模板、**简化原则与必须提示性能风险的情况** |
| 3. 执行模型 | 管理器 / 磁盘 / 标签 / 线缆网络，输入列表的登记与消费 |
| 4. 语言速查 | 词法、触发器、input/output 子句顺序、资源 ID、retain/each、side/slots、forget/if、红石 |
| 5. 执行时序 | 最常见错误"原料绕过机器"及三种解法 |
| 6. 自检清单 | 交付前逐条核对 |

**参考文件** [`references/`](skills/minecraft-sfm-factory/references)（按需读取）

| 文件 | 内容 |
|---|---|
| `language-reference.md` | 完整语言参考：正则表、with/without、except、round robin、empty slots、if 集合限定、红石细节 |
| `templates.md` | 14 个可直接使用的程序（熔炉阵列、AE2 压印器、有机灌注器、聚变反应堆……） |
| `troubleshooting.md` | 40 条常见错误对照、编译错误与磁盘警告速查、排错流程 |
| `efficiency.md` | 输出口数量规则、机器选型实测数据、降低卡顿的手段 |
| `advanced-patterns.md` | 进阶模式：计数寄存器、状态机、多段加工链、AE 样板供应器按槽位分发、防满仓卡死、红石时钟提速、自循环增产、蓄能放电、事件驱动、用容器 + 比较器控制红石电路 |
| `items-and-tools.md` | 物品与方块、标签枪与网络工具操作、编辑器快捷键 |
| `config-and-versions.md` | 服务器配置与命令、版本差异、资料来源与已知出入 |

## 安装

本 Skill 遵循开放的 [Agent Skills](https://agentskills.io) 格式：一个包含 `SKILL.md` 的文件夹（本仓库为 `skills/minecraft-sfm-factory/`，**连同 `references/` 一起复制**）。支持该格式的工具只需把文件夹放进对应目录即可自动加载。

**最简单的方式**：从 [Releases](https://github.com/EvergardenRoxy/SuperFactoryManager_LLM_skill/releases/latest) 下载打包好的 **`SFM_prompt_pack.zip`**，可直接上传到 Claude.ai、Cherry Studio 等工具，或解压到下表目录下的 `minecraft-sfm-factory/` 文件夹中。

### 速查表

| 工具 | 项目级目录 | 用户级目录（所有项目可用） | 一键安装 |
|---|---|---|---|
| [Claude Code](INSTALL.md#claude-code) | `.claude/skills/` | `~/.claude/skills/` | `/plugin` 插件市场 |
| [Claude.ai / 桌面端](INSTALL.md#claudeai--claude-桌面端) | — | 设置中上传 zip | — |
| [OpenAI Codex](INSTALL.md#openai-codexcli--ide-插件--codex-app) | `.agents/skills/` | `~/.agents/skills/` | `$skill-installer` |
| [Cursor](INSTALL.md#cursor) | `.cursor/skills/` 或 `.agents/skills/` | `~/.cursor/skills/` 或 `~/.agents/skills/` | — |
| [VS Code + GitHub Copilot](INSTALL.md#vs-code--github-copilot) | `.github/skills/` 或 `.agents/skills/` | `~/.copilot/skills/` 或 `~/.agents/skills/` | — |
| [Gemini CLI](INSTALL.md#gemini-cli) | `.gemini/skills/` 或 `.agents/skills/` | `~/.gemini/skills/` 或 `~/.agents/skills/` | `gemini skills install` |
| [Cherry Studio](INSTALL.md#cherry-studio) | — | 设置 → 技能 | 从文件夹 / ZIP / GitHub 安装 |
| [ChatGPT、DeepSeek 等网页对话](INSTALL.md#chatgptdeepseek-等不支持-skills-的对话工具) | — | 上传文件或项目知识库 | — |

> 💡 **`.agents/skills/` 是通用目录**：Codex、Cursor、VS Code Copilot、Gemini CLI 都会读取它。同时使用多个工具时，放在 `~/.agents/skills/` 一处即可。

各工具的详细安装步骤见 **[INSTALL.md](INSTALL.md)**。

## 使用

安装后无需额外操作。当你提到 SFM、Super Factory Manager、工厂管理器、标签枪、`every ... do`、`input`/`output` 等内容时，Skill 会自动触发。

建议在提问时附上：

- **SFM 版本**（模组列表中查看）与 Minecraft 版本——语法随版本变化
- 涉及的机器 / 模组，以及要搬运的资源类型
- 现有程序与管理器界面中的报错 / 警告原文

## 准确性说明

- Skill 中全部 `sfml` 代码块均已用 [`scripts/validate_skill.py`](scripts/validate_skill.py) 依据官方 ANTLR 语法文件 [`SFML.g4`](https://github.com/TeamDman/SuperFactoryManager/blob/HEAD/platform/minecraft/src/main/antlr/sfml/SFML.g4) 生成的解析器逐一校验通过。
- 语法校验只能保证"能编译"，不能保证在游戏中的行为。涉及机器朝向与侧面配置、槽位编号、版本相关特性时，Skill 会引导用户在游戏内实测。
- SFM 在大批量物流时自身开销较大。Skill 会优先给出最简单的写法；程序用到状态机、高频红石时钟、大阵列 `each` 等复杂结构时，会附带性能提示。
- 与 DeepWiki、旧文档等资料的已知出入见 `references/config-and-versions.md` 的"资料来源与已知出入"。

## 目录结构

```text
.
├── .claude-plugin/
│   └── marketplace.json          # Claude Code 插件市场清单
├── skills/
│   └── minecraft-sfm-factory/
│       ├── SKILL.md              # 核心：规则、执行模型、语言速查、自检清单
│       └── references/           # 按需读取的细节文件
│           ├── language-reference.md
│           ├── templates.md
│           ├── troubleshooting.md
│           ├── efficiency.md
│           ├── advanced-patterns.md
│           ├── items-and-tools.md
│           └── config-and-versions.md
├── scripts/
│   └── validate_skill.py         # 语法与结构校验
├── INSTALL.md                    # 各工具安装详解
├── LICENSE
└── README.md
```

## 致谢

- [TeamDman/SuperFactoryManager](https://github.com/TeamDman/SuperFactoryManager)——模组本体、语法文件与官方示例
- 社区玩家分享的效率测试数据与工厂程序

## 许可证

[MIT](LICENSE) © 2026 EvergardenRoxy

本仓库仅包含说明文档，不包含 Super Factory Manager 模组本身的代码；SFM 模组遵循其自身的许可证。

---

<a id="english"></a>

## English

An [Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) that teaches Claude to write, review and debug programs for the Minecraft mod **Super Factory Manager** (SFML language). The skill content is written in Chinese and covers the full language reference, execution model, common pitfalls, a template library, a pre-delivery checklist and troubleshooting guides. All `sfml` code blocks are validated against the official ANTLR grammar.

Install with Claude Code:

```text
/plugin marketplace add EvergardenRoxy/SuperFactoryManager_LLM_skill
/plugin install minecraft-sfm-factory@sfm-llm-skills
```

The skill follows the open [Agent Skills](https://agentskills.io) format, so it also works in other tools — copy the whole `skills/minecraft-sfm-factory/` folder (including `references/`) into:

| Tool | User-level directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| OpenAI Codex / Cursor / VS Code Copilot / Gemini CLI | `~/.agents/skills/` (shared by all four) |
| Cherry Studio | Settings → Skills → install from folder or ZIP |

See [INSTALL.md](INSTALL.md) for per-tool details (in Chinese).

Licensed under [MIT](LICENSE). Content was produced with generative-AI assistance and reviewed by the maintainer.

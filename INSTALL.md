# 各工具安装详解

> 返回 [README](README.md#安装)

## 下载安装包（推荐）

从 [Releases 页面](https://github.com/EvergardenRoxy/SuperFactoryManager_LLM_skill/releases/latest) 下载 **`SFM_prompt_pack.zip`**（[v1.0.0 直链](https://github.com/EvergardenRoxy/SuperFactoryManager_LLM_skill/releases/download/v1.0.0/SFM_prompt_pack.zip)）。这是打包好的完整 Skill，已在多个平台测试可直接安装，内容如下：

```text
SFM_prompt_pack.zip
├── SKILL.md
└── references/
    ├── config-and-versions.md
    ├── efficiency.md
    ├── items-and-tools.md
    ├── language-reference.md
    ├── templates.md
    └── troubleshooting.md
```

- **支持上传 ZIP 的工具**（Claude.ai、Cherry Studio 等）：直接上传这个压缩包，无需解压。
- **需要放进 skills 目录的工具**（Claude Code、Codex、Cursor、Copilot、Gemini CLI）：压缩包内的文件位于根目录，解压时请**解压到名为 `minecraft-sfm-factory` 的文件夹中**，例如：

  ```bash
  unzip SFM_prompt_pack.zip -d ~/.claude/skills/minecraft-sfm-factory
  ```

  Windows 可右键 **全部解压缩**，把目标文件夹命名为 `minecraft-sfm-factory`，再移动到对应目录。确认结构为 `<skills 目录>/minecraft-sfm-factory/SKILL.md`。

<details>
<summary>也可以从源码安装</summary>

```bash
git clone https://github.com/EvergardenRoxy/SuperFactoryManager_LLM_skill.git
cd SuperFactoryManager_LLM_skill
# Skill 文件夹位于 skills/minecraft-sfm-factory，复制到下文对应目录即可
```

</details>

以下各节默认你已下载 `SFM_prompt_pack.zip` 并位于其所在目录。

## Claude Code

```bash
unzip SFM_prompt_pack.zip -d ~/.claude/skills/minecraft-sfm-factory            # 用户级
unzip SFM_prompt_pack.zip -d <你的项目>/.claude/skills/minecraft-sfm-factory    # 项目级
```

也可以通过插件市场安装：

```text
/plugin marketplace add EvergardenRoxy/SuperFactoryManager_LLM_skill
/plugin install minecraft-sfm-factory@sfm-llm-skills
```

## Claude.ai / Claude 桌面端

在 **Settings → Capabilities → Skills** 中直接上传 `SFM_prompt_pack.zip`。

## OpenAI Codex（CLI / IDE 插件 / Codex App）

```bash
unzip SFM_prompt_pack.zip -d ~/.agents/skills/minecraft-sfm-factory            # 用户级
unzip SFM_prompt_pack.zip -d <你的项目>/.agents/skills/minecraft-sfm-factory    # 项目级
```

也可以在 Codex 对话中让内置安装器从仓库下载：

```text
$skill-installer 从 https://github.com/EvergardenRoxy/SuperFactoryManager_LLM_skill 安装 skills/minecraft-sfm-factory
```

Codex 通常会自动检测新技能；如果没有出现，重启 Codex。

## Cursor

```bash
unzip SFM_prompt_pack.zip -d ~/.cursor/skills/minecraft-sfm-factory            # 用户级
unzip SFM_prompt_pack.zip -d <你的项目>/.cursor/skills/minecraft-sfm-factory    # 项目级
```

Cursor 也会读取 `.claude/skills/`、`.agents/skills/`。在 Agent 对话框输入 `/` 可看到并手动调用该技能。

## VS Code + GitHub Copilot

```bash
unzip SFM_prompt_pack.zip -d ~/.copilot/skills/minecraft-sfm-factory           # 用户级
unzip SFM_prompt_pack.zip -d <你的项目>/.github/skills/minecraft-sfm-factory    # 项目级
```

在 Copilot Chat 输入 `/skills` 打开 **Configure Skills**，确认列表中出现 `minecraft-sfm-factory`。

## Gemini CLI

```bash
unzip SFM_prompt_pack.zip -d ~/.gemini/skills/minecraft-sfm-factory            # 用户级
unzip SFM_prompt_pack.zip -d <你的项目>/.gemini/skills/minecraft-sfm-factory    # 项目级
gemini skills list                                                             # 确认已安装
```

也可以直接从仓库安装：

```bash
gemini skills install https://github.com/EvergardenRoxy/SuperFactoryManager_LLM_skill.git \
  --path skills/minecraft-sfm-factory          # 默认安装到用户级；加 --scope workspace 装到项目
```

## Cherry Studio

1. 打开 **设置 → 技能**，选择 **从本地 ZIP 安装**，选中 `SFM_prompt_pack.zip`，确认全局开关已打开。
2. 进入 **工作**，打开要使用的智能体（Agent）菜单 → **编辑 → 技能**，为该智能体启用；从下一条消息开始生效。

> ⚠️ Cherry Studio 也支持在 **GitHub** 来源中粘贴 `SKILL.md` 链接安装，但这种方式可能只拉取 `SKILL.md` 本身。本 Skill 依赖 `references/` 目录，**推荐用 ZIP 方式安装**。

## ChatGPT、DeepSeek 等不支持 Skills 的对话工具

1. 解压 `SFM_prompt_pack.zip`，在项目 / 自定义 GPT / 知识库中上传 `SKILL.md` 和 `references/` 下的全部文件；若只能上传少量文件，至少上传 `SKILL.md`、`references/language-reference.md` 和 `references/templates.md`。
2. 在系统提示词或项目指令中写入：

   ```text
   回答 Minecraft Super Factory Manager（SFM / SFML）相关问题时，严格遵循附件 SKILL.md 的规则；
   SKILL.md 第 1 节索引指向的细节，到同名附件中查找。不要凭记忆编写 SFML 语法。
   ```

3. 不支持附件的工具，可直接把 `SKILL.md` 正文（去掉开头的 YAML front matter）粘贴为系统提示词。

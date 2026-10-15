# 各工具安装详解

> 返回 [README](README.md#安装)

先获取文件（以下各节默认已执行）：

```bash
git clone https://github.com/EvergardenRoxy/SuperFactoryManager_LLM_skill.git
cd SuperFactoryManager_LLM_skill
```

也可以在 GitHub 页面点击 **Code → Download ZIP** 后解压。

## Claude Code

插件市场（推荐）：

```text
/plugin marketplace add EvergardenRoxy/SuperFactoryManager_LLM_skill
/plugin install minecraft-sfm-factory@sfm-llm-skills
```

或手动复制：

```bash
cp -r skills/minecraft-sfm-factory ~/.claude/skills/             # 用户级
cp -r skills/minecraft-sfm-factory <你的项目>/.claude/skills/     # 项目级
```

## Claude.ai / Claude 桌面端

将 `skills/minecraft-sfm-factory` 文件夹压缩为 zip，在 **Settings → Capabilities → Skills** 中上传。

## OpenAI Codex（CLI / IDE 插件 / Codex App）

```bash
mkdir -p ~/.agents/skills
cp -r skills/minecraft-sfm-factory ~/.agents/skills/             # 用户级
cp -r skills/minecraft-sfm-factory <你的项目>/.agents/skills/     # 项目级
```

也可以在 Codex 对话中让内置安装器下载：

```text
$skill-installer 从 https://github.com/EvergardenRoxy/SuperFactoryManager_LLM_skill 安装 skills/minecraft-sfm-factory
```

Codex 通常会自动检测新技能；如果没有出现，重启 Codex。

## Cursor

```bash
cp -r skills/minecraft-sfm-factory ~/.cursor/skills/             # 用户级
cp -r skills/minecraft-sfm-factory <你的项目>/.cursor/skills/     # 项目级
```

Cursor 也会读取 `.claude/skills/`、`.agents/skills/`。在 Agent 对话框输入 `/` 可看到并手动调用该技能。

## VS Code + GitHub Copilot

```bash
cp -r skills/minecraft-sfm-factory ~/.copilot/skills/            # 用户级
cp -r skills/minecraft-sfm-factory <你的项目>/.github/skills/    # 项目级
```

在 Copilot Chat 输入 `/skills` 打开 **Configure Skills**，确认列表中出现 `minecraft-sfm-factory`。

## Gemini CLI

```bash
gemini skills install https://github.com/EvergardenRoxy/SuperFactoryManager_LLM_skill.git \
  --path skills/minecraft-sfm-factory          # 默认安装到用户级；加 --scope workspace 装到项目
gemini skills list                             # 确认已安装
```

## Cherry Studio

1. 将 `skills/minecraft-sfm-factory` 文件夹压缩为 ZIP（或直接使用解压后的文件夹）。
2. 打开 **设置 → 技能**，选择 **从本地 ZIP 安装** 或 **从文件夹安装**，确认全局开关已打开。
3. 进入 **工作**，打开要使用的智能体（Agent）菜单 → **编辑 → 技能**，为该智能体启用；从下一条消息开始生效。

> ⚠️ Cherry Studio 也支持在 **GitHub** 来源中粘贴 `SKILL.md` 链接安装，但这种方式可能只拉取 `SKILL.md` 本身。本 Skill 依赖 `references/` 目录，**推荐用 ZIP 或文件夹方式安装**。

## ChatGPT、DeepSeek 等不支持 Skills 的对话工具

1. 在项目 / 自定义 GPT / 知识库中上传 `SKILL.md` 和 `references/` 下的全部文件；若只能上传少量文件，至少上传 `SKILL.md`、`references/language-reference.md` 和 `references/templates.md`。
2. 在系统提示词或项目指令中写入：

   ```text
   回答 Minecraft Super Factory Manager（SFM / SFML）相关问题时，严格遵循附件 SKILL.md 的规则；
   SKILL.md 第 1 节索引指向的细节，到同名附件中查找。不要凭记忆编写 SFML 语法。
   ```

3. 不支持附件的工具，可直接把 `SKILL.md` 正文（去掉开头的 YAML front matter）粘贴为系统提示词。

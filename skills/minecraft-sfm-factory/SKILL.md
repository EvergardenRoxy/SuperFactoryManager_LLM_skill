---
name: minecraft-sfm-factory
description: 协助用户在 Minecraft 中使用 Super Factory Manager（SFM，工厂管理器，程序语言 SFML）搭建自动化工厂：编写、审查、调试 SFM 程序，设计标签与机器阵列的输入输出布局，排查"不工作/卡死/效率低"。当用户提到 SFM、Super Factory Manager、工厂管理器、工厂线缆、标签枪、磁盘程序、every ... do、input/output/forget/if 语句，或要求自动化物品、流体、能量、通用机械化学品传输时使用。
---

# Minecraft SFM（Super Factory Manager）工厂协助指南

本文档是编写 SFM 程序时的**唯一权威参考**。SFM 是一个小众模组，它的语言 SFML 只有几十个关键字，但细节很多、与常见编程语言差别很大。**你的记忆里关于 SFML 的内容很可能是错的或过时的，必须以本文为准。**

---

## 0. 给 AI 的铁律（先读这一节）

1. **只使用本文出现过的语法。** SFML 没有变量赋值、没有循环、没有函数、没有 `;`、没有 `{}`、没有 `==`、没有 `!=`、没有 `while/for`、没有 `elif/elseif`。想不到写法时，宁可告诉用户"SFML 做不到"，也不要发明语法。
2. **SFML 不是"搬运命令"，而是"登记输入 + 消费输出"。** `input` 只登记来源，什么都不会移动；`output` 才会真正从已登记的来源取资源并放入目标。只有 `input` 没有 `output` = 什么也不发生。
3. **每种资源类型要有各自的 input 和 output。** `input from a` 默认只登记**物品**。要搬流体/能量/化学品，必须写 `input fluid:: ...` / `input fe:: ...` / `input gas:: ...`，并且 `output` 也要写同样的类型。
4. **除物品外（流体、能量、化学品、红石），必须写 `side`**（如 `top side`）。物品通常也建议写，尤其是机器。
5. **输入登记不会因为 output 而消失。** 同一触发器里先"放进机器"再"取出产物"，中间必须 `forget` 或拆成两个触发器，否则原料会绕过机器直接进入产物箱（见第 5 节）。
6. **标签名含中文、数字开头、连字符、空格、或与关键字相同，必须加双引号。** 如 `"有机灌注器"`、`"storage a"`、`"east"`。
7. **每个 `every ... do` 要有 `end`；每个 `if` 链（含 else if / else）只有一个 `end`。**
8. **触发器间隔不能小于配置最小值（默认 20 刻 = 1 秒）。** 只传能量的触发器可以到 1 刻。`every 5 ticks` 搬物品会编译失败。
9. **给出的程序必须附带"标签清单"**（每个标签对应哪些方块、哪个面），并且**交付前逐条过第 8 节的自检清单**。
10. **版本不确定时先问版本。** 不要假定用户使用最新版语法（尤其是 `without`、`or`、`empty slots in`、相对方向、`redstone::`）。
11. 不确定某行为时，让用户用游戏内工具验证（网络工具、Ctrl+I、日志界面），不要编造"应该可以"。

---

## 1. 协助流程

### 1.1 先问清的信息（缺失才问，已知就不要再问）

| 要确认的信息 | 为什么重要 |
|---|---|
| SFM 版本（模组列表里看）、Minecraft 版本、加载器 | 语法随版本变化（见第 13 节）；化学品类型名随 MC 版本变化 |
| 涉及哪些机器/模组（Mekanism、AE2、热力、神秘农业、现代工业化…） | 各机器开放的输入输出面、槽位、是否有侧面配置不同 |
| 要搬运的资源：物品/流体/能量/化学品/红石 | 决定 `resourceid` 和是否必须写 `side` |
| 机器数量、每种机器的产物种类数 | 决定输出口数量、`each`/`retain` 写法（第 6 节） |
| 数据流方向：从哪里来、到哪里去、是否需要中转 | 决定标签划分与是否要 `forget` |
| 用户现有的程序/报错/警告文字 | 排错必需 |

### 1.2 设计步骤

1. 画出数据流：`来源 → (机器输入面) → 机器 → (机器输出面) → 目标`。
2. 给每个**角色**起一个标签名（来源箱、各类机器、产物箱、能源、水源……）。同一标签可含多个方块。
3. 为每个标签确认使用哪个面（`top/bottom/north/...`）。
4. 逐触发器写程序：能量单独一个 `every tick`；物品/流体通常 `every 20 ticks`；"放入"与"取出"分开。
5. 过第 8 节自检清单。
6. 向用户交付：**程序 + 标签清单 + 搭建步骤 + 潜在风险**（格式见 1.3）。

### 1.3 回答格式模板

````text
【整体思路】一两句话说明数据流。

【标签清单】
| 标签 | 方块 | 使用的面 |
| a    | 输入箱子 | 无需面 / top |
...

【程序】
```sfml
...
```

【怎么搭】
1. 把磁盘放入管理器，用工厂线缆连接所有方块（管理器本身也可当线缆）。
2. 把上面的程序粘贴进磁盘编辑界面（Ctrl+E 打开，Shift+Enter 完成）。
3. 用标签枪：先在标签枪里建好标签名，右击对应方块，最后对管理器 Shift+右击"拉取"标签，或右击"推送"。
   推荐做法：先写好程序，再 Shift+右击管理器拉取标签名，免得手输。
4. 看磁盘上的警告（管理器界面有警告按钮）。

【风险提示】时序/输出口数量/面/最小间隔……
````

---

## 2. 核心概念（心智模型）

- **管理器（Manager）**：执行程序的方块。放入**磁盘（Disk）**后运行磁盘上的程序。
- **磁盘**：存两样东西——**程序文本**和**标签→方块位置**的映射。
- **标签（Label）**：程序里用名字引用方块，名字与世界中的方块位置由**标签枪**绑定。一个标签可有多个方块，一个方块可有多个标签。标签最长 256 字符。
- **线缆网络**：管理器、线缆、被操作的方块必须通过**工厂线缆**连成一个网络（管理器本身也算线缆）。没连上的标签在程序里"存在"，但搬不了东西。
- **程序结构**：`[name "..."]` + 若干**触发器**。触发器 = 定时器或红石脉冲，内含按顺序执行的**语句**。
- **执行模型**（最重要）：

```text
每当触发器到点：
  按从上到下的顺序执行语句
    input  → 把"来源方块 + 资源过滤 + 数量限制"登记到本触发器的【输入列表】
    output → 从【输入列表】里能提供的资源中取出，放进目标方块（受数量限制、目标容量限制）
    forget → 从【输入列表】里删掉条目（全部或指定标签）
    if     → 条件成立才执行对应分支里的语句
触发器结束 → 【输入列表】自动清空（不会影响别的触发器）
```

- **没有物品缓冲区**：`input` 本身不拿走任何东西。资源是在 `output` 时直接从来源方块转移到目标方块。
- 多个 `output` 依次执行：先满足前一个目标（受它的限制和容量），剩下的再尝试后一个目标。
- `input` 上的数量限制是**共享预算**：被多个 `output` 依次消耗。例：
  `input 10 from a,b` → `output 1 to z` → `forget b` → `output to z`，第二个 output 最多再搬 9 个（来自 a）。
- 触发器**依次**处理机器，而不是并行；见第 6 节。

---

## 3. 物品与方块

| 物品 | 作用 |
|---|---|
| 工厂管理器（Factory Manager） | 工厂核心，放入磁盘后运行程序。同一线缆网络可有多个管理器；管理器本身也可充当线缆；管理器可以操作自己（4.27.0+，可用来换磁盘） |
| 隧道式工厂管理器（Tunnelled Factory Manager，4.27.0+） | 具有管理器全部功能，并把相邻面的输入输出"隧穿"到相对面，可堆叠（如 漏斗→管理器→箱子）。可直线传输物品、流体、能量、通用机械化学品，**不能传红石信号**；也可作管道交叉点避免飞线 |
| 工厂线缆（Inventory Cable） | 连接管理器和操作对象。操作方向与连接方向无关，由程序决定 |
| 精致工厂线缆（Fancy Inventory Cable，4.20.0+） | 非完整方块模型，效果一致且可互连；4.34.0+ 可含水；可套"伪装"（facade） |
| 隧道线缆 / 坚固线缆（Tunnelled / Tough Cable，4.29.0+） | 隧道线缆用于穿过方块；坚固线缆抗爆 |
| 磁盘（Factory Manager Program Disk） | 存程序和标签；放进管理器运行，也可手持右击编辑 |
| 标签枪（Label Gun） | 给方块添加标签 |
| 网络工具（Network Tool） | 诊断与伪装 |
| 蓄水槽（Water Tank） | 至少两个面接触水源时是无限水源 |
| 印刷机（Printing Press） | 复制磁盘等（需要时让用户查 JEI） |

**基本搭建顺序**：磁盘放入管理器 → 线缆连接各方块 → 标签枪标记方块并推送到磁盘 → 编写/粘贴程序 → 检查警告。

### 3.1 标签枪操作

| 操作 | 作用 |
|---|---|
| 右击空气 | 打开 GUI（搜索/新建标签；Prune 清理无用标签；Cycle label view 切换渲染） |
| 右击方块 | 为方块添加/移除当前标签 |
| Shift + 右击方块 | 清除该方块的所有标签 |
| Ctrl + 右击方块 | 连续模式：为所有连续的相同方块添加/移除标签（以每个有效方块为中心 3×3×3 范围内、连接到任意线缆网络的相同方块判定有效；没挨着线缆的会被跳过并在聊天提示） |
| Alt + 右击方块（4.20.0+） | 选取（pick）该方块上的一个标签 |
| Shift + 滚轮 | 上一个/下一个标签（按字母顺序循环；4.24.0+ 可改键位） |
| 右击管理器 | **推送**：标签枪 → 磁盘 |
| Shift + 右击管理器 | **拉取**：标签枪 ← 磁盘 |
| Alt（4.20.0+） | 切换标签渲染：全部 / 此标签 / 此方块 |

> 推荐流程：**先写程序，再 Shift+右击管理器拉取标签**，然后对着世界里的方块逐个贴标签，最后右击管理器推送。

### 3.2 网络工具

手持时穿透显示管理器、线缆、标签。

- **主手右击方块**：聊天栏显示该方块的 BlockState、所属线缆网络、可用能力（物品/流体/能量…）及它们开放的面（点击的那一面为输出方向）。
- **4.20.0+ 线缆伪装（副手拿网络工具，主手拿方块，右击线缆）**：

| 操作 | 范围 |
|---|---|
| 右击 | 单个方块 |
| Ctrl + 右击 | 连续的相同方块 |
| Alt + 右击 | 线缆网络内所有相同方块 |
| Ctrl + Alt + 右击 | 线缆网络内所有方块 |

- 4.29.0+ 网络工具可"调谐"到某个方块位置。

### 3.3 蓄水槽输出量

- ＜4.20.0：不论是否有无限水源，每个提供 1000 mB/t。
- ≥4.20.0：相连水槽需具有无限水源，输出 `1000 × 2^(有效水槽数 − 1)` mB/t。
- 命令 `/sfm bust_water_network_cache` 可清水槽网络缓存。

### 3.4 程序编辑界面快捷键

| 快捷键 | 作用 |
|---|---|
| Ctrl + E | 在管理器界面打开编程界面 |
| Ctrl + Shift + E | 在管理器界面查看示例程序（模板） |
| Ctrl + / | 用 `--` 注释/取消注释当前行 |
| Tab / Shift + Tab | 缩进/取消缩进 |
| `\`（4.21.0+，4.32.0+ 可改键位） | 接受代码补全 |
| Shift + Enter | 完成编辑（保存并关闭） |
| Ctrl + Back / Ctrl + Del | 删除到单词边界 |
| Home / End、Ctrl + Home / Ctrl + End | 行首行尾、全文首尾 |
| Ctrl + Space | 在 input、output、resourceid、label、if、boolexpr 处查看可用项（可获得容器里已有的 resourceid 与标签） |
| Ctrl + I（容器界面中） | 开关容器检查器：显示槽位编号，可导出检查器（**显示的是 GUI 槽位，不一定等于自动化槽位**） |
| 左下角 `#` / 编辑器配置按钮（4.21.0+） | 切换行号与代码补全 |

程序最长约 **32,300 字符**（原版限制）。

---

## 4. 语言参考

> 记号：`[ ]` 可选；`< >` 必填；`*` 可重复（逗号分隔）；`|` 二选一。

### 4.1 词法规则

- **关键字不区分大小写**：`EVERY` = `every`。资源 ID 的大写在解析时会被转成小写，建议一律写小写。
- **注释**：`--` 到行末。
- **空白**（空格、换行、缩进）无语义。
- **数字**：只能是**非负整数**（`20`、`1000`、`4096000`）。没有小数、没有负数、没有千分位、没有 `1k`。
- **标识符（不加引号的标签/资源名）**：只能由字母、数字、下划线、`*` 组成，且**不能以数字开头**。
- **字符串**：用双引号，引号内可写 `\"`。
- **必须加引号的情况**：
  - 含中文或其他非 ASCII 字符：`"有机灌注器"`
  - 含空格、连字符、点、斜杠等：`"storage a"`、`"my-chest"`
  - 以数字开头：`"1号箱"`
  - 与关键字同名的标签：如 `input`、`output`、`from`、`to`、`end`、`do`、`if`、`then`、`else`、`has`、`each`、`in`、`by`、`side`、`slot(s)`、`north/east/south/west`、`name`、`every`、`plus`、`tag`、`with`、`without`、`except`、`retain`、`empty`、`round`、`robin`、`label`、`block`、`not/and/or`、`true/false`、`null`、`some/one/lone/overall`、`tick/ticks`、`pulse`、`by`、`gt/lt/eq/le/ge` 等。**拿不准就加引号，加引号永远安全。**
  - 可以不加引号的"看着像关键字"的词：`top bottom left right front back redstone global second seconds`（4.16.0 起 `redstone` 可作标签与资源名）。
- **`*` 通配**：不加引号时 `*` 被替换为 `.*`（`*_ingot`、`*seed*`）；**加引号时是纯正则，必须自己写 `.*`**（`".*_ingot"`）。
- **标签长度**：最大 256（4.22.0 起，之前 80）。

### 4.2 程序结构

```text
[name "程序名"]          ← 只能是第一行代码
every ... do ... end     ← 一个或多个触发器
every ... do ... end
```

- `name` 可省略；写了，磁盘名称会变成该字符串。
- **除 `name` 和 `every` 外，所有语句只能出现在触发器里。**
- 多个触发器彼此独立；每个触发器结束后自动忘记它登记的输入。

### 4.3 触发器

```text
every [<period>] [global | g] [(plus | +) <offset>] (tick | ticks | second | seconds) do
    <语句>*
end

every redstone pulse do
    <语句>*
end
```

| 写法 | 含义 |
|---|---|
| `every tick do` / `every 1 tick do` | 每刻（只能在**只传能量**时使用，见下） |
| `every 20 ticks do` | 每 20 刻（= 1 秒） |
| `every 5 seconds do` | 每 5 秒（= 100 刻）。`second` 与 `seconds` 等价 |
| `every seconds do` | 缺省 period = 1 → 每秒 |
| `every 20 global ticks do` / `every 20g ticks do` / `every 20 g ticks do` | 使用**世界时间**对齐，而不是管理器内部时钟 |
| `every 20 plus 5 ticks do` / `every 20+5 ticks do` | 偏移 5 刻（偏移的单位与间隔单位相同：`every 20+1 seconds` = 400 刻周期、偏移 20 刻） |
| `every 20g+5 ticks do` / `every 20 global plus 5 ticks do` | 世界时间 + 偏移 |
| `every 20 ticks offset by 5 ticks do`（较新版本） | 新式偏移写法，偏移可以用不同单位；**不能与 `+` 偏移混用** |
| `every redstone pulse do` | 每次红石脉冲上升沿触发；**不受最小间隔限制**，可每刻甚至同刻多次 |

- **计时**：默认使用管理器内部时钟（放置时为 0，每刻 +1，**重新载入世界时随机初始化**）；条件是 `时钟 % 间隔 == 偏移`。用 `global` 则用世界时间，可让多个管理器同步。
- **最小间隔**（服务器配置）：
  - 一般触发器：`timerTriggerMinimumIntervalInTicks`，**默认 20**。
  - 触发器内**所有** input/output 都只涉及 `forge_energy`（`fe::`）或 `mekanism_energy` 时：`timerTriggerMinimumIntervalInTicksWhenOnlyForgeEnergyIOStatementsPresent`，**默认 1**。
  - 小于最小值 → 编译失败，提示 `Minimum trigger interval is N ticks.`
- `every 0 ticks`、`every 20.5 ticks` 是错误。
- 4.20.0 中 `second` 有 bug（效果等同 `ticks`），4.22.0 起修复；4.24.0 起修复秒级偏移未乘 20。
- 较新版本：使用旧式 `+` 偏移会收到"含义不明确，请改用 OFFSET BY"的**警告**（不影响运行）。

### 4.4 input / output 总语法

```text
input  [<限制>, <限制>, ...] [except <资源>, ...] from [each] <标签访问>
output [<限制>, <限制>, ...] [except <资源>, ...] to   [empty slots in] [each] <标签访问>
```

其中：

```text
<限制>     = [<数量> [each]] [retain <保留> [each]] [<资源> [or <资源>]*] [with|without <tag条件>]
<标签访问> = <标签> [, <标签>]*  [round robin by label|block]  [<面>[, <面>]* side]  [slots <范围>]
```

**子句顺序固定，不能乱**（语法分析器按这个顺序读）：

```text
input  5 retain 2 iron_ingot  except gold_ingot  from  each a, b  round robin by block  top, west side  slots 0-3
       └──────限制──────┘     └──排除──┘          └─────────────标签访问────────────────────────────┘
```

要点：
1. `from` 后面可以紧跟 `each`（"逐个方块"）；`output` 的 `to` 后面可以先 `empty slots in`（仅 output）再 `each`。
2. 标签访问内部的顺序固定为：**标签 → round robin → 面(side) → 槽位(slots)**。
3. **`,` 用来分隔多个"限制"**，也用来分隔多个标签和多个面——别把它们混淆（见 4.6 的陷阱）。
4. 语句可以颠倒顺序写成 `from a input ...` / `to b output ...`，**不推荐**。
5. 没有任何限制时：`input from a` = 登记 a 里所有**物品**；`output to b` = 尽可能放入 b。

```sfml
-- 最小例子：把 a 的所有物品搬到 b
every 20 ticks do
    input from a
    output to b
end
```

### 4.5 资源 ID（resourceid）

格式：`[sfm:]<资源类型>:<命名空间>:<名称>`，**默认资源类型是物品**。

| 你写的 | 解析为 | 含义 |
|---|---|---|
| `stone` | 物品，任意命名空间，名称 stone | 所有模组的 stone（4.x 起不再默认 minecraft:） |
| `minecraft:diamond` | 物品 minecraft:diamond | 2 段 = **物品**的 `命名空间:名称` |
| `thermal:phytogro` | 物品 thermal:phytogro | 同上 |
| `item:minecraft:redstone` | 物品，明确写类型 | 红石粉**物品**（规避关键字冲突） |
| `fluid::` | 流体，所有 | `::` 展开为 `:*:`；等价 `fluid:*:*` |
| `fluid::water` | 流体，任意命名空间的 water | |
| `fluid:minecraft:water` | 流体 minecraft:water | 3 段 = `类型:命名空间:名称` |
| `fluid:minecraft:` | minecraft 命名空间下所有流体 | 结尾 `:` 展开为 `:*` |
| `fe::` | 能量 | `fe`、`rf`、`energy`、`power` 都是 `forge_energy` 的别名 |
| `gas::` | 所有气体（Mekanism） | `gas::`、`gas:mekanism:nuclear_waste` |
| `infusion::`、`slurry::`、`pigment::` | Mekanism 灌注/浆液/颜料 | |
| `chemical::` | 所有化学品（MC 1.21.1+ 的统一类型；`gas::` 等是它的别名） | |
| `sfm:forge_energy:forge:energy` | 完整 4 段写法 | 很少需要 |

**资源类型列表**：

| 类型 | 说明 | 别名 | 备注 |
|---|---|---|---|
| `item` | 物品 | | 默认类型 |
| `fluid` | 流体 | | |
| `forge_energy` | Forge 能量（FE） | `fe`、`rf`、`energy`、`power` | 默认只允许它做 1 刻触发器 |
| `mekanism_energy` | 通用机械能量，单次传输上限 MAX_LONG | | 仅 MC 1.19.2 版本；需 Mekanism |
| `chemical` | 通用机械化学品 | `gas`（气体）、`infusion`（灌注）、`slurry`（浆液）、`pigment`（颜料） | `chemical` 这个名字需 MC ≥ 1.21.1，其他版本用别名；需 Mekanism |
| `redstone` | 红石信号（世界方块**只读**）/ 实验性缓冲器里的计数 | | 版本存疑，见 4.12 |

**⚠ 高频错误**：

```text
fluid:water        ← 错！2 段会被当成"命名空间 fluid 的物品 water"，不是流体
fluid::water       ← 对
fluid:minecraft:water ← 对
fe                 ← 错！缺 ::
fe::               ← 对
```

**类型不存在 / 模组没装**会编译报错 `Program references an unknown resource type "xxx"`（比如没装 Mekanism 就用 `gas::`）。服务器可以用配置 `disallowedResourceTypesForTransfer` 禁用某些类型，报错 `disallowed resource type`。

**用 `or` 连接多个资源（4.20.0+）**，表示"合并为一个限制"：

```sfml-snippet
input 5 stone or dirt from a       -- 总共 5 个，石头或泥土都算
input 5 "stone|dirt" from a        -- 同上，用正则
input 5 stone, dirt from a         -- 注意：这是两个限制！5 个石头 + 全部泥土
output to b
```

**正则**（放在双引号里；整个资源名匹配）：

| 正则 | 示例 | 结果 |
|---|---|---|
| `.` | `"...._ingot"` | 匹配 iron_ingot，不匹配 copper_ingot |
| `.*` | `".*_ingot"` | 所有 *_ingot；不加引号时写 `*_ingot` 效果相同 |
| `+` | `"stone.+"` | 匹配 stone_axe，不匹配 stone |
| `?` | `"bricks?"` | brick、bricks |
| `{n}` `{n,}` `{n,m}` | `"oak_wo{2}d"` | 仅 oak_wood |
| `(…)` `\|` | `"(iron\|gold)_ingot"` | iron_ingot 或 gold_ingot |
| `(?!…)` | `"iron_(?!block).*"` | iron_ 开头但后面不是 block |
| `$` | `"(?!quartz$).+"` | 不匹配 quartz，匹配 quartz_block |
| `[xyz]` `[a-z]` | `"[fl]eather"` | feather、leather |
| `[^xyz]` | `"leather_[^hlb].*"` | leather_chestplate；不匹配 leather_helmet 等 |
| `\d` | `"rocket_t\d"` | rocket_t1 |

> ⚠ **不要用 `"[^(iron_ingot)].*"` 来"排除铁锭"**：`[^...]` 是"排除这些**字符**开头"，会误排除以 i/r/o/n/_/g/t 开头的所有物品。要排除某物，用 `except iron_ingot`（4.8 节）或 `"(?!iron_ingot$).+"`。
> 正则里**不要出现 `:`**（`:` 是资源 ID 的段分隔符）。需要 `(?:...)` 时用 `(...)` 代替。

获取容器里真实存在的 resourceid：用网络工具、Ctrl+I，或光标移到该处按 Ctrl+Space。

### 4.6 数量（number）、保留（retain）、each

```text
[<数量> [each]] [retain <保留> [each]] [<资源>]
```

- **数量 N**：本语句最多搬 N 个（总计）。
- **`retain K`**：
  - 在 **input** 里 = 来源里**保留** K 个，其余才可搬；
  - 在 **output** 里 = 目标里补到**拥有** K 个为止（不会超过）。
- **`each`（跟在数字后面）**：对**资源模式匹配到的每一种资源**分别生效（资源模式匹配项不得超过 512 个）。
- 数量和 retain 可以同时用：`3 retain 6 *_ingot` = 保留 6 个，最多搬 3 个。

完整语义对照表：

| 写法 | 含义 |
|---|---|
| `input 1 from a` | 总共输入 1 个物品 |
| `input 1 *_ingot from a` | 总共输入 1 个锭 |
| `input 1 each *_ingot from a` | **每种**锭各输入 1 个 |
| `input retain 5 from a` | 保留 5 个物品，其余可搬 |
| `input retain 5 *_ingot from a` | 锭整体保留 5 个 |
| `input retain 5 each *_ingot from a` | **每种**锭各保留 5 个 |
| `input 3 retain 6 *_ingot from a` | 锭整体保留 6 个，最多搬 3 个 |
| `input 3 each retain 6 *_ingot from a` | 整体保留 6 个，每种最多搬 3 个 |
| `input 3 each retain 6 each *_ingot from a` | 每种保留 6 个，每种最多搬 3 个 |
| `input 1000 fluid:: from a top side` | 最多 1000 mB 流体 |
| `output 7 to b` | 最多放入 7 个 |
| `output retain 12 to b` | 把 b 补到有 12 个物品 |
| `output 5 each retain 9 each *_ingot to b` | 每种锭每次放 5 个，直到 b 里每种各有 9 个 |
| `output retain 2 *_seeds to each m` | **每台 m** 里种子最多补到 2 个 |

**多限制写法**（逗号分隔，每个限制各算各的）：

```sfml-snippet
input
    20 retain 1 red_sand,   -- 红石沙最多搬 20 个，留 1 个
    retain 1 coal           -- 煤炭全部搬走，留 1 个
from a
output to b
```

**陷阱**：`input 5 stone, dirt from a` 是"5 个 stone"+"全部 dirt"两个限制；如果想要"5 个 stone 或 dirt"，写 `input 5 stone or dirt from a`。

**重要**：`retain` 的语义在 4.22.0 前有 bug（#306 等），4.22.0 修复。老版本遇到 retain 异常先升级。

### 4.7 with / without（按 tag 过滤，4.19.0+；`without` 4.20.0+ 才可靠）

```text
with [tag] [#]<tag匹配>            without [tag] [#]<tag匹配>
```

- 组合：`not`、`and`、`or`、括号 `( )`。`without X` = 对整个表达式取反。
- `tag匹配` = `[命名空间:]路径`；省略命名空间匹配所有命名空间；`*` 匹配一段内任意字符；`**` 匹配任意深度的多段。
- 以下三种写法等价：`with #forge:gems`、`with tag forge:gems`、`with tag #forge:gems`。

```sfml-snippet
input with #ores from a                              -- 所有矿石
input with tag #forge:ores_in_ground/deepslate from a
input without tag #minecraft:planks from a           -- 排除所有木板
input minecraft: with #ingots from a                 -- minecraft 命名空间下、带 ingots tag 的物品
input with not #needs_stone_tool and #ores/* from a  -- 是矿石且不需要石制工具
input with #test:** from a                           -- 匹配 test:a、test:a/b、test:a/b/c…
output with #ingots or tag chests except iron_ingot to b
```

> 方块 tag 对物品同样有效（如 `minecraft:mineable/shovel`）。`except` **不支持** with 子句。

### 4.8 except（排除）

```text
input|output [限制…] except <资源>, <资源> from|to …
```

`except` 是**语句级**修饰，排除这些资源（同样支持正则、通配）。

```sfml-snippet
input *_ingot except copper_ingot from a
output except minecraft: to b                -- 排除所有 minecraft 命名空间的物品
output with #storage_blocks except iron_block to c
input *iron*, *copper* except *block* from chest
```

### 4.9 标签访问：each、round robin、side、slots、empty slots

#### 4.9.1 `each`（逐个方块）

| 写法 | 含义 |
|---|---|
| `input 5 from c` | 把所有 `c` 方块当作一个整体，总共输入 5 个 |
| `input 5 from each c` | **每个** `c` 方块各输入 5 个 |
| `output 1 to b` | 所有 `b` 里**只有一个**方块收到 1 个 |
| `output 1 to each b` | **每个** `b` 方块各收到 1 个 |
| `output retain 2 to each b` | 每个 b 补到有 2 个 |

> 不要把 `from each`（逐方块）和数字后的 `each`（逐资源种类）搞混。

#### 4.9.2 round robin（轮询，4.14.0+）

```text
input|output ... from|to a, b round robin by label|block
```

- `by label`：每次执行只选**一个标签**，依次轮换（一个方块有多个标签时可能多次出现）。
- `by block`：每次执行只选**一个方块**，每个方块一轮出现一次。
- 同时用 `each` 和 `round robin` 时行为等同 round robin。
- 轮询索引按"语句 + 资源类型"分别计数，仅在有效取到资源时递增（只有 input 无 output 不递增；input 为空则该 output 不递增；多个 output 复用输入缓存只递增一次；未执行的分支不递增）。
- **官方建议：多数情况不需要 round robin，优先用 `retain`。** 编译器会对不合理用法发警告（`by label` 只有一个标签；`by block` 又用了 `each`）。

```sfml-snippet
input from source
output 128 dirt to dest round robin by block          -- 每次只给一个 dest 方块
forget
input from "storage a", "storage b" round robin by label
output 8 bone_meal to each dispenser
```

#### 4.9.3 side（面）

```text
<面> [, <面>]* side        或        each side
```

| 面 | 说明 |
|---|---|
| `top` `bottom` `north` `south` `east` `west` | 绝对方向 |
| `left` `right` `front` `back`（4.27.0+） | 相对于方块自身朝向（facing）；方块没有朝向时视为 `null` |
| `null` | 不指定（未写 side 时就是 null）；**无法操作限制方向的方块** |
| `each side` | 所有 6 个面 + null，各操作一次 |

- **写法必须以单词 `side` 结尾**：`top side`、`top, west side`、`east, front side`。只写 `top` 是错的。
- 指定多个面或 `each side` 时，**每个面各操作一次**。
- 非物品资源必须写面。很多机器每个面只开放特定能力/槽位——"抽不出来/放不进去"首先检查面。Mekanism 机器从 null 方向是**只读**的，且受机器侧面配置影响（编译器会对此警告）。

```sfml-snippet
input fe:: from a top side
output fe:: to b east, front side
input gas:: from c each side
output retain 200 gas:: to each d each side      -- 每个 d 的每个面补到 200 mB
```

#### 4.9.4 slots（槽位）

```text
slots <范围>[, <范围>]*       范围 = 数字 或 数字-数字
slot  <范围>                  （4.27.0+，单数同义）
```

- 放在 side **之后**：`from a top side slots 0,1,3-4,5` ✓；`from a slots 0 top side` ✗。
- 槽位编号可用：Ctrl+I、网络工具、Export Inspector、Ctrl+Space。**Ctrl+I 显示的是 GUI 槽位，不一定是自动化槽位。**

```sfml-snippet
input from a top side slots 0,1,3-4,5
output to b slots 24-26
input from chest slot 5
output to chest slot 9
```

#### 4.9.5 empty slots in（4.25.0+，**仅 output**）

只放进目标的**空槽位**，对"大型已满的箱子"可显著减少卡顿。

```sfml
every 20 ticks do
    input from mob_loot
    output to empty slots in storage
end
-- 偶尔做一次合并压缩
every 300 seconds do
    input from storage
    output to storage
end
```

### 4.10 forget（遗忘输入）

```text
forget                  -- 遗忘全部输入
forget a, b             -- 只遗忘这些标签的输入
```

用于在**同一触发器内**切开前后两段逻辑。

```sfml
every 20 ticks do
    input from a
    output 1 to b
    forget a            -- 只忘 a；或直接 forget 忘掉全部
    input from c
    output to d         -- 这里只有 c 的输入有效
end
```

### 4.11 if / else if / else

```text
if <条件> then
    <语句>*
[else if <条件> then
    <语句>*]*
[else
    <语句>*]
end                                  ← 整个 if 链只有一个 end
```

- `else` 后面紧跟 `if` 在语法上就是 `else if`。**没有 `elif`/`elseif`/`otherwise`。**
- if 里可以嵌套 if、可以放 input/output/forget。
- 单个触发器里 if 过多（默认 > 10 个）时，编译器的"模拟检查"会被跳过并给出提示，**不影响实际运行**。

#### 条件表达式

| 条件 | 说明 |
|---|---|
| `true` / `false` | 常量 |
| `( 条件 )` | 括号 |
| `not 条件` | 非 |
| `条件 and 条件` / `条件 or 条件` | 与 / 或 |
| `[集合限定] <标签访问> has <比较符> <数量> [资源] [with…] [except…]` | **判断库存数量** |
| `redstone [<比较符> <数量>]` | 判断**管理器自身**的红石信号 |

**优先级**：`not` 最高，其次 `and`，最后 `or`。**但为避免出错，多个条件一律加括号。**

**比较符**：`>`(`gt`) `<`(`lt`) `=`(`eq`) `<=`(`le`) `>=`(`ge`)。**没有 `==`、`!=`、`<>`。** 不等于请写 `not x has = 5 ...`。

**集合限定词**（同一标签有多个方块时，怎么判）：

| 词 | 含义 |
|---|---|
| `overall`（默认，可省略） | 把所有方块的数量**加起来**再比较 |
| `every` / `each` | 每个方块都满足 |
| `some` | 至少一个满足 |
| `one` | 恰好一个满足 |
| `lone` | 零个或一个满足 |

例：三个标签 `a` 的箱子分别有 5、5、10 个 stone。

| 条件 | 结果 | 原因 |
|---|---|---|
| `every a has = 5 stone` | 假 | 不是每个都等于 5 |
| `each a has >= 5 stone` | 真 | each = every |
| `some a has eq 5 stone` | 真 | 至少一个 |
| `one a has = 5 stone` | 假 | 有两个 |
| `lone a has = 5 stone` | 假 | 超过一个 |
| `overall a has eq 5 stone` | 假 | 总共 20 个 |
| `a has eq 5 stone` | 假 | 默认 overall |

**其他要点**：
- `has` 的后面**必须有比较符和数量**：`if a has 5 stone` ✗；`if a has >= 5 stone` ✓。
- 省略资源 = 所有**物品**：`if a has > 5 then`；判断流体/能量要写类型：`if a has >= 1000 fluid:: then`（4.16.0 起省略资源也可）。
- `has` 中可带 side/slots：`if i top side has >= 8 redstone:: then`。
- `has` 里的资源只能用 `or` 连接，不能用逗号列表。
- 红石只读，且优先使用缓存（上次无缓存时读取的强度），**不能即时响应**。

```sfml
every 20 ticks do
    input from a

    -- a 里物品总数 > 5：只放 1 个到 b
    if a has > 5 then
        output 1 to b
    -- b 有 ≥10 个"非金非铜的锭"，且有 ≥2 个纸：补到 c 有 4 个
    else if b has >= 10 "(?!(gold|copper)).*_ingot" and b has >= 2 paper then
        output retain 4 to c
    else
        output to d
    end

    -- e 的每个方块的化学品都 ≥ 200 mB 才转移
    if each e has >= 200 gas:: then
        input gas:: from e top side
        output 200 gas:: to each f top side
    end

    -- 管理器自身有红石信号
    if redstone then
        input fe:: from g top side
        output fe:: to g2 top side
    end
    if redstone < 10 then
        output fe:: to h each side
    end
end
```

### 4.12 红石

三种不同的东西，**不要混淆**：

| 写法 | 含义 | 版本 |
|---|---|---|
| `every redstone pulse do … end` | 红石脉冲触发器（管理器收到脉冲） | 长期支持 |
| `if redstone [<比较符> <数>] then` | 判断**管理器自身**收到的红石强度 | 长期支持 |
| `if abc [<面> side] has <比较符> <数> redstone:: then` | 读取**被标签方块**发出的红石信号（杠杆、比较器、红石块等），只读 | 版本存疑（见下） |
| `redstone`（物品）| 红石粉**物品**，与上面完全无关 | |

- 物品红石粉：`input redstone from a`（4.14.0+ 不加引号也可），或更稳妥地写 `item:minecraft:redstone` / `"minecraft:redstone"`。
- `redstone::`（红石信号资源）：读取的是**方块发出的弱信号 0–15**，不是输入进来的信号；不加面时取六个面的最强值；加 `east side` 则取该面。它**只读**，不能 `output` 到世界方块里。
- 实验性"缓冲器"（`sfm:buffer`，开发期方块）可存红石计数，用 `input 1 redstone:: from donor` / `output redstone:: to counter` 搬运，比较器读数为 `min(存量, 15)`。普通玩家基本用不到。
- **版本存疑**：用户提供的资料标注 `redstone` 资源类型"≥4.27.0"；仓库当前开发线（4.35.0 PRE，MC 1.19.2 分支）的更新日志把"标签红石读取"列在 4.35.0 PRE。**无法确定用户版本是否支持。** 做法：让用户先写一行 `if abc has > 0 redstone:: then output to b end` 测试，编译报 `unknown resource type` 就换成 `if redstone` 或让用户升级。
- 隧道式管理器**不传红石**。

---

## 5. 执行时序（最常见的错误来源）

`input` 登记的来源在后续 `output` 之后**仍然有效**。因此下面的写法有 bug：

```text
every 20 ticks do
    input from "原料" bottom side
    output to "粉碎机" top side

    input from "粉碎机" bottom side      ← 此时输入列表 = 原料 + 粉碎机
    output to "输出" bottom side         ← 原料也被搬到输出箱了！
end
```

核心：把"放入原料"和"取出产物"变成**有间断的两步**。三种解法：

**① `forget` 截断（最常用）**

```sfml
every 20 ticks do
    input from "原料" bottom side
    output to "粉碎机" top side
    forget

    input from "粉碎机" bottom side
    output to "输出" bottom side
end
```

**② 触发器分段**（每个触发器结束后自动遗忘输入，两部分完全独立）

```sfml
every 20 ticks do
    input from "原料" bottom side
    output to "粉碎机" top side
end

every 20 ticks do
    input from "粉碎机" bottom side
    output to "输出" bottom side
end
```

**③ 物品精确描述**（只对少数固定配方有效，机器能吃的物品太多时不可行）

```sfml
every 20 ticks do
    input with #minecraft:sand from "原料" bottom side
    output with #minecraft:sand to "粉碎机" top side
    input with #exdeorum:dust from "粉碎机" bottom side
    output with #exdeorum:dust to "输出" bottom side
end
```

**其他时序要点**
- 每种资源类型的 input/output 要配对（`input fluid::` 配 `output fluid::`）。没有配对时编译器会警告 `has no matching input statement` / `no future output statement consume`。
- 多个触发器如果间隔相同，会在同一刻按**书写顺序**依次执行。
- `every redstone pulse` 与定时触发器互相独立。
- 机器配方耗时较长时，**不要**用过短的间隔反复把原料拿出来再放进去（AE2 例子里的"整理"触发器间隔要大于一次合成的时间），否则会破坏正在进行的合成。

---

## 6. 效率与机器适配（堆量工厂必读）

### 6.1 SFM 的执行逻辑

SFM 遵循"**可执行优先 > 并行优先**"：先检测输入里的物品，然后**依次**（不是并行）输出到各台机器。后果：

1. **输入物品不够同时填满所有机器** → 靠前的机器分到，靠后的机器空转。解法：用 `each`、`retain`、`number` 限制对**每台机器**的输入量。
2. **同刻产物太多堵满输出口返回栏** → 机器输出槽满而卡住。解法：增加输出口数量，或分批多次收取。

### 6.2 输出口数量规则

输出口数量应**不少于**阵列产出的物品/资源**总种类数**，并且最好在程序里把不同种类分别输出到专用输出口。

实测（1024 台机器）：

| 机器 | 输出口 | 同时处理 | 结果 |
|---|---|---|---|
| 1024 | 1 | 2 种物品 | 258 台处理 A 后临时卡死；762 台处理 B 后正常输出；B 处理完后 A 才正常输出 |
| 1024 | 6 | 4 种物品 | 全部正常输出 |

实例：Mekanism 电解分离器——电解水产生氢气+氧气，电解盐水产生氯气+氢气，共 3 种气体，至少 3 个输出口。因氢气产出效率远高于另外两种，**通常不直接输出到 ME 接口**，而是先输出到 Mek 化学品储罐作缓存，再由储罐输出到 AE 网络；**用于氢气的储罐数量应多于其余两种储罐之和**。

### 6.3 多材料批量合成：机器怎么选

用 SFM 堆量合成 AE 及附属的 7 种处理器（逻辑/工程/计算/累积/能量/并发/量子）。512 台机器、每 20 刻分别输入 3 种材料的结论：

| 机器 | 速度 | 合成类型 | 合成时输入限制 | 输入槽 | 卡死 | 卡死频率 |
|---|---|---|---|---|---|---|
| 压印器（AE2） | 基础 | 每次 1 种 | 拒绝其他输入 | 有类型限制 ×3 | **无** | — |
| 高级压印器（高级AE） | 基础 | 每次 4 种 | 允许其他输入 | 有类型限制 ×12 | 有（同时合成 >1 种处理器时） | 1024 台中 10–50 台 |
| 水晶装配器（高级AE） | 4 倍 | 每次 1 种 | 允许其他输入 | 无类型限制 ×9 | 有（大量合成时，即使只合 1 种） | 1024 台中 125–250 台 |
| 装配机（现代工业化） | 基础 | 每次 1 种 | 允许其他输入 | 无类型限制 ×9 + 有类型限制 ×1 | 有（大量合成时） | 1024 台中 25–50 台 |

卡死原因：
- **高级压印器**：12 个槽实质是 4 个独立压印器输入槽，同一份红石粉/硅板优先输入合成槽 1>2>3>4；槽 1 被占后槽 2 的部分原料自动迁移到槽 1，导致两个槽各有部分材料，无法合成。
- **水晶装配器**：输入槽无类型限制，1–2 种原料占满槽位，第三种原料进不去。
- **装配机**：同理，但红石是流体，不占物品槽，所以概率比水晶装配器低。

**结论：用 SFM 堆量合成时，优先选基础的、限制多的、速度稍慢的机器**，尤其是需要同时处理多种材料输入的合成。

对应的 SFM 程序示例（给每台装配机各输入 3 种材料，64 个一组；注意它用的是**每个触发器一种产物**的写法）：

```sfml
every tick do
    input fe:: from "能源" bottom side
    output fe:: to "装配" top side
end
every 20 ticks do
    input from "输入" bottom side
    output 64 minecraft:redstone, 64 ae2:printed_silicon, 64 ae2:printed_logic_processor to each "装配" top side
end
every 20 ticks do
    input from "输入" bottom side
    output 64 minecraft:redstone, 64 ae2:printed_silicon, 64 ae2:printed_calculation_processor to each "装配" top side
end
every 20 ticks do
    input from "装配" bottom side
    output to "输出" bottom side
end
```

### 6.4 一个反面例子：输出口不足导致 60% 机器闲置

```text
every 20 ticks do
    input from "结晶" bottom side
    output to "输出" top side              ← 只有 1 个输出口，却有 4 种产物
end
```

处理 1 种物品时优先级为"产物 A > 输出口"；处理 2 种及以上时，物品 A 先占输出口，物品 B 等待输出口空闲。结果大部分时候只有不到 40% 的机器在工作。

### 6.5 性能提示

- 最小间隔 20 刻就是为了让"糟糕的程序"不要每刻跑。
- 不需要的东西不要用 `each` + 宽泛通配（会枚举注册表）；能写具体名字就写具体名字。
- 能量传输单独放一个 `every tick`，其他放 `every 20 ticks`。
- 用 `empty slots in` 往大型已满的箱子里放东西。
- 在管理器界面有**性能图**，可对比两种写法的耗时。

---

## 7. 模板库（均已通过 SFML 语法校验）

### 7.1 基础搬运

```sfml
name "move items"
every 20 ticks do
    input from a
    output to b
end
```

### 7.2 只搬指定物品 / 限量

```sfml
every 20 ticks do
    input iron_ingot from a                    -- 只搬铁锭
    output to b
end
every 20 ticks do
    input 1 from each a                        -- 每个 a 箱子各出 1 个
    output to b
end
every 20 ticks do
    input retain 64 from a                     -- a 里物品整体保留 64 个，其余搬走
    output to b
end
```

### 7.3 分拣到不同箱子

```sfml
every 20 ticks do
    input from a
    output with #ores to ores_chest
    output *_ingot to ingots_chest
    output to others                           -- 剩下的都进这里
end
```

> 前面的 output 先"吃掉"属于它的物品，后面的 output 处理剩余。

### 7.4 熔炉阵列（来自官方模板 Furnace Manager）

```sfml
name "Furnace Manager"
every 20 ticks do
    input from "to be smelted"
    output 8 to each furnace top side
    forget

    input from fuel
    output retain 1 to each furnace bottom side
    forget

    input from furnace bottom side
    output to results
end
```

### 7.5 熔炉：不同面放不同东西（来自官方示例 smelting）

```sfml
every 20 ticks do
    input from chest

    output minecraft:oak_log to furnace top side

    output
        coal,                  -- 煤炭不限量
        1 retain 1 oak_log,    -- 木头只补到 1 个
        charcoal
    to furnace bottom side
end

every 20 ticks do
    input from furnace bottom side
    output to chest
end
```

### 7.6 能量、流体、化学品

```sfml
-- 能量：单独一个每刻触发器
every tick do
    input fe:: from "能量" top side
    output fe:: to "机器" top side
end

-- 流体：从水罐给机器供水
every 20 ticks do
    input fluid:: from water top side
    output fluid:: to "机器" top side
end

-- 只搬水，并且每个机器最多存 1000 mB
every 20 ticks do
    input fluid::water from source
    output retain 1000 fluid::water to each thingy
end

-- 通用机械：气体（不同 MC 版本里 gas:: 都可用）
every 20 ticks do
    input gas:mekanism:nuclear_waste from "裂变反应堆" each side
    output gas:: to "同位素离心机" each side
end
```

### 7.7 机器阵列：给每台机器补原料

```sfml
every 20 ticks do
    input from "原料箱"
    output retain 8 to each "机器" top side     -- 每台机器补到 8 个
end
```

### 7.8 溢出保护（主仓库满了再进备用箱）

```sfml
every 20 ticks do
    input from "产物"
    output to "主仓库"
    output to "备用仓库"                        -- 主仓库放不下的才会进这里
end
```

### 7.9 按库存条件触发

```sfml
every 20 ticks do
    if "成品箱" has < 1000 iron_ingot then
        input from "原料箱"
        output to "机器" top side
    end
end
```

### 7.10 红石脉冲触发（用杠杆/按钮手动控制）

```sfml
every redstone pulse do
    input from a
    output to b
end
```

### 7.11 有机灌注器阵列（热力 + 神秘农业，用户提供）

能量/水/肥料/种子/产物。将所有机器的**顶部**设为输入输出面，使用 Ctrl+右击快速标记所有有机灌注器；合成仓配种子到 `"input"`，物品接口提供肥料并接收产物；`energy` 是能量立方等供能元件；`water` 是流体储罐。

```sfml
every tick do
    input fe:: from energy top side                          -- 传能量
    output fe:: to "有机灌注器" top side
end

every 20 ticks do
    input fluid:: from water top side                        -- 传水
    output fluid:: to "有机灌注器" top side

    input thermal:phytogro from "物品接口"                   -- 传肥料
    output to "有机灌注器" top side
    forget

    input from "input"
    output retain 2 *_seeds to each "有机灌注器" top side    -- 传种子，每个机器最多有 2 个
    forget

    input from "有机灌注器" top side                         -- 传产物
    output to "物品接口"
end
```

### 7.12 AE2 压印器（官方模板）

```sfml
NAME "AE2 Inscribers"
-- labels:
-- logic, engineering, calculation, silicon, last => inscribers
-- materials, results => chests
EVERY 20 TICKS DO
    INPUT FROM materials

    OUTPUT RETAIN 2 gold_ingot TO EACH logic SLOTS 2
    OUTPUT RETAIN 2 diamond TO EACH engineering SLOTS 2
    OUTPUT RETAIN 2 certus_quartz_crystal TO EACH calculation SLOTS 2

    OUTPUT RETAIN 2 silicon TO EACH silicon SLOTS 2

    OUTPUT RETAIN 2 redstone TO EACH last SLOTS 2
    OUTPUT RETAIN 2 printed_silicon TO EACH last SLOTS 1

    OUTPUT
        RETAIN 2 printed_calculation_processor,
        RETAIN 2 printed_engineering_processor,
        RETAIN 2 printed_logic_processor
    TO EACH last SLOTS 0
FORGET
    INPUT FROM logic, engineering, calculation, silicon west side
    output to materials
FORGET
    INPUT FROM last west SIDE
    OUTPUT TO results
END
EVERY 200 TICKS DO
    IF SOME last HAS LT 3 THEN
        -- 有只装了一部分的压印器：把材料收回来重新分配，避免一次配方被错误分配
        -- 这个间隔必须大于一次合成所需时间，否则会破坏正在进行的合成
        INPUT FROM last
        OUTPUT TO materials
    END
END
```

### 7.13 Mek 聚变反应堆自适应燃料速率（用户提供）

聚变反应堆可直接通入氘氚燃料，速率 1–1000 mB/t。用终极化学品储罐存燃料，设计目标：储罐有 8,192,000 mB 时达到 1000 mB/t，**速率与存量成正比**。每刻都需要燃料以维持运行，因此用 `every redstone pulse` 配合 **1 tick 脉冲发生器**（粘性活塞 + 侦测器，侦测器方向与下层相反）。程序按存量分档：先向反应堆端口输出对应速率，再把对应存量转存到临时储罐 `temp`，最后 `forget` 并把 `temp` 内燃料放回主储罐。

```sfml
every tick do
    input fe:: from energy top side
    output fe:: to need_energy each side
end

every 20 ticks do
    input fluid:: from "电动泵" top side
    output fluid:: to "电解分离器" top side
end

every redstone pulse do
    input gas:: from "燃料" top side
    if "燃料" has >= 4096000 gas:: then
        output 500 gas:: to "聚变反应堆端口" top side
        output 4096000 gas:: to temp top side
    end
    if "燃料" has >= 2048000 gas:: then
        output 250 gas:: to "聚变反应堆端口" top side
        output 2048000 gas:: to temp top side
    end
    if "燃料" has >= 1024000 gas:: then
        output 125 gas:: to "聚变反应堆端口" top side
        output 1024000 gas:: to temp top side
    end
    if "燃料" has >= 512000 gas:: then
        output 62 gas:: to "聚变反应堆端口" top side
        output 512000 gas:: to temp top side
    end
    if "燃料" has >= 256000 gas:: then
        output 32 gas:: to "聚变反应堆端口" top side
        output 256000 gas:: to temp top side
    end
    if "燃料" has >= 128000 gas:: then
        output 16 gas:: to "聚变反应堆端口" top side
        output 128000 gas:: to temp top side
    end
    if "燃料" has >= 64000 gas:: then
        output 8 gas:: to "聚变反应堆端口" top side
        output 64000 gas:: to temp top side
    end
    if "燃料" has >= 32000 gas:: then
        output 4 gas:: to "聚变反应堆端口" top side
        output 32000 gas:: to temp top side
    end
    if "燃料" has >= 16000 gas:: then
        output 2 gas:: to "聚变反应堆端口" top side
        output 16000 gas:: to temp top side
    end
    if "燃料" has >= 8000 gas:: then
        output 1 gas:: to "聚变反应堆端口" top side
    end
    if "聚变反应堆端口" has = 0 gas:mekanismgenerators:fusion_fuel then
        output 1 gas:: to "聚变反应堆端口" top side
    end
    forget
    input gas:: from temp top side
    output gas:: to "燃料" top side
end
```

### 7.14 大批量机器的两步流程（放入原料 → 取出产物）

```sfml
every 20 ticks do
    input from "原料" bottom side
    output retain 16 to each "机器" top side     -- 每台机器至多补到 16 个，避免先到先得
    forget
    input from "机器" bottom side
    output to "输出A" bottom side
end
```

---

## 8. 交付前自检清单（逐条确认）

**结构**
- [ ] `name` 若有，是第一行代码。
- [ ] 所有 `input/output/forget/if` 都在 `every … do … end` 里。
- [ ] 每个 `every` 都有 `end`；每条 `if … else if … else …` 链只有 1 个 `end`；没有多余的 `end`。
- [ ] `if` 后有 `then`；分支用 `else if`（不是 `elif`/`elseif`）。
- [ ] 没有 `;`、`{}`、`==`、`!=`、`:=`、`while`、`for`、`function`、`let x = …`。

**触发器**
- [ ] 间隔 ≥ 最小间隔：普通触发器 ≥ 20 刻；只有 `fe::`（或 `mekanism_energy`）的才能 `every tick`。
- [ ] 间隔是正整数；没有小数/负数。
- [ ] 能量传输单独一个触发器。

**input / output**
- [ ] 每个 `output` 之前都有对应类型的 `input`；每个 `input` 后面都有人消费。
- [ ] 非物品资源都带 `xxx::` 前缀（`fluid::`、`fe::`、`gas::`），并且**都写了 `side`**。
- [ ] 2 段资源 ID 都是**物品**；流体写成 `fluid::name` 或 `fluid:ns:name`，而不是 `fluid:name`。
- [ ] 子句顺序：`限制 → except → from/to → [empty slots in] → [each] → 标签 → [round robin] → [side] → [slots]`。
- [ ] `side` 写成 `top side` / `top, west side`（含单词 `side`）。
- [ ] `slots` 在 `side` 之后；`empty slots in` 只用在 `output`。
- [ ] 逗号没有误用：`input 5 stone, dirt` 是两个限制。
- [ ] 通配/正则：不加引号用 `*`；加引号用 `.*`；正则里没有 `:`。
- [ ] 需要加引号的标签/资源都加了引号（中文、空格、数字开头、关键字）。
- [ ] `retain` 的方向正确：input = 来源保留；output = 目标补到。
- [ ] 分步：先放入再取出的地方有 `forget` 或拆成两个触发器。

**条件**
- [ ] `has` 后有比较符与数量；比较符是 `> < = <= >=`（或 gt lt eq le ge）。
- [ ] 复合条件加了括号。

**交付内容**
- [ ] 附了标签清单（标签 → 方块 → 面）。
- [ ] 说明了版本依赖的特性（`without`、`or`、`empty slots in`、相对方向、`redstone::`）。
- [ ] 提醒了输出口数量/机器选择等效率风险（如果是堆量工厂）。
- [ ] 提醒用户编译后查看磁盘警告。

---

## 9. 常见错误对照表

下面每一行都是真实会发生的错误。**语法错** = 编译失败；**语义错** = 编译通过但行为不对。

| # | 错误写法 | 类型 | 正确写法 / 说明 |
|---|---|---|---|
| 1 | `input from a` 后面没有 `output` | 语义错 | 必须有 `output`，否则什么都不发生 |
| 2 | `input fluid:: from a` 配 `output to b` | 语义错 | `output fluid:: to b top side`；类型要配对 |
| 3 | `input fe:: from a` 没写面 | 语义错 | `input fe:: from a top side` |
| 4 | `output to b top` | 语法错 | 必须以 `side` 结尾：`top side` |
| 5 | `input stone from a slots 0 top side` | 语法错 | 面在前槽位在后：`from a top side slots 0` |
| 6 | `input from a top side round robin by block` | 语法错 | `round robin` 必须在 side 之前：`from a round robin by block top side` |
| 7 | `input from empty slots in a` | 语法错 | `empty slots in` 只用于 output |
| 8 | `every 5 ticks do input … output … end` | 编译失败 | 最小间隔 20（只传能量可到 1） |
| 9 | `every 0.5 seconds do` | 语法错 | 只能是非负整数 |
| 10 | `fluid:water` | 语义错 | 被当作物品；写 `fluid::water` |
| 11 | `output fe to b top side` | 语义错/报错 | 写 `fe::` |
| 12 | `input from 有机灌注器` | 语法错 | 中文标签必须加引号：`"有机灌注器"` |
| 13 | `input from east` | 语法错 | `east` 是关键字，标签名要加引号：`"east"` |
| 14 | `input "*_ingot" from a` | 编译失败（正则非法） | 加引号用 `".*_ingot"`，或不加引号 `*_ingot` |
| 15 | `output "[^(iron_ingot)].*" to c` | 语义错 | 会排除所有以 i/r/o/n/_/g/t 开头的物品；用 `output except iron_ingot to c` |
| 16 | `input 5 stone, dirt from a` 以为是"5 个石头或泥土" | 语义错 | 实际 = 5 stone + 全部 dirt；用 `5 stone or dirt` |
| 17 | `if a has 5 then` | 语法错 | 缺比较符：`if a has >= 5 then` |
| 18 | `if a == 5` / `if a has != 5` | 语法错 | 用 `=`；不等于用 `not a has = 5` |
| 19 | `elif`、`elseif`、`else if … end` 每支一个 `end` | 语法错 | 只有 `else if`，整条链一个 `end` |
| 20 | `forget` 缺失，原料绕过机器直接到产物箱 | 语义错 | 见第 5 节三种方案 |
| 21 | 触发器外直接写 `input/output` | 语法错 | 必须在 `every … do … end` 里 |
| 22 | `name "x"` 写在触发器之后 | 语法错 | `name` 必须是第一行代码 |
| 23 | `output 1000 to b` 想搬流体 | 语义错 | 默认是物品；写 `output 1000 fluid:: to b top side` |
| 24 | `every 20+1 ticks offset by 2 ticks` | 编译失败 | `+` 偏移与 `OFFSET BY` 不能混用 |
| 25 | `input from a iron_ingot`（资源写在标签后） | 语法错 | 资源写在 `from` 之前：`input iron_ingot from a` |
| 26 | 期望 `output 1 to b` 给每个 b 一个 | 语义错 | 只会有一个 b 收到；要每个都收到写 `to each b` |
| 27 | 期望 `input 5 from a` 每个 a 出 5 个 | 语义错 | 总共 5 个；每个出 5 个写 `from each a` |
| 28 | 把 `redstone`（物品）和 `redstone::`（信号）混用 | 语义错 | 物品用 `item:minecraft:redstone` / `"minecraft:redstone"` |
| 29 | `input 1k …` / `input 1,000 …` | 语义错（能编译！） | `1k` 被解析为"1 个名为 k 的物品"，`1,000` 被解析为两个限制；写 `1000` |
| 30 | `fluid::`、`gas::` 在没装 Mekanism/对应模组时使用 | 编译失败 | `unknown resource type` |
| 31 | 在 `has` 里用逗号列多个资源 | 语法错 | 用 `or`（4.20.0+） |
| 32 | 程序超过 ~32,300 字符 | 无法保存 | 精简或拆分（减少重复 if 分支） |
| 33 | 标签没推送到磁盘，或方块没接线缆 | 语义错 | 看磁盘警告：`undefined_label` / `disconnected_label` |

---

## 10. 编译错误与磁盘警告速查

磁盘上的警告会在管理器界面显示；**警告按钮：点击可复制含警告的代码，Shift+点击尝试自动修复警告**。磁盘最多保留 10 条问题（配置 `maxDiskProblems`）。

### 10.1 编译错误

| 提示 | 含义与处理 |
|---|---|
| `Failed to compile.` / `Failed to compile with N errors.` | 语法错误。逐行对照第 4、9 节；可能是缺 `end`、缺 `then`、`side` 拼写、关键字当标签 |
| `Minimum trigger interval is N ticks.` | 间隔太小；改大，或确认触发器是否仅含能量传输 |
| `Program references an unknown resource type "x"` | 类型名拼错或对应模组未装（如 `gas::` 需要 Mekanism） |
| `Program has a malformed resource type "x"` | 资源**类型**必须是字面量，不能是通配或正则 |
| `Program references a disallowed resource type "x"` | 服务器配置禁用了该类型 |
| `Invalid resource identifier pattern …` | 正则非法；常见于加引号后写了裸 `*` |
| `Label name cannot be longer than 256 characters.` | 标签名过长 |
| `Interval exceeds supported tick count` / `Use either legacy + offset or OFFSET BY, not both` | 间隔过大 / 偏移写法混用 |

### 10.2 警告（程序能运行，但可能不对）

| 警告 | 含义 | 怎么办 |
|---|---|---|
| `Label "x" is assigned in the world … but not connected by cables.` | 标签方块没连线缆 | 补线缆；或用管理器界面"重建网络" |
| `Label "x" is assigned … connected by cables but is not detected as a valid inventory.` | 方块有标签也连着线缆，但没有可用的物品/流体/能量能力 | 换对面；确认方块确实有存储能力 |
| `Label "x" is assigned in the world but not defined in code.` | 世界里有标签，程序里没用 | 多余标签，可忽略或清理（标签枪 Prune） |
| `Label "x" is used in code but not assigned in the world.` | 程序用了标签，但世界里没绑定（或没推送到磁盘） | 标签枪给方块贴标签，**右击管理器推送** |
| `Statement … inputs "x" from "y" but no future output statement consume "x".` | 这个 input 没有后续 output 消费 | 补 output，或删掉多余 input |
| `Statement … uses resource type "x" which has no matching input statement.` | output 的类型没有对应 input | 补对应类型的 input（如忘了 `input fluid::`） |
| `Statement matches no slots` | 指定的 slots/side 在目标上没有槽位 | 检查槽位号、面 |
| `No slots support extraction` / `No slots support insertion` | 该面/槽位不允许取出/放入 | 换面；检查机器的自动化配置 |
| `Mekanism blocks are read-only from the null direction` | Mekanism 方块没写 side | 补 `top side` 等 |
| `Mekanism block side config … doesn't agree with statement` | Mekanism 机器侧面配置与语句不符 | 用配置卡/配置器把对应面设为输入或输出 |
| `EACH used without a pattern` | 用了数字后的 `each`，但资源没有通配 | `each` 只在资源是模式（`*_ingot`）时有意义 |
| `Round robin by label should be used with more than one label` / `Round robin by block shouldn't be used with EACH` | round robin 用法不合理 | 改用 `retain`，或去掉 `each` |
| `The legacy + interval offset is ambiguous; use OFFSET BY …` | 旧式 `+` 偏移含义不明（较新版本） | 改成 `OFFSET BY n ticks` |
| `Resource "x" was not found.` | 资源 ID 在注册表里找不到 | 检查拼写、命名空间 |
| `Too many conditions for simulation …` | if 太多，模拟检查被跳过 | 可忽略，或拆成多个触发器 |

---

## 11. 排错流程（"不工作"时按顺序检查）

1. **看磁盘警告**（第 10 节）。没有任何警告 ≠ 没问题，但有警告一定先处理。
2. **标签**：是否已**推送**到磁盘？标签是否贴对了方块、对了面？（网络工具/标签枪渲染可视化）
3. **线缆**：手持网络工具看管理器、线缆、标签是否在同一网络；方块是否**挨着线缆**；管理器界面点"重建线缆网络"；仍不行用 `/sfm bust_cable_network_cache`。
4. **面与槽位**：用网络工具右击目标方块的某个面，看该面开放哪些能力；Ctrl+I 看槽位（注意 GUI 槽位 ≠ 自动化槽位）；Mekanism 机器检查侧面配置。
5. **资源类型配对**：`input` 与 `output` 的 `resourceid` 类型是否一致；流体/能量/化学品是否写了 `::` 和 `side`。
6. **触发器**：间隔是否合适？用 `global` 对齐？重新载入世界后内部时钟会随机初始化，相位会变。
7. **时序**：是否需要 `forget`？是否被前面的 `input` 残留干扰？
8. **数量限制**：`retain`/`number` 是否限制过严？目标是否已满？
9. **日志**：管理器界面的**日志(Logs)**屏，可选 OFF/TRACE/DEBUG/INFO/WARN/ERROR；TRACE/DEBUG 会在执行一次后自动关闭（防卡顿）。
10. **已知问题**：管理器偶尔无故停止工作 → "重建线缆网络"按钮或 `/sfm bust_cable_network_cache`；对堆肥桶不写面输出会跳过可堆肥检查，等于把它变成垃圾桶。
11. **提交 bug**：给出 Minecraft/加载器/SFM 版本、整合包、程序、标签与面、复现步骤、日志。官方问题追踪见第 14 节。

---

## 12. 配置与命令

### 12.1 服务器配置（`sfm-server.toml`；也可在管理器界面左下角点 View server config 查看）

| 选项 | 默认 | 说明 |
|---|---|---|
| `disableProgramExecution` | `false` | 紧急开关：禁止所有管理器编译和运行（游戏被 SFM 卡崩时用） |
| `logResourceLossToConsole` | `true` | 资源被销毁/丢失时记录到控制台 |
| `timerTriggerMinimumIntervalInTicks` | `20` | 触发器最小间隔（刻） |
| `timerTriggerMinimumIntervalInTicksWhenOnlyForgeEnergyIOStatementsPresent` | `1` | 仅能量 I/O 的触发器最小间隔 |
| `maxIfStatementsInTriggerBeforeSimulationIsntAllowed` | `10` | 一个触发器里 if 的数量超过它就不做 2^n 模拟检查 |
| `maxDiskProblems` | `10` | 磁盘最多保留的错误/警告数 |
| `disallowedResourceTypesForTransfer` | 空 | 禁止传输的资源类型（整合包作者用） |
| `levelsToShards` | `JustOne` | 铁砧"附魔书→经验碎片"的转换策略（`JustOne`/`EachOne`/`SumLevels`/`SumLevelsScaledExponentially`） |

改配置后程序缓存会被清空并重新编译。

### 12.2 命令

| 命令 | 权限 | 作用 |
|---|---|---|
| `/sfm config show <SERVER\|CLIENT>` | 所有人 | 显示配置 |
| `/sfm config edit SERVER` | OP(4) | 编辑服务器配置 |
| `/sfm config edit CLIENT` | 所有人 | 编辑客户端配置 |
| `/sfm bust_cable_network_cache` | 所有人（4.16.0+） | 清空所有线缆网络缓存（管理器无故不工作时用） |
| `/sfm bust_water_network_cache` | 所有人 | 清空水槽网络缓存 |
| `/sfm show_bad_cable_cache_entries <方块>` | 管理员 | 在缓存里被判定为"坏"的位置放置指定方块以便可视化 |
| `/sfm changelog` | 所有人 | 在游戏里打开更新日志 |
| `/sfm kit [玩家]` | 管理员 | 给予默认 SFM 物品（管理器、磁盘、标签枪、网络工具） |

---

## 13. 版本差异速查

| 版本 | 变化 |
|---|---|
| 4.12.0 | 数量/保留可用 `each`；`except` 排除 |
| 4.14.0 | `forget`；`round robin`；网络工具；`input redstone` 不加引号可用 |
| 4.15.0 | `each` 作为 `every` 别名；`each side`；`fe::`/`rf::`/`energy::`/`power::` 别名；最小间隔可配置；仅能量可更快 |
| 4.16.0 | `every tick do` 合法；`mekanism_energy`（MC1.19.2）；`redstone` 可作标签；`if x has eq 0` 可省略资源 |
| 4.17.0 | 修复部分 forget 重置计数；加入警告系统；缓存失效修复 |
| 4.19.0 | `with tag`；`gas::`/`infusion::` 等成为 `chemical::` 别名（1.21.1 构建） |
| 4.20.0 | `without` 生效；`or` 连接资源；`each` 限制优化；精致线缆与伪装；`global` 与偏移计时；蓄水槽 2^n；程序长度约 32,300；`/sfm config`；`sfm-server.toml`；禁用资源类型配置 |
| 4.21.0 | 智能补全（`\` 接受），左下角按钮打开编辑器配置 |
| 4.22.0 | 修复 `retain`（#306 等）；修复 `SECOND`；标签最长 256 |
| 4.24.0 | 修复秒级偏移未乘 20 |
| 4.25.0 | `output to empty slots in …` |
| 4.27.0 | 隧道式管理器；`slot` 单数；相对方向 `left/right/front/back`；管理器可操作自己；修复 forget 内存泄漏 |
| 4.29.0 | 隧道线缆、坚固线缆；网络工具调谐；无法抽取槽位的警告 |
| 4.34.0 | 精致线缆可含水 |
| 4.35.0 PRE（开发线） | `redstone::` 标签读取与实验性缓冲器计数；`OFFSET BY` 新式偏移；旧 `+` 偏移警告；Client Manager 等显示/通信功能（与工厂搬运无关，忽略） |

> 开发线语法里还有 `LET … BE …`、`EVERY FRAME …`、`CREATE INPUT`、`BROADCAST`、`RENDER IMAGE`、`INVOKE`、`JSON`、`WITH CAPABILITY`、`AS`：它们属于 Client Manager（客户端显示/收发）实验功能，**不用于工厂物流**。用户没明确要求时不要使用。

---

## 14. 资料来源与已知出入

**官方资源**
- 仓库：`https://github.com/TeamDman/SuperFactoryManager`（语法文件 `platform/minecraft/src/main/antlr/sfml/SFML.g4`；示例 `examples/`；游戏内模板 `platform/minecraft/src/main/resources/assets/sfm/template_programs/`；更新日志 `…/template_programs/changelog.sfml`；`docs/REPORTING_ISSUES.md`；`docs/redstone-support.md`）
- 问题追踪：`https://github.com/TeamDman/SuperFactoryManager/issues`
- Discord：`https://discord.gg/5mbUY3mu6m`
- CurseForge：Super Factory Manager；VSCode 语法高亮扩展：`TeamDman.super-factory-manager-language`
- DeepWiki 索引：`https://deepwiki.com/TeamDman/SuperFactoryManager`（AI 生成，可能滞后，**与源码冲突时以源码/本文为准**）

**本文与零散资料之间已核对出的出入**（遇到时以本文为准）
1. 旧文档/DeepWiki/部分示例注释写"物品默认命名空间是 minecraft:"。**新版已不是**：省略命名空间会匹配所有模组的同名物品（`stone` ≈ `*:stone`）；需要限定时写 `minecraft:stone`。
2. 部分资料写"`empty slots in` 可用于 input"。**语法上只有 output 支持。**
3. 旧示例里"`not`、`and`、`or` 优先级相同"。**语法文件里是 not > and > or**；仍建议加括号。
4. 旧资料的正则示例 `"[^(iron_ingot)].*"` 用来"排除铁锭"是错的（见 4.5）。
5. `redstone::`（信号读取）出现的版本：用户资料写 ≥4.27.0，仓库更新日志写在 4.35.0 PRE。**需让用户实测。**
6. 程序最大长度：更新日志写约 32,300，源码常量为 32,600；以"约 32,300"为安全线。
7. 配置文件：用户资料写 `config/sfm-server.toml`（4.20.0+）或 `config/sfm-common.toml`；Forge 的**服务器配置通常在存档目录的 `serverconfig/` 里**。最稳妥的方式是用管理器界面的 View server config 或 `/sfm config` 命令定位。

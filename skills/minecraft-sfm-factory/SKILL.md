---
name: minecraft-sfm-factory
description: 协助用户在 Minecraft 中使用 Super Factory Manager（SFM，工厂管理器，程序语言 SFML）搭建自动化工厂：编写、审查、调试 SFM 程序，设计标签与机器阵列的输入输出布局，排查"不工作/卡死/效率低"。当用户提到 SFM、Super Factory Manager、工厂管理器、工厂线缆、标签枪、磁盘程序、every ... do、input/output/forget/if 语句，或要求自动化物品、流体、能量、通用机械化学品传输时使用；在使用 SFM 的语境下，用户只说"帮我做某产物（如 Mek 钢、核燃料）的自动化"时也使用。
---

# Minecraft SFM（Super Factory Manager）工厂协助指南

本 Skill 是编写 SFM 程序时的首要参考，适用范围以文中版本说明为准；与用户具体版本的官方源码或游戏内结果冲突时，核对版本并更正本文结论。SFM 是一个小众模组，它的语言 SFML 只有几十个关键字，但细节很多、与常见编程语言差别很大。**你的记忆里关于 SFML 的内容很可能是错的或过时的，不要凭记忆补全；先按本 Skill 查证。**

本文件是常驻的核心部分（规则、任务路由、执行模型、语言速查、自检清单）。细节放在 `references/` 中，按第 1 节的路由**按需读取**。

---

## 0. 给 AI 的铁律（先读这一节）

1. **只使用本 Skill 出现过的语法。** SFML 没有变量赋值、没有循环、没有函数、没有 `;`、没有 `{}`、没有 `==`、没有 `!=`、没有 `while/for`、没有 `elif/elseif`。想不到写法时，宁可告诉用户"SFML 做不到"并给出下表的替代方案，也不要发明语法。
2. **SFML 不是"搬运命令"，而是"登记输入 + 消费输出"。** `input` 只登记来源，什么都不会移动；`output` 才会真正从已登记的来源取资源并放入目标。只有 `input` 没有 `output` = 什么也不发生。
3. **每种资源类型要有各自的 input 和 output。** `input from a` 默认只登记**物品**。要搬流体/能量/化学品，必须写 `input fluid:: ...` / `input fe:: ...` / `input gas:: ...`，并且 `output` 也要写同样的类型。
4. **除物品外（流体、能量、化学品、红石），必须写 `side`**（如 `top side`）。物品通常也建议写，尤其是机器。
5. **输入登记不会因为 output 而消失。** 同一触发器里先"放进机器"再"取出产物"，中间必须 `forget` 或拆成两个触发器，否则原料会绕过机器直接进入产物箱（见第 5 节）。
6. **标签名含中文、数字开头、连字符、空格、或与关键字相同，必须加双引号。** 如 `"有机灌注器"`、`"storage a"`、`"east"`。
7. **每个 `every ... do` 要有 `end`；每个 `if` 链（含 else if / else）只有一个 `end`。**
8. **触发器间隔不能小于配置最小值（默认 20 刻 = 1 秒）。** 只传能量的触发器可以到 1 刻。`every 5 ticks` 搬物品会编译失败。
9. **给出的程序必须附带"标签清单"**（每个标签对应哪些方块、哪个面），并且**交付前逐条过第 6 节的自检清单**。
10. **版本不确定时先问版本（整段对话只问一次，之后沿用）。** 不要假定用户使用最新版语法（尤其是 `without`、`or`、`empty slots in`、相对方向、`offset by`）。**红石不用问**：`every redstone pulse`、`if redstone`、`redstone::` 在现代版本中都可用，按需直接使用。
11. 不确定某行为时，让用户用游戏内工具验证（网络工具、Ctrl+I、日志界面），不要编造"应该可以"。
12. **本文件没写到的细节，先读对应的 `references/` 文件再回答**（见第 1 节）。不要凭记忆补全。
13. **简单优先，复杂必警告。** SFM 在大批量物流时自身开销大，容易拖慢服务器。在满足需求、语法合规的前提下，永远选最简单的写法（见 2.4）；只要程序命中 2.5 中任意一条，交付时**必须**写【性能提示】。

14. **游戏数据不臆造，信息不全只问不写。** 配方链、资源 ID、机器接口必须来自用户确认（JEI/EMI、Ctrl+Space、用户描述）或经用户同意后查到的有出处资料，**不能凭记忆当成事实**。目标产物、配方链任一项不明确时，先按 2.0 提问，**不写代码**；只有用户明确说"直接生成"时才写，且所有未核实内容必须标注。

**必须先确认才能写的事**（缺一项就先问，问法见 `recipe-learning.md`）：

| 事项 | 确认方式 |
|---|---|
| 目标产物（精确到具体物品，有歧义时列选项让用户选） | 用户描述 / JEI 中的物品名 |
| 是否整合包、是否魔改包（魔改包配方常被大量修改） | **对话第一轮**问一次，之后沿用，不重复问 |
| 配方链（步骤、机器、输入输出、副产物） | 用户的 JEI/EMI 为第一依据；用户提供不了时，征得同意后查 wiki 或模组源码 |
| 需要筛选时的资源 ID | Ctrl+Space（实物放进容器后列出）、F3+H、JEI/EMI |
| 机器接口（面、槽位、侧面配置） | **由你按设计指定**，告诉用户把机器改成什么配置；不必先问用户现在怎么配 |

**SFM 做不到的事**（直接告诉用户，并给替代方案）：

| 需求 | 为什么做不到 | 替代方案 |
|---|---|---|
| 变量、计数、记住状态 | 没有变量 | 用容器槽位里的物品数当变量（`advanced-patterns.md`"计数寄存器"） |
| 区分注册 ID 相同、只有 NBT/数据组件不同的物品 | 过滤只看注册 ID 和 tag | 先用能识别 NBT 的模组分开（见 4.4），SFM 只负责运输 |
| 直接发出红石信号 | 没有红石输出语句 | 改变容器内物品数，用比较器读出（`advanced-patterns.md`"间接输出红石信号"） |
| 自己合成物品、模拟玩家右键 | 只能搬运资源 | 交给机器、合成器、AE 自动合成，或能模拟右键的模组 |
| 操作没有物品/流体/能量能力的方块 | 只能访问方块开放的能力 | 用网络工具确认方块开放了哪些能力，换一个面或换一种方块 |

---

## 1. 任务路由

| 用户要做的事 | 怎么做 |
|---|---|
| 写新程序 | **先做 2.0 需求解析**（读 `recipe-learning.md`），确认后按第 2 节流程写；在 `templates.md` 找相似案例；涉及具体模组时读 `mod-notes.md` 对应小节 |
| 审查已有程序 | 逐条过第 6 节自检清单，再对照 `troubleshooting.md` 的常见错误表；指出问题时给出修改后的完整程序 |
| 排错（报错、不工作、卡住） | 先读 `troubleshooting.md`：有报错原文就查速查表，否则按排错流程逐项检查 |
| 优化卡顿或效率 | 读 `efficiency.md`，按第 2.4 节简化；给出改写前后的对比 |
| 解释概念或语法 | 以第 3、4 节为准；细节查 `language-reference.md` |

**参考文件索引**（遇到下列情况必须先读，不要凭记忆补全）：

| 遇到这种情况 | 必须先读 |
|---|---|
| 用到第 4 节速查表没覆盖的语法细节：正则、`with/without` tag 过滤、`except`、`round robin`、`empty slots in`、红石三种含义、`has` 的集合限定词、触发器偏移/`global` | `references/language-reference.md` |
| 要写一个新程序，想找相似案例（熔炉阵列、分拣、溢出、AE2 压印器、有机灌注器、Mek 聚变燃料……） | `references/templates.md` |
| 用户贴出报错/警告原文，或说"不工作/没反应/卡住" | `references/troubleshooting.md` |
| 机器阵列 ≥ 数十台、多种产物、"只有一部分机器在干活"、选哪种机器堆量 | `references/efficiency.md` |
| 问到标签枪/网络工具操作、编辑器快捷键、线缆种类、蓄水槽、隧道式管理器 | `references/items-and-tools.md` |
| 问到服务器配置、`/sfm` 命令、某特性从哪个版本开始、资料出入 | `references/config-and-versions.md` |
| 用户要自动化生产某样东西，而目标产物、配方链、资源 ID、机器接口有任何一项不确定（**写代码前必读**） | `references/recipe-learning.md` |
| 涉及具体模组：Mekanism、AE2、GregTech CEu、神秘农业、资源蜜蜂、热力、Oritech、仪式类模组；或用户提到整合包（如 ATM10） | `references/mod-notes.md` |
| 需求有严格的加料顺序、"等 A 完成再做 B"、多方块/仪式类合成、计数、多段化学链、AE 样板供应器配合、多种副产物防卡死、红石时钟提速、**自循环增产**、蓄能后定量放电、**用 SFM 控制红石电路** | `references/advanced-patterns.md` |

---

## 2. 协助流程

### 2.0 需求解析（写代码前必做）

用户只说了"帮我做 X 的自动化"时，**陪用户分几轮完成**，每轮只问当下最关键的 1–3 件事，已知的跳过：

1. **环境（只在对话第一轮问一次）**：SFM/MC 版本、是否整合包、哪个整合包、是否魔改包。之后整段对话沿用，**不重复问**；用户在后续消息里提到换了环境时再更新。魔改包一律以 JEI 为准，不套用原版配方。
2. **目标产物**：精确到具体物品；有歧义（如"核燃料""钢""处理器"）时列出候选，**不替用户选**。可以和第 1 项放在同一轮问。
3. **配方链**：一步步引导用户在 JEI/EMI 中查（对目标按 R，配方里有中间产物就继续对中间产物按 R），每轮只查一两步。把用户发来的内容整理成生产链表（步骤、机器、输入、输出、副产物），最后请用户整体确认。用户提供不了且没有可靠参考时，**先请求协助**，征得同意后再查官方 wiki 或模组源码（注明来源和版本）。
4. **机器接口：由你指定，不是问**。根据设计直接告诉用户每台机器要怎么配：哪个面设为输入或输出、关闭自动弹出、需要的编程电路或催化剂等。只有用户说明无法按建议配置（如机器位置受限）时，再按用户的实际情况调整程序。

目标产物和配方链没确认完，**只提问和引导，不写代码**（问法与模板见 `recipe-learning.md`）。用户明确说"直接生成"时例外：可以写，但开头声明哪些内容未核实，代码中对应位置加 `-- 未核实` 注释，并在末尾列出验证步骤。

### 2.1 其他要问清的信息（缺失才问，已知就不要再问）

| 要确认的信息 | 为什么重要 |
|---|---|
| SFM 版本（模组列表里看）、Minecraft 版本、加载器 | 语法随版本变化；化学品类型名随 MC 版本变化 |
| 涉及哪些机器/模组，是否在整合包里（如 ATM10） | 各机器开放的面、槽位、侧面配置不同；不同整合包的物品 tag 可能不同 |
| 要搬运的资源：物品/流体/能量/化学品/红石 | 决定 `resourceid` 和是否必须写 `side` |
| 机器数量、每种机器的产物种类数 | 决定接收槽/罐容量、`each`/`retain` 写法（大阵列读 `efficiency.md`） |
| 数据流方向：从哪里来、到哪里去、是否需要中转 | 决定标签划分与是否要 `forget` |
| 用户现有的程序/报错/警告文字 | 排错必需 |

### 2.2 设计步骤

1. 画出数据流：`来源 → (机器输入面) → 机器 → (机器输出面) → 目标`。
2. 给每个**角色**起一个标签名（来源箱、各类机器、产物箱、能源、水源……）。同一标签可含多个方块。同类机器要做不同配方时，按配方分成不同标签，每台机器固定只做一个配方。
3. 为每个标签确认使用哪个面（`top/bottom/north/...`）。
4. 逐触发器写程序：能量单独一个 `every tick`；物品/流体通常 `every 20 ticks`；"放入"与"取出"分开。
5. 按 2.4 逐条简化；按 2.5 判断是否需要【性能提示】；过第 6 节自检清单。
6. 向用户交付：**程序 + 标签清单 + 搭建步骤 + 风险与性能提示**（格式见 2.3）。

### 2.3 回答格式模板

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
3. 用标签枪：先写好程序，再对管理器 Shift+右击"拉取"标签名，
   然后右击世界里的方块贴标签（Ctrl+右击可一次标记相连的同种机器），最后右击管理器"推送"。
4. 一次性手动设置：机器朝向、侧面配置（Mekanism 可用配置卡复制）、关闭与 SFM 冲突的自动弹出、编程电路/不消耗的催化剂、供应器锁定与产物回流路径等。
5. 看磁盘上的警告（管理器界面有警告按钮）。

【风险提示】时序/接收槽罐/面/满仓停机或资源丢弃……
【性能提示】（命中 2.5 时必写）哪一段可能卡、为什么、更省的替代写法、建议用管理器性能图观察
````

### 2.4 简化原则（写完程序后逐条过一遍）

1. **能不用 SFM 就不用**：固定方向、单一路线的搬运（机器自动弹出、管道、AE/RS 接口能完成的），建议交给它们；SFM 负责需要分配、判断、跨距离的部分。模组本身或其扩展模组提供了更简单的自动化方式时，优先推荐那种方式。
2. **一类机器一个标签**，用 `to each` / `from each` 批量处理；不要每台机器一个标签、一段代码。
3. **控制数量用 `retain`**，不用 `if … has` 判断后再搬。
4. **溢出靠 output 的先后顺序**（先主仓、后备用/垃圾桶），不用 `if` 判断是否满了。
5. **写具体的面**：`each side` 会对 7 个方向各操作一次，大阵列上开销成倍增加，只在确实不知道面时临时使用。
6. **能不写资源 ID 就不写**：每种原料放一个专用标签容器、一台机器只做一个配方、一个面只走一种资源，程序就不需要知道资源叫什么（也就不会写错 ID）。必须筛选时才写 ID，且写具体 ID：宽泛通配/正则（尤其配合数字后的 `each`）会匹配大量资源。大型整合包里不同模组常有同名资源（如多个模组的 `sulfuric_acid`），送进只接受特定资源的机器时写上命名空间（`fluid:gtceu:sulfuric_acid`）。
7. **间隔够用就好**：物品、流体默认 20 刻；收产物、整理仓库这类不急的用 40–200 刻；只有能量用 `every tick`。
8. **状态机、计数寄存器、快于 20 刻的红石时钟是最后手段**：先尝试 `retain`、`slots`、拆触发器、AE 样板供应器等待主产物返回的锁定能否解决顺序问题。
9. **整条产线要能暂停**：在管理器上接一个拉杆，用 `if redstone > 0 then … end` 包住整段逻辑，就是一个总开关（只多一个 `if`，不算复杂）。

### 2.5 必须写【性能提示】的情况（经验阈值）

- 使用了状态机或计数寄存器。
- 单个触发器里有 3 个及以上 `if`，或有嵌套 `if`。
- `every redstone pulse` 配合快于 20 刻的红石时钟。
- 对大量方块（约 64 台以上）使用 `each`，尤其再叠加 `each side` 或宽泛正则。
- 以 20 刻或更快的频率从大型存储（大箱子、抽屉管理器、AE 接口）读取全部内容。
- 定时触发器达到 5 个及以上，或程序接近长度上限。

---

## 3. 核心概念与执行模型

- **管理器（Manager）**：执行程序的方块，放入**磁盘**后运行磁盘上的程序。
- **磁盘**：存**程序文本**和**标签→方块位置**的映射。
- **标签（Label）**：程序里用名字引用方块，名字与方块位置由**标签枪**绑定。一个标签可有多个方块，一个方块可有多个标签。
- **线缆网络**：管理器、线缆、被操作的方块必须通过**工厂线缆**连成一个网络（管理器本身也算线缆）。没连上的标签在程序里"存在"，但搬不了东西。
- **程序结构**：`[name "..."]` + 若干**触发器**。触发器 = 定时器或红石脉冲，内含按顺序执行的**语句**。

**执行模型**（最重要）：

```text
每当触发器到点：
  按从上到下的顺序执行语句
    input  → 把"来源方块 + 资源过滤 + 数量限制"登记到本触发器的【输入列表】
    output → 从【输入列表】里能提供的资源中取出，放进目标方块（受数量限制、目标容量限制）
    forget → 从【输入列表】里删掉条目（全部或指定标签）
    if     → 条件成立才执行对应分支里的语句
触发器结束 → 【输入列表】自动清空（不会影响别的触发器）
```

- **没有物品缓冲区**：资源是在 `output` 时直接从来源方块转移到目标方块。
- 多个 `output` 依次执行：先满足前一个目标（受它的限制和容量），剩下的再尝试后一个目标。
- `input` 上的数量限制是**共享预算**，被多个 `output` 依次消耗。例：
  `input 10 from a,b` → `output 1 to z` → `forget b` → `output to z`，第二个 output 最多再搬 9 个（来自 a）。
- 触发器**依次**处理机器，而不是并行：原料不够时靠前的机器分到、靠后的空转（解法见 `efficiency.md`）。
- **开销来源**：每次触发都要逐个访问相关方块的槽位。方块越多、面越多、槽位越多、触发越频繁，越容易卡（这正是 2.4、2.5 的依据）。
- `if … has` 读取的是**当时的真实库存**：同一触发器里前面的 output 搬走的东西，后面的 `has` 立刻就能看到。

---

## 4. 语言速查

> 本节覆盖日常写程序所需的全部语法。表里没有的写法，先查 `references/language-reference.md`。

### 4.1 词法

- **关键字不区分大小写**；资源 ID 建议一律小写。**注释** `--` 到行末。空白无语义。
- **数字**只能是**非负整数**：没有小数、负数、千分位、`1k`。（`1k` 会被解析成"1 个名为 k 的物品"，能编译但完全错误。）
- **标识符**（不加引号的标签/资源名）：字母、数字、下划线、`*`，不能以数字开头。
- **字符串**用双引号。**以下情况必须加引号**：含中文/空格/连字符/点；数字开头；与关键字同名（`input output from to end do if then else has each in by side slot slots north east south west name every plus tag with without except retain empty round robin label block not and or true false null some one lone overall tick ticks pulse gt lt eq le ge` 等）。**拿不准就加引号，加引号永远安全。**
- 可以不加引号的"像关键字"的词：`top bottom left right front back redstone global second seconds`。
- **通配**：不加引号时 `*` = `.*`（`*_ingot`）；**加引号时是纯正则**，必须写 `".*_ingot"`。引号里的 `:` 是段分隔符：`"mysticalagriculture:.*_essence"` 表示"该命名空间下名称匹配正则的物品"；正则语法本身不能用 `:`（如 `(?:…)` 要写成 `(…)`）。

### 4.2 程序结构与触发器

```text
[name "程序名"]                 ← 只能是第一行代码
every <间隔> do <语句>* end      ← 一个或多个触发器
every redstone pulse do <语句>* end
```

| 写法 | 含义 |
|---|---|
| `every tick do` | 每刻（**只能**用于只传 `fe::`/`mekanism_energy` 的触发器） |
| `every 20 ticks do` / `every 5 seconds do` | 每 20 刻 / 每 5 秒；`every seconds do` = 每秒 |
| `every 20 global ticks do` / `every 20g ticks do` | 按世界时间对齐（多个管理器同步） |
| `every 20 plus 5 ticks do` / `every 20+5 ticks do` | 旧式偏移 5 刻（新版会警告，建议改 `offset by`） |
| `every 20 ticks offset by 5 ticks do` | 新式偏移（较新版本）；**不能与 `+` 混用** |
| `every redstone pulse do` | 管理器收到红石脉冲上升沿时触发；**不受最小间隔限制**，可配合红石时钟让物品搬运快于 20 刻（频率越高越卡，须写【性能提示】） |

- 最小间隔默认 **20 刻**；触发器内**所有** I/O 都只涉及能量时默认 **1 刻**。小于最小值 → `Minimum trigger interval is N ticks.`
- 默认用管理器内部时钟（重载世界时随机初始化）；同间隔的多个触发器同刻按书写顺序执行；`every redstone pulse` 与定时触发器互相独立。
- 除 `name` 和 `every` 外，所有语句只能出现在触发器里。

### 4.3 input / output

```text
input  [<限制>, ...] [except <资源>, ...] from [each] <标签访问>
output [<限制>, ...] [except <资源>, ...] to [empty slots in] [each] <标签访问>

<限制>     = [<数量> [each]] [retain <保留> [each]] [<资源> [or <资源>]*] [with|without <tag条件>]
<标签访问> = <标签>[, <标签>]* [round robin by label|block] [<面>[, <面>]* side | each side] [slots <范围>]
```

**子句顺序固定**：`限制 → except → from/to → [empty slots in] → [each] → 标签 → [round robin] → [side] → [slots]`。

```sfml-snippet
input 5 retain 2 iron_ingot except gold_ingot from each a, b top, west side slots 0-3
output to b
```

- **逗号**同时用来分隔多个限制、多个标签、多个面——`input 5 stone, dirt from a` 是**两个限制**（5 个石头 + 全部泥土）；要"共 5 个石头或泥土"写 `5 stone or dirt`（4.20.0+）。
- 无限制时：`input from a` = a 里所有**物品**；`output to b` = 尽可能放入 b。
- `except` 是语句级排除：`input *_ingot except copper_ingot from a`。
- tag 过滤：`input with #forge:ores from a`、`input without tag #minecraft:planks from a`（`with` 4.19.0+，`without` 4.20.0+；组合与通配见 `language-reference.md`）。
- `empty slots in`（4.25.0+）**仅 output**：只放进空槽位，适合往大型已满的箱子里放。
- `round robin`（4.14.0+）：每次只选一个标签/方块轮换。**多数情况用 `retain` 更好**，细节见 `language-reference.md`。

### 4.4 资源 ID

格式 `[sfm:]<类型>:<命名空间>:<名称>`，**默认类型是物品**。

| 写法 | 含义 |
|---|---|
| `stone` | **所有模组**的 stone 物品（不再默认 minecraft:） |
| `minecraft:diamond` | 2 段 = **物品**的 `命名空间:名称` |
| `item:minecraft:redstone` | 显式写类型（红石粉物品，规避与红石信号混淆） |
| `fluid::` / `fluid::water` / `fluid:minecraft:water` | 所有流体 / 任意命名空间的 water / 精确 |
| `fe::` | Forge 能量；`fe` `rf` `energy` `power` 是 `forge_energy` 的别名 |
| `gas::` `infusion::` `slurry::` `pigment::` | Mekanism 化学品；MC 1.21.1+ 统一为 `chemical::`（旧名仍是别名） |
| `mekanism_energy::` | 通用机械能量（仅 MC 1.19.2） |
| `redstone::` | 读取被标签方块发出的红石信号（只读，4.27.0+，见 4.8） |

**⚠ 高频错误**：`fluid:water`（2 段 → 被当成"命名空间 fluid 的物品 water"）✗ → `fluid::water` ✓；`fe` ✗ → `fe::` ✓。

**通用 tag 随版本不同**：MC 1.20.1（Forge）多用 `#forge:…`，MC 1.21+（NeoForge）改为 `#c:…`（如 `#c:seeds`、`#c:ingots`）。不确定时让用户按 Ctrl+Space 或在 JEI/EMI 中查看。

**⚠ SFM 无法区分 NBT / 数据组件**：过滤只看注册 ID 和 tag。注册 ID 相同、只靠 NBT/数据组件区分的物品，SFM 的这类过滤会同时匹配，运输仍保留组件。常见例子：ATM10 中资源蜜蜂的各种蜜脾（都是 `productivebees:configurable_honeycomb`）、药水、附魔书、刷怪蛋类物品。遇到这种需求，**直接告诉用户 SFM 做不到按种类区分**，不要用正则或 tag 硬凑；应先用能识别 NBT 的模组（如 AE2/RS 的分区或过滤卡、带 NBT 过滤的管道或过滤器）把它们分开，再由 SFM 负责运输。
模组没装会报 `Program references an unknown resource type "xxx"`。

### 4.5 数量、retain、each

| 写法 | 含义 |
|---|---|
| `input 1 from a` | 总共输入 1 个物品 |
| `input 1 each *_ingot from a` | **每种**锭各 1 个（数字后的 `each` = 逐资源种类） |
| `input retain 5 from a` | **来源**保留 5 个，其余可搬 |
| `input 3 retain 6 *_ingot from a` | 锭整体保留 6 个，最多搬 3 个 |
| `input 5 from each c` | **每个** c 方块各输入 5 个（`from each` = 逐方块） |
| `output 7 to b` | 所有 b 方块合计最多放入 7 个，可能分给多个方块；只选一个方块用 `round robin by block` |
| `output 1 to each b` | **每个** b 方块各收到 1 个 |
| `output retain 12 to b` | **目标**补到拥有 12 个为止 |
| `output retain 8 to each m top side` | 每台 m 补到 8 个（机器阵列最常用） |
| `input 1000 fluid:: from a top side` | 最多 1000 mB 流体 |

`retain` 方向：**input = 来源保留；output = 目标补到。** 4.22.0 前 `retain` 有 bug，老版本先升级。

### 4.6 面（side）与槽位（slots）

- 面：`top bottom north south east west`；`left right front back`（4.27.0+，相对方块朝向）；`null`（未写 side 时）；`each side`（6 个面 + null 各操作一次）。
- **必须以单词 `side` 结尾**：`top side`、`top, west side`。只写 `top` 是语法错。
- `slots 0,1,3-4`（4.27.0+ 也可写 `slot 5`）放在 side **之后**：`from a top side slots 0-2`。
- 非物品资源必须写面。Mekanism 机器从 null 方向只读，且受机器侧面配置影响。
- 槽位编号：Ctrl+I 显示的是 **GUI 槽位**，不一定等于自动化槽位；以网络工具或 Ctrl+Space 为准。

### 4.7 forget 与 if

```text
forget              -- 遗忘全部输入
forget a, b         -- 只遗忘这些标签的输入

if <条件> then
    <语句>*
[else if <条件> then
    <语句>*]*
[else
    <语句>*]
end                 -- 整个 if 链只有一个 end
```

| 条件 | 示例 |
|---|---|
| 库存比较 | `a has >= 64 iron_ingot`、`a has > 5`（省略资源 = 所有物品）、`a top side has >= 1000 fluid::` |
| 管理器自身红石 | `redstone`、`redstone >= 8` |
| 组合 | `not`、`and`、`or`、`( )`；优先级 not > and > or，**多个条件一律加括号** |
| 集合限定（多方块标签） | `overall`（默认，求和）、`every`/`each`（每个都满足）、`some`、`one`、`lone`：`some last has < 3` |

- 比较符：`>` `<` `=` `<=` `>=`（或 `gt lt eq le ge`）。**没有 `==`、`!=`**；不等于写 `not a has = 5`。
- `has` 后**必须**有比较符和数量：`a has 5` ✗。`has` 里多个资源用 `or`，不能用逗号。

### 4.8 红石：三种不同的东西

| 写法 | 含义 |
|---|---|
| `every redstone pulse do … end` | 管理器收到脉冲时触发 |
| `if redstone [>= n] then` | 判断**管理器自身**收到的信号强度（读缓存，不即时） |
| `if abc has > 0 redstone:: then` | 读**被标签方块**发出的弱信号 0–15，只读；不写面时取六个面的最大值（4.27.0+） |
| `redstone`（物品） | 红石粉物品；稳妥写法 `item:minecraft:redstone` |

隧道式管理器**不传红石**。

---

## 5. 执行时序（最常见的错误来源）

`input` 登记的来源在后续 `output` 之后**仍然有效**。下面的写法会让原料绕过机器：

```text
every 20 ticks do
    input from "原料" bottom side
    output to "粉碎机" top side
    input from "粉碎机" bottom side      ← 此时输入列表 = 原料 + 粉碎机
    output to "输出" bottom side         ← 原料也被搬到输出箱了！
end
```

把"放入原料"和"取出产物"变成**有间断的两步**：

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

**② 拆成两个触发器**（每个触发器结束后自动遗忘输入）

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

**③ 精确描述资源**（仅适合配方固定、物品种类很少的机器）

```sfml
every 20 ticks do
    input with #minecraft:sand from "原料" bottom side
    output with #minecraft:sand to "粉碎机" top side
    input exdeorum:dust from "粉碎机" bottom side
    output exdeorum:dust to "输出" bottom side
end
```

其他时序要点：
- **output 只搬自己类型的资源**：先放物品、再放气体时，两段之间不需要 `forget`。但同一台机器的不同面要放入**同类型**的不同资源（例如两种气体分别进左、右两面）时，两组之间必须 `forget`，或在 input/output 里写精确资源 ID，否则后一个 output 会把前一种资源也送进错误的面。
- 每种资源类型的 input/output 要配对，否则编译器警告 `has no matching input statement` / `no future output statement consume`。
- 配方耗时长的机器，**不要**用过短的间隔反复把原料取出再放入，会破坏正在进行的合成。

---

## 6. 交付前自检清单（逐条确认）

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
- [ ] 通配/正则：不加引号用 `*`；加引号用 `.*`；引号里的 `:` 只用作段分隔符，正则语法里没有 `:`。
- [ ] 需要加引号的标签/资源都加了引号（中文、空格、数字开头、关键字）。
- [ ] `retain` 的方向正确：input = 来源保留；output = 目标补到。
- [ ] `output N to b` 与 `to each b`、`input N from a` 与 `from each a` 的区别符合意图。
- [ ] 分步：先放入再取出的地方有 `forget` 或拆成两个触发器。

**条件**
- [ ] `has` 后有比较符与数量；比较符是 `> < = <= >=`（或 gt lt eq le ge）。
- [ ] 复合条件加了括号。
- [ ] 状态类的连续 `if` 用了 `else if` 链，避免同一次执行里连跳多个状态。

**简化与性能**
- [ ] 已按 2.4 逐条简化，没有可以用 `retain` / 输出顺序 / 拆触发器代替的 `if`。
- [ ] 命中 2.5 任一条时，写了【性能提示】。
- [ ] 每种产物和副产物都有足够的接收槽/罐；已核对满仓时停机还是丢弃资源。需要保留的产物不进垃圾桶，只有用户允许丢弃的副产物才设销毁出口。

**游戏数据**
- [ ] 目标产物、配方链已由用户确认（或用户明确要求"直接生成"）；没有自己替用户选目标。
- [ ] 代码里的每个资源 ID 都来自用户确认或有出处的资料；能用专用容器、专用面避开 ID 的地方已经避开。
- [ ] 来自记忆、未核实的内容都已标注"未核实"，并附了验证方法。

**交付内容**
- [ ] 附了标签清单（标签 → 方块 → 面），并写明了一次性手动设置（侧面配置、自动弹出、编程电路、供应器锁定与产物回流路径等）。
- [ ] 需求涉及 SFM 做不到的事（第 0 节表格）时，已明确说明并给出替代方案。
- [ ] 说明了版本依赖的特性（`without`、`or`、`empty slots in`、相对方向、`offset by`）。
- [ ] 堆量工厂：核对了接收槽/罐容量、机器选项和满仓行为等效率风险（读过 `efficiency.md`）。
- [ ] 提醒用户编译后查看磁盘警告；出问题按 `troubleshooting.md` 的排错流程检查。

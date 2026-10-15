# 排错：常见错误、编译错误与磁盘警告

## 常见错误对照表

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
| 20 | `forget` 缺失，原料绕过机器直接到产物箱 | 语义错 | 见 SKILL.md 第 5 节三种方案 |
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
| 34 | 两种同类型资源（如两种气体）分别送进同一机器的不同面，中间没 `forget` 且只写了 `gas::` | 语义错 | 第二个 output 会把第一种也送进去；两组之间 `forget`，或写精确资源 ID |
| 35 | 用多个独立 `if` 写状态机，同一次执行里状态连跳 | 语义错 | `has` 读的是实时库存；改成 `if … else if … end` 链 |
| 36 | 多产物机器只给主产物设了出口，副产物（尤其流体）积满后整台机器停工 | 语义错 | 每种产物都要有出口；可丢弃的副产物用"先主罐、后垃圾桶"的输出顺序做溢出 |
| 37 | `if each "储罐" >= 1000 fluid:: then`（漏了 `has`）或用全角 `＞` | 语法错 | `if each "储罐" has >= 1000 fluid:: then`；比较符必须是半角 |
| 38 | 为了"保险"到处用 `each side` 和每刻/高频触发 | 能运行但卡顿 | 写具体面、降低频率；见 `efficiency.md`"性能提示" |

## 编译错误与磁盘警告速查

磁盘上的警告会在管理器界面显示；**警告按钮：点击可复制含警告的代码，Shift+点击尝试自动修复警告**。磁盘最多保留 10 条问题（配置 `maxDiskProblems`）。

## 编译错误

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

## 警告（程序能运行，但可能不对）

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

## 排错流程（"不工作"时按顺序检查）

1. **看磁盘警告**（见上方"编译错误与磁盘警告速查"）。没有任何警告 ≠ 没问题，但有警告一定先处理。
2. **标签**：是否已**推送**到磁盘？标签是否贴对了方块、对了面？（网络工具/标签枪渲染可视化）
3. **线缆**：手持网络工具看管理器、线缆、标签是否在同一网络；方块是否**挨着线缆**；管理器界面点"重建线缆网络"；仍不行用 `/sfm bust_cable_network_cache`。
4. **面与槽位**：用网络工具右击目标方块的某个面，看该面开放哪些能力；Ctrl+I 看槽位（注意 GUI 槽位 ≠ 自动化槽位）；Mekanism 机器检查侧面配置。
5. **资源类型配对**：`input` 与 `output` 的 `resourceid` 类型是否一致；流体/能量/化学品是否写了 `::` 和 `side`。
6. **触发器**：间隔是否合适？用 `global` 对齐？重新载入世界后内部时钟会随机初始化，相位会变。
7. **时序**：是否需要 `forget`？是否被前面的 `input` 残留干扰？
8. **数量限制与满仓**：`retain`/`number` 是否限制过严？目标是否已满？机器是否被某种没有出口的副产物（尤其流体、气体）堵住？
9. **日志**：管理器界面的**日志(Logs)**屏，可选 OFF/TRACE/DEBUG/INFO/WARN/ERROR；TRACE/DEBUG 会在执行一次后自动关闭（防卡顿）。
10. **已知问题**：管理器偶尔无故停止工作 → "重建线缆网络"按钮或 `/sfm bust_cable_network_cache`；对堆肥桶不写面输出会跳过可堆肥检查，等于把它变成垃圾桶。
11. **提交 bug**：给出 Minecraft/加载器/SFM 版本、整合包、程序、标签与面、复现步骤、日志。官方问题追踪见 `config-and-versions.md` 的"资料来源"。

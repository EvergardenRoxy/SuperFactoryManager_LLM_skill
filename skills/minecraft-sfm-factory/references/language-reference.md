# SFML 完整语言参考

> SKILL.md 第 4 节是速查版；本文件是完整版，含全部子句细节、语义对照表与示例。
> 记号：`[ ]` 可选；`< >` 必填；`*` 可重复（逗号分隔）；`|` 二选一。

## 词法规则

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

## 程序结构

```text
[name "程序名"]          ← 只能是第一行代码
every ... do ... end     ← 一个或多个触发器
every ... do ... end
```

- `name` 可省略；写了，磁盘名称会变成该字符串。
- **除 `name` 和 `every` 外，所有语句只能出现在触发器里。**
- 多个触发器彼此独立；每个触发器结束后自动忘记它登记的输入。

## 触发器

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

## input / output 总语法

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
3. **`,` 用来分隔多个"限制"**，也用来分隔多个标签和多个面——别把它们混淆（见下方"数量、保留、each"一节的陷阱）。
4. 语句可以颠倒顺序写成 `from a input ...` / `to b output ...`，**不推荐**。
5. 没有任何限制时：`input from a` = 登记 a 里所有**物品**；`output to b` = 尽可能放入 b。

```sfml
-- 最小例子：把 a 的所有物品搬到 b
every 20 ticks do
    input from a
    output to b
end
```

## 资源 ID（resourceid）

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
| `redstone` | 红石信号（世界方块**只读**）/ 实验性缓冲器里的计数 | | 4.27.0+，见下方"红石"一节 |

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

> ⚠ **不要用 `"[^(iron_ingot)].*"` 来"排除铁锭"**：`[^...]` 是"排除这些**字符**开头"，会误排除以 i/r/o/n/_/g/t 开头的所有物品。要排除某物，用 `except iron_ingot`（见下方"except"一节）或 `"(?!iron_ingot$).+"`。
> 正则里**不要出现 `:`**（`:` 是资源 ID 的段分隔符）。需要 `(?:...)` 时用 `(...)` 代替。

获取容器里真实存在的 resourceid：用网络工具、Ctrl+I，或光标移到该处按 Ctrl+Space。

## 数量（number）、保留（retain）、each

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

## with / without（按 tag 过滤，4.19.0+；`without` 4.20.0+ 才可靠）

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

## except（排除）

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

## 标签访问：each、round robin、side、slots、empty slots

### `each`（逐个方块）

| 写法 | 含义 |
|---|---|
| `input 5 from c` | 把所有 `c` 方块当作一个整体，总共输入 5 个 |
| `input 5 from each c` | **每个** `c` 方块各输入 5 个 |
| `output 1 to b` | 所有 `b` 里**只有一个**方块收到 1 个 |
| `output 1 to each b` | **每个** `b` 方块各收到 1 个 |
| `output retain 2 to each b` | 每个 b 补到有 2 个 |

> 不要把 `from each`（逐方块）和数字后的 `each`（逐资源种类）搞混。

### round robin（轮询，4.14.0+）

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

### side（面）

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

### slots（槽位）

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

### empty slots in（4.25.0+，**仅 output**）

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

## forget（遗忘输入）

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

## if / else if / else

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

### 条件表达式

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

## 红石

三种不同的东西，**不要混淆**：

| 写法 | 含义 | 版本 |
|---|---|---|
| `every redstone pulse do … end` | 红石脉冲触发器（管理器收到脉冲）；不受最小间隔限制 | 长期支持 |
| `if redstone [<比较符> <数>] then` | 判断**管理器自身**收到的红石强度 | 长期支持 |
| `if abc [<面> side] has <比较符> <数> redstone:: then` | 读取**被标签方块**发出的红石信号（杠杆、比较器、红石块等），只读 | 4.27.0+ |
| `redstone`（物品）| 红石粉**物品**，与上面完全无关 | |

- 物品红石粉：`input redstone from a`（4.14.0+ 不加引号也可），或更稳妥地写 `item:minecraft:redstone` / `"minecraft:redstone"`。
- `redstone::`（红石信号资源）：读取的是**方块发出的弱信号 0–15**，不是输入进来的信号；不加面时取六个面的最强值；加 `east side` 则取该面。它**只读**，不能 `output` 到世界方块里。
- 实验性"缓冲器"（`sfm:buffer`，开发期方块）可存红石计数，用 `input 1 redstone:: from donor` / `output redstone:: to counter` 搬运，比较器读数为 `min(存量, 15)`。普通玩家基本用不到。
- 现代版本均支持以上红石功能，**不需要先询问用户版本**；只有用户明确使用很旧的版本（< 4.27.0）且编译报 `unknown resource type "redstone"` 时，才改用 `if redstone` 或建议升级。
- 用红石时钟驱动 `every redstone pulse` 可以突破 20 刻的最小间隔，但频率越高开销越大，见 `advanced-patterns.md`"红石时钟提速"。
- 隧道式管理器**不传红石**。

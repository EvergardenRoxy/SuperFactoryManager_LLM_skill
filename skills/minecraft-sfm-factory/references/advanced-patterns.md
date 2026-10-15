# 进阶模式

> ⚠️ 本文件的模式都比普通搬运复杂。**使用前先确认 SKILL.md 2.4 的简化手段确实解决不了问题**；用了以后，交付时必须附【性能提示】（SKILL.md 2.5）。
> 资源 ID（尤其是模组物品、气体）请让用户用 Ctrl+Space 或 F3+H 确认，示例中的 ID 仅供参考。

## 先试更简单的办法

| 需求 | 先试 | 实在不行再用 |
|---|---|---|
| 每台机器只放一份原料 | `output retain N to each 机器` | 计数寄存器 |
| 主材必须最后放入 | AE 样板供应器阻挡模式 + 按槽位分发（见"AE 样板供应器配合"） | 状态机 |
| 多段加工链 | 一个触发器内分段 + `forget`（见"多段加工链"） | — |
| 仓库满了不要卡死 | output 先后顺序做溢出（见"防满仓卡死"） | `if` 判断 |
| 想比 20 刻更快 | 先确认瓶颈真的是间隔，而不是输出口或机器速度 | 红石时钟 + `every redstone pulse` |

---

## 计数寄存器：用槽位里的物品数存一个小整数

SFML 没有变量。需要记住"现在进行到第几步""已经放了几个"时，可以用容器某个槽位里的**物品数量**当变量：

| 角色 | 建议 | 说明 |
|---|---|---|
| 寄存器 | 原版木桶，单独一个标签 | 每个槽位存一个 0–64 的整数（16 堆叠物品只到 16）；**不要**让其他程序或漏斗往里放东西 |
| 令牌源 | 装满一种廉价原版物品（如圆石）的箱子 | 加 1 就从这里取 1 个；清零时把令牌还回这里，不需要垃圾桶 |

```sfml-snippet
-- 读：判断寄存器槽 0 的值
if state slots 0 has = 2 then
    input from a
    output to b
end

-- 加 1
input 1 from tokens
output 1 to state slots 0
forget

-- 清零：令牌还回令牌源
input from state slots 0
output to tokens
forget
```

要点：
- `has` 读的是**当时的真实库存**。同一次执行里先把值改成 1，紧接着的 `if state slots 0 has = 1` 会立刻成立，状态会"连跳"。用 `if … else if … end` 链保证每次执行只走一个分支。
- 寄存器标签只贴一个方块。贴了多个时，`has` 默认把它们**加总**比较，值就乱了。
- 不建议用模组容器或模组物品当寄存器，堆叠规则和自动化槽位可能和预期不同。

## 状态机：多步骤、有顺序要求的合成

适用：仪式/多方块合成要求"辅料先放好、主材最后放、等产物出现后再收"，而且用 AE 阻挡模式也解决不了时。

```sfml
name "单主材多合一"
-- 寄存器 state 槽 0 的值（每轮只走一个分支）：
--   0 = 空闲：给每个基座放 1 个辅料，辅料发完后进入 1
--   1 = 辅料就位：放入 1 个主材，进入 2
--   2 = 合成中：产物出现后收走，回到 0
every 40 ticks do
    if state slots 0 has = 0 then
        input from "辅料"
        output 1 to empty slots in each "基座"
        forget
        if "辅料" has = 0 then
            input 1 from tokens
            output 1 to state slots 0
            forget
        end
    else if state slots 0 has = 1 then
        if "主材" has > 0 then
            input 1 from "主材"
            output 1 to "核心"
            forget
            input 1 from tokens
            output 1 to state slots 0
            forget
        end
    else if state slots 0 has = 2 then
        if "产物" has > 0 then
            input from "产物"
            output to "成品"
            forget
            input from state slots 0
            output to tokens
            forget
        end
    end
end
```

写状态机的习惯：
- **在程序开头用注释列出所有状态的含义**，SFML 没有函数，注释是唯一的文档。
- 每个状态只做一件事，转移条件写在该状态的分支末尾。
- 间隔不要太短：合成需要时间，用 40 刻以上即可。
- 给用户说明**卡住时如何手动复位**：清空寄存器（把令牌拿回令牌源）就回到状态 0。

## 多段加工链：一个触发器里的流水线

适用：Mekanism 等化学链（原料 → 机器 A → 中间产物 → 机器 B → 产物）。每一段 input → output → `forget`，互不干扰：

```sfml
every 20 ticks do
    -- 第 1 段：硫粉送进化学氧化机
    input mekanism:dust_sulfur from "原料" top side
    output to each "氧化机" top side
    forget

    -- 第 2 段：两种气体送进化学灌注机的不同面，用精确 ID 区分，避免串面
    input gas:mekanism:oxygen from "氧气" top side
    output gas:mekanism:oxygen to each "灌注机" left side
    input gas:mekanism:sulfur_dioxide from each "氧化机" right side
    output gas:mekanism:sulfur_dioxide to each "灌注机" right side
    forget

    -- 第 3 段：收集产物
    input gas:: from each "灌注机" back side
    output gas:: to "产物罐" top side
end
```

要点：
- **同一台机器的不同面放同类型资源时**（如两种气体），要么写精确资源 ID（如上），要么两组之间 `forget`。只写 `gas::` 又不 `forget`，第二个 output 会把第一种气体也送到第二个面。
- 示例用了相对方向 `left/right/back`（4.27.0+），机器朝向不同时不用改代码；更早的版本改成绝对方向。
- 机器的面向和侧面配置必须和程序一致，写进标签清单；Mekanism 可用配置卡批量复制侧面配置。
- 链条很长时，可以按段拆成几个触发器，并错开偏移（如 `every 20 ticks offset by 5 ticks`），避免所有工作挤在同一刻。

## AE 样板供应器配合：按槽位分发

适用：多输入配方（仪式、祭坛、注魔台、组装台）。让 AE 样板供应器把一份配方推进**缓存箱**，再由 SFM 按槽位分发。样板供应器开启**阻挡模式**，产物回来前不会推下一份，所以**不需要状态机**。

样板里把**主材排在第一位**，它就会落在缓存箱槽 0：

```sfml
every 20 ticks do
    -- 槽 1 以后是辅料：每个基座放 1 个
    input from "缓存" slots 1-26
    output 1 to empty slots in each "基座"
    forget

    -- 辅料都发完了，才把槽 0 的主材放进核心
    if "缓存" slots 1-26 has = 0 then
        input from "缓存" slots 0
        output to "核心"
        forget
    end

    -- 产物送回 AE
    input from "产物"
    output to "AE接口" top side
end
```

要点：
- 产物必须回到 AE，阻挡才会解除；没有实体产物的配方（如召唤生物），需要在样板里换成一个能回收的标记物品。
- 如果对时序要求不高，可以去掉 `if`，直接分别把槽 0 送核心、其余槽送基座，更省。

## 防满仓卡死：每种产物都要有去处

机器的输出槽、输出罐被**任意一种**产物占满，整台机器就会停工。多产物、尤其多流体或多气体的机器最容易出问题。

规则：
1. **每种产物都要有出口**：输出口数量 ≥ 产物种类数（`efficiency.md` 有实测数据）。
2. **会积压的副产物要有溢出口**：利用 output 的先后顺序，主仓放不下的才进入溢出口，不需要 `if`。
3. 溢出口可以是垃圾桶（会**销毁**资源，只用于可以丢弃的副产物）、无上限存储，或带溢出销毁卡的 AE 存储元件。

```sfml
every 20 ticks do
    -- 主产物：先进主罐，满了才进垃圾桶
    input fluid::honey from each "离心机" top side
    output fluid::honey to "蜂蜜罐" top side
    output fluid::honey to "流体垃圾桶" top side
    forget

    -- 其他副产物流体：同理
    input fluid:: from each "离心机" top side
    output fluid:: to "副产物罐" top side
    output fluid:: to "流体垃圾桶" top side
end
```

另一种更简单的做法：**按产物种类把机器分组**，每组只处理一种会产生特定流体的原料，就不会出现"错误流体占住输出罐"的情况。

## 红石时钟提速

`every redstone pulse` 不受 20 刻最小间隔限制。用红石时钟（例如侦测器 + 粘性活塞的快速时钟）给管理器供脉冲，可以让物品搬运更频繁：

```sfml
every redstone pulse do
    input from "原料" top side
    output retain 16 to each "机器" top side
    forget
    input from each "机器" bottom side
    output to "产物" top side
end
```

要点：
- **先确认瓶颈真的是间隔**：多数"太慢"其实是输出口不够、机器数量不够或机器本身速度慢。
- 时钟频率调到**刚好够用**：只要机器的输入不断供、输出不堆满即可，不追求最快。
- 脉冲触发器的开销与频率成正比，**必须写【性能提示】**。也可以加一个拉杆控制时钟，需要时才开。
- 隧道式管理器不传红石，时钟要直接接到普通管理器上。

# 进阶模式

> ⚠️ 本文件的模式都比普通搬运复杂。**使用前先确认 SKILL.md 2.4 的简化手段确实解决不了问题**；用了以后，交付时必须附【性能提示】（SKILL.md 2.5）。
> 资源 ID（尤其是模组物品、气体）请让用户用 Ctrl+Space 或 F3+H 确认，示例中的 ID 仅供参考。

**目录**：先试更简单的办法 · 计数寄存器：用槽位里的物品数存一个小整数 · 状态机：多步骤、有顺序要求的合成 · 多段加工链：一个触发器里的流水线 · AE 样板供应器配合：按槽位分发 · 防满仓卡死：每种产物都要有去处 · 红石时钟提速 · 自循环增产（社区经验） · 蓄能后定量放电 · 事件驱动：用管理器收到的红石信号 · 间接输出红石信号：容器 + 比较器

## 先试更简单的办法

| 需求 | 先试 | 实在不行再用 |
|---|---|---|
| 每台机器只放一份原料 | `output retain N to each 机器` | 计数寄存器 |
| 主材必须最后放入 | AE 样板供应器等待结果锁定 + 按槽位分发（见"AE 样板供应器配合"） | 状态机 |
| 多段加工链 | 一个触发器内分段 + `forget`（见"多段加工链"） | — |
| 仓库满了不要卡死 | output 先后顺序做溢出（见"防满仓卡死"） | `if` 判断 |
| 想比 20 刻更快 | 先确认瓶颈真的是间隔，而不是输出口或机器速度 | 红石时钟 + `every redstone pulse` |
| 机器完成某事后立刻响应 | 加大定时间隔、容忍延迟 | 机器比较器信号接管理器 + `every redstone pulse`（见"事件驱动"） |
| 想让 SFM 开关红石电路 | 用 `redstone::` 读信号、让红石电路自己处理 | 容器 + 比较器间接输出（见"间接输出红石信号"） |

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
- **一个木桶就是多个变量**：不同槽位存不同的状态（例如槽 0 = 主流程状态，槽 1 = 能量缓冲状态）。两个子系统各自推进自己的槽位，需要协调时读取对方的槽位（`if state slots 0 has = 1 and state slots 1 has = 2 then`）。在程序开头注释里写清每个槽位的含义。

## 状态机：多步骤、有顺序要求的合成

适用：仪式/多方块合成要求"辅料先放好、主材最后放、等产物出现后再收"，而且用 AE 等待结果锁定也解决不了时。

前提：只控制一个工位；每个基座只有一个可用物品槽、容量为 1，所有标签已绑定、接线且无相关警告，基座集合非空；配方不要求特定基座位置，辅料箱只装一批已核对的完整配方；核心只有一个可用主材槽，开始时为空，产物在独立库存。tokens 至少有 2 个令牌且可接收回流。先验证核心物品插入后不会在同一次 SFML 执行期间消失；不符合时改用设备完成信号，不能直接套这个状态机。

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
        if ("辅料" has = 0) and (every "基座" has = 1) then
            input 1 from tokens
            output 1 to state slots 0
            forget
        end
    else if state slots 0 has = 1 then
        if "核心" has = 0 then
            input 1 from "主材"
            output 1 to "核心"
            forget
        end
        -- 只有目标实际收到主材，才补到状态 2；失败后可重试
        if "核心" has = 1 then
            input 2 from tokens
            output retain 2 to state slots 0
            forget
        end
    else if state slots 0 has = 2 then
        if "产物" has > 0 then
            input from "产物"
            output to "成品"
            forget
            if "产物" has = 0 then
                input from state slots 0
                output to tokens
                forget
            end
        end
    end
end
```

写状态机的习惯：
- **在程序开头用注释列出所有状态的含义**，SFML 没有函数，注释是唯一的文档。
- 每个状态只做一件事，转移条件写在该状态的分支末尾。
- 间隔不要太短：合成需要时间，用 40 刻以上即可。
- 给用户说明**卡住时如何手动复位**：先暂停，检查核心/基座/产物库存，恢复成一批完整配方的初始状态，再清空寄存器；仅清令牌可能把新旧批次混在一起。

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

适用：单工位、每个基座容量 1、核心仅接收 1 个主材且不要求特定基座位置的多输入配方。所有标签须已绑定并连线，基座集合非空且启动时无剩料。缓存使用独占空箱，只允许一个样板供应器写入。**普通 Blocking Mode 只检查相邻容器是否仍有配方输入**；SFM 搬空缓存后就可能接收下一批。严格串行应设置 **Lock Crafting → Until primary crafting result is returned**，并让主产物经过**同一个样板供应器的返回库存**，普通 ME 接口不能替代这个回流路径。没有该设置的版本须另设完成信号或状态机。

样板每次发送完整的一份配方，主材数量为 1 且排第一。空箱通常会将其放到槽 0，但替代物、合并堆叠或其他管道可能改变槽位；先单次投料实测槽 0 为主材、1–26 为辅料，确认后再用下例。基座数量必须与该配方辅料总件数一致，不能混用不同配方的剩料。

```sfml
every 20 ticks do
    input from "缓存" slots 1-26
    output 1 to empty slots in each "基座"
    forget

    -- 来源已发完且每个基座实际收到 1 件，才投放主材
    if ("缓存" slots 1-26 has = 0) and (every "基座" has = 1) then
        input 1 from "缓存" slots 0
        output 1 to "核心"
        forget
    end

    -- “产物”只暴露成品；回到发送这一批的同一个供应器
    input from "产物"
    output to "样板供应器" top side
end
```

- 标签：缓存=独占箱；基座=这一工位的全部基座；核心=单个主材接收器；产物=仅含成品的输出库存；样板供应器=发送本批配方的供应器。按网络工具确认面和槽位。
- 神秘农业 1.21 祭坛需要红石激活，给**祭坛**接常亮信号；管理器开关不会自动激活祭坛。其输出槽可用作“产物”，须按能力检查槽位；不以所有物品作为回收过滤。非种子配方不能用 seeds tag 判断完成。
- 没有实体产物的任务需要能反映真实完成的信号。只有机器实际产出或回收了标记物，才可在样板中把它列为结果，不能凭空声明一个结果来解锁。

### 多工位并行（堆叠）

**每个工位独立一组缓存/基座/核心/产物/供应器标签**，复制上面程序并替换标签，例如缓存1、基座1、核心1、产物1、供应器1；工位2使用对应的另一组。每个供应器发送一份完整配方，产物回到自己的供应器。

不要把多个祭坛的所有基座合到一个标签，再仅靠“样板倍数=工位数”分料。两工位各需 A×4+B×4 时，A×8 可能先占满第一个工位的 8 个基座，B×8 再占满第二个；总量正确仍都无法合成。`to each` 不建立工位关系。只有已按材料角色建立专用标签并验证每工位齐料时，才考虑共享批次。

可用 `global` 对齐节奏；慢配方使用 100 刻左右的轮询，锁定由实际产物回流解除。

## 防满仓卡死：每种产物都要有去处

先核对具体机器满仓时的行为：有些停工，有些继续加工并丢弃装不下的产物。Productive Bees 的核对分支会继续加工且忽略未装入的流体余量，不能依靠“停机”判断没有损失（版本与来源见 `mod-notes.md`）。

规则：
1. **每种产物都要有可用接收空间**：看槽/罐容量、过滤与吞吐，不按出口方块数推导资源种类数（见 `efficiency.md`）。
2. **可丢弃的副产物可设溢出口**：利用 output 的先后顺序，主仓放不下的才进入溢出口，不需要 `if`。
3. 溢出口可以是垃圾桶（会**销毁**资源，只用于可以丢弃的副产物）、无上限存储，或带溢出销毁卡的 AE 存储元件。

```sfml
every 20 ticks do
    -- 前提：用户允许丢弃蜂蜜；需要保留时删去垃圾桶输出并设计停机条件
    input fluid::honey from each "离心机" top side
    output fluid::honey to "蜂蜜罐" top side
    output fluid::honey to "流体垃圾桶" top side
    forget

    -- 前提：其余所有匹配流体也允许丢弃；否则逐种筛选，不要用全匹配销毁
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

## 自循环增产（社区经验）

适用：产物又是原料的循环生产，例如"水晶 → 粉碎 → 粉 → 生长/反应 → 更多水晶"。SFM 能同时看到多个容器的库存，并按 `retain` 精确地给每台机器配料，是做这类循环的好工具。

```sfml
-- 供水（只有流体，单独一个触发器）
every 20 ticks do
    input fluid:: from "水" top side
    output fluid:: to each "反应仓" bottom side
end

every 40 ticks do
    -- 1. 水晶 → 粉碎机：粉库存不足时才补，避免把种子全部磨掉
    input from "水晶库"
    if "粉库" has < 256 ae2:certus_quartz_dust then
        output retain 16 ae2:certus_quartz_crystal to each "粉碎机" bottom side
    end
    forget

    -- 2. 粉碎产物 → 粉库 → 反应仓
    input from each "粉碎机" bottom side
    output to "粉库"
    forget
    input from "粉库"
    output retain 16 ae2:certus_quartz_dust to each "反应仓" bottom side
    forget

    -- 3. 反应仓产物回到水晶库，形成循环；水晶库满了再送进 AE
    input from each "反应仓" bottom side slots 9
    output to "水晶库"
    output to "AE接口" top side
end
```

经验要点：
- **启动物料（种子）要够**：至少覆盖所有机器 `retain` 的总量，再留余量。种子太少时，物料分散在各台机器里都不够开工，循环会卡死。之后要持续补充被产出消耗掉的物料。
- **这里的 `if` 是必要的**：它决定"多少水晶拿去磨粉、多少留作种子"，`retain` 做不到这种跨容器的分流。
- **机器按比例堆量**：先算清各环节速度比，再按比例增加机器；一个环节过剩，另一个就会空转。
- **侧面配置交给 SFM**：Mekanism 工厂类机器建议只开放一个面（如底部）做物品输入输出，其他面禁用，并关闭自动弹出，搬运全部由 SFM 完成。Mekanism 标准加工输入槽限制外部抽取；先核对具体机器的槽位和过滤，符合时，所以同一个面既输入又输出不会把原料抽回来。
- **产物槽号因机器而异**（示例中的 `slots 9` 仅作示意），用 Ctrl+I 或网络工具确认。
- **耗电提醒**：循环生产通常耗电很高，且波动大，交付时提醒用户确认供电。

## 蓄能后定量放电

前提：单个缓冲电池、单个 FE 设备；确认设备能接收本次所需数量，且两端能力没有更低的单次传输上限。下例每次**红石上升沿**尝试发送至多 1,000,000 FE，库存不足时不发送。就绪信号长亮不会重复放电；充够后需要新的上升沿。SFML 不能保证目标原子地接收全部数量，目标拒收或部分接收时须按设备库存/完成信号另设恢复流程。

```sfml
every tick do
    input fe:: from "电网" top side
    output retain 1000000 fe:: to "缓冲电池" top side
end

every redstone pulse do
    if "缓冲电池" bottom side has >= 1000000 fe:: then
        input 1000000 fe:: from "缓冲电池" bottom side
        output 1000000 fe:: to "设备" bottom side
    end
end
```

阈值和上限按实际需求一起修改。该模板只适用于支持 FE 的设备；Oritech 加速器应按速度传感器和电机供电设计，Ars Nouveau 的 Source 也不是 FE。

## 事件驱动：用管理器收到的红石信号

定时触发器只能"每隔一段时间看一眼"。如果机器能在完成某事时输出红石（比较器、侦测器、机器自带的信号输出），把信号接到管理器上，用脉冲触发器立刻响应：

```sfml
-- 例行工作：定时
every 40 ticks do
    input from "原料"
    output retain 4 to each "机器" top side
end

-- 事件：机器完成时立刻取走产物
every redstone pulse do
    if redstone = 15 then
        input from each "机器" bottom side
        output to "产物"
    end
end
```

要点：
- `if redstone` 读的是**管理器自身**收到的信号强度，可以用不同强度区分不同事件。
- 脉冲触发器只在事件发生时执行，比高频定时器更省；但事件非常频繁时同样需要【性能提示】。

## 间接输出红石信号：容器 + 比较器

SFM 不能直接发出红石信号，但可以**改变容器里的物品数量**，由比较器读出信号，从而控制红石电路（开关机器、切换轨道、驱动活塞等）。

```sfml
every 20 ticks do
    -- 产物箱快满时打开信号（例如让上游机器停工），否则关闭
    if "产物" has >= 1000 then
        input from tokens
        output retain 1 to "信号箱"
        forget
    else
        input from "信号箱"
        output to tokens
    end
end
```

要点：
- 比较器信号由容器"装满程度"决定（原版公式）：**信号 = ⌊1 + 14 × (各槽 物品数/最大堆叠 之和) / 槽位数⌋**，容器非空时至少为 1，空时为 0。
- 只需要开/关：放 1 个物品就够了（信号 1，必要时用中继器放大）。
- 需要**精确的信号强度**（例如用 1–15 选择不同轨道或配方）：用槽位少的容器（漏斗 5 格、投掷器 9 格），按上面的公式算出需要的物品数，用 `output retain N` 精确放入。漏斗会自己移动物品，需要用红石锁住或换成投掷器。
- 搭配 `redstone::` 读取（4.27.0+）或管理器自身的红石输入，可以组成"SFM 写信号 → 红石电路 → 机器 → 信号回到 SFM"的闭环，替代大量手搭的红石逻辑。

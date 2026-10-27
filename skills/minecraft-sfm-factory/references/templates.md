# SFM 程序模板库

> 全部 `sfml` 代码块均已通过官方 `SFML.g4` 语法校验。按场景挑选最接近的模板改写，不要原样照抄标签名。
> 更复杂的模式（状态机、按槽位分发、自循环、红石控制）见 `advanced-patterns.md`；各模组的注意事项见 `mod-notes.md`。

使用前为选中的模板填写适用条件，未知项先在游戏内核对：

| 条件 | 必须写明 |
|---|---|
| 版本 | MC、加载器、SFM、目标模组及兼容附属模组版本 |
| 接口 | 标签绑定对象、具体面、自动化槽位、配方输入/产物过滤 |
| 机器选项 | 侧面分离、输入缓冲/锁槽、印模/电路、自动输出、循环处理增幅 |
| 资源与恢复 | 能源类型、满仓停机或丢弃行为、缺料/断电/重载恢复方式 |

| 场景 | 模板 |
|---|---|
| A 搬到 B、只搬某些物品、限量 | 基础搬运；只搬指定物品 / 限量 |
| 按种类分到不同箱子、主仓满了进备用仓 | 分拣到不同箱子；溢出保护 |
| 熔炉、机器阵列补原料、取产物 | 熔炉阵列；熔炉：不同面放不同东西；机器阵列；大批量机器的两步流程 |
| 能量、流体、化学品 | 能量、流体、化学品 |
| 按库存或红石控制开关 | 按库存条件触发；红石脉冲触发；整条产线总开关 |
| 完整产线实例 | 有机灌注器阵列；AE2 压印器；Mek 聚变反应堆 |

## 基础搬运

```sfml
name "move items"
every 20 ticks do
    input from a
    output to b
end
```

## 只搬指定物品 / 限量

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

## 分拣到不同箱子

```sfml
every 20 ticks do
    input from a
    output with #ores to ores_chest
    output *_ingot to ingots_chest
    output to others                           -- 剩下的都进这里
end
```

> 前面的 output 先"吃掉"属于它的物品，后面的 output 处理剩余。

## 熔炉阵列（来自官方模板 Furnace Manager）

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

## 熔炉：不同面放不同东西（来自官方示例 smelting）

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

## 能量、流体、化学品

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
    input fluid::water from source top side
    output retain 1000 fluid::water to each thingy top side
end

-- 通用机械：气体（不同 MC 版本里 gas:: 都可用）
every 20 ticks do
    input gas:mekanism:nuclear_waste from "裂变反应堆" each side
    output gas:: to "同位素离心机" each side
end
```

## 机器阵列：给每台机器补原料

```sfml
every 20 ticks do
    input from "原料箱"
    output retain 8 to each "机器" top side     -- 每台机器补到 8 个
end
```

## 溢出保护（主仓库满了再进备用箱）

```sfml
every 20 ticks do
    input from "产物"
    output to "主仓库"
    output to "备用仓库"                        -- 主仓库放不下的才会进这里
end
```

## 按库存条件触发

```sfml
every 20 ticks do
    if "成品箱" has < 1000 iron_ingot then
        input from "原料箱"
        output to "机器" top side
    end
end
```

## 红石脉冲触发（用杠杆/按钮手动控制）

```sfml
every redstone pulse do
    input from a
    output to b
end
```

## 整条产线总开关

在管理器上接一个拉杆，打开时整条产线运行，关闭时全部暂停，方便排查和维护。只多一个 `if`，不算复杂逻辑：

```sfml
every 20 ticks do
    if redstone > 0 then
        input from "原料" top side
        output retain 16 to each "机器" top side
        forget
        input from each "机器" bottom side
        output to "产物" top side
    end
end
```

> 能量触发器通常不需要放进总开关：机器没有原料时本来就不耗电。

## 有机灌注器阵列（热力 + 神秘农业，用户提供）

适用基线为 Thermal 1.20.x，配方与增幅按用户环境核对。能量/水/肥料/种子/产物分别配置能力；将所有机器的**顶部**按资源类型设为输入/输出面，使用 Ctrl+右击快速标记所有有机灌注器；合成仓配种子到 `"input"`，物品接口提供肥料并接收产物；`energy` 是能量立方等供能元件；`water` 是流体储罐。

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

## AE2 压印器（官方模板）

适用前提：先核对 AE2 版本、侧面分离设置及槽位映射。示例中的无面访问使用内部库存，不等于有方向的自动化库存；不能把同一槽号直接移到 `top side` 等面。现代版本可先调小机器输入缓冲；印模应预先装好，自动输出按设计统一。

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

## Mek 聚变反应堆自适应燃料速率（社区示例）

以下是**待游戏内验证的社区实验程序，不是可直接交付的反应堆供料方案**；数值是该程序的分档设计，不是所有版本的燃烧速率上限。聚变反应堆可直接通入氘氚燃料。用终极化学品储罐存燃料，设计目标：储罐有 8,192,000 mB 时达到 1000 mB/t，**速率与存量成正比**。燃料消耗按游戏刻执行，烧不到燃料会停止燃烧。**1 tick 脉冲宽度不等于每 tick 一个上升沿**，不能仅靠侦测器时钟保证持续供料；必须实测每刻供料、库存、温度和燃烧状态。程序按存量分档：先向反应堆端口输出对应速率，再把对应存量转存到临时储罐 `temp`，最后 `forget` 并把 `temp` 内燃料放回主储罐。

> ⚠️ 本模板在红石脉冲触发器里有 11 个 `if`，属于复杂程序（SKILL.md 2.5）：交付时必须附【性能提示】，并说明脉冲频率越高开销越大；固定供料优先使用已验证的连续化学品输送方案；`output retain` 控制库存，不等同于每刻燃烧速率。临时罐容量、回流失败及重载恢复也必须验证。

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

## 大批量机器的两步流程（放入原料 → 取出产物）

```sfml
every 20 ticks do
    input from "原料" bottom side
    output retain 16 to each "机器" top side     -- 每台机器至多补到 16 个，避免先到先得
    forget
    input from "机器" bottom side
    output to "输出A" bottom side
end
```

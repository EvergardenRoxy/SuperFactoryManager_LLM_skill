# SFM 技能仓库：模组行为核对与改进建议

审查日期：2026-10-27（Asia/Seoul）
仓库基线：2ff5bc6c9b2d6f74de1ef068dd0f25472a33f133

本次对照官方源码和维护者文档审查机器接口、资源标识、配方投放、库存与能量行为。主要核对 MC 1.21/1.21.1 对应分支；Thermal 对照其 1.20.x 分支，GTCEu Modern 对照 1.20.1 分支。分支名不等于某个已发布模组版本，结论不能无条件外推到所有历史版本或魔改包。

没有运行 Minecraft 集成测试。下文明确区分源码确认、控制流反例和待实测项。本提交保存审查结果，技能正文和模板中的修正建议尚未实施。

[来源清单与文件哈希](mod-audit-sources.json)记录了本次核对的 41 份上游文件。

## 1. 优先修正的问题

### 1.1 AE2：阻挡模式、合成锁定和产物回流路径被混为一谈

位置：[skills/minecraft-sfm-factory/references/advanced-patterns.md](../skills/minecraft-sfm-factory/references/advanced-patterns.md#L135)；[skills/minecraft-sfm-factory/references/mod-notes.md](../skills/minecraft-sfm-factory/references/mod-notes.md#L27)。

**源码确认：**普通 Blocking Mode 在相邻目标包含样板输入时阻挡再次投料。SFM 清空缓存箱后，该条件即可能解除，不需要等待上一批完成。独立的 LOCK_UNTIL_RESULT 模式才记录主产物并等待返回。

等待结果模式还要求主产物经过**原来的样板供应器**返回。模板的“产物 → AE接口”能让网络收到成品，但不能据此保证供应器解锁。

**影响：**仅开普通阻挡模式时可能混批；只把设置改成等待产物模式而保留原回流路径，又可能首批后锁死。

**建议：**给模板明确标注两种模式；需要严格串行时选择等待主产物返回，并把产物输出目标改为同一供应器的返回库存。没有可返回产物的任务应设计真实完成信号，不能只在样板上凭空声明一个标记物就认为它会产生。

证据：[AE2 1.21.1 PatternProviderLogic](https://github.com/AppliedEnergistics/Applied-Energistics-2/blob/1.21.1/src/main/java/appeng/helpers/patternprovider/PatternProviderLogic.java)（pushPattern、onPushPatternSuccess、onStackReturnedToNetwork）。

### 1.2 神秘农业：共享全部基座标签不能保证每个祭坛各得到完整配方

位置：[skills/minecraft-sfm-factory/references/advanced-patterns.md](../skills/minecraft-sfm-factory/references/advanced-patterns.md#L164)；[skills/minecraft-sfm-factory/references/mod-notes.md](../skills/minecraft-sfm-factory/references/mod-notes.md#L48)。

**控制流反例：**两个祭坛，每份配方需要 A×4+B×4；输入两份材料为 A×8+B×8，16 个基座共用一个标签。按来源和目标遍历顺序，完全可能前 8 个基座收到 A、后 8 个收到 B。总材料数和样板倍数都正确，两个祭坛仍都无法完成配方。

“to each 基座”只约束每个目标的投放量，不建立“祭坛—所属基座”的关系，也不按工位拆分配方。此反例验证的是分配算法缺少约束，不代表每种坐标布局都会出现同一种结果。

**建议：**每个祭坛独立一组核心/基座/缓存标签；或按材料角色建立专用基座标签，并保证每个工位包含正确的数量。样板倍数只是条件之一，还需要每工位配方完整性、空闲状态及缺料恢复机制。

证据：[MA 1.21 InfusionAltarTileEntity](https://github.com/BlakeBr0/MysticalAgriculture/blob/1.21/src/main/java/com/blakebr0/mysticalagriculture/tileentity/InfusionAltarTileEntity.java)（每个祭坛从自己周边基座构建配方）；SFM 的目标遍历及共享预算逻辑见 [OutputStatement.gatherSlots / tick](https://github.com/TeamDman/SuperFactoryManager/blob/e2ba833b2b235835d69475b641e24b22bfd9551a/platform/minecraft/src/main/java/ca/teamdman/sfml/ast/OutputStatement.java)。

### 1.3 神秘农业：搭建说明遗漏祭坛激活条件

位置：[skills/minecraft-sfm-factory/references/mod-notes.md](../skills/minecraft-sfm-factory/references/mod-notes.md#L43)；[skills/minecraft-sfm-factory/references/advanced-patterns.md](../skills/minecraft-sfm-factory/references/advanced-patterns.md#L166)。

**源码确认：**在核对的 1.21 分支中，祭坛有材料并不等于开始加工。isActive 会检查相邻红石信号，亦可由其他交互激活。

**建议：**在一次性搭建步骤中明确给每个祭坛接常亮信号，或设计可验证的启动信号。要把“给 SFM 管理器的开关”和“给祭坛的激活信号”区分开。

证据：[MA 祭坛源码](https://github.com/BlakeBr0/MysticalAgriculture/blob/1.21/src/main/java/com/blakebr0/mysticalagriculture/tileentity/InfusionAltarTileEntity.java)；[维护者的种子制作说明](https://blakesmods.com/wiki/1.21/mysticalagriculture/guides/creating-seeds)。

### 1.4 Mekanism：盐水电解产物写错，后续出口和比例推导也失去依据

位置：[skills/minecraft-sfm-factory/references/efficiency.md](../skills/minecraft-sfm-factory/references/efficiency.md#L23)。

**源码确认：**核对分支的原版配方为：
- 水 2 mB → 氢 2 + 氧 1。
- 盐水 10 mB → 钠 1 + 氯 1。

文档写成盐水产生“氯+氢”，并把两条路线合计成三种气体。原版两条路线实际涉及氢、氧、钠、氯四种化学品。“氢气储罐数量必须多于另外两种之和”也不能从这两条配方得出。

**建议：**修正产物；按每条产线实际吞吐、消耗、缓存时间和罐容量计算库存，避免给出无前提的固定罐数比例。魔改包另按 JEI 核对。

证据：[Mekanism SeparatingRecipeProvider](https://github.com/mekanism/Mekanism/blob/1.21.x/src/datagen/main/java/mekanism/common/recipe/impl/SeparatingRecipeProvider.java)。

### 1.5 Productive Bees：可配置蜜脾注册名写错

位置：[skills/minecraft-sfm-factory/references/mod-notes.md](../skills/minecraft-sfm-factory/references/mod-notes.md#L53)；SKILL.md 4.4、troubleshooting.md 第 39 条也有同一处错误。

**源码确认：**核对分支注册的是 productivebees:configurable_honeycomb，种类保存在 BEE_TYPE 数据组件里。仓库写的是 productivebees:configurable_comb。

“SFM 的注册 ID/tag 过滤不能按这些蜜脾的种类区分”这个方向正确，但引用的 ID 需要修正。搬运时保留组件与能否按组件筛选是两件不同的事，不应让读者误以为 SFM 运输会抹掉种类。

**建议：**同步修正所有出现位置；补充精确匹配的 AE2/RS 过滤和物理分仓方案，并标注版本。

证据：[Productive Bees ModItems](https://github.com/JDKDigital/productive-bees/blob/dev-1.21.0/src/main/java/cy/jdkdigital/productivebees/init/ModItems.java)；[蜜脾组件匹配代码](https://github.com/JDKDigital/productive-bees/blob/dev-1.21.0/src/main/java/cy/jdkdigital/productivebees/common/recipe/ConfigurableHoneycombRecipe.java)；[SFM 注册 ID 读取逻辑](https://github.com/TeamDman/SuperFactoryManager/blob/main/platform/minecraft/src/main/java/ca/teamdman/sfm/common/resourcetype/RegistryBackedResourceType.java)。

### 1.6 Productive Bees：离心机流体问题可能表现为丢产物，而不是停机

位置：[skills/minecraft-sfm-factory/references/mod-notes.md](../skills/minecraft-sfm-factory/references/mod-notes.md#L54)；[skills/minecraft-sfm-factory/references/advanced-patterns.md](../skills/minecraft-sfm-factory/references/advanced-patterns.md#L188)。

**源码确认，限定所核对分支：**CentrifugeBlockEntity.canProcessRecipe 检查物品输出空间，流体检查被注释；完成加工后调用 fill，却没有处理装不下的流体余量。罐满或流体不兼容时，机器可能继续消耗输入，而部分流体没有保存下来。PoweredCentrifugeBlockEntity 继承这套处理逻辑。

**影响：**用“机器停工”作为唯一告警，会漏掉副产物流体损失。

**建议：**将通用规则改成“必须核对机器满仓时是停止、溢出丢弃还是可配置销毁”。蜜蜂离心机单列版本说明，实测满罐、异种流体切换、蜂蜜是否可丢弃，再决定储罐、分组或停机策略。

证据：[离心机源码](https://github.com/JDKDigital/productive-bees/blob/dev-1.21.0/src/main/java/cy/jdkdigital/productivebees/common/block/entity/CentrifugeBlockEntity.java)（canProcessRecipe、completeRecipeProcessing）；[电动离心机继承关系](https://github.com/JDKDigital/productive-bees/blob/dev-1.21.0/src/main/java/cy/jdkdigital/productivebees/common/block/entity/PoweredCentrifugeBlockEntity.java)。核对提交：656641c1054dde8aa8690a10e6bb07ff1e75da41。

### 1.7 Modern Industrialization：默认配置下不能假定直接接受 FE

位置：[skills/minecraft-sfm-factory/references/efficiency.md](../skills/minecraft-sfm-factory/references/efficiency.md#L43)。

**源码确认：**MI 使用独立的 EU 能力。bidirectionalEnergyCompat 默认 false；向 MI 方块暴露外部能量接口的包装位于启用该配置的分支。

**影响：**如果此示例的“装配”指上文 MI 装配机，直接 output fe:: 不能作为默认可用的供电方案。NeoForge/GrandPower 接口与 SFM 使用的能力也应实际核对。

**建议：**注明具体目标机器。MI 默认使用相应电压的 MI 电缆供电，SFM 负责物料；只有确认版本、兼容配置和能力暴露后，才给 FE 方案。另外，正文说红石是流体，紧接着示例却发送 minecraft:redstone 物品，配方前提应统一。

证据：[MI EnergyApi](https://github.com/AztechMC/Modern-Industrialization/blob/1.21.x/src/main/java/aztech/modern_industrialization/api/energy/EnergyApi.java)；[MIStartupConfig 默认值](https://github.com/AztechMC/Modern-Industrialization/blob/1.21.x/src/main/java/aztech/modern_industrialization/config/MIStartupConfig.java)；[MI 官方电力机器指南](https://github.com/AztechMC/Modern-Industrialization/blob/1.21.x/src/main/resources/assets/modern_industrialization/mi_guidebook/electric_age/basic_machines.md)。

### 1.8 Ex Deorum：把物品 ID 当成现成 tag 使用

位置：[skills/minecraft-sfm-factory/SKILL.md](../skills/minecraft-sfm-factory/SKILL.md#L382)。

**上游资源确认：**exdeorum:dust 是物品 ID；核对的 1.21.1 上游资源树没有 exdeorum:dust 这个同名物品 tag。示例却使用 with #exdeorum:dust 筛选产物。

**建议：**在该示例中直接使用资源 ID exdeorum:dust；如果依赖整合包自建 tag，就必须明确标注这个前提。物品存在不代表同名 tag 存在。

证据：[Ex Deorum 沙子→粉尘配方](https://github.com/thedarkcolour/ExDeorum/blob/1.21.1/src/generated/resources/data/exdeorum/recipe/hammer/dust.json)；[核对的完整资源树](https://github.com/thedarkcolour/ExDeorum/tree/9b7b15d52d4be942335aac333e8cd402e28cc92d/src/generated/resources/data/exdeorum)。

### 1.9 “输出口数 ≥ 产物种类数”不适合作为跨模组硬规则

位置：[skills/minecraft-sfm-factory/references/efficiency.md](../skills/minecraft-sfm-factory/references/efficiency.md#L14)；[skills/minecraft-sfm-factory/references/advanced-patterns.md](../skills/minecraft-sfm-factory/references/advanced-patterns.md#L194)。

**接口能力确认：**一个外部容器/接口可以有多个物品槽或多个流体罐。GTCEu 有 4/9 槽流体仓；MI 的可配置储罐有 9 个独立流体槽。因此方块/出口数量不等于能同时接收的资源种类数。

**建议：**先区分机器输出槽、储罐、外部接收接口、AE 返回缓存、网络存储容量；再按独立可用槽/罐、过滤规则、吞吐量和余量设计。专用出口是便于排错的设计选择，不能说成 SFM 的普遍限制。

证据：[GTCEu FluidHatchPartMachine](https://github.com/GregTechCEu/GregTech-Modern/blob/1.20.1/src/main/java/com/gregtechceu/gtceu/common/machine/multiblock/part/FluidHatchPartMachine.java)；[MI 可配置储罐说明](https://github.com/AztechMC/Modern-Industrialization/blob/1.21.x/src/main/resources/assets/modern_industrialization/mi_guidebook/electric_age/advanced_machines.md)。

### 1.10 蓄能放电模板没有兑现“攒够后定量放电”

位置：[skills/minecraft-sfm-factory/references/advanced-patterns.md](../skills/minecraft-sfm-factory/references/advanced-patterns.md#L283)。

**控制流确认：**1000000 仅控制是否充电；放电分支只检查红石。电网断供、缓冲仅有 100 FE 时，只要红石有效也会放电。output fe:: 又没有数量限制，信号持续时每次触发都会再次执行。

**建议：**若目标是攒够后放出固定数量，应在放电分支同时检查可用能量，设置输出上限，并按需求采用脉冲或一次性状态。还须核对目标能否一次接收该数量。若只是常规供电，应重写说明，避免承诺定量行为。

该问题由本地分支条件反例确认，未模拟目标机器的实际接收行为。

## 2. 逐模组的保留项与改进方向

| 模组 | 可保留的结论 | 应补充或调整 |
|---|---|---|
| Mekanism | 标准加工输入槽限制外部抽取；侧面配置影响能力；1.21 化学品统一 | “只能抽输出”应限定标准加工槽，别扩展到一切容器/机器。每种资源类型的面配置单独列出。气体进 ME 需要 Applied Mekanistics 等对应兼容层，不能假定基础 AE2 支持。 |
| AE2 | 精确资源过滤、压印器小输入缓冲、专用接口都能简化设计 | 写清普通阻挡与等待结果锁；产物返回同一供应器。压印器需要注明是否开启侧面分离，null 内部库存和有方向的自动化库存不是同一映射。 |
| ExtendedAE / AdvancedAE | ExtendedAE 扩展压印器确有 4 个工作线程，水晶装配器确有 9 个输入槽 | 文档的“高级AE”应改为英文名+modid。这两台设备属于 ExtendedAE；AdvancedAE 是另一个模组。先介绍扩展压印器 1/4/64 输入缓冲选项，再讨论额外控制。 |
| GTCEu Modern | 多方块仓口应分别标记；电路/模具等应明确配置 | 区分普通单罐仓、4/9 槽仓、ME 仓和各自 IO；“一台机器固定配方”作为设计建议，而非能力限制。 |
| Mystical Agriculture | 每基座 1 件、种子 tag、较慢采样频率均有依据 | 增加祭坛激活；分工位投料；针对非种子配方不能沿用 seeds 回收过滤。 |
| Productive Bees | 组件决定蜜脾种类，按注册 ID 筛选有边界 | 修正 ID；按版本区分流体溢出丢失与停机；空罐/满罐/混合配方分别验证。 |
| Thermal | 有机灌注器存在种子输入、催化剂槽、水罐及输出槽 | 明确 1.20.x 基线。其循环处理增幅功能可回收匹配种子，适合减少外部循环；不要默认每个环境都已安装。各类型侧面配置和回收种子的去向写清。 |
| Modern Industrialization | 槽位锁定、输入量限制、自动输出是原生功能 | 先锁定配方槽并限制数量，避免输入挤满，再比较机器性能；注明 EU 供电与电压等级。 |
| Occultism | 1.21.1 献祭碗支持物品处理；黄金碗的插入路径会验证并启动仪式 | 单列“辅料先到、激活物最后到”、阵法有效性、额外条件及完成信号。不能一概要求右键模拟器；也不能把所有仪式当作普通机器库存。 |
| Ars Nouveau | Imbuement Chamber 可以自动化输入/输出，周边基座提供配方条件 | 将灌注室和附魔装置分开。灌注室基座材料通常不消耗，适合一次性配置，不应逐批重复分发；Source 与 FE 也须区分。 |
| Oritech | 官方加速器机制确实包含物品注入、红石导向和速度传感 | 优先写“速度传感器→比较器→达到阈值后投第二粒子”。能量消耗发生在加速电机，泛化的一次性放电模板不能代表完整加速器控制。 |
| Ex Deorum | 沙/红沙到 dust 的上游配方可确认 | 核实物品与 tag 的区别；注明机器种类、工具/能源及面槽，别仅凭输出名套用泛用粉碎机。 |
| Refined Storage | 物理分仓与精确组件过滤适合作为 SFM 的前置分拣 | 标注 RS 1.x/2.x/3.x 差别；新文档的外部存储默认是黑名单，Fuzzy 默认关闭，不能只说“设置过滤”而不说明模式。 |

对应证据：
- [Mekanism InputInventorySlot](https://github.com/mekanism/Mekanism/blob/1.21.x/src/main/java/mekanism/common/inventory/slot/InputInventorySlot.java)；[化学品储罐外部传输与内部速率区别](https://github.com/mekanism/Mekanism/blob/1.21.x/src/main/java/mekanism/common/capabilities/chemical/ChemicalTankChemicalTank.java)；[Applied Mekanistics](https://github.com/AppliedEnergistics/Applied-Mekanistics/blob/dev/1.21.1/README.md)。
- [AE2 压印器官方指南](https://github.com/AppliedEnergistics/Applied-Energistics-2/blob/1.21.1/guidebook/items-blocks-machines/inscriber.md)；[AE2 null/有方向库存暴露](https://github.com/AppliedEnergistics/Applied-Energistics-2/blob/1.21.1/src/main/java/appeng/blockentity/AEBaseInvBlockEntity.java)；[AE2 存储总线过滤](https://github.com/AppliedEnergistics/Applied-Energistics-2/blob/1.21.1/guidebook/items-blocks-machines/storage_bus.md)。
- [ExtendedAE 扩展压印器](https://github.com/GlodBlock/ExtendedAE/blob/1.21.1-neoforge/src/main/java/com/glodblock/github/extendedae/common/tileentities/TileExInscriber.java)；[ExtendedAE 水晶装配器](https://github.com/GlodBlock/ExtendedAE/blob/1.21.1-neoforge/src/main/java/com/glodblock/github/extendedae/common/tileentities/TileCrystalAssembler.java)；[AdvancedAE 功能与原生限量 IO 总线](https://github.com/pedroksl/AdvancedAE/blob/main/README.md)。
- [Thermal 有机灌注器](https://github.com/CoFH/ThermalExpansion/blob/1.20.x/src/main/java/cofh/thermal/expansion/common/block/entity/machine/MachineInsolatorBlockEntity.java)（cyclicProcessingFeature / resolveInputs）。
- [MI 原生槽位锁定与限量](https://github.com/AztechMC/Modern-Industrialization/blob/1.21.x/src/main/resources/assets/modern_industrialization/mi_guidebook/steam_age/steam_machines.md)；[MI 装配机的多配方槽位锁定](https://github.com/AztechMC/Modern-Industrialization/blob/1.21.x/src/main/resources/assets/modern_industrialization/mi_guidebook/electric_age/basic_machines.md)。
- [MA 的 c:seeds 标签声明](https://github.com/BlakeBr0/MysticalAgriculture/blob/1.21/src/main/resources/data/c/tags/item/seeds.json)。
- [Occultism 1.21.1 黄金献祭碗](https://github.com/klikli-dev/occultism/blob/version/1.21.1/src/main/java/com/klikli_dev/occultism/common/blockentity/GoldenSacrificialBowlBlockEntity.java)（insertItem 中的配方验证与启动）。
- [Ars Nouveau 1.21 灌注室](https://github.com/baileyholl/Ars-Nouveau/blob/1.21.x/src/main/java/com/hollingsworth/arsnouveau/common/block/tile/ImbuementTile.java)；[灌注室说明](https://ars.guide/book/crafting/imbuement_chamber/)。
- [Oritech 1.21 加速器官方指南](https://github.com/Rearth/Oritech/blob/1.21/wiki/docs/particle_accelerator.mdx)；[速度传感器阈值](https://github.com/Rearth/Oritech/blob/1.21/wiki/content/particle/accelerator_sensor.mdx)；[控制器输入与产物槽](https://github.com/Rearth/Oritech/blob/1.21/wiki/content/particle/accelerator_controller.mdx)。
- [Refined Storage 外部存储官方文档](https://refinedmods.com/refined-storage/storage/external-storage.html)。

## 3. 不能从现有材料确认的性能结论

efficiency.md 的“258/762 台”“1024 台中 10–50 台卡死”“固定 4 倍速度”等数据缺少完整复现环境：模组版本、整合包版本、配置、供电、升级、槽位锁定、配方、布局和测试程序都未列出。

本次源码确认了若干槽位结构，但没有重现这些具体数字，也没有足够证据把“跨线程原料自动迁移”认定为所有版本的既定机制。建议：
1. 把它们标为某环境下的社区观察。
2. 附完整程序、来源和最小复现存档/搭建说明。
3. 在相同配置下比较单台吞吐、阵列吞吐、管理器耗时与停机原因。
4. 先利用机器原生过滤、锁槽和缓冲上限，再得出选型结论。

Mekanism 聚变燃料模板也需要独立实测。核对源码中燃料消耗每 tick 执行，温度足够时可消耗罐内全部可用燃料，烧不到燃料会停止燃烧。因此不能把“1 tick 宽度脉冲”直接当成“每 tick 都有一次上升沿”，也不能仅凭解析成功保证维持反应堆。需要记录每 tick 实际供料、库存、温度和燃烧状态，并验证临时罐容量、回流成功及重载恢复。

证据：[Mekanism FusionReactorMultiblockData](https://github.com/mekanism/Mekanism/blob/1.21.x/src/generators/java/mekanism/generators/common/content/fusion/FusionReactorMultiblockData.java)（tick、burnFuel）；[储罐容量基线](https://github.com/mekanism/Mekanism/blob/1.21.x/src/main/java/mekanism/common/tier/ChemicalTankTier.java)。

## 4. 文档和验证流程的建议

1. **每个模板加适用条件表。** 至少列 MC/加载器、SFM、目标模组版本、必需附属模组、机器选项、原料/产物槽位和能源类型。
2. **把事实、设计选择和经验阈值分开。** “每台固定配方”“一个面统一搬运”可以是建议；不要写成模组只能这样工作的能力限制。
3. **把机器原生功能放在复杂 SFML 前面。** AE2 小缓冲、ExtendedAE 输入上限、MI 锁槽、Thermal 循环处理、AdvancedAE 限量 IO 都可能减少扫描和状态机。
4. **补充无损与有损出口策略。** 满仓先停机、专用缓存、可丢弃副产物溢出销毁，应由具体任务决定；不要默认把所有主产物也送垃圾桶。
5. **为参考事实添加出处。** 记录分支/发布版本和源码位置；对开发分支保存提交或文件哈希，更新时有针对性复核。
6. **扩充静态检查。** 搜索所有资源 ID/tag 的来源；检查精确 ID 与 tag 混用；提示无条件推进状态、只看来源空而未看目标齐料、放电无阈值等模式。启发式检查只能提示人工审查。
7. **保留语法校验，同时写清边界。** 当前 42 个代码块解析通过不能保证游戏内编译通过，更不能验证接口和配方行为。依赖版本应固定；mutable HEAD 缓存需要刷新策略。

## 5. 最小游戏内验证清单

| 场景 | 要确认的结果 |
|---|---|
| AE2 连续请求两份长耗时配方 | 第二份不会在第一份完成前混入；产物经同一供应器返回后可解锁 |
| MA 两工位、两类辅料、材料量刚好 | 每工位均收到完整配方；缺一种材料时不误启动 |
| MA 无启动信号/有启动信号 | 可区分未激活和配方不匹配 |
| Productive Bees 满罐及异种流体切换 | 记录是否停机、是否丢流体；物品是否继续加工 |
| MI 默认供电兼容配置 | SFM 能看到的能源能力、EU 电缆供电、配置变化后的差异 |
| ExtendedAE 各种侧面/缓冲模式 | 自动化槽位编号、每线程材料齐备、持续输入是否挤占 |
| Thermal 开启/关闭循环处理 | 种子是否被消耗、回收和重新补给；产物不挤占补种预算 |
| 所有流水线：来源空、目标满、断电、重载 | 不丢资源、不跳过工序、有明确恢复方式 |

本次实际执行的是源码/资源核对、现有解析结果复查，以及两个小型控制流反例（多工位分料、未蓄满放电）。上述游戏内项目尚未执行。

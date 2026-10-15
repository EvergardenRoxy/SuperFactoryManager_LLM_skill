# 配置、命令、版本差异与资料来源

## 配置与命令

## 服务器配置（`sfm-server.toml`；也可在管理器界面左下角点 View server config 查看）

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

## 命令

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

## 版本差异速查

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

## 资料来源与已知出入

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
4. 旧资料的正则示例 `"[^(iron_ingot)].*"` 用来"排除铁锭"是错的（见 `language-reference.md` 的"资源 ID"一节）。
5. `redstone::`（信号读取）出现的版本：用户资料写 ≥4.27.0，仓库更新日志写在 4.35.0 PRE。**需让用户实测。**
6. 程序最大长度：更新日志写约 32,300，源码常量为 32,600；以"约 32,300"为安全线。
7. 配置文件：用户资料写 `config/sfm-server.toml`（4.20.0+）或 `config/sfm-common.toml`；Forge 的**服务器配置通常在存档目录的 `serverconfig/` 里**。最稳妥的方式是用管理器界面的 View server config 或 `/sfm config` 命令定位。

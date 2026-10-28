# Configuration, commands, versions, and sources

Read this for server settings, `/sfm` commands, feature availability, or conflicting documentation.

## Server configuration

Use **View server config** in the manager GUI or `/sfm config` to find the active configuration. The file is normally `sfm-server.toml`; Forge server configs are commonly under the world's `serverconfig/` directory. Do not assume a global `config/` path applies to every version.

| Setting | Default | Purpose |
|---|---|---|
| `disableProgramExecution` | `false` | Emergency switch preventing all managers from compiling and running programs |
| `logResourceLossToConsole` | `true` | Log detected resource loss to the console |
| `timerTriggerMinimumIntervalInTicks` | `20` | Ordinary timer minimum in ticks |
| `timerTriggerMinimumIntervalInTicksWhenOnlyForgeEnergyIOStatementsPresent` | `1` | Minimum for supported energy-only I/O |
| `maxIfStatementsInTriggerBeforeSimulationIsntAllowed` | `10` | Above this count, skip the compiler's exponential branch-simulation check |
| `maxDiskProblems` | `10` | Maximum diagnostics annotated on a disk |
| `disallowedResourceTypesForTransfer` | Empty list | Resource types the server forbids transferring |
| `levelsToShards` | `JustOne` | Enchanted-book-to-Experience-Shard policy for anvil processing: `JustOne`, `EachOne`, `SumLevels`, or `SumLevelsScaledExponentially` |

Loading/reloading server configuration clears the program-build cache and causes managers to rebuild their programs.

## Commands

Permission levels below follow the checked upstream command registration; servers may impose additional restrictions.

| Command | Permission | Purpose |
|---|---|---|
| `/sfm config show <SERVER\|CLIENT>` | All players | Show configuration |
| `/sfm config edit SERVER` | Level 4 | Edit server configuration |
| `/sfm config edit CLIENT` | All players | Edit client configuration |
| `/sfm bust_cable_network_cache` | All players, 4.16.0+ | Clear cable-network caches |
| `/sfm bust_water_network_cache` | All players | Clear Water Tank network caches |
| `/sfm show_bad_cable_cache_entries <block>` | Level 2 | Place a block at cached invalid positions for diagnosis; this changes the world |
| `/sfm changelog` | All players | Open the changelog in game |
| `/sfm kit [player]` | Level 2 | Give the standard SFM tools and blocks |

## Feature availability

These are historical feature milestones, not a statement that every Minecraft build exposes every integration. Check the user's exact artifact when behavior differs.

| SFM version | Relevant changes |
|---|---|
| 4.12.0 | Per-resource quantity/retention `each`; `except` |
| 4.14.0 | `forget`, round robin, Network Tool; bare `input redstone` |
| 4.15.0 | `each` as an `every` synonym; `each side`; FE aliases; configurable minima and faster energy-only timers |
| 4.16.0 | `every tick`; MC 1.19.2 `mekanism_energy`; redstone label support; omitted resource in `has` |
| 4.17.0 | Forget-budget fixes, warnings, cache invalidation fixes |
| 4.19.0 | Tag filters; unified-chemical aliases on MC 1.21.1 builds |
| 4.20.0 | Reliable `without`, resource `or`, per-resource optimizations, Fancy Cables/facades, global/offset timing, exponential Water Tank scaling, approximately 32,300-character programs, `/sfm config`, server-config and disallowed-type settings |
| 4.21.0 | Completion acceptance with `\`; editor configuration button |
| 4.22.0 | Retention fixes, `second` fix, 256-character labels |
| 4.24.0 | Seconds-based offset conversion fix |
| 4.25.0 | `output to empty slots in ...` |
| 4.27.0 | Tunnelled Factory Manager, singular `slot`, relative sides, labeled-block `redstone::`, manager self-access, forget leak fix |
| 4.29.0 | Tunnelled/Tough Inventory Cables, Network Tool tuning, extraction diagnostics |
| 4.34.0 | Waterlogging for Fancy Inventory Cables |
| 4.35.0 PRE / development line | Experimental Resource Buffer redstone counts, explicit `OFFSET BY`, warnings for legacy offsets, Client Manager display/communication features |

Development grammar also contains declarations, `LET ... BE ...`, frame triggers, `CREATE INPUT`, `BROADCAST`, `RENDER IMAGE`, `INVOKE`, JSON expressions, capability selection, and bindings. These Client Manager extensions are outside this skill's factory-logistics scope. Do not conclude that ordinary logistics programs can use them as general-purpose variables or loops.

## Official references and source precedence

- [SuperFactoryManager repository](https://github.com/TeamDman/SuperFactoryManager)
- [SFML grammar](https://github.com/TeamDman/SuperFactoryManager/blob/main/platform/minecraft/src/main/antlr/sfml/SFML.g4)
- [Examples](https://github.com/TeamDman/SuperFactoryManager/tree/main/examples) and [in-game template programs/changelog](https://github.com/TeamDman/SuperFactoryManager/tree/main/platform/minecraft/src/main/resources/assets/sfm/template_programs)
- [Issue-reporting guide](https://github.com/TeamDman/SuperFactoryManager/blob/main/docs/REPORTING_ISSUES.md), [redstone notes](https://github.com/TeamDman/SuperFactoryManager/blob/main/docs/redstone-support.md), and [issue tracker](https://github.com/TeamDman/SuperFactoryManager/issues)
- [SFM Discord](https://discord.gg/5mbUY3mu6m); CurseForge listing: Super Factory Manager; VS Code extension: `TeamDman.super-factory-manager-language`
- [DeepWiki](https://deepwiki.com/TeamDman/SuperFactoryManager) is AI-generated and may lag behind. Prefer matching-version source and in-game evidence when they conflict.

SFM wording and syntax were rechecked on 2026-10-28 against commit [`e2ba833b2b235835d69475b641e24b22bfd9551a`](https://github.com/TeamDman/SuperFactoryManager/commit/e2ba833b2b235835d69475b641e24b22bfd9551a). Relevant files include `SFML.g4`, `SFMServerConfig.java`, `SFMCommand.java`, `BoolRedstone.java`, `RedstoneSignalCapabilityProvider.java`, `WaterTankBlockEntity.java`, English localization, and bundled templates under `platform/minecraft/`.

### Known documentation discrepancies

1. **Omitted namespace:** current `stone` matches that item name across namespaces. Older comments claiming an implicit `minecraft:` namespace do not describe this behavior.
2. **Empty slots:** grammar supports this on output only. It skips all occupied slots, including partially filled stacks.
3. **Boolean precedence:** grammar gives `not > and > or`; parenthesize combinations even if an old example says otherwise.
4. **Regex exclusion:** `"[^(iron_ingot)].*"` is a negated character class, not an item exclusion. Use `except iron_ingot`.
5. **Redstone versions:** ordinary labeled-block signal reads date from 4.27.0; experimental buffer counts are a separate development feature. At the checked commit, both manager `if redstone` and world-signal resource reads query current world state. Do not repeat older blanket claims that all redstone reads cache signal strength.
6. **Program length:** changelog guidance is about 32,300 characters; the checked source constant is 32,600. Use the lower value as a conservative budget.
7. **Water Tank scaling:** the exponential expression describes exposed amount/capacity in the checked implementation, not guaranteed throughput per tick. Actual output also depends on transfer calls and destination limits.
8. **Native ejection limits:** direct capability access may bypass an ejection schedule; it does not bypass capability transfer limits or side restrictions.

## Mod behavior audit sources

The following sources were recorded in the 2026-10-27 interface audit. They describe branch implementations, not every release or modified pack. Preserve that scope when adapting examples; recheck the user's version if it differs.

| Mod / checked branch | Source files |
|---|---|
| Mekanism 1.21.x | [mek_electro](https://github.com/mekanism/Mekanism/blob/1.21.x/src/datagen/main/java/mekanism/common/recipe/impl/SeparatingRecipeProvider.java)；[mek_input](https://github.com/mekanism/Mekanism/blob/1.21.x/src/main/java/mekanism/common/inventory/slot/InputInventorySlot.java)；[mek_fusion](https://github.com/mekanism/Mekanism/blob/1.21.x/src/generators/java/mekanism/generators/common/content/fusion/FusionReactorMultiblockData.java) |
| AE2 1.21.1 | [ae_provider](https://github.com/AppliedEnergistics/Applied-Energistics-2/blob/1.21.1/src/main/java/appeng/helpers/patternprovider/PatternProviderLogic.java)；[ae_base](https://github.com/AppliedEnergistics/Applied-Energistics-2/blob/1.21.1/src/main/java/appeng/blockentity/AEBaseInvBlockEntity.java)；[ae2_inscriber_doc](https://github.com/AppliedEnergistics/Applied-Energistics-2/blob/1.21.1/guidebook/items-blocks-machines/inscriber.md) |
| ExtendedAE 1.21.1-neoforge | [ext_inscriber](https://github.com/GlodBlock/ExtendedAE/blob/1.21.1-neoforge/src/main/java/com/glodblock/github/extendedae/common/tileentities/TileExInscriber.java)；[ext_thread](https://github.com/GlodBlock/ExtendedAE/blob/1.21.1-neoforge/src/main/java/com/glodblock/github/extendedae/common/me/InscriberThread.java)；[ext_assembler](https://github.com/GlodBlock/ExtendedAE/blob/1.21.1-neoforge/src/main/java/com/glodblock/github/extendedae/common/tileentities/TileCrystalAssembler.java) |
| AdvancedAE main | [adv_readme](https://github.com/pedroksl/AdvancedAE/blob/main/README.md) |
| GTCEu Modern 1.20.1 | [gt_hatch](https://github.com/GregTechCEu/GregTech-Modern/blob/1.20.1/src/main/java/com/gregtechceu/gtceu/common/machine/multiblock/part/FluidHatchPartMachine.java) |
| Mystical Agriculture 1.21 | [ma](https://github.com/BlakeBr0/MysticalAgriculture/blob/1.21/src/main/java/com/blakebr0/mysticalagriculture/tileentity/InfusionAltarTileEntity.java)；[ma_seeds](https://github.com/BlakeBr0/MysticalAgriculture/blob/1.21/src/main/resources/data/c/tags/item/seeds.json) |
| Productive Bees dev-1.21.0 | [bees_items](https://github.com/JDKDigital/productive-bees/blob/dev-1.21.0/src/main/java/cy/jdkdigital/productivebees/init/ModItems.java)；[bees_recipe](https://github.com/JDKDigital/productive-bees/blob/dev-1.21.0/src/main/java/cy/jdkdigital/productivebees/common/recipe/ConfigurableHoneycombRecipe.java)；[bees_centrifuge](https://github.com/JDKDigital/productive-bees/blob/dev-1.21.0/src/main/java/cy/jdkdigital/productivebees/common/block/entity/CentrifugeBlockEntity.java)；[bees_power](https://github.com/JDKDigital/productive-bees/blob/dev-1.21.0/src/main/java/cy/jdkdigital/productivebees/common/block/entity/PoweredCentrifugeBlockEntity.java) |
| Thermal 1.20.x | [thermal](https://github.com/CoFH/ThermalExpansion/blob/1.20.x/src/main/java/cofh/thermal/expansion/common/block/entity/machine/MachineInsolatorBlockEntity.java) |
| MI 1.21.x | [mi_energy](https://github.com/AztechMC/Modern-Industrialization/blob/1.21.x/src/main/java/aztech/modern_industrialization/api/energy/EnergyApi.java)；[mi_config](https://github.com/AztechMC/Modern-Industrialization/blob/1.21.x/src/main/java/aztech/modern_industrialization/config/MIStartupConfig.java)；[mi_slots_doc](https://github.com/AztechMC/Modern-Industrialization/blob/1.21.x/src/main/resources/assets/modern_industrialization/mi_guidebook/steam_age/steam_machines.md) |
| Occultism version/1.21.1 | [occ_gold_121](https://github.com/klikli-dev/occultism/blob/version/1.21.1/src/main/java/com/klikli_dev/occultism/common/blockentity/GoldenSacrificialBowlBlockEntity.java) |
| Ars Nouveau 1.21.x | [ars_imb_121](https://github.com/baileyholl/Ars-Nouveau/blob/1.21.x/src/main/java/com/hollingsworth/arsnouveau/common/block/tile/ImbuementTile.java) |
| Oritech 1.21 | [ori_doc](https://github.com/Rearth/Oritech/blob/1.21/wiki/docs/particle_accelerator.mdx)；[ori_sensor_doc](https://github.com/Rearth/Oritech/blob/1.21/wiki/content/particle/accelerator_sensor.mdx)；[ori_ctrl_doc](https://github.com/Rearth/Oritech/blob/1.21/wiki/content/particle/accelerator_controller.mdx) |
| Ex Deorum 1.21.1 | [ex_dust](https://github.com/thedarkcolour/ExDeorum/blob/1.21.1/src/generated/resources/data/exdeorum/recipe/hammer/dust.json) |


- Productive Bees fluid-loss behavior is pinned to commit `656641c1054dde8aa8690a10e6bb07ff1e75da41`. Recheck `canProcessRecipe` and `completeRecipeProcessing` after upgrades.
- [Applied Mekanistics](https://github.com/AppliedEnergistics/Applied-Mekanistics/blob/dev/1.21.1/README.md) provides ME chemical integration. Check [RS External Storage documentation](https://refinedmods.com/refined-storage/storage/external-storage.html) against the installed RS version.

## Validation scope

Run `python3 scripts/validate_skill.py --ref <upstream commit SHA>` for a reproducible grammar check. It requires Java 11+, Python 3.8+, and `antlr4-python3-runtime==4.13.2`. Downloads are cached; the default mutable HEAD cache does not automatically track upstream updates. Change the SHA or clear the matching cache when updating the baseline.

The validator runs ANTLR parsing and skill-structure checks. It does **not** run SFM compiler checks for timer minima, resource types, regex validity, or actual game capabilities. It also does not validate recipes, slot mappings, transfer acceptance, timing, or Minecraft behavior.

Before deploying a production design, test one complete recipe, two consecutive long batches, parallel-station completeness, missing inputs, full targets, power loss, and reload recovery. Verify component filtering, side/slot mappings, pulse periods, and per-call transfer limits in game. No Minecraft integration test is claimed for these documents.

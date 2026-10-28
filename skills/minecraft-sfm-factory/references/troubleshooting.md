# Troubleshooting programs and disk diagnostics

Read this for errors, warnings, stalled machines, or program reviews. Start with the exact diagnostic when available; otherwise follow the investigation sequence below. A syntax error, compiler validation failure, and valid program with incorrect behavior are different failure classes.

## Common mistakes

| # | Mistake | Failure class | Correction or explanation |
|---|---|---|---|
| 1 | `input from a` without a consuming output | Behavior | Input only registers a source; add an output |
| 2 | `input fluid:: from a` followed by `output to b` | Type mismatch | Use matching fluid I/O and concrete sides |
| 3 | `input fe:: from a` without a side on a restricted block | Capability access | Use a verified face such as `top side` |
| 4 | `output to b top` | Syntax | Include `side`: `top side` |
| 5 | `input stone from a slots 0 top side` | Syntax | Side before slots: `from a top side slots 0` |
| 6 | `input from a top side round robin by block` | Syntax | Round robin precedes sides |
| 7 | `input from empty slots in a` | Syntax | Empty-slot selection is output-only |
| 8 | Item transfers in `every 5 ticks` under default settings | Compiler validation | Ordinary minimum is 20 ticks; supported energy-only I/O defaults to one |
| 9 | `every 0.5 seconds do` | Syntax | Use integer periods; timer periods must be positive |
| 10 | `fluid:water` | Wrong resource | This means an item in namespace fluid; use `fluid::water` |
| 11 | `output fe to b top side` | Wrong resource | Use `fe::` for energy |
| 12 | `input from my-chest` | Syntax | Quote punctuation: `input from "my-chest"` |
| 13 | `input from east` | Syntax | Quote reserved-word labels: `"east"` |
| 14 | `input "*_ingot" from a` | Regex validation | Use quoted `".*_ingot"` or bare `*_ingot` |
| 15 | `"[^(iron_ingot)].*"` used to exclude iron ingots | Wrong filter | Negated character class; prefer `except iron_ingot` |
| 16 | Reading `5 stone, dirt` as five stone-or-dirt items | Wrong budget | Commas separate limits; use `5 stone or dirt` on 4.20.0+ |
| 17 | `if a has 5 then` | Syntax | Include comparison: `if a has >= 5 then` |
| 18 | `if a == 5` or `if a has != 5` | Syntax | Use `has =`; negate with `not (a has = 5)` |
| 19 | `elif`, `elseif`, or one `end` per else-if branch | Syntax | Use `else if`; one end closes the complete chain |
| 20 | Feeding and collecting without isolating registered sources | Bypassed processing | Add `forget`, separate triggers, or verified disjoint filters; see SKILL.md section 5 |
| 21 | Input/output outside a trigger | Syntax | Put logistics statements in `every … do … end` |
| 22 | `name "x"` after a trigger | Syntax | Put the optional name before all triggers |
| 23 | `output 1000 to b` intended to transfer fluid | Wrong resource | Use `output 1000 fluid:: to b top side` |
| 24 | `every 20+1 ticks offset by 2 ticks` | Compiler validation | Choose legacy offset or explicit offset, not both |
| 25 | `input from a iron_ingot` | Syntax | Resource precedes `from`: `input iron_ingot from a` |
| 26 | Expecting `output N to b` to give N to every block | Wrong allocation | It shares N across the group and may split it. Use `to each b`; use round robin to select only one block |
| 27 | Expecting `input 5 from a` to take five per block | Wrong allocation | Use `from each a` for a per-block budget |
| 28 | Confusing redstone dust with `redstone::` signals | Wrong type | Use `item:minecraft:redstone` for dust |
| 29 | Writing `1k` or `1,000` as a quantity | Misparsed/rejected | `1k` can mean one resource k; commas separate limits. Write `1000` |
| 30 | Using a mod-specific resource type without its integration | Compiler validation | For example, `gas::` requires the appropriate Mekanism integration; check the installed build |
| 31 | Comma-separated resources inside `has` | Syntax | Use resource `or` on 4.20.0+ |
| 32 | Exceeding the disk's program length | Save limit | Keep below the conservative ~32,300-character budget; simplify or split |
| 33 | Labels not pushed to the disk or targets disconnected | World setup | Assign and push labels; check the cable network and disk warnings |
| 34 | Two chemicals enter different faces using only `gas::`, without isolation | Wrong routing | Clear registrations between routes or use exact chemical IDs on both input/output |
| 35 | Independent state-transition conditions run several states at once | Control flow | `has` sees current inventory; use an `if … else if … end` chain |
| 36 | Ignoring full-storage behavior | Stall or loss | Verify whether the machine stops or discards output; provide capacity and permitted overflow routes |
| 37 | `if each tanks >= 1000 fluid:: then`, or a full-width comparison symbol | Syntax | Include `has`, a side where needed, and ASCII operators: `if each tanks top side has >= 1000 fluid:: then` |
| 38 | Using `each side` and high-frequency triggers everywhere | Performance | Narrow sides, slots, resources, and frequency; read `efficiency.md` |
| 39 | Sorting same-ID variants by NBT/components with registry filters | Capability limit | Separate with exact component-aware AE2/RS or other filtering first; SFM transport preserves components |
| 40 | Feedback loop leaves every machine with an incomplete recipe | Allocation/startup | Provide enough startup material for complete recipes and reserve, and balance ongoing inputs/exports |
| 41 | All stations share pedestal labels and only pattern quantities are multiplied | Incomplete batches | Use station-specific groups/providers or verified ingredient-role allocation; total quantity alone is insufficient |
| 42 | `fluid::sulfuric_acid` selects another mod's similarly named fluid | Wrong namespace | Use the verified exact ID, such as `fluid:gtceu:sulfuric_acid` |
| 43 | Correct routing but no recipe starts | Machine setup | Check circuits, catalysts, presses, power, side configuration, activation, and conflicting automatic output |
| 44 | Unknown resource warnings or an impossible recipe chain | Unsupported data | Recheck JEI/EMI and Ctrl+Space; follow `recipe-learning.md`; replace unnecessary filters with dedicated sources |

For example, Productive Bees variants share `productivebees:configurable_honeycomb` and differ by component. A regex on that ID cannot separate them. For all rows above, “parses” does not mean “passes the game compiler” or “works in the world.”

## Compiler errors

Disk diagnostics appear in the manager GUI. Clicking the warning button copies annotated code; Shift+click attempts automatic fixes. Review the result. The default `maxDiskProblems` is ten, so an abbreviated list may hide additional issues.

| Message | Meaning and action |
|---|---|
| `Failed to compile.` / `Failed to compile with N errors.` | Inspect the reported lines for missing `end`/`then`, clause order, invalid tokens, and unquoted labels |
| `Minimum trigger interval is N ticks.` | Increase the period or verify that the trigger contains only eligible energy I/O |
| `Program references an unknown resource type "x"` | Misspelled type or unavailable integration |
| `Program has a malformed resource type "x"` | Type must be literal, not wildcard or regex |
| `Program references a disallowed resource type "x"` | Server configuration forbids it |
| `Invalid resource identifier pattern …` | Invalid regex, commonly a bare `*` inside quotes |
| `Label name cannot be longer than 256 characters.` | Shorten the label; older releases may have a lower limit |
| `Interval exceeds supported tick count` | Period or converted time exceeds the supported range |
| `Use either legacy + offset or OFFSET BY, not both` | Remove one offset syntax |

## Warnings

A program may run despite warnings and still behave incorrectly.

| Warning text or fragment | Meaning | Action |
|---|---|---|
| `Label "x" is assigned in the world … but not connected by cables.` | Disconnected target | Connect cables or rebuild the network |
| `… connected by cables but is not detected as a valid inventory.` | No usable capability found | Check face, resource type, and block support |
| `Label "x" is assigned in the world but not defined in code.` | Unused mapping | Ignore if intentional or Prune it with the Label Gun |
| `Label "x" is used in code but not assigned in the world.` | Missing mapping or push | Apply the label and right-click the manager to push |
| `… inputs "x" from "y" but no future output statement consume "x".` | No consuming output | Add the matching output or remove the input |
| `… resource type "x" which has no matching input statement.` | Output lacks a source of its type | Add the corresponding input before it |
| `Statement matches no slots` | Invalid face/slot selection | Check automation mappings |
| `No slots support extraction` / `No slots support insertion` | Operation rejected by capability | Change face/slot or machine configuration |
| `Mekanism blocks are read-only from the null direction` | Missing usable side | Specify a configured concrete face |
| `Mekanism block side config … doesn't agree with statement` | I/O settings conflict with program | Configure the appropriate resource type and face |
| `EACH used without a pattern` | Per-resource each adds no useful split | Remove it or use a deliberate resource pattern |
| `Round robin by label should be used with more than one label` | One-label rotation | Remove round robin or select multiple labels |
| `Round robin by block shouldn't be used with EACH` | Conflicting allocation intent | Choose rotation or per-block distribution |
| `The legacy + interval offset is ambiguous; use OFFSET BY …` | Newer build prefers explicit offset | Use the supported explicit form |
| `Resource "x" was not found.` | No registry match | Check spelling, namespace, version, and actual IDs |
| `Too many conditions for simulation …` | Compiler simulation skipped | Simplify or split if helpful; this does not itself prohibit execution |

## Investigation sequence

0. **Check capability scope.** Component-based sorting, direct world redstone output, and crafting/player interaction may require another mechanism. See SKILL.md section 0 before attempting syntax changes.
1. **Read disk diagnostics.** Address relevant errors and warnings first. A clean diagnostic list is not proof of correct behavior.
2. **Check labels.** Were the right block positions labeled and pushed to the disk? Labels bind blocks, not faces. Use Label Gun rendering to inspect them.
3. **Check connectivity.** Hold the Network Tool and confirm manager, cables, and targets form one network. Rebuild the cable network in the manager GUI; if needed, use `/sfm bust_cable_network_cache`.
4. **Inspect capabilities and machine setup.** Verify sides, resource-specific I/O configuration, automation slots, activation, power type/voltage, circuits, catalysts, and presses. Ctrl+I GUI indices may differ from automation indices.
5. **Pair resource types.** Both statements need the intended type; fluids, energy, and chemicals need explicit prefixes and usable sides.
6. **Check trigger timing.** Respect configured minima, world/local clock choice, reload phase, and actual pulse periods. A held redstone signal is not repeated rising edges.
7. **Inspect registered sources.** Identify missing `forget` boundaries and sources that can bypass processing or enter the wrong face.
8. **Check budgets and storage.** Are quantities or retention targets too restrictive? Are receiving slots/tanks full or incompatible? Check byproducts for both stalls and silent loss.
9. **Use logs and performance data.** The manager Logs screen provides OFF/TRACE/DEBUG/INFO/WARN/ERROR. Detailed logging can auto-disable after execution; collect a focused trace. Compare execution time in the performance graph.
10. **Reduce to one machine and one batch.** Use a dedicated source, verified sides, and a simple input/output pair. Add filtering and array allocation only after that works. Older composter null-side behavior could bypass normal compost checks; use an explicit side and verify the installed version before moving valuable items.
11. **Report a reproducible bug.** Include Minecraft/loader/SFM/pack versions, program, label bindings, sides/slots, machine settings, reproduction steps, and logs. Use the official tracker linked in `config-and-versions.md`.

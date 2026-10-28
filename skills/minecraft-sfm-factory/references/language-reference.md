# SFML logistics language reference

Read this for details beyond SKILL.md section 4. This reference covers factory logistics, not the experimental Client Manager language extensions.

Notation in syntax diagrams: `[ ]` means optional, `< >` names a placeholder, `*` means repetition, and `|` separates alternatives. Diagrams are not paste-ready programs. `sfml` blocks are complete programs; `sfml-snippet` blocks demonstrate statements inside a trigger and may need surrounding application logic.

## Lexical rules

- Keywords are case-insensitive: `EVERY` and `every` are equivalent. Resource identifiers are normalized to lowercase; write them that way.
- `--` begins a comment extending to the end of the line.
- Spaces, newlines, and indentation do not define scope.
- Numbers are **nonnegative integers**, such as `20`, `1000`, and `4096000`. No decimals, negative numbers, thousands separators, or `1k` suffixes. Timer periods must be positive.
- Bare identifiers contain ASCII letters, digits, `_`, and `*`; they cannot start with a digit.
- Strings use double quotes; an embedded quote can be written as `\"`.
- Quote labels containing non-ASCII characters (`"café"`), spaces or punctuation (`"storage a"`, `"my-chest"`), leading digits (`"1st chest"`), or reserved words (`"east"`, `"input"`).
- Reserved words include `input output from to end do if then else has each in by side slot slots north east south west name every plus tag with without except retain empty round robin label block not and or true false null some one lone overall tick ticks pulse gt lt eq le ge`. Quote labels when uncertain.
- Some keyword-like tokens are also valid identifiers, including `top bottom left right front back redstone global second seconds`. Availability depends on version; `redstone` became usable in these roles in the 4.14–4.16 series.
- **Quoting labels and quoting resource patterns have different consequences.** Quoted labels are literal names. Bare resource `*_ingot` expands `*` to `.*`; quoted resource `".*_ingot"` is a regular expression and needs the dot explicitly.
- Maximum label length is 256 characters from 4.22.0 onward; earlier versions used 80.

## Program structure

```text
[name "Program name"]
every ... do ... end
every ... do ... end
```

An optional `name` must precede the triggers and becomes the disk's name. Logistics statements belong inside triggers. Each trigger has its own registered inputs, which are cleared when it finishes.

## Triggers

```text
every [<period>] [global | g] [(plus | +) <offset>] <time unit> do
    <statements>
end

every <period> <time unit> offset by <offset> <offset unit> do
    <statements>
end

every redstone pulse do
    <statements>
end
```

| Form | Behavior |
|---|---|
| `every tick do` / `every 1 tick do` | Every tick; under defaults, only supported energy-only I/O can run this fast |
| `every 20 ticks do` | Every 20 game ticks, nominally one second at 20 TPS |
| `every 5 seconds do` | Every 100 ticks; `second` and `seconds` are equivalent on fixed versions |
| `every seconds do` | Omitted period defaults to one |
| `every 20 global ticks do`, `every 20g ticks do`, `every 20 g ticks do` | Align with world time instead of the manager's local clock |
| `every 20 plus 5 ticks do`, `every 20+5 ticks do` | Legacy offset of five ticks |
| `every 20+1 seconds do` | 400-tick period, 20-tick offset on fixed versions |
| `every 20g+5 ticks do`, `every 20 global plus 5 ticks do` | World-time alignment plus legacy offset |
| `every 20 ticks offset by 5 ticks do` | Explicit offset on supporting newer builds; offset units may differ |
| `every redstone pulse do` | Run on a rising edge received by the manager; timer minimum does not apply |

The default local clock begins at zero on placement and is randomized on world reload. Timers run when `clock % period == offset`. World-time alignment can synchronize managers; it does not synchronize machine completion. Do not combine legacy `+` and `offset by` in one interval.

Server configuration controls minimum periods:

| Setting | Default |
|---|---|
| `timerTriggerMinimumIntervalInTicks` | 20 ticks |
| `timerTriggerMinimumIntervalInTicksWhenOnlyForgeEnergyIOStatementsPresent` | 1 tick |

The shorter minimum applies when all I/O in the trigger uses supported `forge_energy` or `mekanism_energy` types. Otherwise, a shorter period fails with `Minimum trigger interval is N ticks.` `every 0 ticks` and fractional periods are invalid.

Version caveats: the `second` issue in 4.20.0 was fixed in 4.22.0; seconds-based legacy offsets were fixed in 4.24.0. Newer development builds warn about ambiguous legacy offsets. Pulse width is not the rising-edge interval: a one-tick-wide pulse does not establish one transfer every tick. Measure the actual clock and the manager's execution timing.

## Input and output syntax

```text
input  [<limit>, ...] [except <resource>, ...] from [each] <label access>
output [<limit>, ...] [except <resource>, ...] to [empty slots in] [each] <label access>

<limit> = [<quantity> [each]] [retain <count> [each]] [<resource> [or <resource>]*] [with|without <tag condition>]
<label access> = <label>[, <label>]* [round robin by label|block] [<side>[, <side>]* side | each side] [slots <ranges>]
```

Clause order is fixed: **limits → exclusions → from/to → empty slots in → each → labels → round robin → sides → slots**. Commas separate limits, labels, or sides according to their position.

```sfml-snippet
input 5 retain 2 iron_ingot except gold_ingot from each a, b top, west side slots 0-3
output to results
```

`from a input ...` and `to b output ...` are also accepted but are discouraged here for consistency. Without an explicit resource type or filter, I/O operates on items.

```sfml
-- Register a's items, then transfer them directly to b.
every 20 ticks do
    input from a
    output to b
end
```

## Resource identifiers

Full form: `[sfm:]<resource type>:<namespace>:<name>`. Missing segments act as wildcards according to the shortened form. The default resource type is item.

| Written form | Interpretation |
|---|---|
| `stone` | Items named stone in any namespace, not only minecraft |
| `minecraft:diamond` | Item minecraft:diamond; two segments mean namespace:name |
| `thermal:phytogro` | Item thermal:phytogro |
| `item:minecraft:redstone` | Explicit redstone-dust item |
| `fluid::` | All fluids; equivalent to `fluid:*:*` |
| `fluid::water` | Water in any namespace |
| `fluid:minecraft:water` | Exact Minecraft water |
| `fluid:minecraft:` | All fluids in namespace minecraft |
| `fe::` | Forge Energy |
| `gas::`, `gas:mekanism:nuclear_waste` | Mekanism gas type, or chemical alias on unified builds |
| `infusion::`, `slurry::`, `pigment::` | Separate Mekanism types on older builds; unified aliases on MC 1.21.1 |
| `chemical::` | Unified Mekanism chemical type on MC 1.21.1 builds |
| `sfm:forge_energy:forge:energy` | Full four-segment form, seldom necessary |

| Type | Aliases and availability |
|---|---|
| `item` | Default type |
| `fluid` | Fluid capabilities |
| `forge_energy` | Aliases `fe`, `rf`, `energy`, `power`; eligible for the energy-only timer minimum |
| `mekanism_energy` | MC 1.19.2 integration; long-valued transfers, still limited by actual capabilities |
| `chemical` | MC 1.21.1 integration; `gas`, `infusion`, `slurry`, `pigment` are aliases there; needs Mekanism |
| `redstone` | Read emitted signals from world blocks, SFM 4.27.0+; experimental buffers have separate storage behavior |

Common mistakes:

```text
fluid:water             -- ITEM named water in namespace fluid
fluid::water            -- fluid named water in any namespace
fluid:minecraft:water   -- exact fluid
fe                      -- item filter, not energy
fe::                    -- energy
```

The type segment must be literal, not a wildcard or regex. Missing integrations can produce `Program references an unknown resource type "xxx"`; server configuration can reject a type as disallowed.

### Resource alternatives and regular expressions

From 4.20.0 onward, `or` combines resources under one limit. Commas introduce independent limits.

```sfml-snippet
input 5 stone or dirt from a       -- five items total across these resources
output to b
forget
input 5 "stone|dirt" from a        -- equivalent resource-name regex
output to b
forget
input 5 stone, dirt from a         -- up to five stone PLUS unrestricted dirt
output to b
```

Quoted regex matches the entire resource segment:

| Regex feature | Resource pattern | Example matches |
|---|---|---|
| `.` | `"...._ingot"` | iron_ingot, not copper_ingot |
| `.*` | `".*_ingot"` | Any name ending in _ingot |
| `+` | `"stone.+"` | stone_axe, not stone |
| `?` | `"bricks?"` | brick, bricks |
| Repetition | `"oak_wo{2}d"` | oak_wood |
| Group/alternation | `"(iron\|gold)_ingot"` | iron_ingot, gold_ingot |
| Negative lookahead | `"iron_(?!block).*"` | iron_ names whose suffix does not begin with block |
| End anchor | `"(?!quartz$).+"` | quartz_block, not quartz |
| Character class | `"[fl]eather"` | feather, leather |
| Negated character class | `"leather_[^hlb].*"` | leather_chestplate, not leather_helmet |
| Digit | `"rocket_t\d"` | rocket_t1 |

Do not use `"[^(iron_ingot)].*"` to exclude iron ingots. It excludes names beginning with any listed character, including i, r, o, n, _, g, t, and parentheses. Prefer `except iron_ingot` or `"(?!iron_ingot$).+"`.

Colons remain resource-segment separators inside quotes. `"mysticalagriculture:.*_essence"` is valid; a regex noncapturing group `(?:...)` contains a colon and must be replaced with `(...)` here.

Obtain real IDs using Ctrl+Space with the resource in a labeled container, F3+H, or JEI/EMI. Registry-ID and tag filters do not distinguish same-ID NBT/data-component variants. Transport preserves those components; use an exact component-aware sorter before SFM when variants must be separated.

## Quantities, retention, and per-resource each

```text
[<quantity> [each]] [retain <count> [each]] [<resource>]
```

A quantity is a transfer budget. Input `retain K` leaves K matching resources at the source; output `retain K` fills the destination to K. `each` immediately after a number applies that number separately to every matching resource kind. Matching more than 512 resource kinds is unsupported for this expansion; avoid broad registry patterns.

| Form | Meaning |
|---|---|
| `input 1 from a` | One item collectively |
| `input 1 *_ingot from a` | One ingot collectively |
| `input 1 each *_ingot from a` | One of each matching ingot |
| `input retain 5 from a` | Leave five items collectively |
| `input retain 5 *_ingot from a` | Leave five ingots collectively |
| `input retain 5 each *_ingot from a` | Leave five of each ingot kind |
| `input 3 retain 6 *_ingot from a` | Leave six ingots collectively; move at most three |
| `input 3 each retain 6 *_ingot from a` | Leave six collectively; move at most three per kind |
| `input 3 each retain 6 each *_ingot from a` | Leave six per kind; move at most three per kind |
| `input 1000 fluid:: from a top side` | At most 1,000 mB of fluid |
| `output 7 to b` | At most seven collectively across b's blocks |
| `output retain 12 to b` | Fill b to twelve matching items collectively |
| `output 5 each retain 9 each *_ingot to b` | Move at most five per kind, filling each kind to nine |
| `output retain 2 *_seeds to each m` | Fill every m block to two matching seeds collectively |

Each comma-separated limit has its own budget:

```sfml-snippet
input
    20 retain 1 red_sand,   -- leave one red sand; move at most twenty
    retain 1 coal          -- leave one coal; move the rest
from a
output to b
```

Retention had known bugs before 4.22.0. Check the installed version when observed behavior differs.

## With and without: tag filters

`with` is available from 4.19.0; use `without` on 4.20.0+.

```text
with [tag] [#]<tag matcher>
without [tag] [#]<tag matcher>
```

Expressions support `not`, `and`, `or`, and parentheses. `without X` negates the whole expression. A matcher is `[namespace:]path`: omit the namespace to match any namespace; `*` matches within a path segment and `**` spans any depth. `with #forge:gems`, `with tag forge:gems`, and `with tag #forge:gems` are equivalent.

```sfml-snippet
input with #ores from a
input with tag #forge:ores_in_ground/deepslate from a
input without tag #minecraft:planks from a
input minecraft: with #ingots from a
input with (not #needs_stone_tool) and #ores/* from a
input with #test:** from a
output with #ingots or tag chests except iron_ingot to b
```

These are tag-syntax examples, not a promise that those tags exist in the user's pack. Many 1.20.1 Forge packs use `forge:` while 1.21+ NeoForge uses `c:`. Block tags can also classify their corresponding items, for example `minecraft:mineable/shovel`. An item ID does not imply an identically named tag exists. The `except` clause itself does not accept a `with` expression.

## Except: statement-wide exclusions

```text
input|output [<limits>] except <resource>, <resource> from|to <label access>
```

Excluded IDs may use wildcards or regex.

```sfml-snippet
input *_ingot except copper_ingot from a
output except minecraft: to b
output with #storage_blocks except iron_block to c
forget
input *iron*, *copper* except *block* from chest
output to metals
```

## Label access

### Per-block each

| Form | Meaning |
|---|---|
| `input 5 from c` | Up to five collectively across c |
| `input 5 from each c` | Up to five from every c block |
| `output 1 to b` | Up to one collectively; only one block can receive that item |
| `output 1 to each b` | Up to one per b block |
| `output retain 2 to each b` | Fill each b block to two |

`from each` and `to each` apply to blocks; `each` after a number applies to resource kinds. A larger aggregate output budget may be split among several blocks. Use round robin if a transfer must target only one block.

### Round robin, 4.14.0+

```text
input|output ... from|to a, b round robin by label|block
```

- `by label` selects one label per execution and rotates. A block with several selected labels may appear more than once.
- `by block` selects one block per execution and rotates through blocks.
- Combining round robin with `each` does not produce ordinary per-block distribution; round robin takes precedence.
- Indices are tracked per statement and resource type and advance through resource-consuming execution. An unused input does not rotate; empty sources, shared input caches, and unexecuted branches affect advancement. Do not treat round robin as an independent clock.
- Prefer `retain` for normal distribution. The compiler warns about `by label` with one label and `by block` combined with `each`.

```sfml-snippet
input from source
output 128 dirt to dest round robin by block
forget
input from "storage a", "storage b" round robin by label
output 8 bone_meal to each dispenser
```

### Sides

```text
<side>[, <side>]* side
or: each side
```

| Side | Meaning |
|---|---|
| `top bottom north south east west` | Absolute directions |
| `left right front back` | Relative to the block's facing, 4.27.0+; falls back to null when no facing exists |
| `null` | Unspecified-direction capability, also used when side is omitted |
| `each side` | Six faces plus null, visited separately |

The word `side` is required. Capabilities and slot mappings may differ by face. A null capability is not universally usable; Mekanism null-side access can be read-only. Use concrete sides for fluid, energy, and chemical transfers. Redstone reads may deliberately omit the side to take the strongest signal.

```sfml-snippet
input fe:: from a top side
output fe:: to b east, front side
input gas:: from c top side
output retain 200 gas:: to each d top side
```

Multiple faces can expose the same underlying storage; do not assume they represent independent capacity. `each side` increases work and does not guarantee fair distribution.

### Slots

```text
slots <range>[, <range>]*
slot <range>                 -- singular synonym from 4.27.0
<range> = <number> | <number>-<number>
```

Slots follow the side qualifier. Ctrl+I and Export Inspector show GUI indices, which may differ from automation indices; check the capability mapping with the Network Tool and targeted transfers.

```sfml-snippet
input from a top side slots 0,1,3-4,5
output to b slots 24-26
forget
input from chest slot 5
output to chest slot 9
```

### Empty slots, 4.25.0+, output only

`output to empty slots in ...` skips occupied slots, including partially filled stacks. This can reduce insertion work in large storage but may consume empty slots faster. It does not provide input filtering.

```sfml
every 20 ticks do
    input from mob_loot
    output to empty slots in storage
end
-- Consolidate less frequently; measure this scan on large inventories.
every 300 seconds do
    input from storage
    output to storage
end
```

## Forget

```text
forget                  -- clear all registered inputs
forget a, b             -- clear registrations for these labels
```

Use this to isolate stages within one trigger. It does not move resources, undo transfers, reset consumed budgets, or wait for processing.

```sfml
every 20 ticks do
    input from a
    output 1 to b
    forget a
    input from c
    output to d         -- only c is registered here
end
```

## If, else if, and else

```text
if <condition> then
    <statements>
[else if <condition> then
    <statements>]*
[else
    <statements>]
end
```

One `end` closes the entire chain. There is no `elif`, `elseif`, or `otherwise`. Branches may contain nested conditions and ordinary logistics statements. Too many `if` statements in a trigger (default: more than ten) skip compiler simulation checks with a warning; execution itself is still allowed.

### Conditions

| Form | Meaning |
|---|---|
| `true`, `false` | Boolean constants |
| `(condition)`, `not condition` | Grouping and negation |
| `condition and condition`, `condition or condition` | Boolean combinations |
| `[set qualifier] <label access> has <comparison> <number> [<resources>] [with…] [except…]` | Inventory/resource count test |
| `redstone [<comparison> <number>]` | Manager's received redstone signal; read from world state at the audited commit |

Precedence is `not` > `and` > `or`; parenthesize compound conditions. Comparisons are `>`/`gt`, `<`/`lt`, `=`/`eq`, `<=`/`le`, and `>=`/`ge`. There is no `==`, `!=`, or `<>`; use `not (x has = 5)`.

| Set qualifier | Meaning |
|---|---|
| `overall`, or omitted | Sum matching resources across the selected blocks, then compare |
| `every`, `each` | Every selected block satisfies the comparison |
| `some` | At least one satisfies it |
| `one` | Exactly one satisfies it |
| `lone` | At most one satisfies it |

For three a chests holding 5, 5, and 10 stone:

| Condition | Result |
|---|---|
| `every a has = 5 stone` | False |
| `each a has >= 5 stone` | True |
| `some a has eq 5 stone` | True |
| `one a has = 5 stone` | False: two qualify |
| `lone a has = 5 stone` | False: two qualify |
| `overall a has eq 5 stone` | False: total is twenty |
| `a has eq 5 stone` | False: overall is the default |

A `has` test requires both comparison and quantity. Omitting the resource means all items, not fluids or energy. Use resource `or`, not commas. Side/slot selection is allowed before `has`. Verify that a station's label set is nonempty and connected before using `every` as evidence of readiness.

```sfml
every 20 ticks do
    input from a
    if a has > 5 then
        output 1 to b
    else if (b has >= 10 "(?!(gold|copper)).*_ingot") and (b has >= 2 paper) then
        output retain 4 to c
    else
        output to d
    end
    forget

    if each e top side has >= 200 gas:: then
        input gas:: from e top side
        output 200 gas:: to each f top side
    end
    forget

    input fe:: from g top side
    if redstone then
        output fe:: to g2 top side
    end
    if redstone < 10 then
        output fe:: to h top side
    end
end
```

`has` sees current inventory, including changes made earlier in the same trigger. For state transitions, use one `if … else if … end` chain to prevent several successive states from running in one invocation.

## Redstone

| Form | Meaning and availability |
|---|---|
| `every redstone pulse do … end` | Rising-edge trigger at the manager; longstanding support |
| `if redstone [>= n] then` | Manager's received signal strength; longstanding support |
| `if sensor [<side> side] has >= n redstone:: then` | Labeled block's emitted weak signal; 4.27.0+ |
| `item:minecraft:redstone` | Redstone-dust item, unrelated to signal I/O |

- Ordinary `redstone::` reads emitted strength from 0–15, not the signal entering that block. Omit the side to take the strongest of six faces; specify a side for that face. Ordinary world signals are read-only.
- At the audited commit, manager conditions and labeled world-signal reads query current world state. A capability handler may be cached without caching its measured strength. With multiple blocks, default `overall` sums signals; use `some`/`every` for per-block tests. Avoid `each side` here: it sums face readings and also the null-side maximum rather than returning a single 0–15 value.
- Experimental Resource Buffers (`sfm:buffer`) can store transferable redstone counts. Their comparator output is `min(stored count, 15)`. This is outside ordinary factory workflows and does not imply a general world-redstone output command.
- Use the established environment; do not ask for versions repeatedly. On known pre-4.27.0 versions, use manager redstone input or recommend upgrading instead of `redstone::`.
- Fast clocks bypass the timer minimum but need performance notes and in-game timing verification; see `advanced-patterns.md`.
- Tunnelled Factory Managers do not tunnel redstone signals.

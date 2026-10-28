---
name: minecraft-sfm-factory
description: Help build Minecraft automation with Super Factory Manager (SFM) and its SFML logistics language. Write, review, and debug programs; plan labels, machine arrays, and resource routing; investigate stalled machines and server lag. Use for SFM, Factory Managers, Inventory Cables, Label Guns, Program Disks, every ... do, input/output/forget/if statements, and item, fluid, energy, or Mekanism chemical transfers. Also use when an established SFM conversation asks to automate a product such as steel or nuclear fuel.
---

# Minecraft automation with Super Factory Manager

Use this skill as the starting reference for SFM logistics. Apply its version limits: if the user's version, official source, or observed behavior disagrees, investigate and correct the advice. SFML differs substantially from general-purpose languages. **Verify syntax here instead of completing it from memory.**

This file contains the core rules, workflow, execution model, syntax summary, and delivery checklist. Read files in `references/` as needed using section 1.

## 0. Essential rules

1. **Use the logistics syntax documented here.** Do not invent assignments, loops, functions, `;`, braces, `==`, `!=`, `while/for`, or `elif/elseif`. Experimental Client Manager features are outside this skill's factory-logistics scope; their existence does not make them suitable replacements. Check the relevant reference before declaring a task unsupported.
2. **`input` registers sources; `output` transfers resources.** An `input` alone moves nothing. There is no intermediate inventory inside the program.
3. **Pair input and output for each resource type.** `input from a` registers items only. Fluids, energy, and chemicals need explicit types on both statements: `fluid::`, `fe::`, and the version-appropriate chemical type.
4. **Specify a concrete side for fluid, energy, and chemical transfers.** Usually do so for machines' items as well. A missing side requests the `null` capability, which many machines restrict. Reading `redstone::` is an exception: without a side it reads the strongest of six faces.
5. **An output does not clear its registered inputs.** Separate machine feeding from product collection with `forget` or different triggers unless exact filters prove the flows cannot mix (section 5).
6. **Quote labels containing spaces, punctuation, non-ASCII characters, leading digits, or reserved words.** Examples: `"Phytogenic Insolator"`, `"1st buffer"`, `"east"`.
7. **Close each trigger and each complete if chain with one `end`.** An `else if` branch does not get its own `end`.
8. **Respect configured timer minima.** Defaults are 20 ticks for ordinary transfers and 1 tick for energy-only I/O. Item transfers in `every 5 ticks` fail compilation under default settings.
9. **Deliver a label map with every program**, identifying blocks and access sides. Complete section 6 before delivery.
10. **Establish the environment once and reuse it.** Ask for missing SFM/Minecraft versions, loader, and modpack information. Do not assume support for `without`, resource `or`, `empty slots in`, relative sides, or `offset by`. Manager redstone triggers and conditions are longstanding; labeled-block `redstone::` requires SFM 4.27.0+.
11. **Verify uncertain behavior in game.** Use the Network Tool, Ctrl+Space, the Container Inspector, and manager logs. Do not promise an interface works without evidence.
12. **Read the relevant reference before using details absent from this file.** Do not fill gaps from memory.
13. **Prefer the simplest adequate design.** Apply section 2.4. Include a **Performance notes** paragraph whenever section 2.5 applies.
14. **Do not invent recipes, resource IDs, or machine capabilities.** Resolve an unclear target or recipe chain before writing a production program. If the user explicitly requests an immediate draft, identify all unverified assumptions, mark them with `-- UNVERIFIED`, and provide verification steps.

Before writing a production program, establish:

| Requirement | Evidence or action |
|---|---|
| Exact target product | User's description or JEI/EMI item name; offer choices if ambiguous |
| Modpack and recipe changes | Ask once early, then retain the answer |
| Recipe chain, machines, quantities, and byproducts | Prefer the user's JEI/EMI; cite versioned official sources when researching |
| Resource IDs where filtering is necessary | Ctrl+Space with resources in a labeled container, F3+H, or JEI/EMI |
| Machine sides, slots, and settings | Specify a supported configuration as part of the design; verify uncertain capabilities |

Read `references/recipe-learning.md` for the discovery workflow. Avoid asking users to repeat information already supplied or to approve research they have already authorized.

Supported alternatives to common capability gaps:

| Request | Limitation in this logistics workflow | Alternative |
|---|---|---|
| Remember a state or count | No general-purpose logistics variables | Item counts in isolated slots; see counter registers in `advanced-patterns.md` |
| Sort same-ID items by NBT/data components | Registry-ID and tag filters do not distinguish those variants | Separate them using exact component-aware filtering, then transport with SFM |
| Emit a world redstone signal directly | No ordinary redstone-output statement | Change a container's contents and read it with a comparator |
| Craft directly or simulate player interaction | SFM moves resources; the machine performs the operation | Use a machine, crafter, AE crafting, or a suitable interaction mod |
| Access a block with no usable capability | SFM needs an exposed inventory/resource capability | Check other sides with the Network Tool or use another block/interface |

## 1. Task routing

| Task | Workflow |
|---|---|
| Write a new production program | Discover requirements in 2.0 and `recipe-learning.md`; follow section 2; adapt `templates.md`; read relevant `mod-notes.md` entries |
| Review a program | Apply section 6 and `troubleshooting.md`; provide the complete corrected program |
| Diagnose errors or stalled transfers | Read `troubleshooting.md`; start with the exact error if available |
| Improve throughput or server performance | Read `efficiency.md`, apply 2.4, and explain the before/after behavior |
| Explain syntax or concepts | Start with sections 3–4, then `language-reference.md` |

Read these references before addressing their topics:

| Topic | Reference |
|---|---|
| Regex, tags, exclusions, round robin, empty slots, set qualifiers, timer offsets, redstone details | `references/language-reference.md` |
| Worked transfer, furnace, machine-array, Insolator, Inscriber, or fusion examples | `references/templates.md` |
| Errors, warnings, stalled machines, and review pitfalls | `references/troubleshooting.md` |
| Arrays of dozens of machines, mixed outputs, partial utilization, machine selection | `references/efficiency.md` |
| Label Gun, Network Tool, editor shortcuts, cables, Water Tanks, Tunnelled Managers | `references/items-and-tools.md` |
| Server configuration, commands, feature versions, conflicting sources | `references/config-and-versions.md` |
| Any uncertainty about the target, recipe chain, resource IDs, or machine interface | `references/recipe-learning.md` |
| Mekanism, AE2/addons, GTCEu, Mystical Agriculture, Productive Bees, Thermal, MI, ritual mods, or modpacks | `references/mod-notes.md` |
| Ordered batches, state, chemical chains, Pattern Providers, byproducts, fast pulses, feedback loops, buffered energy, indirect redstone | `references/advanced-patterns.md` |

## 2. Assistance workflow

### 2.0 Discover the production requirements

For “automate X,” resolve the following progressively. Ask only the most useful 1–3 questions per turn and skip known information.

1. **Environment:** Minecraft, loader, SFM, modpack and pack version, and whether recipes are customized. Retain this context until the user changes it. In modified packs, use JEI/EMI rather than assuming upstream recipes.
2. **Target:** identify the exact item or resource. Terms such as “nuclear fuel,” “steel,” and “processor” may be ambiguous; offer candidates without choosing for the user.
3. **Recipe chain:** guide the user through JEI/EMI one or two steps at a time, including intermediate products. Build a table of machines, inputs, outputs, byproducts, and quantities. Resolve remaining ambiguities before implementation. When research is needed, use available authorization and cite the source and version.
4. **Interfaces:** propose machine orientation, resource-specific side settings, slots, circuits, catalysts, and transfer ownership. Disable automatic ejection only where it conflicts with SFM. Adapt if the user's layout prevents the proposed setup.

Until the target and chain are clear, provide discovery guidance instead of a speculative production program. An explicitly requested immediate draft may use marked assumptions and must include checks for them.

### 2.1 Additional details to establish when relevant

| Detail | Why it matters |
|---|---|
| Machine counts and distinct outputs | Input allocation, receiving capacity, and throughput |
| Resource types | Matching I/O types and suitable capabilities |
| Source, destination, and intermediate buffers | Labels, transfer order, and `forget` boundaries |
| Existing program and exact diagnostics | Reproducing and correcting failures |

### 2.2 Design sequence

1. Map `source → machine input → processing → machine output → destination`.
2. Label roles: input storage, each machine group, results, power, water, and buffers. Multiple blocks may share a label; a block may have several labels. Group identical machines by recipe when that simplifies allocation.
3. Specify the access side and any verified automation-slot restrictions for each route.
4. Separate energy into its own `every tick` trigger. Start ordinary item/fluid work at 20 ticks; separate feeding from collection.
5. Simplify using 2.4, assess 2.5, and complete section 6.
6. Deliver the program, label map, build instructions, operating limits, and any required performance notes.

### 2.3 Delivery format

````text
Approach: Explain the resource flow in one or two sentences.

Label map:
| Label | Blocks | Access sides / automation slots |
| source | Input chest | top |
...

Program:
```sfml
...
```

Build and configure:
1. Insert a Program Disk into the Factory Manager and connect all labeled blocks
   using Inventory Cables. The manager also acts as cable.
2. Paste the program into the disk editor: Ctrl+E opens it from the manager;
   Shift+Enter saves and closes it.
3. With the Label Gun, Shift+right-click the manager to pull labels from the disk.
   Apply them to blocks, then right-click the manager to push the mappings back.
4. Configure orientation, sides, slots, catalysts/circuits, automatic ejection,
   and any Pattern Provider lock and product-return path.
5. Review the disk warnings and test one complete batch before scaling up.

Operating limits: Explain timing, full storage, partial transfers, and recovery.
Performance notes: When 2.5 applies, identify the expensive work, simpler options,
and what to compare in the manager's performance graph.
````

### 2.4 Simplification checklist

1. **Use native automation where sufficient.** Machine ejection, pipes, AE/RS interfaces, slot locks, and addon features may handle a fixed route more simply. Reserve SFM for allocation, conditions, or routing that benefits from it.
2. **Group equivalent machines under one label.** Use `to each`/`from each` rather than one code block per machine. Ordered recipe stations may still need separate labels.
3. **Use `retain` for inventory targets** instead of repeated `if … has` checks.
4. **Use output order for overflow:** primary storage, then backup, then a disposal route only for resources the user allows discarding.
5. **Specify sides.** `each side` visits six faces plus null. Use it temporarily for diagnosis, then narrow the route.
6. **Avoid unnecessary resource IDs.** Dedicated source containers and fixed recipes can eliminate filters. Where needed, prefer precise IDs; broad patterns with per-resource `each` can enumerate many registry entries. Qualify same-named mod resources, for example `fluid:gtceu:sulfuric_acid`.
7. **Use only the frequency needed.** Start ordinary work at 20 ticks and nonurgent collection/storage work at 40–200 ticks. Reserve 1-tick timers for supported energy-only I/O under the configured minima.
8. **Use state registers and fast redstone clocks last.** Try retention, verified slots, separate triggers, or a Pattern Provider locked until its result returns.
9. **Provide a pause mechanism when useful.** A lever powering the manager can gate logistics with `if redstone > 0 then … end`. Already-started machines may continue processing; gate energy or the machine separately if a full shutdown is required.

### 2.5 When performance notes are required

These are review heuristics, not measured hardware limits:

- A state machine or counter register is used.
- A trigger has at least three `if` statements or nested conditions.
- A pulse trigger runs from a clock faster than once per 20 ticks.
- `each` visits roughly 64+ blocks, especially with `each side` or broad regex.
- Large storage is scanned in full every 20 ticks or faster.
- There are at least five timer triggers, or the program approaches the disk length limit.

## 3. Core concepts and execution model

- **Factory Manager:** executes the program on its inserted Program Disk.
- **Program Disk:** stores program text and label-to-position mappings.
- **Label:** names one or more blocks; assign positions with the Label Gun.
- **Cable network:** connects the manager to accessible labeled blocks. A label may exist in code while its blocks remain disconnected.
- **Program:** an optional `name` followed by independent timer or redstone-pulse triggers containing ordered statements.

```text
When a trigger runs, process its statements from top to bottom:
  input  → register source blocks, resource filters, and transfer budgets
  output → transfer matching resources directly from registered sources to targets
  forget → remove all or selected source registrations
  if     → execute only the selected branch
At trigger completion, discard its registrations; other triggers are independent.
```

- Outputs run in order, subject to source budgets, target limits, and capacity.
- An input's quantity limit is shared by subsequent outputs. With `input 10 from a,b`, then `output 1 to z`, `forget b`, and `output to z`, the last output can move at most nine more items from a.
- Sources and targets are processed sequentially. Earlier machines may consume scarce materials first; `to each` does not ensure every machine gets a complete recipe.
- `has` reads actual inventory when evaluated. A transfer earlier in the same trigger can change a later condition immediately.
- Cost grows with blocks, sides, slots, resource matching, and execution frequency. Measure substantial designs in the manager's performance graph.

## 4. Language quick reference

For details beyond this summary, read `references/language-reference.md`.

### 4.1 Lexical rules

- Keywords are case-insensitive. Write resource IDs in lowercase. `--` starts a line comment; whitespace and indentation do not define blocks.
- Numbers are nonnegative integers: no decimals, negatives, thousands separators, or `1k`. The latter can parse as quantity 1 of resource `k`.
- Bare identifiers use ASCII letters, digits, `_`, and `*`, and cannot begin with a digit.
- Quote labels with spaces, punctuation, non-ASCII characters, leading digits, or reserved words. `"storage a"` and `"east"` are labels; bare `east` is a direction keyword. Quoting a label is a safe default.
- Some keyword-like names, including `top bottom left right front back redstone global second seconds`, are accepted as identifiers in supported versions.
- Bare `*_ingot` is a wildcard; quoted `".*_ingot"` is regex. Quoting changes resource-pattern semantics. Colons separate resource-ID segments even inside quotes; use `(…)`, not `(?:…)`, for grouping.

### 4.2 Programs and triggers

```text
[name "Program name"]
every <interval> do <statements> end
every redstone pulse do <statements> end
```

| Form | Meaning |
|---|---|
| `every tick do` | Every tick; use for supported energy-only I/O under default settings |
| `every 20 ticks do` / `every 5 seconds do` | Every 20 ticks / 100 ticks; `every seconds do` means every second |
| `every 20 global ticks do` / `every 20g ticks do` | Align with world time |
| `every 20 plus 5 ticks do` / `every 20+5 ticks do` | Legacy 5-tick offset; newer builds warn |
| `every 20 ticks offset by 5 ticks do` | Explicit offset on supporting builds; do not combine with legacy `+` |
| `every redstone pulse do` | Run on a rising edge at the manager; timer minimum does not apply |

The ordinary timer minimum defaults to 20 ticks; supported energy-only I/O defaults to 1. Smaller intervals produce `Minimum trigger interval is N ticks.` The local manager clock is randomized on world reload. Timers due on the same tick run in source order. Pulse triggers are independent. Keep logistics statements inside triggers and put `name`, if present, before them.

### 4.3 Input and output

```text
input  [<limit>, ...] [except <resource>, ...] from [each] <label access>
output [<limit>, ...] [except <resource>, ...] to [empty slots in] [each] <label access>

<limit> = [<quantity> [each]] [retain <count> [each]] [<resource> [or <resource>]*] [with|without <tag condition>]
<label access> = <label>[, <label>]* [round robin by label|block] [<side>[, <side>]* side | each side] [slots <ranges>]
```

Clause order is **limits → exclusion → from/to → empty slots in → each → labels → round robin → sides → slots**.

```sfml-snippet
input 5 retain 2 iron_ingot except gold_ingot from each a, b top, west side slots 0-3
output to b
```

- No explicit filter means items: `input from a` and `output to b`.
- Commas separate independent limits: `5 stone, dirt` means five stone plus unrestricted dirt. `5 stone or dirt` shares one budget (4.20.0+).
- `except` excludes resources for the whole statement.
- Tags: `with #forge:ores` (4.19.0+), `without tag #minecraft:planks` (4.20.0+). Verify actual tags in the user's pack.
- `empty slots in` is output-only (4.25.0+); it skips occupied slots, including partial stacks.
- `round robin` chooses one label or block per execution (4.14.0+). Prefer `retain` for ordinary array feeding.

### 4.4 Resource IDs

Full form: `[sfm:]<type>:<namespace>:<name>`. The default type is item.

| Form | Meaning |
|---|---|
| `stone` | Items named stone in any namespace |
| `minecraft:diamond` | Two segments: item namespace and name |
| `item:minecraft:redstone` | Explicit redstone-dust item |
| `fluid::` / `fluid::water` / `fluid:minecraft:water` | All fluids / water in any namespace / exact water |
| `fe::` | Forge Energy; aliases include `fe`, `rf`, `energy`, and `power` for `forge_energy` |
| `gas::`, `infusion::`, `slurry::`, `pigment::` | Mekanism types on older builds; aliases for unified `chemical::` on MC 1.21.1 builds |
| `mekanism_energy::` | Mekanism energy support on MC 1.19.2 only |
| `redstone::` | Read a labeled block's emitted signal, SFM 4.27.0+ |

`fluid:water` is an item in namespace `fluid`; use `fluid::water`. Bare `fe` is an item filter; use `fe::`.

Common tags differ by platform: many MC 1.20.1 Forge packs use `#forge:…`; MC 1.21+ NeoForge commonly uses `#c:…`. Check rather than inferring a tag from an item ID.

**Registry-ID/tag filters cannot distinguish same-ID NBT or component variants.** Examples include `productivebees:configurable_honeycomb`, potions, and enchanted books. SFM preserves their components during transport, but these filters do not select variants by them. Use precise component-aware AE2/RS or other filtering into dedicated containers first. Do not improvise a regex as a component filter.

An unavailable integration can produce `Program references an unknown resource type "xxx"`.

### 4.5 Quantities, retention, and each

| Form | Meaning |
|---|---|
| `input 1 from a` | One item across all a blocks |
| `input 1 each *_ingot from a` | One of each matching resource |
| `input retain 5 from a` | Leave five matching items at the source |
| `input 3 retain 6 *_ingot from a` | Leave six ingots collectively; move at most three |
| `input 5 from each c` | Up to five from each c block |
| `output 7 to b` | Up to seven across all b blocks, possibly split |
| `output 1 to each b` | Up to one for each b block |
| `output retain 12 to b` | Fill the destination to twelve matching items |
| `output retain 8 to each m top side` | Fill each machine to eight |
| `input 1000 fluid:: from a top side` | Up to 1,000 mB of fluid |

**Input retention leaves resources behind; output retention fills to a target.** Before 4.22.0, retention had known bugs; check the version if results disagree.

### 4.6 Sides and slots

- Absolute sides: `top bottom north south east west`. Relative sides: `left right front back` (4.27.0+).
- Omitted side means `null`; `each side` visits six faces plus null. Capabilities may expose different slots on each face.
- Include the word `side`: `top side`, `top, west side`.
- Put slots after sides: `from a top side slots 0,1,3-4`. Singular `slot` is supported in 4.27.0+.
- Specify concrete sides for fluid, energy, and chemical transfers. Mekanism null-side access can be read-only.
- Ctrl+I displays GUI slot indices, which may differ from automation indices. Confirm the actual capability and mapping with the Network Tool and in-game tests.

### 4.7 Forget and conditions

```text
forget              -- remove all registered inputs
forget a, b         -- remove registrations for these labels

if <condition> then
    <statements>
[else if <condition> then
    <statements>]*
[else
    <statements>]
end                 -- one end for the entire chain
```

| Condition | Examples |
|---|---|
| Inventory | `a has >= 64 iron_ingot`, `a has > 5`, `a top side has >= 1000 fluid::` |
| Manager redstone input | `redstone`, `redstone >= 8` |
| Boolean combinations | `not`, `and`, `or`, parentheses; precedence is not > and > or |
| Multiple blocks | `overall` (default sum), `every`/`each`, `some`, `one`, `lone` |

Use `> < = <= >=` or `gt lt eq le ge`. There is no `==` or `!=`; write `not (a has = 5)`. A `has` condition requires a comparison and number. Resource alternatives use `or`, not commas. Parenthesize compound conditions.

### 4.8 Redstone meanings

| Form | Meaning |
|---|---|
| `every redstone pulse do … end` | Trigger on a rising edge received by the manager |
| `if redstone [>= n] then` | Check the manager's received signal strength; the audited commit reads world state directly |
| `if sensor has > 0 redstone:: then` | Read the labeled block's emitted weak signal, 0–15; without a side, take the maximum of six faces |
| `item:minecraft:redstone` | Redstone-dust item |

Ordinary world `redstone::` is read-only. Tunnelled Managers do not tunnel redstone signals.

## 5. Transfer ordering

Registered sources remain available after an output. This illustrative **incorrect** flow can bypass processing:

```text
every 20 ticks do
    input from raw_materials bottom side
    output to crusher top side
    input from crusher bottom side     -- sources now include raw materials AND crusher
    output to results top side         -- raw materials may go directly to results
end
```

**Option 1: clear registrations between stages.**

```sfml
every 20 ticks do
    input from raw_materials bottom side
    output to crusher top side
    forget
    input from crusher bottom side
    output to results top side
end
```

**Option 2: use independent triggers.**

```sfml
every 20 ticks do
    input from raw_materials bottom side
    output to crusher top side
end
every 20 ticks do
    input from crusher bottom side
    output to results top side
end
```

**Option 3: constrain both flows with exact filters.** Use this only for a verified fixed recipe whose input and output sets do not overlap. The following uses the sourced Ex Deorum sand-to-dust example; it does not imply any generic crusher can perform that recipe.

```sfml
every 20 ticks do
    input with #minecraft:sand from raw_materials bottom side
    output with #minecraft:sand to processing_machine top side
    input exdeorum:dust from processing_machine bottom side
    output exdeorum:dust to results top side
end
```

- Different resource types are isolated: item and chemical transfers do not inherently require `forget` between them. Two chemicals going to different sides do need exact filters or a `forget` boundary.
- Each input needs a consuming output, and each output needs an earlier input of the same type.
- Clearing registrations does not wait for a machine to finish. Product collection can see only what is currently available.
- Do not periodically remove and reinsert ingredients during a long recipe; that can interrupt processing.

## 6. Pre-delivery checklist

**Structure and compatibility**

- [ ] Optional `name` precedes triggers; all logistics statements are inside triggers.
- [ ] Each trigger and complete if chain has its required `end`; every `if` has `then`.
- [ ] No invented general-purpose syntax or experimental client features.
- [ ] Positive timer intervals satisfy the server's minima; energy-only work is separate.
- [ ] Features match the user's version, especially tags, resource `or`, empty slots, relative sides, and offsets.

**Transfers**

- [ ] Every output has a matching registered input; no unused inputs remain unintentionally.
- [ ] Non-item types use correct prefixes; fluid/energy/chemical transfers specify sides.
- [ ] Two-part IDs are items; fluid IDs use `fluid::name` or `fluid:namespace:name`.
- [ ] Clauses are in order; `side` is explicit and precedes `slots`; empty slots is output-only.
- [ ] Commas, wildcards, regex, label quoting, and exact namespaces mean what the design needs.
- [ ] Retention direction, per-resource `each`, and per-block `each` match the intended budgets.
- [ ] Feed/collection stages cannot share unintended sources; use `forget` or separate triggers.

**Conditions and allocation**

- [ ] Each `has` includes a valid comparison and quantity; compound conditions are parenthesized.
- [ ] State transitions use an `else if` chain and verify actual progress before advancing.
- [ ] Every station receives a complete recipe; aggregate counts alone do not prove this.

**Performance and resources**

- [ ] Apply 2.4 and include performance notes when 2.5 applies.
- [ ] All products and byproducts have adequate receiving capacity and throughput.
- [ ] Check whether full storage stops the machine or loses resources; disposal is limited to permitted byproducts.

**Evidence and delivery**

- [ ] Target and recipe are established, or the user requested an explicitly marked draft.
- [ ] IDs and interface claims are user-confirmed or sourced; unverified assumptions have checks.
- [ ] Include a label map and one-time setup: sides, slots, circuits/catalysts, ejection, provider locks and return paths.
- [ ] Explain unsupported requirements and workable alternatives.
- [ ] For large arrays, review `efficiency.md`; verify capacity, machine options, and full-storage behavior.
- [ ] Ask the user to review disk warnings and test a full batch, missing inputs, full targets, power loss, and reload recovery.

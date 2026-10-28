# Discovering a production recipe

Read this **before writing a production program** whenever the target, recipe chain, resource IDs, or machine interface is uncertain. This file is a discovery method, not a recipe database. Recipes change between versions and modpacks.

## Why memory is insufficient

| Required fact | What can change |
|---|---|
| Recipe chain: machines, steps, ingredients, quantities, outputs | Mod updates; KubeJS, CraftTweaker, datapacks, and other pack changes |
| Resource IDs and tags | Renames, platform tag conventions, and same-named resources from different mods |
| Machine interface: sides, slots, power, settings | Mod version, orientation, side configuration, upgrades, and the actual world layout |

A syntactically valid program can still be unusable: no recipe starts, inputs reach the wrong inventory, or the disk warns `Resource "x" was not found.`

## Evidence levels

| Level | Source | How to use it |
|---|---|---|
| **A — Confirmed** | User's JEI/EMI, actual Ctrl+Space IDs, or explicit description | Suitable for implementation |
| **B — Sourced** | Matching-version official documentation or mod source | Cite source/version and ask the user to cross-check JEI, since packs can override it |
| **C — Recalled** | Model memory or a plausible naming convention | Use only to frame questions; do not present it as a verified recipe or ID |

Resolve missing essentials before producing a production program. If the user explicitly requests an immediate draft, mark assumptions in the explanation and with `-- UNVERIFIED` comments, minimize guessed IDs, and provide verification steps.

## Discovery workflow

Skip known information. Ask the most useful 1–3 questions per turn and explain exactly what the user should inspect.

### 1. Identify the exact target

Use the precise JEI/EMI name where possible. “Fuel,” “steel,” “processor,” “alloy,” or “nuclear fuel” can refer to several mods or several products in one mod. Offer plausible choices as questions; do not choose the target for the user. If the mod is unknown, identify it first or present mod/product choices.

### 2. Establish the environment once

Ask early for Minecraft, loader, SFM version, and modpack/version if missing. Determine whether recipes are customized. Reuse this context until the user changes it; do not ask every turn.

In heavily modified packs, upstream recipes are reference material. The user's installed JEI/EMI is the primary evidence for the actual recipe.

### 3. Build the recipe chain

Guide the user to view the target's recipe, then inspect missing intermediate ingredients. JEI normally uses **R** for recipes and **U** for uses; bindings may differ. Inspect one or two steps at a time until the remaining inputs are resources the user already supplies.

Organize the evidence into a table and resolve ambiguities before coding:

| Step | Machine | Inputs and quantities | Outputs and quantities | Byproducts | Timing / catalyst / circuit / power |
|---|---|---|---|---|---|

Do not omit byproducts. Depending on the machine, blocked byproducts can stop processing or be lost. Nonconsumed catalysts, circuits, molds, and presses normally belong in one-time setup rather than every-batch routing.

### 4. Specify a supported machine configuration

Design the required configuration instead of repeatedly asking how every machine is currently configured. Include:

- Orientation and resource-specific input/output sides.
- Verified automation-slot mappings and any slot locks or buffer limits.
- Which routes SFM owns and which use native ejection or pipes.
- One-time circuits, catalysts, molds, or presses.
- Power type and voltage/integration requirements.

For Mekanism, configure one machine and copy to matching machines with a Configuration Card. Adapt when the user reports layout constraints. If a capability or slot mapping is uncertain, inspect it with the Network Tool and targeted tests; Ctrl+I indices alone may be GUI indices.

### 5. Derive the SFM design

Use the mapping below, then return to SKILL.md section 2 for implementation, simplification, and review.

## Source priority

### User's installed JEI/EMI

Useful guidance:

- Hover the target and press **R** to view its recipe, or use the configured recipe key.
- If several machines or recipe pages are shown, identify the intended route.
- A screenshot or a typed `machine: inputs → outputs` description works.
- Enable **F3+H** for item registry IDs; use Ctrl+Space with resources in a labeled container for SFM identifiers.

### Matching-version official references

When user-provided evidence is unavailable, explain what is missing. If the user requested research or has already authorized it, proceed; otherwise ask whether they prefer to provide JEI details or use sourced upstream recipes. Do not ask for the same authorization repeatedly.

Check, in order:

1. Official wiki/documentation for the matching version.
2. Recipe files in the mod's matching branch/tag: commonly `src/main/resources/data/<modid>/recipe/` on 1.21+, `recipes/` on older versions, or generated/datagen sources.
3. The modpack's overrides, including `kubejs/server_scripts/`, CraftTweaker `scripts/`, and datapacks. Search by the target's confirmed ID.

Cite the link and version and state that the pack may override the result. If sources conflict or no reliable source exists, say what remains unknown and return to in-game evidence. Do not assemble a plausible chain from incompatible versions.

### Memory

Use recollection to narrow the question, offer possible targets, or remind the user to check byproducts. It is not evidence for executable production recipes or invented IDs such as `modid:guessed_dust`.

## From recipe chain to program

| Recipe requirement | SFM design |
|---|---|
| Processing step | A label for the machine role; separate groups where identical machines perform different recipes |
| External ingredient | Dedicated labeled source container, or mixed storage with a verified exact filter |
| Intermediate output | Read the preceding machine's output and feed the next stage; clear registrations between stages |
| Byproduct | Usable receiving space and a deliberate full-storage policy |
| Unequal processing times | Balance machine counts against measured stage throughput |
| Nonconsumed circuit, press, catalyst, or mold | One-time setup with slot details |
| Ordered or parallel batches | Station-specific allocation and a verified completion/return path |

## Reduce dependency on IDs

Dedicated inventories can make the program independent of ingredient names:

- One source container per ingredient: `input from sulfur_supply` needs no item ID when the container is dedicated.
- One recipe per machine group and a single resource role per face: a version-appropriate `gas::` or `chemical::` route may need no exact chemical ID.
- Use exact IDs when selecting from mixed storage or when several resources of one type must enter different machine faces. `forget` can also isolate separate dedicated sources.

For an ID that is needed, place the real resource in a labeled container and use **Ctrl+Space** at the resource position in SFM. Confirm tags independently; a resource's registry ID does not establish a tag.

## Response examples

### Ambiguous target, environment unknown

```text
Before writing the program, I need two details:
1. Which exact product do you mean by “nuclear fuel”? The JEI name is enough.
2. Which modpack/version, Minecraft version, and SFM version are you using?
```

Ask the environment question only when it is not already known. Offer actual target options when there is enough context to do so accurately.

### Continue recipe discovery

```text
For that target, open its recipe in JEI and share the machine, inputs, quantities,
and outputs. Include any byproducts. If an ingredient needs another processing
step, open that recipe too; we can work through the chain one stage at a time.
```

### Target known, chain incomplete

```text
I have the target and environment. The remaining gap is the processing chain.
Please confirm the missing rows in this table from JEI:

| Step | Machine | Inputs | Outputs | Byproducts |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

Also include the machine count for each stage and where the raw materials come
from. Dedicated ingredient containers can avoid most resource-ID filters.
```

Populate confirmed rows from evidence. Do not fill unknown rows with remembered recipes merely to make the table look complete.

### No reliable recipe source

```text
I do not have a reliable recipe for this product in your version or pack.
You can provide the JEI recipe, or I can check the matching official documentation
and source. Upstream recipes will still need a JEI cross-check for pack changes.
```

### Immediate draft requested

State the unverified assumptions at the start, mark affected code with `-- UNVERIFIED: ...`, prefer dedicated sources, and finish with checks for recipes, IDs, capabilities, and disk warnings.

## Avoid these mistakes

- Choosing a common target when the user's wording is ambiguous.
- Treating recalled recipes or guessed IDs as confirmed.
- Applying unmodified upstream recipes to a customized pack without qualification.
- Hiding missing evidence behind a plausible-looking production chain.
- Repeating known environment questions or presenting a long questionnaire.
- Asking about current side settings when you can propose a supported configuration; verify only the facts and constraints that affect that design.

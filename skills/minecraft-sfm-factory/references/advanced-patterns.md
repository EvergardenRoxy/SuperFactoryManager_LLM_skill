# Advanced logistics patterns

Use these only after checking the simpler options in SKILL.md 2.4. They add state, ordering, or high-frequency work; include **Performance notes** when delivering them. Confirm mod IDs, capabilities, sides, and slots in the user's environment. Examples with generic machine roles are design skeletons, not verified recipes.

## Try simpler controls first

| Requirement | First choice | Escalation |
|---|---|---|
| Keep one recipe's ingredients in each machine | `output retain N to each machines` | Counter/state register |
| Insert the primary ingredient last | Result-locked Pattern Provider and verified staging slots | State machine |
| Chain processing stages | Separate `input → output → forget` sections | Separate triggers if needed |
| Handle full primary storage | Ordered outputs to backup storage | Explicit cutoff conditions |
| Transfer faster than every 20 ticks | Verify the actual bottleneck | Redstone clock and pulse trigger |
| React to completion | Tolerate an adequate polling interval | Verified machine/comparator event into manager |
| Control a redstone circuit | Read signals and use native redstone logic | Container plus comparator as indirect output |

## Counter registers: item counts as state

The logistics subset has no general-purpose variables. An isolated container slot can store a small integer as an item count.

| Role | Suggested implementation |
|---|---|
| Register `state` | One vanilla barrel, with a dedicated label; one slot per counter |
| Token source `tokens` | A chest containing one cheap stackable vanilla item, such as cobblestone; accept returned tokens |

A slot holds 0–64 with a 64-stack item, or only 0–16 with a 16-stack item. Exclude hoppers, other programs, and unrelated items from both inventories.

```sfml-snippet
-- Read slot zero.
if state slots 0 has = 2 then
    input from a
    output to b
end
forget

-- Increment by one.
input 1 from tokens
output 1 to state slots 0
forget

-- Reset by returning tokens.
input from state slots 0
output to tokens
forget
```

`has` reads current inventory. Updating a counter to one can make the next independent `if state slots 0 has = 1` true in the same invocation. Use `if … else if … end` for mutually exclusive state transitions.

Bind `state` to exactly one block; default `has` would otherwise sum counts across blocks. Vanilla containers/items avoid unexpected stacking and slot behavior. Different slots can represent independent subsystems; document each slot and coordinate with parenthesized conditions such as `(state slots 0 has = 1) and (state slots 1 has = 2)`.

## State machine for ordered recipes

Use this when a single station requires secondary ingredients first, a primary ingredient last, then product collection, and a result-locked Pattern Provider cannot provide the needed sequencing.

Prerequisites:

- One station; a nonempty, connected set of pedestals, each exposing one usable slot with capacity one.
- No ingredient-position requirements; `secondary` contains exactly one verified batch, and there are no leftovers.
- `core` exposes one primary-ingredient slot and starts empty; `products` exposes only finished output.
- `tokens` contains at least two tokens and can receive them back; `state` is one isolated barrel.
- The primary item remains observable after insertion during that SFML invocation. If insertion consumes it immediately, use a real device/completion signal instead of this readiness test.

Labels `primary` and `secondary` are dedicated ingredient chests; `pedestals` and `core` bind this station; `products` is its isolated output and `finished` is receiving storage. Null-side item access must be supported or replaced with verified sides.

```sfml
name "Ordered single-station recipe"
-- state slot 0:
-- 0 = distribute one secondary ingredient to every pedestal
-- 1 = insert the primary ingredient and verify arrival
-- 2 = wait for products, collect them, then return to idle
every 40 ticks do
    if state slots 0 has = 0 then
        input from secondary
        output 1 to empty slots in each pedestals
        forget
        if (secondary has = 0) and (every pedestals has = 1) then
            input 1 from tokens
            output 1 to state slots 0
            forget
        end
    else if state slots 0 has = 1 then
        if core has = 0 then
            input 1 from primary
            output 1 to core
            forget
        end
        -- Advance only after the target actually received the ingredient.
        if core has = 1 then
            input 2 from tokens
            output retain 2 to state slots 0
            forget
        end
    else if state slots 0 has = 2 then
        if products has > 0 then
            input from products
            output to finished
            forget
            if products has = 0 then
                input from state slots 0
                output to tokens
                forget
            end
        end
    end
end
```

Document every state at the top of the program and place its transition condition at the end of its branch. A source becoming empty is not enough; verify target readiness. Use an interval appropriate to the machine, commonly 40 ticks or more.

For manual recovery, pause first. Inspect core, pedestals, and output; restore a coherent initial batch, then reset the register. Clearing tokens alone can mix old and new batches. This program's nesting requires performance notes.

## Multiple processing stages in one trigger

Each stage registers sources, transfers, then clears registrations. This chemical-chain skeleton uses Mekanism IDs that must match the installed recipe and chemical integration. `ingredients` and `oxygen` are dedicated sources; `oxidizers` and `infusers` are configured machine groups; `product_tank` is compatible receiving storage. Supply energy separately.

```sfml
every 20 ticks do
    -- Stage one: verified sulfur feed into Chemical Oxidizers.
    input mekanism:dust_sulfur from ingredients top side
    output to each oxidizers top side
    forget

    -- Stage two: exact IDs isolate two chemicals entering different faces.
    input gas:mekanism:oxygen from oxygen top side
    output gas:mekanism:oxygen to each infusers left side
    input gas:mekanism:sulfur_dioxide from each oxidizers right side
    output gas:mekanism:sulfur_dioxide to each infusers right side
    forget

    -- Stage three: collect only from the configured chemical-output face.
    input gas:: from each infusers back side
    output gas:: to product_tank top side
end
```

If broad `gas::` filters replace the exact IDs, put `forget` between the two feed routes. Otherwise the second output can consume the first route's registered chemical. Relative sides require 4.27.0+; use absolute sides on older versions. Document orientation and per-resource side settings, using a Configuration Card for identical Mekanism machines.

Long chains can use separate triggers with supported offsets to spread work. Neither statement order nor `forget` makes a machine finish immediately; downstream stages move only available intermediates.

## Pattern Providers and staging slots

This pattern supports one station with capacity-one pedestals, one primary item, and no ingredient-position constraints. All labels must be assigned, connected, and free of relevant warnings. Start with empty pedestals and a dedicated empty staging chest written by exactly one Pattern Provider.

**Ordinary Blocking Mode is insufficient for strict serialization.** It checks the adjacent target for remaining pattern inputs; SFM emptying the staging chest may allow another batch before processing finishes. Use **Lock Crafting → Until primary crafting result is returned**, and route the primary result through **the same provider's return inventory**. A generic ME Interface does not establish that unlock path. Versions without that lock need another verified completion mechanism.

The pattern must send one complete recipe, with a quantity-one primary ingredient first. In an empty chest it may land in slot 0, but substitutions, stacking, or other writers can change the layout. **Test one submission** and verify primary slot 0 and secondary slots 1–26 before using this program. The pedestal count must equal the total secondary-item count for that batch.

```sfml
every 20 ticks do
    input from staging slots 1-26
    output 1 to empty slots in each pedestals
    forget

    -- Check actual arrival, not just an empty source.
    if (staging slots 1-26 has = 0) and (every pedestals has = 1) then
        input 1 from staging slots 0
        output 1 to core
        forget
    end

    -- Return through the provider that issued this batch.
    input from products
    output to pattern_provider top side
end
```

| Label | Binding |
|---|---|
| `staging` | Exclusive staging chest with verified slot layout |
| `pedestals` | All and only this station's pedestals |
| `core` | Single primary-ingredient receiver |
| `products` | Product-only inventory or verified output-slot selection |
| `pattern_provider` | The provider that issued the batch, with a verified return face |

For Mystical Agriculture 1.21, give the **altar** a constant activation signal. A manager switch does not activate the altar. Verify its output slot; do not collect all altar items indiscriminately or apply a seeds-only completion filter to non-seed recipes.

A job with no physical result needs a real completion signal. Declare a marker as a pattern output only if the machine actually produces or returns it.

### Parallel stations

Give **each station its own staging/pedestal/core/product/provider labels**. Repeat the pattern with station-specific names, for example `staging_1`, `pedestals_1`, `core_1`, `products_1`, `provider_1`. Each provider sends a complete recipe and receives its own result.

Combining all pedestals under one label and multiplying pattern quantities does not guarantee complete recipes per station. If each of two stations needs four A and four B, eight A may fill the first station's pedestals and eight B the second. `to each` does not know station membership. Shared batches require verified grouping by ingredient role and complete-recipe checks per station.

Use world-time alignment if useful; slow recipes often need polling only about every 100 ticks. The actual result return, not the polling schedule, unlocks the provider.

## Full storage and byproduct handling

Check the machine's actual full-storage policy. Some stop; others continue and lose excess output. The audited Productive Bees branch can discard uninserted fluid, so continued processing is not evidence of safe buffering. See `mod-notes.md` for its pinned scope.

Every product needs usable receiving capacity and throughput, not necessarily its own block. Use output order for backup storage or permitted disposal. A trash can destroys resources; use it only for byproducts the user allows discarding.

The following deliberately permits discarding honey **and all other matched fluids** from this centrifuge group. If any fluid must be preserved, replace broad disposal with exact filters and a validated input cutoff before buffers fill.

```sfml
every 20 ticks do
    -- Only use this void route when honey may be discarded.
    input fluid::honey from each centrifuges top side
    output fluid::honey to honey_tank top side
    output fluid::honey to fluid_trash top side
    forget

    -- All remaining matched fluids must also be disposable here.
    input fluid:: from each centrifuges top side
    output fluid:: to byproduct_tanks top side
    output fluid:: to fluid_trash top side
end
```

Bind `centrifuges` to verified fluid-output faces, `honey_tank` and `byproduct_tanks` to suitable storage, and `fluid_trash` to an intentional sink. Confirm namespaces if several honey fluids exist. Grouping machines by fluid output can prevent incompatible fluids from occupying the same machine tank, but does not remove capacity limits.

## Faster transfers with redstone clocks

Pulse triggers bypass timer minima. Use this only after confirming the interval, rather than machine speed, blocked output, or insufficient capacity, is the bottleneck. Choose the lowest sufficient clock frequency and measure its actual rising-edge period.

```sfml
every redstone pulse do
    input from ingredients top side
    output retain 16 to each machines top side
    forget
    input from each machines bottom side
    output to results top side
end
```

Labels and side separation follow the ordinary two-stage array template. Put a switch on the clock if useful. **Include performance notes:** work increases with pulse frequency. Tunnelled Managers do not tunnel redstone; connect the signal to the executing manager's own redstone input rather than relying on the tunnel path.

## Feedback production loops

Use for a verified resource-multiplication recipe where part of the output feeds earlier stages, such as crystal → dust → more crystal. Confirm the actual machines, recipe yield, external inputs, and power before adapting this skeleton. `slots 9` is illustrative, not a universal product slot.

Labels: `water` = dedicated source; `crystal_stock` and `dust_stock` = buffers; `crushers` = verified crystal-to-dust machines; `reaction_chambers` = verified dust-to-crystal machines; `me_interface` = surplus destination. Configure product-only extraction where shown and supply power separately.

```sfml
every 20 ticks do
    input fluid:: from water top side
    output fluid:: to each reaction_chambers bottom side
end

every 40 ticks do
    -- Reserve crystals by stopping crushing when enough dust is available.
    input from crystal_stock
    if dust_stock has < 256 ae2:certus_quartz_dust then
        output retain 16 ae2:certus_quartz_crystal to each crushers bottom side
    end
    forget

    input from each crushers bottom side
    output to dust_stock
    forget
    input from dust_stock
    output retain 16 ae2:certus_quartz_dust to each reaction_chambers bottom side
    forget

    input from each reaction_chambers bottom side slots 9
    output to crystal_stock
    output to me_interface top side
end
```

- **Provide enough startup material:** each active machine must receive a complete recipe. Budgeting for all configured retention targets plus reserve is a conservative starting point. Too little seed stock can leave every machine partially filled and idle. External inputs and exported surplus must remain balanced.
- The condition controls a cross-inventory decision: whether crystals should be crushed. A simple per-destination retention limit alone does not express that policy.
- Balance machine counts using actual stage throughput. Excess capacity at one stage cannot compensate for another stage's bottleneck.
- Supported Mekanism processing machines may expose item I/O on one face because standard input slots prevent external extraction. Verify this for the exact machine; it is not a general container rule.
- Confirm output indices and capability mappings; GUI slot numbers may differ.
- State the potentially high and variable power demand. Prefer native limited I/O or machine controls when available.

## Buffered, quantity-limited energy discharge

Prerequisites: one FE buffer and one FE consumer with verified sides and per-call transfer capacity. This example attempts **at most 1,000,000 FE per rising edge** only when that amount is available. A held readiness signal does not repeat; after charging, a new edge is needed.

SFML cannot guarantee atomic acceptance of the entire amount. If the device rejects or partially accepts it, recovery must use the device's actual energy/completion signal. Change the charge threshold and transfer limits together.

```sfml
every tick do
    input fe:: from grid top side
    output retain 1000000 fe:: to energy_buffer top side
end

every redstone pulse do
    if energy_buffer bottom side has >= 1000000 fe:: then
        input 1000000 fe:: from energy_buffer bottom side
        output 1000000 fe:: to device bottom side
    end
end
```

`grid` supplies FE, `energy_buffer` is the single buffer, and `device` is the target. Verify both capabilities' limits. This does not model Oritech accelerator speed control, and Ars Nouveau Source is not FE.

## Completion events through manager redstone input

If a machine or comparator produces a reliable completion edge, wire it to the manager. The pulse queues work for manager execution; do not assume arbitrary zero-latency control. Distinguish the real completion transition from unrelated neighbor updates.

```sfml
-- Routine replenishment.
every 40 ticks do
    input from ingredients
    output retain 4 to each machines top side
end

-- Product collection when the completion circuit sends an edge.
every redstone pulse do
    if redstone = 15 then
        input from each machines bottom side
        output to results
    end
end
```

`if redstone` checks received strength at the manager; at the audited commit it reads the world directly. Signal strengths can encode events only if the circuit and timing preserve them. Event-driven work can avoid frequent polling, but frequent events still need performance review.

## Indirect redstone output: container and comparator

SFM can change a container's contents and let a comparator convert fullness into a signal. This can switch machines, tracks, or pistons without an ordinary world-redstone output statement.

`products` is monitored storage, `signal_chest` is an isolated empty container facing a comparator, and `tokens` supplies/reclaims one stackable item. Configure the downstream circuit so a nonzero signal has the intended effect.

```sfml
every 20 ticks do
    if products has >= 1000 then
        input from tokens
        output retain 1 to signal_chest
        forget
    else
        input from signal_chest
        output to tokens
    end
end
```

For an ordinary nonempty container, vanilla comparator strength is `floor(1 + 14 × sum(slot item count / item maximum stack size) / slot count)`; empty means zero. One item is sufficient for an on/off signal of one; amplify with a repeater if needed.

For precise strength, use a small vanilla container and calculate the item count, then fill with `output retain N`. A hopper moves items by itself unless locked; a dropper may be easier to isolate. Combined with `redstone::` reads or the manager's received signal, this can form a control loop, subject to polling and circuit delay.

# SFM program templates

Choose the closest pattern and adapt its labels, filters, and interfaces. `sfml` blocks are complete programs, not guarantees that the named machines expose those capabilities in every version. The repository validator checks their syntax against the official grammar; it does not simulate Minecraft.

For more involved workflows, read `advanced-patterns.md`; for mod-specific setup, read `mod-notes.md`.

Before delivering an adapted template, establish:

| Area | Required details |
|---|---|
| Versions | Minecraft, loader, SFM, target mod, required integration/addons |
| Interfaces | Label bindings, concrete sides, automation slots, ingredient/product filters |
| Machine settings | Sided separation, input buffer/locks, presses/circuits, automatic output, cyclical-processing augment |
| Capacity and recovery | Power type, full-storage behavior, missing inputs, power loss, reload recovery |

| Task | Template |
|---|---|
| A → B, filtering, transfer limits | Basic transfer; selected items and limits |
| Sorting and fallback storage | Sorting; overflow |
| Feeding and collecting machine arrays | Furnaces; machine replenishment; two-stage array |
| Non-item resources | Energy, fluids, and chemicals |
| Inventory/redstone control | Stock condition; pulse trigger; logistics enable switch |
| Mod examples | Phytogenic Insolators; AE2 Inscribers; experimental fusion fueling |

## Basic item transfer

Labels `a` and `b` bind ordinary source and destination inventories supporting null-side access.

```sfml
name "Move items"
every 20 ticks do
    input from a
    output to b
end
```

## Selected items and limits

These independent triggers illustrate different limits; choose the one needed rather than enabling all three on the same route.

```sfml
every 20 ticks do
    input minecraft:iron_ingot from a
    output to b
end
every 20 ticks do
    input 1 from each a           -- up to one item from each source block
    output to b
end
every 20 ticks do
    input retain 64 from a        -- leave sixty-four items collectively
    output to b
end
```

## Sorting into different chests

`source`, `ores_chest`, `ingots_chest`, and `others` are inventories. Verify the ore tag in the pack; `#ores` is an illustrative cross-namespace tag matcher.

```sfml
every 20 ticks do
    input from source
    output with #ores to ores_chest
    output *_ingot to ingots_chest
    output to others              -- remaining resources
end
```

Earlier outputs consume available resources first. A later catch-all can also receive items rejected because an earlier destination is full; use additional filters if those must stay at the source.

## Furnace array

Adapted from the official **Furnace Manager** template. `to_be_smelted` and `fuel` are dedicated chests; `furnaces` contains the furnace blocks; `results` receives products. Vanilla furnaces accept smelting inputs from above and fuel from below, with products extracted below.

```sfml
name "Furnace Manager"
every 20 ticks do
    input from to_be_smelted
    output 8 to each furnaces top side
    forget

    input from fuel
    output retain 1 to each furnaces bottom side
    forget

    input from furnaces bottom side
    output to results
end
```

## Furnace inputs on different sides

Adapted from the official smelting example. `chest` supplies logs/fuel and receives products; `furnace` is the furnace. The source should contain only resources appropriate for this route.

```sfml
every 20 ticks do
    input from chest
    output minecraft:oak_log to furnace top side
    output
        coal,                     -- unrestricted coal
        1 retain 1 oak_log,        -- at most one log, filling to one
        charcoal
    to furnace bottom side
end

every 20 ticks do
    input from furnace bottom side
    output to chest
end
```

## Energy, fluids, and chemicals

These are independent patterns. Bind `energy` to an FE source; bind each machine/tank label to a block with the shown capability and a configured top face. The chemical example needs Mekanism and a supported `gas` type/alias. Verify nuclear-waste handling and the actual recipient before adapting it.

```sfml
-- Energy-only work can use the default one-tick minimum.
every tick do
    input fe:: from energy top side
    output fe:: to powered_machines top side
end

-- Dedicated water tank to machine fluid inputs.
every 20 ticks do
    input fluid:: from water top side
    output fluid:: to fluid_consumers top side
end

-- Fill each consumer to one bucket of water.
every 20 ticks do
    input fluid:minecraft:water from water_source top side
    output retain 1000 fluid:minecraft:water to each water_consumers top side
end

-- Gas on older builds; chemical alias on unified MC 1.21.1 builds.
every 20 ticks do
    input gas:mekanism:nuclear_waste from fission_port top side
    output gas:: to isotope_centrifuges top side
end
```

Use distinct labels or select only the needed triggers. Do not infer that a fluid or chemical transfer is safe merely because it parses; inspect the source/target capability and receiving capacity.

## Replenish a machine array

`ingredients` contains one verified ingredient; `machines` is a fixed-recipe group with matching top-side inputs.

```sfml
every 20 ticks do
    input from ingredients
    output retain 8 to each machines top side
end
```

## Overflow to backup storage

`products` is source storage; `primary_storage` and `backup_storage` are receiving inventories. Nothing is discarded.

```sfml
every 20 ticks do
    input from products
    output to primary_storage
    output to backup_storage
end
```

## Gate production by stock

`results` holds the counted item; `ingredients` supplies a verified recipe; `machines` exposes its input face. This starts/stops replenishment; existing machine contents may continue processing and overshoot the stock threshold.

```sfml
every 20 ticks do
    if results has < 1000 minecraft:iron_ingot then
        input from ingredients
        output to machines top side
    end
end
```

## Manual redstone-pulse transfer

A button or lever's rising edge at the manager triggers a transfer. A held signal does not repeatedly retrigger it.

```sfml
every redstone pulse do
    input from a
    output to b
end
```

## Logistics enable switch

Power the manager with a lever. This gates SFM's feeding and collection; it does not cancel in-progress recipes or inherently shut off machines. Use a verified input/output side split and configure the labels shown.

```sfml
every 20 ticks do
    if redstone > 0 then
        input from ingredients top side
        output retain 16 to each machines top side
        forget
        input from each machines bottom side
        output to results top side
    end
end
```

Energy may remain in a separate trigger if that matches the desired pause behavior. Some machines consume idle power; verify rather than assuming zero draw.

## Phytogenic Insolator array

Community setup for **Thermal 1.20.x**, optionally processing Mystical Agriculture seeds. Confirm recipe and augment behavior in the installed pack. Configure each Insolator's top face for the required resource capabilities. `seed_supply` is dedicated seed storage, `item_interface` supplies Phyto-Gro and receives products, `energy` is an FE source, and `water` supplies water. `insolators` labels all configured machines.

This assumes top-side extraction exposes only intended outputs. If it also exposes seeds or catalysts, use verified product filters or a separate output face. Check whether the cyclical-processing augment is installed and where recovered seeds go. `*_seeds` is a naming-pattern example; replace it when the actual seed IDs differ.

```sfml
every tick do
    input fe:: from energy top side
    output fe:: to insolators top side
end

every 20 ticks do
    input fluid:minecraft:water from water top side
    output fluid:: to insolators top side

    input thermal:phytogro from item_interface
    output to insolators top side
    forget

    input from seed_supply
    output retain 2 *_seeds to each insolators top side
    forget

    input from insolators top side
    output to item_interface
end
```

## AE2 Inscribers

Adapted from the official template. Confirm AE2 version, sided-separation settings, buffer limits, and automation mapping. **Null-side/internal slot numbers are not automatically the same as directional slot numbers.** Preload the appropriate presses in the first-stage Inscribers. `logic`, `engineering`, `calculation`, `silicon`, and `last` label their respective Inscriber groups; `materials` and `results` are chests.

The second trigger is the upstream example's **optional rebalancing behavior**. Remove it unless extraction mappings are verified and its interval exceeds a complete craft under actual power/upgrade conditions. It can otherwise interrupt active recipes. Prefer native small buffers and correctly allocated ingredients.

```sfml
name "AE2 Inscribers"
every 20 ticks do
    input from materials
    output retain 2 gold_ingot to each logic slots 2
    output retain 2 diamond to each engineering slots 2
    output retain 2 certus_quartz_crystal to each calculation slots 2
    output retain 2 silicon to each silicon slots 2
    output retain 2 item:minecraft:redstone to each last slots 2
    output retain 2 printed_silicon to each last slots 1
    output
        retain 2 printed_calculation_processor,
        retain 2 printed_engineering_processor,
        retain 2 printed_logic_processor
    to each last slots 0
    forget
    input from logic, engineering, calculation, silicon west side
    output to materials
    forget
    input from last west side
    output to results
end

-- Optional recovery; verify mappings and craft time before enabling.
every 200 ticks do
    if some last has < 3 then
        input from last
        output to materials
    end
end
```

Unqualified item names follow the upstream template and match across namespaces. Use confirmed exact IDs where the pack has name collisions.

## Experimental adaptive fusion fueling

**This community experiment is retained for analysis, not as a validated reactor controller.** Prefer a tested continuous chemical-transfer system for actual fusion fueling. The amounts below are tiers chosen by the example, not universal burn-rate limits.

The original goal was approximately proportional fueling from an 8,192,000 mB reserve toward 1,000 mB per tick. The program transfers fuel to the reactor and temporarily moves portions of the reserve into `temp`, changing the inventory seen by subsequent conditions. Its actual behavior depends on pulse period, transfer acceptance, and available storage. One-tick pulse width does not mean one rising edge per tick. Reactor consumption occurs each game tick, and fuel starvation can stop burning.

Prerequisites: `fuel` contains only the intended fusion fuel; `temp` is an empty compatible tank with adequate capacity and a guaranteed return path; `reactor_port` exposes the fuel capability on the configured face. Confirm all resource IDs, rates, capacities, temperature behavior, and reload recovery in game. The chemical ID in the fallback check must be verified for the user's version.

**Performance notes are mandatory:** the pulse trigger has eleven independent `if` statements and several large transfers. Higher pulse frequency increases work. `output retain` would control inventory, not directly specify a per-tick burn rate.

```sfml
every tick do
    input fe:: from energy top side
    output fe:: to powered_machines top side
end

every 20 ticks do
    input fluid:: from electric_pumps top side
    output fluid:: to separators top side
end

every redstone pulse do
    input gas:: from fuel top side
    if fuel top side has >= 4096000 gas:: then
        output 500 gas:: to reactor_port top side
        output 4096000 gas:: to temp top side
    end
    if fuel top side has >= 2048000 gas:: then
        output 250 gas:: to reactor_port top side
        output 2048000 gas:: to temp top side
    end
    if fuel top side has >= 1024000 gas:: then
        output 125 gas:: to reactor_port top side
        output 1024000 gas:: to temp top side
    end
    if fuel top side has >= 512000 gas:: then
        output 62 gas:: to reactor_port top side
        output 512000 gas:: to temp top side
    end
    if fuel top side has >= 256000 gas:: then
        output 32 gas:: to reactor_port top side
        output 256000 gas:: to temp top side
    end
    if fuel top side has >= 128000 gas:: then
        output 16 gas:: to reactor_port top side
        output 128000 gas:: to temp top side
    end
    if fuel top side has >= 64000 gas:: then
        output 8 gas:: to reactor_port top side
        output 64000 gas:: to temp top side
    end
    if fuel top side has >= 32000 gas:: then
        output 4 gas:: to reactor_port top side
        output 32000 gas:: to temp top side
    end
    if fuel top side has >= 16000 gas:: then
        output 2 gas:: to reactor_port top side
        output 16000 gas:: to temp top side
    end
    if fuel top side has >= 8000 gas:: then
        output 1 gas:: to reactor_port top side
    end
    -- UNVERIFIED: confirm this exact fuel ID in the installed version.
    if reactor_port top side has = 0 gas:mekanismgenerators:fusion_fuel then
        output 1 gas:: to reactor_port top side
    end
    forget
    input gas:: from temp top side
    output gas:: to fuel top side
end
```

Before any production use, measure actual per-tick deliveries, stock, temperature, and burning state; test a full/rejecting temporary tank, failed return transfer, missing fuel, and world reload. Parsing success alone establishes none of these properties.

## Two-stage machine array

`ingredients` is dedicated source storage, `machines` has top-side inputs and bottom-side product-only extraction, and `results` is receiving storage. The retention limit prevents one machine from absorbing the entire supply but does not guarantee fair allocation when ingredients are scarce.

```sfml
every 20 ticks do
    input from ingredients bottom side
    output retain 16 to each machines top side
    forget
    input from machines bottom side
    output to results top side
end
```

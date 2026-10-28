# Throughput, machine arrays, and performance

Read this for arrays of dozens of machines, mixed products, uneven utilization, server lag, or machine selection. Interface/version notes are in `mod-notes.md`; sources are in `config-and-versions.md`.

## Allocation is sequential

Within a trigger, SFM visits sources and targets in order. Earlier targets may receive scarce ingredients first. Use small per-machine budgets or `output retain N to each ...`, but ensure each machine can obtain a complete recipe. `output N to group` shares one budget across the entire group and may split it among blocks; it does not select one complete workstation.

## Receiving capacity and throughput

Check these separately: machine output slots/tanks, external receiving inventories, AE return buffers, and network storage. **There is no general rule that output-block count must equal or exceed product-type count.** A chest has many slots; a multi-tank hatch can hold several fluids; a single tank usually holds one fluid at a time.

Calculate usable slots/tanks, filters, sustained transfer rate, and reserve capacity. Dedicated outputs simplify diagnosis but are a design choice. When storage fills, some machines stop and others discard excess resources. Verify the behavior before choosing extra buffers, more transfer capacity, or an input cutoff. Void only byproducts the user agrees may be discarded.

In the checked Mekanism branch, water separation uses 2 mB water to produce 2 hydrogen and 1 oxygen; brine separation uses 10 mB brine to produce 1 sodium and 1 chlorine. These routes produce four chemicals in total. Size buffers from production rate, downstream consumption, and desired buffering time; do not prescribe a universal hydrogen-tank ratio. ME chemical storage also needs suitable integration, such as Applied Mekanistics.

## Multi-ingredient recipes: configure before replacing machines

| Machine | Checked structure and native controls | Array design |
|---|---|---|
| AE2 Inscriber | Three inputs, one output; small input buffer; optional sided separation | Verify inventory mapping, preload presses, group by recipe |
| ExtendedAE Extended Inscriber | Four threads, each with three inputs and one output; 1/4/64 buffer options | Limit buffers and provide complete materials per thread; distinguish ExtendedAE from AdvancedAE |
| ExtendedAE Crystal Assembler | Nine input slots, one output | Reserve slots for different ingredients and limit replenishment |
| MI Assembler | Slot locks, per-slot limits, native automatic output | Lock recipe inputs and fluids; supply matching-voltage EU through MI cables |

Prefer native filtering, locks, and buffer limits before adding state. Speed depends on versions, recipes, power, and upgrades. Compare machines under equivalent conditions; a single stalled array does not establish a universal machine-selection rule.

This skeleton feeds **dedicated recipe storage into slot-locked MI Assemblers**. The source contains only the verified ingredients for one recipe. Each illustrated input slot requires one item; change limits for the real recipe. Lock unused slots empty, supply fluids separately, and use MI's own EU power system unless FE compatibility is confirmed.

```sfml
every 20 ticks do
    input from recipe_items top side
    output retain 1 to each assemblers top side slots 0
    output retain 1 to each assemblers top side slots 1
    output retain 1 to each assemblers top side slots 2
    forget
    input from each assemblers bottom side
    output to results top side
end
```

Labels: `recipe_items` = dedicated input chest; `assemblers` = machines with verified input locks; `results` = receiving chest. Slot numbers 0–2 are illustrative. Confirm automation indices per face, lock each to its intended ingredient, and ensure the collection face exposes only products. Different recipes need separate groups or an explicit changeover procedure.

## Limits of community measurements

Earlier notes reported splits such as 258/762 machines in a 1,024-machine array, 10–50 or 125–250 stalled machines, and utilization below 40%. Those reports lack sufficient versions, settings, recipes, power, layouts, and reproducible programs. **Do not use them as throughput guarantees or stall probabilities.** Ingredient migration between Inscriber threads is also not established as universal behavior.

For a useful reproduction, record Minecraft/loader/mod versions, configuration, machine count, recipe, locks/buffers, upgrades, power, destination storage, and the SFM program. Compare single-machine and array throughput and manager execution time. Distinguish incomplete recipes, insufficient power, rejected insertion, full buffers, and resource loss.

## Reduce execution cost

A useful cost approximation is **blocks × sides × slots × trigger frequency**, with additional work for resource-pattern expansion and conditions. This is a heuristic, not a precise complexity guarantee.

1. **Run less often:** use 40–200 ticks for nonurgent collection, storage, and fuel replenishment. Enable fast clocks only when needed.
2. **Visit less inventory:** restrict labels and slots where useful. `empty slots in` skips occupied insertion targets but also skips partial stacks. Grouping labels simplifies code; it does not by itself reduce the number of machines visited.
3. **Use concrete sides:** avoid seven capability visits from `each side` when one face works.
4. **Narrow resource matching:** avoid broad regex combined with per-resource `each`.
5. **Simplify conditions:** use retention and output order where equivalent; reserve state machines for real ordering needs.
6. **Spread work:** use supported timer offsets to avoid running several large triggers on the same tick.
7. **Use native transport:** fixed routes may be cheaper with ejection, pipes, or AE/RS interfaces.

Compare designs in the manager's performance graph. If the server has spark or another profiler, use it to confirm whether SFM causes the lag. Keep energy in a separate eligible 1-tick trigger; ordinary transfers should meet the configured timer minimum. See SKILL.md 2.5 for cases requiring performance notes.

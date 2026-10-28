# Mod integration notes

The checked baseline uses Minecraft 1.21/1.21.1 branches for Mekanism, AE2, ExtendedAE, Mystical Agriculture, Productive Bees, MI, Occultism, Ars Nouveau, and Oritech; Thermal uses 1.20.x and GTCEu Modern uses 1.20.1. A branch is not a released version. Modified-pack recipes must be checked in JEI/EMI. Sources are in `config-and-versions.md`.

These are interface/design notes. Programs are in `templates.md` and `advanced-patterns.md`. For delivery, state Minecraft/loader/SFM/target-mod/addon versions and required side, slot, power, buffer, and upgrade settings.

## General rules

- Qualify exact resource IDs with namespaces when multiple mods register similarly named materials.
- An item ID is not a tag: `exdeorum:dust` does not establish `#exdeorum:dust`.
- Common tags are often `forge:` on 1.20.1 Forge and `c:` on 1.21 NeoForge; verify the actual pack.
- Registry-ID/tag filters cannot distinguish same-ID NBT/component variants. Transport preserves components, but these filters do not select by them.
- Prefer native slot locks, buffers, filters, and automatic output. Assign responsibility for each route; disable ejection only where it conflicts with SFM.
- Verify full-storage behavior. Machines may stop, discard overflow, or offer configurable voiding. Continued operation does not prove lossless processing.

## Mekanism

- Configure sides **separately for items, fluids, chemicals, and energy**. Null-side access may be read-only; use explicit sides and inspect capabilities. Copy settings with a Configuration Card.
- Standard processing `InputInventorySlot` implementations restrict external extraction, allowing supported machines to share an input/output face. Do not generalize this to tanks, ordinary inventories, or all special machines.
- MC 1.21.1 builds unify chemicals under `chemical::`; older names such as `gas::` are aliases there. Earlier builds distinguish types.
- Use exact chemical IDs or `forget` boundaries when different chemicals enter different faces of one machine.
- Checked upstream separator recipes: 2 mB water → 2 hydrogen + 1 oxygen; 10 mB brine → 1 sodium + 1 chlorine. Size storage from actual production and consumption, not fixed tank-count ratios.
- ME chemical storage requires appropriate integration such as Applied Mekanistics. Base AE2 item/fluid capabilities do not substitute for chemical capabilities.
- Fusion fueling needs per-tick validation. Pulse width is not pulse period. The adaptive example in `templates.md` is an unverified community experiment, not a continuous-fueling guarantee.

## AE2 and addons

- **Blocking Mode and result locking differ.** Ordinary blocking checks whether adjacent storage still contains pattern inputs. Emptying the staging chest may allow another batch immediately. For strict serialization, use **Lock Crafting → Until primary crafting result is returned**, and route the primary result through **the same Pattern Provider's return inventory**. An ordinary ME Interface does not establish that unlock path.
- Jobs with no physical result need a real completion signal. A token may be declared as a pattern result only if the process actually returns or creates it.
- Parallel stations need independent buffers, pedestals, cores, and providers unless a verified role-based allocation scheme guarantees complete recipes at every station. `to each` and multiplied pattern quantities do not guarantee this.
- For component-sensitive sorting, use exact-match storage/export devices to populate dedicated containers. Do not enable fuzzy matching that ignores the distinguishing component.
- **AE2 Inscriber:** start with a small input buffer. Sided-separation settings change accessible slots; null/internal and directional automation mappings must be checked separately. Preload presses.
- **ExtendedAE (`extendedae`):** provides the Extended Inscriber and Crystal Assembler. In the checked branch, the Inscriber has four threads, each with three inputs and one output, and 1/4/64 buffer options. The Crystal Assembler has nine inputs and one output. Use buffer limits and ingredient-role slots before custom state logic.
- **AdvancedAE (`advanced_ae`):** a separate mod. Native limited export/I/O buses and reaction-chamber features may simplify automation. Confirm the actual machine and recipe before adapting the crystal-loop skeleton.

## GregTech CEu Modern

- Label input buses, input hatches, and output hatches separately. Access the appropriate part rather than assuming the controller exposes all resources.
- Single-tank, 4/9-compartment, and ME hatches expose different capabilities. Use verified independent tanks/hatches or multi-compartment storage; “one hatch holds one fluid” is not a universal rule.
- Fixed recipes simplify routing but are not an inherent machine limitation. Document circuits, molds, and nonconsumed catalysts as one-time setup. Recipe switching needs a clearing/recovery design.
- Verify GT voltage/EU requirements; do not assume FE support. Isolate material stages with `input → output → forget` and provide usable receiving capacity for every byproduct.

## Mystical Agriculture

- Each altar uses its own surrounding pedestals. Supply one item per required pedestal according to a complete recipe; correct aggregate quantities across several altars are insufficient.
- **Activate the altar:** the checked 1.21 branch requires redstone or activation interaction. A constant signal can support automation. A switch on the SFM manager does not automatically activate the altar.
- Verified `#c:seeds` or `#mysticalagriculture:seeds` tags may help collect seed recipes. Non-seed recipes need their own result filter or isolated output slot.
- `"mysticalagriculture:.*_seed_base"` matches seed bases only. Verify other primary ingredients separately. Slow recipes often need polling only about every 100 ticks.

## Productive Bees

- Configurable combs use **`productivebees:configurable_honeycomb`**. The checked 1.21 branch stores the variant in the `BEE_TYPE` data component. SFM can transport them together; sort variants first with exact component-aware filtering when needed.
- **Centrifuges may lose fluids.** At checked commit `656641c1054dde8aa8690a10e6bb07ff1e75da41`, fluid space is omitted from recipe readiness and uninserted fluid is ignored at completion. Powered Centrifuges inherit this behavior. A full tank or incompatible fluid may cause loss while item processing continues.
- For fluids that must be kept, export continuously, monitor buffers, and stop input before capacity is exhausted. Grouping machines by fluid output can avoid incompatible-fluid contention. Add a void route only with permission to discard that byproduct; retest other versions/packs.

## Thermal

- The Phytogenic Insolator has seed input, catalyst input, water, and output storage. Configure capabilities separately; the array example uses the top face. Confirm the installed recipe in JEI.
- The checked 1.20.x branch supports a cyclical-processing augment that recovers matching seeds. State whether it is installed and how remaining seeds return. Do not assume every machine has that upgrade.

## Modern Industrialization

- Supply matching-voltage EU through MI cables by default. The checked branch defaults `bidirectionalEnergyCompat` to false; do not assume `output fe::` powers an Assembler. Use FE only after checking the configuration and exposed compatible capability.
- Use native slot locks, per-slot limits, and automatic output to stop one ingredient from occupying all input slots. Verify recipes and fluid requirements in the pack.

## Refined Storage

Use exact component-aware filtering to separate variants. RS 1.x/2.x/3.x interfaces and behavior differ. In the checked newer documentation, External Storage defaults to blacklist mode and Fuzzy is off. Specify allow-list versus deny-list mode and exact matching explicitly.

## Ritual and multistep mods

First inspect automation capabilities. Use a right-click simulator only when the relevant operation requires it. Distinguish ingredient insertion, activation, processing conditions, and result extraction.

- **Occultism 1.21.1:** Sacrificial Bowls support item handling; inserting the activation item into a Golden Sacrificial Bowl validates and attempts to start the ritual. Stage secondary ingredients first and the activation item last. Check the pentacle and other conditions, and provide a real completion signal.
- **Ars Nouveau:** design Imbuement Chamber and Enchanting Apparatus workflows separately. Chamber pedestal ingredients are generally nonconsumed recipe conditions; configure them once rather than distributing them every batch. Source and FE are different systems.
- **Oritech 1.21:** use the accelerator's speed sensor → comparator → second-particle insertion at the required threshold. Motors supply acceleration energy. A generic one-shot discharge is not a complete accelerator controller. Declare any simplifying addon and its version.

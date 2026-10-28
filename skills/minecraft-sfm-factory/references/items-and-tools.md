# SFM blocks, items, and in-game tools

Read this for block names, Label Gun and Network Tool operation, editor shortcuts, and physical setup. Names below follow the upstream English localization; key bindings may be remapped.

| Block or item | Purpose |
|---|---|
| Factory Manager | Runs the inserted disk. Several managers may share a cable network. The manager acts as cable and can access itself from 4.27.0, including disk replacement |
| Tunnelled Factory Manager, 4.27.0+ | Manager functionality plus straight-through capability access between opposite faces, for example hopper → manager → chest. Supports item/fluid/energy/chemical interfaces, but does not tunnel redstone signals |
| Inventory Cable | Connects managers and targets. The program's side selection is independent of the cable's attachment face |
| Fancy Inventory Cable, 4.20.0+ | Smaller cable model with equivalent connectivity; supports facades and, from 4.34.0, waterlogging |
| Tunnelled Inventory Cable / Tough Inventory Cable, 4.29.0+ | Tunneling through blocks / blast-resistant cabling |
| Factory Manager Program Disk | Stores code and labels; insert it to run, or right-click while holding it to edit |
| Label Gun | Assigns labels to world positions and exchanges mappings with the disk |
| Network Tool | Inspects networks and capabilities; also used when applying cable facades |
| Water Tank | Renewable water source when activated by adjacent source blocks; see below |
| Printing Press | Copies disks and other supported items; consult JEI for the installed version's recipes |

Basic setup: insert disk → connect targets → write the program → pull its labels into the Label Gun → assign blocks → push labels back → inspect warnings and test.

## Label Gun

| Default action | Effect |
|---|---|
| Right-click air | Open the GUI to search/create labels, Prune unused labels, or change label rendering |
| Right-click a block | Add/remove the active label |
| Shift+right-click a block | Clear all labels on that block |
| Ctrl+right-click a block | Contiguous mode: label/unlabel nearby matching connected blocks. Searches around valid blocks within a 3×3×3 neighborhood; blocks not touching a cable network are skipped with a chat message |
| Alt+right-click a block, 4.20.0+ | Pick a label from that block |
| Shift+scroll | Cycle labels alphabetically; binding configurable from 4.24.0 |
| Right-click the manager | **Push:** gun mappings → disk |
| Shift+right-click the manager | **Pull:** disk mappings → gun |
| Alt, 4.20.0+ | Change label rendering mode |

Manager clicks have special push/pull behavior. Recommended order: write code, pull labels from the manager, label the world blocks, then push. A label names a **block position**, not a face; the program specifies the face.

## Network Tool

While held, the tool highlights managers, cables, and labels through blocks.

- **Main-hand right-click a target:** inspect its BlockState, cable-network membership, resource capabilities, and accessible sides. Click the relevant face when diagnosing a route.
- **Apply facades, 4.20.0+:** hold the Network Tool in the offhand and the facade block in the main hand, then right-click a cable.

| Facade modifier | Scope |
|---|---|
| None | One block |
| Ctrl | Contiguous matching blocks |
| Alt | Matching blocks throughout the cable network |
| Ctrl+Alt | All blocks in the cable network |

From 4.29.0, the tool can be tuned to a block position.

## Water Tanks

A tank becomes active with at least two adjacent water source blocks. Check placement and activation rather than treating any tank as infinite water.

- Before 4.20.0, older behavior was documented as a fixed 1,000 mB supply; use the matching version's source when supporting it.
- In the checked modern implementation, an active tank exposes an amount based on connected active tanks: `1000 × 2^(active tanks − 1)` mB, subject to integer limits. Draining copies water without consuming the renewable supply.
- **This formula describes the exposed amount/per-drain ceiling, not a guaranteed mB-per-tick throughput.** Trigger frequency, transfer calls, and the receiving capability still matter.
- `/sfm bust_water_network_cache` clears the water-network cache if topology is stale.

## Editor and inspector shortcuts

| Default shortcut | Action |
|---|---|
| Ctrl+E in manager GUI | Open the program editor |
| Ctrl+Shift+E in manager GUI | Open example/template programs |
| Ctrl+/ | Toggle `--` comments |
| Tab / Shift+Tab | Indent / unindent |
| `\`, 4.21.0+ | Accept completion; configurable from 4.32.0 |
| Shift+Enter | Save and close the editor |
| Ctrl+Backspace / Ctrl+Delete | Delete to a word boundary |
| Home / End | Start/end of line |
| Ctrl+Home / Ctrl+End | Start/end of document |
| Ctrl+Space | Inspect available IDs, labels, or completions at the relevant program position; resources in labeled containers are especially useful |
| Ctrl+I in a container GUI | Toggle the Container Inspector, show GUI slot indices, and access export tools |
| Lower-left `#` / editor configuration button, 4.21.0+ | Line-number and completion settings |

**GUI slot indices may differ from automation indices.** Confirm side-specific capabilities and mappings before using `slots` in a production program. A conservative disk budget is about 32,300 characters; the checked source constant is 32,600.

## Practical setup notes

- **IDs and tags:** F3+H enables advanced item tooltips with registry IDs. Use JEI/EMI or SFM inspection for tags; do not assume the ID is also a tag.
- **Several labels per block:** one machine may belong to both `powered_machines` and `oxidizers`, sharing energy distribution while retaining separate material routes.
- **Relative sides:** `front` follows the block's facing, which depends on placement and mod behavior. Confirm it with the Network Tool.
- **Mekanism Configuration Card:** configure one machine, then copy its settings to matching machines in an array.
- **Cable face and access face are independent:** the cable only needs to connect the block; SFML selects the capability face.
- **Transfer limits:** SFM may bypass a machine's native automatic-ejection schedule by accessing its inventory directly. It still respects capability insertion/extraction rules and transfer limits; do not promise unlimited throughput.

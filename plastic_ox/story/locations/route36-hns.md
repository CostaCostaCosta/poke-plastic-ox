---
title: Route 36
slug: route36-hns
kind: Route
act: 1
stage: "3 — Goldenrod to Ecruteak"
depth: full
wiki: route36-hns
maps: [Route36_hns]
flags: [FLAG_POX_SUDOWOODO_CLEARED, FLAG_POX_ROUTE36_SNORLAX_CLEARED]
trainers: [TRAINER_PLASTIC_OX_PU_ROUTE36, TRAINER_PLASTIC_OX_JOHTO_ALAN]
items: [ITEM_AWAKENING, ITEM_SQUIRT_BOTTLE, ITEM_POKE_FLUTE]
status: drafted
---

# Route 36

## Snapshot

A crossroads rather than a corridor: the road down to Route 35, the road up to Route 37, a short spur into the National Park gate, and a third road east that is deliberately unusable. The odd tree at the junction is Stage 3's only puzzle — Whitney's badge, a borrowed SquirtBottle, a Lv. 20 Sudowoodo. The note is a junction that reads as a promise: three directions visibly exist and you are allowed exactly one of them.

## Plot points

1. **The junction reads as a junction.** Real connections `up` to `MAP_ROUTE37_HNS` and `down` to `MAP_ROUTE35_HNS`, a warp at `(16,20)` into `Gate_NationalPark_hns`, and the blocked eastern road. The player should see all four before touching any of them.
2. **Sudowoodo, and the borrowed bottle.** `Pox_Sudowoodo` at `(39,19)` refuses until `FLAG_BADGE02_GET` and `ITEM_SQUIRT_BOTTLE` are both present; the waiting line points at "someone near WHITNEY's GYM", i.e. the `GoldenrodCity_FlowerShop_hns` giver. Spending the bottle starts a single wild Lv. 20 Sudowoodo; catch or defeat both set `FLAG_POX_SUDOWOODO_CLEARED`, remove the object and take the bottle back. One clean errand: talk, walk back, walk out.
3. **The east road is closed on purpose.** Snorlax at `(43,19)` blocks it until `ITEM_POKE_FLUTE`, which Mr. Fuji hands out in Lavender, long after this stage; past him the coord event at `(65,18)` (`PoxRegion_route36_shortcut_a`) refuses the seam unless `FLAG_POX_REACHED_FORTREE` is set. Keep the visible teasing; two locks on one road is the open question below.
4. **The Ruins gate guards nothing.** Three identical men at `(55,25)`, `(56,25)`, `(57,25)` all run `Route36_EventScript_RuinsGateClosed` and repeat one line about the Ruins of Alph. No Ruins map exists in the build.
5. **Reveal ladder: nothing here.** Step 4 at most, and unused. The east road is a geography tease, not a clue; the bible asks that this obstruction feel physical and ordinary.

**Must not:** name Route 110, Fortree or Lavender on the sign or in refusal text; explain why the east road exists; let Sudowoodo talk; put a Rocket, a researcher or a "strange signal" on this map.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Sudowoodo check | `(39,19)`, `Pox_Sudowoodo` | `FLAG_POX_SUDOWOODO_CLEARED` unset, badge 2 or bottle missing | refuses with a hint naming Whitney's Gym | keep the hint, but sound like a park warden's advice, not a fetch-quest log |
| Sudowoodo battle | `(39,19)` | badge 2 set + `ITEM_SQUIRT_BOTTLE` held | wild `SPECIES_SUDOWOODO` Lv. 20; catch or win clears and returns the bottle | keep; add a line about the flattened grass afterwards |
| East road block | `(43,19)`, `Route36_EventScript_Snorlax` | no `ITEM_POKE_FLUTE` | "SNORLAX blocks the eastern road" + flute hint | keep the block; do not name who holds the flute |
| Snorlax woken | `(43,19)` | flute held | Lv. 30 battle, sets `FLAG_POX_ROUTE36_SNORLAX_CLEARED` | keep; the "went back to sleep" retry line is good |
| Shortcut seam | coord `(65,18)`, `PoxRegion_route36_shortcut_a` | `FLAG_POX_REACHED_FORTREE` | bounce back with `PoxRegion_ClosedText` ("Return after your next objective") | replace the system register with a physical obstruction line |
| PU trainer | `(24,24)`, `Pox_PU_ROUTE36` | unbeaten | `TRAINER_PLASTIC_OX_PU_ROUTE36`, six Lv. 21 | keep; his after-line about the moving tree is the map's best foreshadow |
| Alan | `(31,23)`, `Route36_EventScript_Alan` | unbeaten | `TRAINER_PLASTIC_OX_JOHTO_ALAN`, Magnemite / Ponyta Lv. 21 | keep; his notebook already points at Sudowoodo |
| Ruins minders | `(55,25)`/`(56,25)`/`(57,25)` | always | three identical sprites, one repeated line | cut to one man with one specific job, or delete all three |
| Wall repairman | `(46,20)`, `LOCALID_ROUTE36_ROCKSMASHGUY` | always | dry-stone wall monologue | keep; he should react once Sudowoodo is gone |
| Orphan text | `Route36_EventScript_Npc4`, `Npc5` | no object uses them | bird and sketch lines sit unused in the script file | attach or delete; unused labels rot |
| Hidden item | `(59,17)` | once | `ITEM_AWAKENING` | keep; it is the only reward for walking the dead-end east stub |

## Dialogue guidance

- **The wall repairman** is the anchor: craft terms, frost heave, which wall is older, and time measured by the junction rather than by badges.
- **Alan** is a schoolboy botanist quietly rethinking his hobby because a tree turned out to be an animal. Earnest, slightly deflated, never comic relief.
- **Travellers** (triathlete, the boy, the psychic) talk about habit and route lore — Thursday family lunches, seeds that bloom early, a tree that moves. The psychic stays uncanny and unhelpful.
- The **one remaining Ruins minder** should sound bored and institutional. He is guarding a fence, not a secret. After Sudowoodo everything shifts a half-step: the repairman mentions the grass, Alan has something new to draw, the trainer stops hinting and starts asking about Ecruteak.

> WALL REPAIRMAN: That course hasn't moved since my grandfather's day. The tree moved instead, and nobody wants to talk about it.

> ALAN: I pressed a leaf from it. It was warm. Leaves are not supposed to be warm.

> PSYCHIC: Don't stare at it. It can tell when it's being watched, and it dislikes being flattered.

> TRIATHLETE: My grandmother still sets four places on Thursdays. Two of us come. She sets four anyway.

**Do not:** explain where the east road goes, describe the convergence, or let Alan or the psychic correctly diagnose Sudowoodo before the bottle does. Do not give the Ruins minder lore the build cannot pay off.

## Inspiration

- **Gen 2's Route 36 junction:** a crossroad with a stationary obstacle in the middle, berry trees along the edge, and an NPC who repairs dry-stone walls. The drama is entirely "what is blocking the road today".
- **Dry-stone walling in the Cotswolds:** no mortar, no frost tolerance, a lifetime of maintenance. One NPC, a real job, complaints about frost, walkers and a fallen branch.
- **The archaeology-fence problem:** real sites close with a chain and a laminated notice. That is the register for a door leading nowhere — a bored custodian, not a mystic.
- **Japanese three-way junctions:** a tiny shrine, a mirror, a vending machine, a signboard with distances scraped off. Good dressing and a place for overheard directions.
- **Sudowoodo in the anime:** the "don't water it" joke works because everyone treats it as scenery. Let the locals be wrong in a grounded way.

## Implementation hooks

- Wiki page: `route36-hns.html`
- Maps: `Route36_hns` (`MAP_ROUTE36_HNS`); neighbours `MAP_ROUTE35_HNS`, `MAP_ROUTE37_HNS`, `MAP_GATE_NATIONAL_PARK_HNS`
- Scripts: `data/maps/Route36_hns/scripts.inc` (`Route36_EventScript_Snorlax`, `Route36_EventScript_RuinsGateClosed`, `Route36_EventScript_Alan`); `data/scripts/plastic_ox_story.inc` (`Pox_Sudowoodo`); `data/scripts/plastic_ox_region.inc` (`PoxRegion_route36_shortcut_a`, `PoxRegion_ClosedText`)
- Flags: `FLAG_POX_SUDOWOODO_CLEARED`, `FLAG_POX_ROUTE36_SNORLAX_CLEARED`, badge 2 (`FLAG_BADGE02_GET`), `FLAG_POX_REACHED_FORTREE` at the seam
- Items: `ITEM_SQUIRT_BOTTLE` (borrowed from the Goldenrod flower shop), `ITEM_POKE_FLUTE` (Lavender), hidden `ITEM_AWAKENING` at `(59,17)`; trainers `TRAINER_PLASTIC_OX_PU_ROUTE36`, `TRAINER_PLASTIC_OX_JOHTO_ALAN`
- Known gaps: three duplicate Ruins minders guarding a non-existent interior; generic `PoxRegion_ClosedText` used for an in-world obstruction; orphan labels `Route36_EventScript_Npc4`/`Npc5`; the east stub is walked only for the hidden Awakening.

## Open questions

- Snorlax is approved as-is: keep the visible block and the second lock. Waking him is the moment the player learns the road goes somewhere new, even while `FLAG_POX_REACHED_FORTREE` holds the seam shut.
- Should the Ruins of Alph gate become an honest "not in this build" sign, one bored guard, or a removable prop? Do not leave three clones.
- Does Route 36 need any Eevee / Bill-family texture (ladder step 4), or is that Goldenrod's alone? Recommendation: Goldenrod only.

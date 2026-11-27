---
title: Route 36
slug: route36-hns
kind: Route
act: 1
stage: "3 — Goldenrod to Ecruteak"
depth: full
wiki: route36-hns
maps: [Route36_hns]
flags: [FLAG_POX_SUDOWOODO_CLEARED, FLAG_POX_ROUTE36_SLEEPER_MOVED, FLAG_POX_HIDE_RUINS_RESEARCHER, FLAG_POX_STORY_MANSION]
trainers: [TRAINER_PLASTIC_OX_PU_ROUTE36, TRAINER_PLASTIC_OX_JOHTO_ALAN]
items: [ITEM_AWAKENING, ITEM_SQUIRT_BOTTLE]
status: drafted
---

# Route 36

## Snapshot

A crossroads rather than a corridor: the road down to Route 35, the road up to Route 37, a short spur into the National Park gate, and a third road east that is deliberately unusable. The odd tree at the junction is Stage 3's only puzzle — Whitney's badge, a borrowed SquirtBottle, a Lv. 20 Sudowoodo. The note is a junction that reads as a promise: three directions visibly exist and you are allowed exactly one of them.

## Plot points

1. **The junction reads as a junction.** Real connections `up` to `MAP_ROUTE37_HNS` and `down` to `MAP_ROUTE35_HNS`, a warp at `(16,20)` into `Gate_NationalPark_hns`, and the blocked eastern road. The player should see all four before touching any of them.
2. **Sudowoodo, and the borrowed bottle.** `Pox_Sudowoodo` at `(39,19)` refuses until `FLAG_BADGE02_GET` and `ITEM_SQUIRT_BOTTLE` are both present; the waiting line points at "someone near WHITNEY's GYM", i.e. the `GoldenrodCity_FlowerShop_hns` giver. Spending the bottle starts a single wild Lv. 20 Sudowoodo; catch or defeat both set `FLAG_POX_SUDOWOODO_CLEARED`, remove the object and take the bottle back. One clean errand: talk, walk back, walk out.
3. **The east road is closed on purpose.** A hiker is asleep across it at `(43,19)` (`Route36_EventScript_Sleeper`). Spoken to, he only mumbles about "the feather one" until the player holds Winona's badge (`FLAG_BADGE04_GET`); then he wakes, walks off and sets `FLAG_POX_ROUTE36_SLEEPER_MOVED`. Past him the road runs off the east edge as a real connection to Route 110's west spur (rows `18..22`), whose edge tiles still refuse without `FLAG_POX_REACHED_FORTREE`. He replaced the Snorlax and its Poké Flute lock.
4. **The Ruins gate has one keeper and a real door.** A researcher stands in the middle lane of the south path at `(56,24)` (`Route36_EventScript_RuinsResearcher`); step triggers on `(55,24)` and `(57,24)` (`Route36_EventScript_RuinsResearcherStep`) cover the lanes beside him. Until the Cinnabar archives are read (`FLAG_POX_STORY_MANSION`) he says the dig is closed while the team is away and the player is turned back. After it he says a crate of old site records came up from Cinnabar, walks down into the gatehouse and sets `FLAG_POX_HIDE_RUINS_RESEARCHER`; the three lanes `(55,25)`–`(57,25)` then warp into `Gate_RuinsOfAlph_Route36_hns`, where he sits at the desk with a new line. The Mansion flag is checked when the player arrives, so a save that already finished Cinnabar is let through on its first visit. There is still no seam: the dig site is reached through the gatehouse only.
5. **Reveal ladder: nothing here.** Step 4 at most, and unused. The east road is a geography tease, not a clue; the bible asks that this obstruction feel physical and ordinary.

**Must not:** name Route 110, Fortree or Lavender on the sign or in refusal text; explain why the east road exists; let Sudowoodo talk; put a Rocket or a "strange signal" on this map; let the Ruins researcher say anything about why the land changed (he minds a gate and reads a delivery note).

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Sudowoodo check | `(39,19)`, `Pox_Sudowoodo` | `FLAG_POX_SUDOWOODO_CLEARED` unset, badge 2 or bottle missing | refuses with a hint naming Whitney's Gym | keep the hint, but sound like a park warden's advice, not a fetch-quest log |
| Sudowoodo battle | `(39,19)` | badge 2 set + `ITEM_SQUIRT_BOTTLE` held | wild `SPECIES_SUDOWOODO` Lv. 20; catch or win clears and returns the bottle | keep; add a line about the flattened grass afterwards |
| East road block | `(43,19)`, `Route36_EventScript_Sleeper` | badge 4 unset | "Zzz…" and a sleep-talked hint about the feather badge | keep; never name Fortree or Winona outright |
| Sleeper woken | `(43,19)` | badge 4 set | wakes, says his piece, walks away from the player, sets `FLAG_POX_ROUTE36_SLEEPER_MOVED` | keep; works from either side of him |
| Shortcut seam | east edge `(65,18..22)`, `PoxRegion_route36_shortcut_a` | `FLAG_POX_REACHED_FORTREE` | open: walk straight across into Route 110 `(0,67..71)`; closed: `PoxRegion_ClosedText` and a step back | replace the system register with a physical obstruction line |
| PU trainer | `(24,24)`, `Pox_PU_ROUTE36` | unbeaten | `TRAINER_PLASTIC_OX_PU_ROUTE36`, six Lv. 21 | keep; his after-line about the moving tree is the map's best foreshadow |
| Alan | `(31,23)`, `Route36_EventScript_Alan` | unbeaten | `TRAINER_PLASTIC_OX_JOHTO_ALAN`, Magnemite / Ponyta Lv. 21 | keep; his notebook already points at Sudowoodo |
| Ruins researcher | `(56,24)`, triggers `(55,24)`/`(57,24)` | `FLAG_POX_STORY_MANSION` unset | "the dig is closed while the team is away"; the side lanes push the player back a step | keep; bored and institutional |
| Ruins researcher opens | same | `FLAG_POX_STORY_MANSION` set | names the crate from Cinnabar, walks into the gatehouse, sets `FLAG_POX_HIDE_RUINS_RESEARCHER` | keep; he reappears at the gatehouse desk |
| Ruins gate | `(55,25)`–`(57,25)` south arrows | researcher gone | warp to `Gate_RuinsOfAlph_Route36_hns` `(7,1)`; the gatehouse returns to `(56,25)` | keep |
| Wall repairman | `(46,20)`, `LOCALID_ROUTE36_ROCKSMASHGUY` | always | dry-stone wall monologue | keep; he should react once Sudowoodo is gone |
| Orphan text | `Route36_EventScript_Npc4`, `Npc5` | no object uses them | bird and sketch lines sit unused in the script file | attach or delete; unused labels rot |
| Hidden item | `(59,17)` | once | `ITEM_AWAKENING` | keep; it is the only reward for walking the dead-end east stub |

## Dialogue guidance

- **The wall repairman** is the anchor: craft terms, frost heave, which wall is older, and time measured by the junction rather than by badges.
- **Alan** is a schoolboy botanist quietly rethinking his hobby because a tree turned out to be an animal. Earnest, slightly deflated, never comic relief.
- **Travellers** (triathlete, the boy, the psychic) talk about habit and route lore — Thursday family lunches, seeds that bloom early, a tree that moves. The psychic stays uncanny and unhelpful.
- The **Ruins researcher** should sound bored and institutional. He is guarding a fence, not a secret, and what reopens the dig is a delivery, not a revelation. After Sudowoodo everything shifts a half-step: the repairman mentions the grass, Alan has something new to draw, the trainer stops hinting and starts asking about Ecruteak.

> WALL REPAIRMAN: That course hasn't moved since my grandfather's day. The tree moved instead, and nobody wants to talk about it.

> ALAN: I pressed a leaf from it. It was warm. Leaves are not supposed to be warm.

> PSYCHIC: Don't stare at it. It can tell when it's being watched, and it dislikes being flattered.

> TRIATHLETE: My grandmother still sets four places on Thursdays. Two of us come. She sets four anyway.

**Do not:** explain where the east road goes, describe the convergence, or let Alan or the psychic correctly diagnose Sudowoodo before the bottle does. Do not give the Ruins researcher lore the build cannot pay off: he may name Cinnabar, the Mansion and Dr. Fuji's site records, nothing wider.

## Inspiration

- **Gen 2's Route 36 junction:** a crossroad with a stationary obstacle in the middle, berry trees along the edge, and an NPC who repairs dry-stone walls. The drama is entirely "what is blocking the road today".
- **Dry-stone walling in the Cotswolds:** no mortar, no frost tolerance, a lifetime of maintenance. One NPC, a real job, complaints about frost, walkers and a fallen branch.
- **The archaeology-fence problem:** real sites close with a chain and a laminated notice. That is the register for a door leading nowhere — a bored custodian, not a mystic.
- **Japanese three-way junctions:** a tiny shrine, a mirror, a vending machine, a signboard with distances scraped off. Good dressing and a place for overheard directions.
- **Sudowoodo in the anime:** the "don't water it" joke works because everyone treats it as scenery. Let the locals be wrong in a grounded way.

## Implementation hooks

- Wiki page: `route36-hns.html`
- Maps: `Route36_hns` (`MAP_ROUTE36_HNS`); neighbours `MAP_ROUTE35_HNS`, `MAP_ROUTE37_HNS`, `MAP_GATE_NATIONAL_PARK_HNS`, `MAP_GATE_RUINS_OF_ALPH_ROUTE36_HNS`
- Scripts: `data/maps/Route36_hns/scripts.inc` (`Route36_EventScript_Sleeper`, `Route36_EventScript_RuinsResearcher`, `Route36_EventScript_RuinsResearcherStep`, `Route36_EventScript_Alan`); the researcher, his triggers and the gate warps are placed by `plastic_ox/alpha/region_v7.py`; `data/scripts/plastic_ox_story.inc` (`Pox_Sudowoodo`); `data/scripts/plastic_ox_region.inc` (`PoxRegion_route36_shortcut_a`, `PoxRegion_ClosedText`)
- Flags: `FLAG_POX_SUDOWOODO_CLEARED`, `FLAG_POX_ROUTE36_SLEEPER_MOVED` (id `0x914`, formerly the Snorlax flag), badge 2 (`FLAG_BADGE02_GET`), badge 4 for the sleeper, `FLAG_POX_REACHED_FORTREE` at the seam
- Items: `ITEM_SQUIRT_BOTTLE` (borrowed from the Goldenrod flower shop), hidden `ITEM_AWAKENING` at `(59,17)`; trainers `TRAINER_PLASTIC_OX_PU_ROUTE36`, `TRAINER_PLASTIC_OX_JOHTO_ALAN`
- Demo check for the Ruins gate: `plastic_ox/demo/test_ruins_of_alph.py`.
- Known gaps: generic `PoxRegion_ClosedText` used for an in-world obstruction; orphan labels `Route36_EventScript_Npc4`/`Npc5`; the east stub is walked only for the hidden Awakening.

## Open questions

- 2026-11-24: the Snorlax was replaced by the sleeping hiker at the owner's request; he moves for Winona's badge, not the Poké Flute.
- 2026-11-27: resolved. The three clones are one researcher who holds the gate until `FLAG_POX_STORY_MANSION` and then moves to the gatehouse desk; the Ruins of Alph are in the build behind him (`ruinsofalph-outside-hns`).
- Does Route 36 need any Eevee / Bill-family texture (ladder step 4), or is that Goldenrod's alone? Recommendation: Goldenrod only.

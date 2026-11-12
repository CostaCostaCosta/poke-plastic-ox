---
title: Route 37
slug: route37-hns
kind: Route
act: 1
stage: "3 — Goldenrod to Ecruteak"
depth: full
wiki: route37-hns
maps: [Route37_hns]
trainers: [TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE, TRAINER_PLASTIC_OX_JOHTO_GREG]
status: drafted
---

# Route 37

## Snapshot

The last climb before Ecruteak: an orchard road that narrows between berry trees, ends at the city connection, and has no gatehouse, no warp, no item and only five objects. It is the quietest map in Stage 3 and should stay that way — the approach that lets the player hear Ecruteak before seeing it. The note is dusk on a road that smells of fruit and somebody else's cooking.

## Plot points

1. **Approach, not arrival.** Connections only: `down` to `MAP_ROUTE36_HNS`, `up` to `MAP_ECRUTEAK_CITY_HNS`, zero warps. The map carries no gate, so the transition into Ecruteak must do the work of a gatehouse — first sight of the towers, first bell.
2. **The twins are one trainer.** ANN at `(13,29)` and ANNE at `(14,29)` both run `TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE` (Ledian, Ariados, Jigglypuff, Lv. 22). Beating one marks the shared id defeated, so the second sister silently stops battling. Either split them into two ids or make them a genuine double battle; the sisters' written voice assumes both.
3. **Roadside fruit.** A Sitrus tree at `(33,24)` (`PlasticOx_BerryTree_Route37Sitrus`) and the boy at `(20,26)` explaining the orchard keeper's "take some, leave the next crop" rule. This is the map's only economy and its best small courtesy beat.
4. **The psychic, and the bells.** Greg at `(28,27)` meditates between chimes. He is the permitted edge of ladder step 5: he can hear Ecruteak and be odd about it, but the Burned Tower's behaviour must stay inside Ecruteak.
5. **Unplaced furniture.** `Route37_EventScript_CitySign` ("ECRUTEAK CITY - NORTH") exists with no object at all, and the labels `Route37_EventScript_Npc1`–`Npc3` (ANN/ANNE/sage lines) are unused. The map is one sign and three voices short of finished.

**Must not:** show a tower anomaly, a memory effect or a ghost; explain Ecruteak's history; mention Morty, the Dance Theater's plot role, or the convergence. Route 37 is the hush, not the reveal.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| ANN | `(13,29)`, `Route37_EventScript_Ann` | trainer undefeated | single battle, shared `TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE` | split the id or run a double battle; two sisters, one of whom never fights, is a bug the player will notice |
| ANNE | `(14,29)`, `Route37_EventScript_Anne` | shared id defeated | line only, no battle | after the battle she should be rehearsing, not sulking |
| Greg | `(28,27)`, `Route37_EventScript_Greg` | undefeated | `TRAINER_PLASTIC_OX_JOHTO_GREG`, six Lv. 22 | keep; his after-line about the bell chimes is the right amount of strange |
| Orchard boy | `(20,26)`, `Route37_EventScript_Npc4` | always | Sitrus courtesy speech | keep; add a line if the tree has already been picked today |
| Sitrus tree | `(33,24)` | daily | `PlasticOx_BerryTree_Route37Sitrus` | keep; move a trainer nearer so the detour is a choice, not a chore |
| City sign | no object | — | `Route37_EventScript_CitySign` exists, unplaced | place it at the north end; the road currently announces nothing |
| Unused voices | `Route37_EventScript_Npc1`–`Npc3` | no objects | ANN, ANNE and a sage line sit in the script file | attach them to bodies or delete; they duplicate the twins' after-battle text |
| Night grass | whole map | 18:00+ table | Hoothoot, Spinarak, Murkrow replace the day mix | keep; this is the map where night should feel different, and it already does |

## Dialogue guidance

- **ANN and ANNE** finish each other's sentences about practice, not about battling. One keeps time, one keeps steps; both intend to audition at the Dance Theater and are frightened of it.
- **Greg** is the map's meter. He talks about intervals, wind direction and how far sound carries, and answers questions about Ecruteak with an anecdote instead of information.
- **The orchard boy** is proud of knowing the rule and slightly bored of explaining it. He should sound like a child left in charge of something valuable.
- Register: slower than Route 36, longer sentences, more pauses. The road is uphill and everyone here is either practising or resting.
- Before/after the twins' battle: they swap roles — the one who fought starts listening, the one who did not starts counting.

> ANN: Count it in four. If you count in three you rush the turn, and the turn is the whole dance.

> ANNE: She says that, but she has never once been on the stage. I have. It is much bigger up close.

> GREG: Six chimes tonight. Yesterday it was five, and the day before, none — but that was the wind, not the tower.

> ORCHARD BOY: Take the ripe ones only. The green ones are tomorrow's, and tomorrow has to eat too.

**Do not:** let Greg explain what the tower is or why it rings oddly; let the twins mention badges, gyms or the player's team beyond the battle itself; turn the orchard into a shop.

## Inspiration

- **Gen 2's Route 37:** the short orchard climb with the twin trainers and the berry tree, ending at Ecruteak's edge. Its whole character is "nearly there".
- **Japanese persimmon and citrus orchards on a hillside:** wooden crates, a ladder left out, an honesty box, fruit dropping on the road. Converts into the keeper's rule and into NPCs carrying crates downhill.
- **Kyoto temple bells at dusk:** the sound arriving before the building does, a difference in the air on still evenings. This is the correct dose of Ecruteak before the player enters it.
- **Dance-school siblings:** one who practises and one who performs, both certain the other has it easier. That dynamic is the map's only real dialogue engine.
- **Mountain-road dusk in autumn:** long shadows, cold starting at the ankles, someone's dinner cooking behind a hedge. Use weather and light, not lore, to set the mood.

## Implementation hooks

- Wiki page: `route37-hns.html`
- Maps: `Route37_hns` (`MAP_ROUTE37_HNS`); neighbours `MAP_ROUTE36_HNS` (south), `MAP_ECRUTEAK_CITY_HNS` (north)
- Scripts: `data/maps/Route37_hns/scripts.inc` (`Route37_EventScript_Ann`, `_Anne`, `_Greg`, `_Npc4`, `Route37_EventScript_CitySign`, unused `Route37_EventScript_Npc1`–`Npc3`); berry tree `PlasticOx_BerryTree_Route37Sitrus`
- Trainers: `TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE` (shared by two objects), `TRAINER_PLASTIC_OX_JOHTO_GREG`
- Known gaps: no placed sign object; three orphan text labels; both twins share one trainer id; zero warps and zero items, so the map has no state of its own; night encounters are set but nothing in dialogue acknowledges them.

## Open questions

- Split the twins into two trainer ids, or rewrite them as one double battle? Recommendation: one double battle — it preserves the shared-id economy and finally matches the writing.
- Should Route 37 carry a small optional scene at all (a lost crate, a rehearsal, a bell that rings twice), or is a nearly empty road the correct design? Recommendation: one scene, the twins', and nothing else.
- Place the city sign as written, or rewrite it now that Ecruteak's entrance has its own identity? The current text ("Follow the stone road through the city arch") promises an arch the map does not show.

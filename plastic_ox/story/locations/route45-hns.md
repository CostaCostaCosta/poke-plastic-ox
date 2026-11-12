---
title: Route 45
slug: route45-hns
kind: Route
act: 5
stage: "14 — Blackthorn and Clair"
depth: supporting
wiki: route45-hns
maps: [Route45_hns]
flags: [FLAG_POX_STORY_SPACE_CENTER]
status: drafted
---

# Route 45

## Snapshot

A 46 × 100 southward descent off Blackthorn's plateau, entered at `(25,1)` from `BlackthornCity_hns` and leaving at `(15,90)` for `Route46_hns`. It carries no trainer, no wild encounter, no item, and no hidden object: eight hikers stand on it reciting one line, and two signs point at raw map directory names. Treat this note as a design ticket for a corridor that v7 calls the *fast downhill return into the early world* — the walk is the whole reward, so the work is voice and directionality, not combat.

## Plot points

1. **One direction, by construction.** The north portal `(25,0)` runs `PoxRegion_blackthorn_route45_b` back to Blackthorn `(24,59)`; the south portal `(15,90)` runs `PoxRegion_route45_route46_a` to `Route46_hns` `(12,10)`. `Route46_hns` has **no** matching trigger, so the chain is a chute: a player who descends before beating Clair must climb back through Meteor Falls.
2. **The gate is the wrong predicate for the promise.** Both portals check `FLAG_POX_STORY_SPACE_CENTER`, so the road opens with the northern region — before badge 8. `plastic_ox_map_v7.md`'s gating matrix gives the unlock as *reach Blackthorn*, and the player has that on arrival. Decide which sentence is true; today the player can drop into the early world holding seven badges.
3. **Eight hikers, one script, no facing.** Every body runs `PoxRegion_TrailHint`, which is `msgbox PoxRegion_TrailText, MSGBOX_SIGN` — the hikers do not lock, do not turn, and all say "Follow the marked trails to the next town."
4. **The signs read like debug output.** `(25,2)` prints "BlackthornCity / Marked passage ahead." and `(15,88)` prints "Route46 / Marked passage ahead." Both sit within two tiles of a portal, so the first and last thing the player reads is a directory name.
5. **Nothing can happen on 100 tiles.** No `gWildMonHeaders` entry exists for `MAP_ROUTE45_HNS`, and `data/maps/Route45_hns/scripts.inc` holds only the empty arrival stub. That is either a deliberate free descent or an unfinished route; the note assumes the first and spends the budget on three voices.
6. **Reveal-ladder step 15, and nothing new.** This trail knows weather, knees and sheep. It does not know why the world is folded.

**Must not:** add a Rocket, a "convergence" line, a shortcut back uphill, a legendary sighting, or an item that outclasses Act 6 gear; do not let anyone explain the merge as geography.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Eight identical hikers | `(8,10)`, `(37,25)`, `(25,28)`, `(30,14)`, `(28,45)`, `(33,64)`, `(29,61)`, `(12,73)` all `PoxRegion_TrailHint` | always | one sign-style line, no lock, no facing | three jobs: trail crew at the top, shepherd mid-slope, kid near the bottom; delete the other five or give each a one-liner |
| North sign | `(25,2)` `PoxRegion_blackthorn_route45_b_Sign` | always | "BlackthornCity / Marked passage ahead." | "BLACKTHORN CITY — north. The pass closes in weather." |
| South sign | `(15,88)` `PoxRegion_route45_route46_a_Sign` | always | "Route46 / Marked passage ahead." | "ROUTE 46 — south. Steep. Mind your knees." |
| North portal | `(25,0)` `PoxRegion_blackthorn_route45_b` | `FLAG_POX_STORY_SPACE_CENTER` | warps to Blackthorn `(24,59)`; closed arm returns to `(25,1)` | keep; if the gate is re-keyed to `FLAG_BADGE08_GET`, rewrite the refusal to name the pass |
| South portal | `(15,90)` `PoxRegion_route45_route46_a` | `FLAG_POX_STORY_SPACE_CENTER` | warps to `Route46_hns` `(12,10)` | keep; add the missing return trigger on Route 46's side or state plainly that the descent is one-way |

## Dialogue guidance

- **Register:** seasonal labour finishing a shift. Blazes, cattle, water, knees. Everyone here is walking in the opposite direction from the player and has an opinion about the grade.
- **Trail crew** talk maintenance — paint, cairns, a washed-out culvert — and treat the player as traffic. **The shepherd** sells nothing but has a barrel and a dipper. **The kid** is local, unimpressed, and knows which shortcut will end badly.
- Before badge 8 the road is a way home from a hard place; afterwards it is the shortcut everyone promised. Nobody says so outright; the shepherd mentions the traffic and leaves it there.

> TRAIL CREW: New blaze every spring. Old ones go grey, people miss a turn, and then it's the mountain's fault, not theirs.

> UPHILL HIKER: You're going down? Sensible. I came up this in the dark and I'd like it on the record that I regret it.

> SHEPHERD: They come off that plateau smelling of cave and they all want water. Barrel's there. Dipper's there. That's the whole business.

> KID: If you're heading for ROUTE 46, don't take the short grass. There's a nest in it and it holds a grudge.

- **Do not:** make the hikers mystical, mention Blackthorn's Gym as a wonder, promise a view as a reward, or let anyone explain why the road runs one way.

## Inspiration

- **Appalachian Trail maintainers and white blazes.** Volunteer crews, painted marks, a register at a gap, complaints about through-hikers. Converts to the trail-crew hiker and to the sign rewrite above.
- **A Welsh or Scottish long-distance footpath in late autumn.** Wet stone, no trees, sheep that ignore you, a stile that needs mending. Gives the shepherd his barrel and the route its colour palette.
- **A Japanese mountain pass bus stop.** One timetable, a vending machine, drivers checking brakes before the descent. Converts to a hiker waiting for a lift that is not coming.
- **Fell-running and downhill cycling culture.** Poles, taped knees, the mantra that the descent is the reward. Explains why the uphill hiker is envious and why "one way" is a boast here rather than a bug.
- **GSC Route 45 as a set of ledges.** The original's drop-offs are what make the descent feel like falling toward the early world; the port has none, which is why the corridor currently feels flat. Reuse that idea, not its encounter table.

## Implementation hooks

- Wiki page: `route45-hns.html`; maps `Route45_hns` (`MAP_ROUTE45_HNS`, group `gMapGroup_PlasticOxV7`), neighbour `Route46_hns` (`MAP_ROUTE46_HNS`).
- Scripts: `data/maps/Route45_hns/scripts.inc` (map scripts only, empty `PoxRegion_Arrival_Route45_hns`); `data/scripts/plastic_ox_region.inc` (`PoxRegion_TrailHint`, `PoxRegion_blackthorn_route45_a/_b`, `PoxRegion_route45_route46_a`).
- Known gaps: no wild encounters registered for this map, no trainers, no items; eight NPCs share one sign-style string and never face the player; both signs print internal map names; the pair is one-way because `Route46_hns` has no return coord event; music is `MUS_RG_ROUTE3` rather than a Johto route theme.

## Open questions

- Should this route get a wild table at all? A 100-tile walk with no encounters is honest as a descent, but it is also the only route in the game with nothing to do.
- Re-key both portals to `FLAG_BADGE08_GET` so the descent happens after Clair as written in `plastic_ox_map_v7.md`, or keep `FLAG_POX_STORY_SPACE_CENTER` and accept an early return?
- Add ledges on the steep sections so the direction lives in the geometry, or keep relying on the missing Route 46 trigger for one-wayness?
- Keep Route 45 as a corridor with three voices, or retire it and send the player from Blackthorn straight to `Route46_hns`?

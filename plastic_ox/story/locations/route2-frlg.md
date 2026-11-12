---
title: Route 2
slug: route2-frlg
kind: Route
act: 1
stage: "0 — Opening network"
depth: full
wiki: route2-frlg
maps: [Route2_Frlg]
flags: [FLAG_POX_STORY_ILEX, FLAG_POX_ROUTE2_ETHER, FLAG_POX_ROUTE2_PARALYZE_HEAL]
trainers: [TRAINER_PLASTIC_OX_ROUTE2_BEN, TRAINER_PLASTIC_OX_ROUTE2_WADE]
items: [ITEM_ETHER, ITEM_PARALYZE_HEAL]
status: drafted
---

# Route 2

## Snapshot

The live Route 2: a long climb from the Cherrygrove trail to the Rustboro seam,
split at the Ilex gatehouses into two biomes. The player walks it in through Ilex
and out toward Gym 1, building an LC team from eight Kanto species in the south
grass and eleven Johto/Hoenn species in the north — a border road where the birds
change halfway.

## Plot points

1. **South half (`y ≥ 51`) is the Kanto verge.** Lv.4–6 Mankey, Growlithe,
   Vulpix, Pidgey, Rattata, Ekans, Meowth, Spearow; Ben at `(10,72)` has three
   Lv.6. Generous, shallow grass for a first team.
2. **The gate rows flip the biome.** North is Lv.7–10 Taillow, Skitty, Electrike,
   Bellsprout, Hoppip, Ralts, Magnemite, Spoink, Trapinch, Voltorb and Gulpin,
   with Hoothoot, Koffing and Gastly at night. Nobody explains it; the calls
   simply change.
3. **North half is the pre-Gym exam.** Wade at `(9,8)` sends six Lv.9 — Venonat,
   Aron, Baltoy, Spoink, Ralts, Voltorb — the fight that proves one type will not
   carry Roxanne.
4. **The hiker at `(8,0)` is the only lock.** `PoxRoute2_RustboroGate` turns the
   player back until `FLAG_POX_STORY_ILEX` is set, then vanishes and opens the
   Rustboro seam without a line of dialogue.
5. **Dark Cave is a promise, not a path.** `(17,11)` leads into
   `MAP_DARK_CAVE_SOUTH_SIDE_HNS` and on to `MAP_ROUTE46_HNS`; v7 forbids an
   early Blackthorn climb, so verify it.

**Must not:** explain the biome seam; name Bill, Rocket or Silph; make Dark Cave
mandatory; add a rival.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Ben | `Route2_Frlg` `(10,72)`, `Route2_EventScript_Ben` | `TRAINER_PLASTIC_OX_ROUTE2_BEN` | three Lv.6, then trail chat | keep; one Pokémon named as a neighbour |
| Wade | `(9,8)`, `Route2_EventScript_Wade` | `TRAINER_PLASTIC_OX_ROUTE2_WADE` | six Lv.9, then bug-net line | keep; the breadth lesson |
| Hiker | `(8,0)`, `PoxRoute2_RustboroGate` | hidden once `FLAG_POX_STORY_ILEX` is set | turns the player back to Ilex | keep; one line about the roots |
| Signs | `(7,73)` `Route2_EventScript_RouteSign`, `(14,12)` `Route2_EventScript_DiglettsCaveSign` | always | "CHERRYGROVE - RUSTBORO", "DARK CAVE" | keep; add nothing |
| Loot and Cut | `(17,54)` `PoxRoute2_Ether`, `(17,64)` `PoxRoute2_ParalyzeHeal`; trees at `(16,62)`, `(15,69)`, `(11,13)`, `(18,26)` | `FLAG_POX_ROUTE2_ETHER`, `FLAG_POX_ROUTE2_PARALYZE_HEAL`, `FLAG_TEMP_13`–`FLAG_TEMP_16` | `ITEM_ETHER`, `ITEM_PARALYZE_HEAL`, vanilla Cut trees | keep; no Cut is needed to finish the route |

## Dialogue guidance

- **Ben** treats his team as neighbours; **Wade** counts his six and explains
  breadth without saying "coverage"; **the hiker** is plain and brief. The
  gatehouse keepers keep their broom-and-carpet register — domestic and bored.
  The seam is heard, not explained.

> BEN: You came up the south trail? Then you've met my whole team. They live in
> that grass.

> WADE: Six of them, no favourites. That's the only trick I know, and it keeps
> working.

> HIKER: Roots, mostly. Roots, and one very smug PIDGEY.

- **Do not:** say "convergence" or name the regions; make the seam eerie; reuse
  Ilex's tree imagery; give Ben a quest.

## Inspiration

- **The climb out of a fruit basin.** Japan's Yamanashi and Kofu valleys: orchards
  and warm grass below, larch and colder air an hour up, birdsong changing before
  the view does. Staff it with a courier cycling the climb, a berry forager, a kid
  counting bird calls and the keeper with a broom and a schedule.

## Implementation hooks

- Wiki page: `route2-frlg.html`
- Maps: `Route2_Frlg` (`MAP_ROUTE2`), reusing `LAYOUT_ROUTE2_HNS`; the retired
  duplicate `Route2_hns` (`MAP_ROUTE2_HNS`) is covered by `route2-hns.md`.
- Scripts: `data/maps/Route2_Frlg/scripts.inc`; `PoxRoute2_RustboroGate` in
  `data/scripts/plastic_ox_region.inc`.
- Known gaps: the gatehouses, house and east building keep FRLG `ViridianForest`
  names and sprite IDs though their text is local; the east building's doors both
  return to Route 2; `Route2_House_Frlg` keeps a Mr. Mime trade asking for a
  Stantler; the Dark Cave mouth is untested against Route 46.

## Open questions

- Promote this note to `full` and demote `route2-hns`, since this is the map the
  player actually walks?
- Seal the Dark Cave mouth until the Route 45/46 return is gated, or leave it as
  visible geography?

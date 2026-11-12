---
title: Route 119
slug: route119
kind: Route
act: 2
stage: "5 — Route 119 and Fortree"
depth: full
wiki: route119
maps: [Route119]
also_maps: [Route119_WeatherInstitute_1F, Route119_WeatherInstitute_2F]
flags: [FLAG_POX_STORY_WEATHER]
items: [ITEM_CALCIUM, ITEM_ULTRA_BALL, ITEM_FULL_HEAL, ITEM_MAX_ETHER]
trainers: [TRAINER_PLASTIC_OX_WEATHER]
status: drafted
---

# Route 119

## Snapshot

A river gorge climbing through wet forest, crossed by three wooden decks, with a weather station bolted to the cliff halfway up. The player fights up it, is asked to help the Institute finish its survey, and only then may pass east to `FortreeCity`. This is reveal-ladder step 6: the region is not a finished wreck, it is still being edited, and the evidence is a line on a map that moved overnight.

## Plot points

1. **Arrival is wet work.** The route should read as terrain before it reads as a plot stop: tall grass on the switchbacks, decks that flex, a river running lower than the flood marks on the piers. The player's only job here is to get up the gorge.
2. **The Institute is a workplace, not a base.** `Route119_WeatherInstitute_1F` staff meet the player with instrument problems, not a rescue. Their line to the player should be a task: the survey is short-handed.
3. **The test battle.** On 2F, the duty scientist at `(18,6)` `Pox_Weather` requires badge 3, fights `TRAINER_PLASTIC_OX_WEATHER` (Lv.32–34), and only after the battle explains what the instruments say.
4. **Reveal-ladder step 6.** The findings are concrete and small: the habitat line moved, the rainfall total is wrong for the season, species are appearing on the wrong side of a surveyed stake line. "It is not just damage left by the initial convergence. Something is still changing our habitats."
5. **The gate east.** `(39,8)` `PoxRegion_route119_fortree_a` refuses passage until `FLAG_POX_STORY_WEATHER`, currently with the generic `PoxRegion_ClosedText`. After the flag, `FortreeCity` `(0,10)` opens in both directions permanently.
6. **After completion.** The route keeps its weather and its station; the staff stop asking for help and start filing. No second reveal.

**Must not:** name Bill, Silph, or an adaptive system; let anyone *say* "convergence" in dialogue; turn the Institute into a battle base; explain the mechanism; let the player reach Fortree before the survey flag.

## Key interactions

| Interaction | Where | Trigger / state | Current behavior | Target behavior |
| --- | --- | --- | --- | --- |
| Fortree gate | `(39,8)` `PoxRegion_route119_fortree_a` | `FLAG_POX_STORY_WEATHER` | closed → generic "still closed… next objective" text and a warp back | make the closure physical (a deck out, a washout) and give it one local who explains the delay |
| Institute door | `(6,32)` → `Route119_WeatherInstitute_1F` | always | plain warp | keep; the sign outside should read like a public office, with hours |
| Five 1F staff | `(15,3)`, `(10,5)`, `(5,4)`, `(2,11)`, `(14,11)`, all `Pox_FacilityWorker` | always | one identical line: "our field researchers can explain…" | five jobs: instrument tech, cook, archivist, driver, intern — each with a different complaint |
| Duty scientist | 2F `(18,6)` `Pox_Weather` | badge 3, `FLAG_POX_STORY_WEATHER` unset | trainer battle then a report that **uses the word "convergence"** | keep the battle; rewrite the report as readings and uncertainty, not the banned noun |
| Seven 2F workers | 2F `(15,6)`, `(10,8)`, `(4,6)`, `(0,6)`, `(1,7)`, `(16,6)`, `(19,6)` | always | all `Pox_FacilityWorker`, one line, **all on Aqua grunt sprites** | recast as institute staff on civilian sprites; this is a workplace, not a team |
| MIMIC CIRCLE | `(12,123)`, `(26,123)`, `(5,125)`, `(28,116)`, `(34,122)`, `(17,128)` | always | six Hoenn trainers whose gimmick is copying the player | cut or recast two, and give the rest river work: ferry, bridge, berries |
| Invisible Kecleon | `(31,6)`, `(25,15)` | always | "Something unseeable is in the way." | keep one as an oddity the Institute has tagged; remove the other or make it findable |
| Dead actors | `(25,32)` rival, `(17,33)` rival on bike, `(28,25) Scott` | — | three objects with script `0x0` | delete or repurpose; they are invisible to play but still cost map space |
| Berry trees | `(24,5)`–`(26,5)`, `(8,23)`, `(9,23)`, `(29,90)`, `(30,90)` | daily | `BerryTreeScript` | keep; give one picker a line about what ripens early this year |
| Hidden items | `(17,82)` `ITEM_CALCIUM`, `(38,63)` `ITEM_ULTRA_BALL`, `(26,120)` `ITEM_FULL_HEAL`, `(20,29)` `ITEM_MAX_ETHER` | once | hidden pickups | keep; `ITEM_MAX_ETHER` near the Institute reads as a dropped supply |
| Bike remark | `(19,133)` cycling triathlete | always | "tall grass snares BIKE tires" | keep; it is honest terrain information |

## Dialogue guidance

- **Institute staff speak in readings.** Numbers, times, instrument names, and what they expected instead. They are tired, competent, and not frightened yet.
- **The duty scientist** is the only person allowed to state the conclusion, and states it as a limit: "I can show you the line. I can't tell you who moved it."
- **Route people are river people:** ferry, decks, berries, fish. They notice the water level before they notice the weather station, and they resent the station slightly.
- **Trainers here are hikers and workers,** not a themed gang. Anyone whose entire personality is a gimmick (the copying circle, the ninja) should be rewritten or removed.
- After `FLAG_POX_STORY_WEATHER`, the staff's register shifts from asking to filing: shorter answers, more clipboards, no gratitude.

> RESEARCHER: Nine millimetres overnight and the gauge is fine. That isn't rain. That's the river deciding to be somewhere else.

> BRIDGE CARPENTER: Third deck in six years. I keep the old span measurements on the shed wall and the new wood doesn't match any of them.

> DUTY SCIENTIST: I can show you the line on the map. I can't show you who moved it, and I'm not going to pretend I can.

> FERRYMAN: Water's low enough to wade at the second bend. Two years ago you'd lose a boot there, and the boot with it.

- **Do not:** say "convergence" aloud; explain the cause; use "anomaly" as a noun more than once; give the Institute a villain; reuse the Burned Tower's "places remember" line.

## Inspiration

- **Hoenn Route 119 in RSE:** the vertical gorge, the rain, the Institute on stilts. The conversion is structural: keep the climb and the three decks, and let weather be a character rather than a filter.
- **Flood marks on bridge piers and old stone gauges:** painted lines recording past high water. Converts into the carpenter's span records and the single best piece of visible evidence that the river has changed its mind.
- **Ridge weather stations (Mt. Washington, UK fell tops):** a nine o'clock balloon, an iced anemometer, a logbook nobody reads. Give the staff those chores and the building stops being a set.
- **Ecological transect surveys:** a measured stake line across a meadow, resurveyed yearly, with species crossing it. This is how the Institute shows "the boundary moved" without a lecture — one stake line, one wrong plant.
- **East Asian typhoon season:** the fifth typhoon, shutters, a ferry cancellation, umbrellas sold at the trailhead. Use it for the route's small talk and the gate's closure reason.

## Implementation hooks

- Wiki page: `route119.html`
- Maps: `Route119` (`MAP_ROUTE119`), `Route119_WeatherInstitute_1F` (`MAP_ROUTE119_WEATHER_INSTITUTE_1F`), `Route119_WeatherInstitute_2F` (`MAP_ROUTE119_WEATHER_INSTITUTE_2F`)
- Scripts: `data/maps/Route119/scripts.inc`, `data/maps/Route119_WeatherInstitute_1F/scripts.inc`, `data/maps/Route119_WeatherInstitute_2F/scripts.inc`, `data/scripts/plastic_ox_story.inc` (`Pox_Weather`), `data/scripts/plastic_ox_region.inc` (`PoxRegion_route119_fortree_a/b`)
- Flags: `FLAG_POX_STORY_WEATHER` (set by `Pox_Weather_Won`); gate also respects `FLAG_POX_TRIGGERS_ENABLED`
- Trainer: `TRAINER_PLASTIC_OX_WEATHER` (Lv.32–34, Castform lead)
- Known gaps: **no implemented western access** — the canonical "Ecruteak east → Route 119" link does not exist; `Route119` has no connections and its only other entry is the Fortree gate, so the Institute is currently reachable only through the Hoenn `Route118` chain. All twelve Institute NPCs run `Pox_FacilityWorker` with one shared line on Aqua grunt sprites. Three objects have script `0x0`. The scientist's report contains the word "convergence".

## Open questions

- Where does Route 119 actually connect on the west? Nothing in `data/` links it to Ecruteak, so stage 5 cannot be walked as written.
- Recast the Institute staff as civilians, or keep the Aqua sprites as surplus uniforms bought cheap? The story has no Team Aqua, and `Route110`'s grunts make the confusion worse.
- Does the route keep the MIMIC CIRCLE at all? Six trainers doing one joke is a lot of map for a gag that predates the story.
- Should the Fortree gate stay a warp-and-refuse, or become a physical obstruction the player can see from a distance?

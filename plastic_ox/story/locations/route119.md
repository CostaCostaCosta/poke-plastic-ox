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
flags: [FLAG_POX_STORY_WEATHER, FLAG_POX_TRAINER_WEATHER_DEVON]
items: [ITEM_CALCIUM, ITEM_ULTRA_BALL, ITEM_FULL_HEAL, ITEM_MAX_ETHER]
trainers: [TRAINER_PLASTIC_OX_WEATHER_DEVON, TRAINER_PLASTIC_OX_WEATHER]
status: implemented
---

# Route 119

## Snapshot

A river gorge climbing through wet forest, crossed by three wooden decks, with a weather station bolted to the cliff halfway up. A Silph engineer has closed the Fortree crossing while **Project Equilibrium** — a joint Weather Institute / Devon / Silph study — runs its final battle trials. The player wins two research battles, the Director closes the day's experiments, and the crossing reopens. This is reveal-ladder step 6: the region is still being edited, and every edit lands somewhere tidy.

## Plot points

1. **The crossing has a face.** At `(39,8)` the generated gate `PoxRegion_route119_fortree_a` still refuses passage until `FLAG_POX_STORY_WEATHER`, but now speaks as the Silph ENGINEER at `(38,7)` (`Pox_WI_Engineer`): Devon's sensors cover the gorge, Silph's model checks itself against them live, and the team inside needs a TRAINER. The engineer is hidden by `FLAG_POX_STORY_WEATHER` and reappears on 1F `(1,11)` (`Pox_WI_EngineerInside`) afterwards.
2. **The Director frames the project.** 1F `(10,5)` `Pox_WI_Director`: "Devon brought the instruments. Silph brought the computers. We brought decades of weather observations… Mostly, we have better questions." Sends the player upstairs; Devon goes first.
3. **Trial 1 — Devon, rain.** 2F `(11,6)` `Pox_WI_Devon`, LINDEN (`TRAINER_PLASTIC_OX_WEATHER_DEVON`, id 957, Lv33–36 rain/Swift Swim). Requires badge 3. Victory flag `FLAG_POX_TRAINER_WEATHER_DEVON`.
4. **Trial 2 — Silph, sun and prediction.** 2F `(18,6)` `Pox_WI_Vale`, VALE (`TRAINER_PLASTIC_OX_WEATHER`, id 872, Lv33–36 sun). Refuses to battle until trial 1 is won. Afterwards forwards the results to Silph's head office in SAFFRON — "the roads there are closed, but the data lines still run."
5. **Conclusion.** With both trainer flags set, the Director sets `FLAG_POX_STORY_WEATHER`. Nothing downstream changed: the crossing, `PoxRegion_Arrival_FortreeCity` (`FLAG_POX_REACHED_FORTREE`) and `Pox_Winona` already key on that flag. Gabby/Ty, the Kecleon and badge 4 still hold Fortree's east exit.
6. **Reveal-ladder step 6, reconciled with the brief.** The researchers' disagreement is scientific: Devon reads the fast resettling of habitats as adaptability; Silph notes the patterns were present too soon for adaptation; the Institute collects evidence. The Director's post-event line keeps the canonical step — the habitat lines keep moving — and adds that each move lands somewhere suitable.
7. **Optional research files.** Six `Pox_WI_File00x` signs (two to five boxes each) on the 1F/2F racks and desks; none changes state.

**Must not:** say "convergence" aloud; explain the cause; name Bill; make Devon or Silph villains; introduce Steven, Aqua, Magma or Rocket; mention tiers or encounter tables; let the player reach Fortree before `FLAG_POX_STORY_WEATHER`.

## Key interactions

| Interaction | Where | Trigger / state | Behavior |
| --- | --- | --- | --- |
| Fortree crossing | Route119 `(39,8)` `PoxRegion_route119_fortree_a` | `FLAG_POX_STORY_WEATHER` unset | engineer's refusal (`Pox_Text_WI_CrossingClosed`), bounce to `(38,8)` |
| Silph engineer | Route119 `(38,7)` `Pox_WI_Engineer` | visible until `FLAG_POX_STORY_WEATHER` | explains the closure, points to the Institute |
| Engineer, indoors | 1F `(1,11)` `Pox_WI_EngineerInside` | hidden via `FLAG_TEMP_1` (1F `ON_TRANSITION`) until `FLAG_POX_STORY_WEATHER` | "sensor line pulled off the crossing" |
| Director | 1F `(10,5)` `Pox_WI_Director` | intro → halfway (trial 1 won) → conclude (both won; sets flag) → after | concise; only the conclusion writes state |
| LINDEN (Devon) | 2F `(11,6)` `Pox_WI_Devon` | badge 3; talk-triggered | battle → post line; after event: adaptability speech |
| VALE (Silph) | 2F `(18,6)` `Pox_WI_Vale` | trial 1 won; talk-triggered | battle → post line (Saffron); after event: "adaptation takes time" |
| Research files 001/003/004 | 2F racks `(5-7,2)`, `(10-14,2)`; desk `(8-9,3-5)` | always | `MSGBOX_SIGN` |
| Research files 002/005/006 | 1F rack `(9-12,2)`; cabinet `(13-14,1)`; desk `(16-17,4-6)` | always | `MSGBOX_SIGN` |
| Institute door | `(6,32)` → `Route119_WeatherInstitute_1F` | always | plain warp |
| Other 1F/2F staff | `Pox_FacilityWorker` | always | unchanged generic line; Aqua-sprite actors stay hidden |
| MIMIC CIRCLE, Kecleon, berry trees, hidden items | route | — | unchanged by this pass |

## Project Equilibrium teams (ADV RU, `fortree` checkpoint, cap 36)

Authored in `src/data/trainers.party` and listed in `KEEP_AS_IS` in `plastic_ox/agent/apply_trainer_teams_v2.py`; `plastic_ox/demo/test_weather_institute.py --static` re-checks species availability, level range, species clause, no hidden abilities, and every move against the ROM learnsets.

- **LINDEN (Devon, rain):** Politoed 34 (Rain Dance lead), Lombre 33, Huntail 33, Raichu 34 (rain Thunder), Sharpedo 33, Kabutops 36 (Swords Dance Swift Swim ace).
- **VALE (Silph, sun):** Castform 34 (Sunny Day / Weather Ball lead), Victreebel 34 (Chlorophyll), Ninetales 36, Metang 34, Magnemite 33, Xatu 35 (Calm Mind / Future Sight — the "prediction" mon).

## Future threads (not implemented)

- **VALE** is the recurring Silph researcher: quiet, curious, never alarmed. Reuse the Silph FRLG scientist sprite (`OBJ_EVENT_GFX_SCIENTIST`) and the name VALE. Mossdeep Space Center is **implemented** (`Pox_SC_Vale`, the two-beat `Pox_SpaceReport`, file 007, and the Director's post-Mossdeep line `Pox_Text_WI_DirectorMossdeep`). Still to do: Silph Co. (VALE is among the staff trapped by Rocket and is the first to admit the model was never theirs — lead-in to step 14). VALE must never name Bill.
- **LINDEN** can return in Rustboro's Devon office as the field researcher back from Route 119.
- **New Mauville:** research file 003 (data-like signals during storms) is the hook; an engineer there could cite the Institute's log.
- **Mossdeep Space Center:** done; the report opens with the Institute's survey.
- **Legendary research:** file 005 (energy under the seafloor and an old volcano) can seed Groudon/Kyogre/Rayquaza research later. Encounter requirements and the Underground Battle Ring rewards are untouched.

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
- Source of truth: `plastic_ox/alpha/weather_institute.py` (writes `data/scripts/plastic_ox_weather_institute.inc`, the three maps' Project Equilibrium objects/signs and the 1F `ON_TRANSITION`; `--check` reports drift)
- Scripts: `data/scripts/plastic_ox_weather_institute.inc` (`Pox_WI_*`), `data/scripts/plastic_ox_region.inc` (`PoxRegion_route119_fortree_a/b`; the `_a` refusal text is overridden in `region_v7.py`)
- Flags: `FLAG_POX_STORY_WEATHER` (event complete; set only by `Pox_WI_Director`), `FLAG_POX_TRAINER_WEATHER_DEVON` (`POX_EVENT_FLAGS_START + 40`, trial 1), trainer flag of id 872 (`0x4AF`, trial 2), `FLAG_TEMP_1` (1F engineer visibility, recomputed on entry)
- Trainers: `TRAINER_PLASTIC_OX_WEATHER_DEVON` (957, LINDEN), `TRAINER_PLASTIC_OX_WEATHER` (872, VALE)
- Test: `plastic_ox/demo/test_weather_institute.py`
- Known gaps: the remaining `Pox_FacilityWorker` staff share one generic line; three route objects still have script `0x0`.

## Open questions

- (Resolved) Route 119's west side now connects to Ecruteak's east gatehouse (bottom path).
- Recast the Institute staff as civilians, or keep the Aqua sprites as surplus uniforms bought cheap? The story has no Team Aqua, and `Route110`'s grunts make the confusion worse.
- Does the route keep the MIMIC CIRCLE at all? Six trainers doing one joke is a lot of map for a gag that predates the story.
- (Resolved for now) The Fortree gate stays a warp-and-refuse, now voiced by the Silph engineer standing beside it.
- The brief proposed a world that is "unexpectedly stable"; the bible's step 6 is "boundaries still moving". This pass keeps both: the lines move, the Pokémon land well. Confirm that framing before Mossdeep is written.

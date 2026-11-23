# 2026-11-22 NPC dialogue audit (cross-map)

Not a single-location pass. Three cross-cutting fixes:

1. **Duplicate dialogue gate.** New `plastic_ox/tools/audit_npc_dialogue.py`, wired into
   `make pox-check-static`. Walks every Plastic Ox map (region manifest + PlasticOx map
   groups + everything reachable by warp/connection), resolves each object's script to the
   text it can print, and fails on (a) the same text from two NPC scripts, (b) one script on
   NPCs of several maps, (c) one script on several NPCs of one map. Service prompts and
   system messages are listed with reasons in `plastic_ox/tools/npc_dialogue_allow.json`.
2. **Sprite plausibility.** Same tool: children speaking as working adults/parents, elders
   speaking as children, adults speaking as schoolkids, and inanimate objects (trees, balls)
   speaking in the first person.
3. **Gabby & Ty** now chase the invisible Kecleon (Fortree roadblock, roaming battle text in
   `data/text/tv.inc`, Slateport cameo). Fortree note updated.

## Fixed
- Weather Institute / Space Center: shared `Pox_FacilityWorker` replaced by per-object
  lines chosen for the sprite (the Institute child is on a school field trip). Generator:
  `FACILITY_LINES` in `build_story.py`.
- Story trainers: per-trainer defeat lines (`DEFEAT_LINES`), unique Tower/Silph/Moon grunt
  intros, per-room exit attendants (`ROOM_EXIT_LINES`), per-gift repeat lines for Fuji and
  the Space Center.
- League: per-ridge-trainer defeat/after lines, per-E4 after lines (`league.py`).
- Region trail signs: second line names the map the sign stands on (`region_v7.py`).
- Lavender south-road and Route 36 ruins guards: one script per guard (`region_v7.py`).
- Hand maps: Route 12/14/21/34/38, Saffron, Blackthorn, Saffron Route 6 gate, Route 44
  trainers, Oak's lab aides, Pallet Oak, Cinnabar Gym Quinn, National Park gate officers and
  contestants (generator copy `plastic_ox/alpha/national_park/gate.*`), Route 25 picnicker
  (son -> little brother), Route 36 Alan, Route 8 Aidan, Route 38 sailor.
- `local_dialogue.py` prefix bug (Route3 matched Route34/38, Route2 matched Route21).

## Left open (owned by parallel work, not edited)
- Ecruteak: Kimono dancers and Morty still use the shared `Pox_Text_Defeat`; the Burned
  Tower B1F `PoxBurnedTower_AssembledSage` script is on two NPCs; the Dance Theater and
  Morty gym exit attendants still say "I'll show you back outside."
- Allowlisted service text (haircut brothers, contest attendants, Name Raters, Frontier).

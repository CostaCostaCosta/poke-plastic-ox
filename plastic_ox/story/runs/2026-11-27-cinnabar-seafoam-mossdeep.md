# 2026-11-27 — cinnabarisland-frlg, plasticox-route20west, plasticox-route20east, mossdeepcity

- Notes: cinnabarisland-frlg, plasticox-route20west, mossdeepcity (drafted → implemented);
  plasticox-route20east audited and left empty on purpose.
- Generator: new `plastic_ox/alpha/south_isles.py` (installed last by `region_v7.apply_region`),
  emits `data/scripts/plastic_ox_south_isles.inc` (`PoxIsles_*`), rewrites named text labels in the
  area's map scripts, and patches the story scripts that fell back to the global
  `Pox_NotReady` / `Pox_Done` / `Pox_Text_Badge` lines. Sage speeches and the Mansion door are in
  `plastic_ox/alpha/cinnabar/events.inc` and `plastic_ox/alpha/seafoam/events.inc`.
- Audit findings fixed:
  - Cinnabar Pokemon Center: FRLG's One Island BILL (and two journal props) hung on FRLG-only
    flags that are 0 here, so BILL was always in the lobby and his Sevii ferry script ran.
  - Cinnabar: two interchangeable MAN_3 direction-givers ignored the closed sea; the gym guide
    advised BURN HEALS against a team with one Fire type; BLAINE, the archives and the closed
    sea all answered with shared system lines; re-reading an archive said "Good luck on the next
    road!"; the 2F Mew diary contradicted the archive story; the key was a "MANSION KEY" in
    dialogue and a SECRET KEY in the bag.
  - Seafoam: no voices at all; B4F signs were "Hint:" system text; the landing's drawn signpost
    had no text.
  - Mossdeep: town spoke vanilla Hoenn (Magma letter, Sootopolis/Wallace, Battle Frontier Scott);
    the Pokefan's and Gym guide's "after" branches hung on flags never set here; TATE & LIZA used
    the generic challenge, refusal and badge lines; the Gym guide described the Hoenn psychic
    gym; the Space Center child was an invisible object on the plan table; the EEVEE read as a prize.
- Maps touched: CinnabarIsland_Frlg (+3 people, -2 donor props, -2 direction-givers), Cinnabar
  Gym / Center / Mart / Lab (3 rooms), PokemonMansion 1F-B1F, SeafoamIslands 1F (+2) and B4F,
  PlasticOx_Route20West (+1, sign text), MossdeepCity (+2), Mossdeep Gym / Center / Mart,
  Space Center 1F, CinnabarIsland_hns (retired copy: leftovers flagged unused).
- Dialogue: 154 authored strings (20 new scripts, 34 staged or single NPC texts; the rest replace
  existing labels). No new flags, trainers or warps.
- Verified: see the PR. `plastic_ox/demo/test_south_isles.py` talks to every changed speaker in
  each story state in mGBA.
- Second pass (release readiness), same generator:
  - Gym rules: the Cinnabar and Mossdeep gym guides (`PoxIsles_CinnabarGymGuide`,
    `PoxIsles_MossdeepGymGuide`) run `CheckCinnabarGymUURules` / `CheckMossdeepGymUUBLRules`
    which now check ADV tier rules in `src/field_specials.c` (`CheckADVTierGymRules`): species at or
    below UU / UUBL in `evolution_tier_gates.h`, no Ubers, and the OHKO, evasion and Assist/Swagger
    clauses. The Little Cup bans (sleep, Thunder Wave, Baton Pass) no longer apply there. The guide
    names the first offender, or says the team is clean. It warns and does not block.
  - Entei: the sage and Entei share `PoxIsles_EnteiSage`, which asks the player to read all three
    files first and hands over to `PoxCinnabar_EnteiSage` once `FLAG_POX_STORY_MANSION` is set.
  - Mossdeep: four houses, Steven's house and the Game Corner have their own lines (mechanics unchanged).
    The Game Corner's two men now stand beside dark link cabinets, since the link is off.
  - Magma: the 14 objects are deleted from MossdeepCity and Space Center 1F/2F, and `south_isles.prune`
    removes every script block nothing reaches (about 1,200 lines). The debug menu's Steven multi
    battle keeps its 2F block, minus the Magma movements.
  - Encounters: Route 20 West gets `gPoxUURoute20West` (Surf + fishing, UU, cap 42). Route 20 East
    stays barren as its note requires.
- Third pass: every gym special uses the same helper. Rustboro is Little Cup: LC species, the
  Little Cup move/item bans and the ADV clauses. Goldenrod PU, Ecruteak NU, Fortree RU, Cinnabar UU,
  Mossdeep UUBL, and Saffron and Blackthorn OU use `CheckADVTierGymRules(tier)`. The generated
  greeters (`build_story.greeter_scripts`) and Rustboro's guide and door gain a species branch
  (result 3). `plastic_ox/demo/test_gym_rules.py` runs all eight specials in mGBA and talks to the
  reachable greeters.
- Closed in agent/gym-greeters: the gym specials now check the Species Clause and the Sand Veil /
  Soundproof bans, and Ecruteak, Fortree, Saffron and Blackthorn have greeters. Still open: the debug-only Steven multi battle
  on Space Center 2F still references Maxie/Tabitha trainers.

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
- Still open: live Cinnabar gym enforces no tier rule; Entei ritual does not wait for archive 3;
  Mossdeep houses, Game Corner and Steven's house still speak vanilla text; hidden Magma objects
  and their dead scripts remain in the Mossdeep maps; Route 20 West / East have no encounter tables.

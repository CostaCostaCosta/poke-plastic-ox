# Region Plan — Plastic Ox Alpha

Legend: `A ↔ B (dir, off)` = seamless camera connection; `A → B` = warp pair.
Offsets marked `calc` are computed by the implementing agent using the reciprocal
formula and verified by headless walk. Native maps already in this repo are marked
**(native)**.

Reciprocal offset rule (from committed demo): for A(up,+n)↔B(down,−n), n =
(width_A − width_B)/2 when the seam is vertical; analogous with heights for
horizontal seams. When reusing an hns connection verbatim (both endpoints imported),
keep hns offsets. When substituting a different map into an existing slot, compute
fresh offsets from layout dimensions in `data/layouts/layouts.json`.

## Leg A — Start & Johto loop (wave 1)

```
PalletTown_Frlg (native-stitched) N ↔ Route101 (native) N ↔ OldaleTown (native)
OldaleTown W ↔ Route29_hns E            # R29 east slot replaces NewBark (hns had offset 5); calc both sides
Route29_hns N ↔ Route46_hns S           # verbatim hns (-24/24)
Route46_hns → DarkCave_SouthSide_hns    # warp pair; cave exit → Route31_hns warp
Route31_hns S ↔ Route30_hns N           # verbatim hns (-10/10)
Route30_hns S ↔ CherrygroveCity_hns N   # verbatim hns (-9/9)
Route29_hns W ↔ CherrygroveCity_hns E   # verbatim hns (6/-6)
Route31_hns W end → gate → ILEX is wave 2 (Leg B)
```
Drop: Route29's NewBark connection. DarkCave_NorthSide not imported in alpha.
R46/R31 keep their item balls as FLAG_POX_ITEM_* hidden items.

Imports: Route29_hns, Route30_hns, Route31_hns, Route46_hns,
DarkCave_SouthSide_hns, CherrygroveCity_hns.
Tilesets (from recon): primaries Johto_General_Hns; secondaries NewBarkTown_Hns,
CherrygroveCity_Hns, Cave_Default_Hns.
Shared interiors wired here: PC_Johto, Mart_Johto, House_Generic ×2.

## Leg B — Ilex → Rustboro (wave 2) — SHIPPED (with substitutions, see below)

```
Route31_hns W-end door → Gate_AzaleaTown_IlexForest_hns → IlexForest_hns E-side warp
IlexForest_hns N ↔ Route34_hns N        # verbatim hns (-39)
Route34_hns S ↔ Route116 (native) W     # calc; cross-tileset seam accepted
Route116 E ↔ RustboroCity (native)      # native offsets already correct
```
Gate interior is small; retarget its two doors (R31 side / Ilex side).
Rustboro Gym = native RustboroCity_Gym. Devon NPCs keep native scripts + new lines.

### Wave 2 shipped topology (differs from the sketch above — logged per plan rules)
- Ilex↔Route34: the hns north seam (-39) exists but its crossing columns are
  walled; Route34's own south edge is sealed. Shipped instead: coord-warp
  portals `IlexForest (20,13) ⇄ Route34 (31,67)` (gate plaza), plus
  `Route34 (31,89) ⇄ Route116 (40,1)` for the southward leg.
- Goldenrod attaches to Route34's verbatim `up/-7` seam (north edge), so the
  walking order is Ilex → R34 → GOLDENROD → R14 → R4 → Mt.Moon(spur) → R3 →
  R2 → Rustboro → R116. Leg C's `R14 S ↔ Goldenrod S` was geometrically
  impossible (Goldenrod's south is R34); replaced by the canyon portal pair.
- Route2 east slot ↔ Route3 west slot works verbatim-free via calc offsets;
  R4↔R14 elbow DROPPED (both R14 link slots were isolated pockets);
  R14 remains reachable only through Goldenrod's canyon (scenic).
- Rustboro City's NW and SE districts are internally split (native data);
  a city portal pair `(5,10)⇄(37,9)` bridges them. R116 far point hosts the
  demo Return Stone (`warp MAP_PALLET_TOWN, 10, 4`).
- MtMoon_Cave keeps both original exits ((46,31)→R4-east landing,
  (4,12)→R4-west); traversed as an optional spur in alpha demos.

## Leg C — Rustboro → Mt. Moon → Goldenrod (wave 2)

```
RustboroCity N ↔ Route2_hns S           # calc
Route2_hns E ↔ Route3_hns W             # calc (elbow)
Route3_hns E door → MtMoon_Cave_hns     # through-dungeon warp pair
MtMoon_Cave_hns → Route4_hns W door
Route4_hns E ↔ Route13_hns W? NO — use: Route4_hns E ↔ Route14_hns N  # calc elbow via shared corner tiles
Route14_hns S ↔ GoldenrodCity_hns S     # calc
```
If the R4↔R14 elbow geometry fights the layouts, substitute any unused vertical
Kanto route (R5/R6/R26) — record the substitution here.
Goldenrod Gym (Whitney) = GoldenrodCity_Gym_hns. Bill family house =
GoldenrodCity_BillsHouse_hns (Eevee gift site).

## Leg D — Goldenrod → Park → Ecruteak (wave 3) — SHIPPED

```
GoldenrodCity_hns plaza coord portal (34,7) → Route35_hns (14,48)      # POX portal pair
Gate_GoldenrodCity_Route35_hns interior wired both ways:               # canon gate kept walkable
  (7,9)→Goldenrod(33,8)   (7,1)→Route35(14,48)
Route35_hns N coord (17,5) → NationalPark_Normal_hns (12,49)           # POX portal
NationalPark_Normal E coord (40,19) ↔ Route36_hns W (16,20)            # POX portal pair
Route36_hns N seam → Route37_hns        # map connection, offset -22 (open cols 33-41 ↔ 12-19)
Route37_hns N seam → EcruteakCity_hns   # map connection, offset -16 (open cols 16-19 ↔ 0-1)
IlexForest_hns (20,13) → Route34_hns (31,66)  # wave-2 portal re-pointed to explicit landing coords
```
Ecruteak Gym / Burned Tower / Dance Theater interiors NOT imported in wave 3
(city exterior only).

## Leg E — Ecruteak → Route119 → Fortree (+ Sea Cottage spur) (wave 3) — SHIPPED

```
EcruteakCity_hns W seam → Route38_hns   # map connection, offset -19
                                        # open rows 33-36 on Ecruteak ↔ 14-17 on R38
Route38_hns W coord portal (0,21) → Route119 native (18,138)     # POX portal pair
Route119 native W coord (0,86) → Route38_hns (1,21)              # reverse direction
Route119 traverse north on foot (native map; no HM gates)
Route119 E exit rows 6-10 → FortreeCity   # NATIVE right-connection, offset 0
FortreeCity Return Stone coord (20,4) → Pallet Town (10,4)       # wave-end shortcut home
```
Weather Institute stays native on R119 (warps/NPCs untouched).
# Sea Cottage spur: Route16/24/25_hns + Route25_BillsHouse_hns imported in
# wave 3 but NOT yet wired into the walkable graph (no portals/seams); wave 4
# continues from Fortree.


## Leg F — Fortree → Lavender (wave 4)

```
Route24_hns continues north past the R25 junction ↔ Route7_hns S        # calc
Route7_hns E ↔ LavenderTown_hns W                                       # calc
```
(If R24's north end cannot host another seam, hang R7 off Route16's east end
instead and run R24/R25 purely as the cottage spur; document whichever shipped.)
Lavender Pokémon Tower door retargeted → MAP_POKEMON_TOWER_1F (FRLG set, present).
Mr. Fuji site = LavenderTown_House1_hns.

## Leg G — Lavender → Cinnabar (wave 4)

```
LavenderTown_hns S ↔ Route12_hns N      # calc
Route12_hns W ↔ Route13_hns E           # calc
Route13_hns W ↔ Route19_hns N? use direct: Route12_hns S ↔ Route21_hns N   # calc (water)
Route21_hns S ↔ CinnabarIsland_hns N    # calc (water)
```
Cinnabar Gym door → MAP_CINNABAR_GYM (FRLG, present). Mansion entrance: add a warp
on a free Cinnabar tile → MAP_POKEMON_MANSION_1F (FRLG, present; Entei chamber B1F).

## Leg H — Cinnabar → Whirl Islands → Mossdeep (wave 5)

```
CinnabarIsland_hns E ↔ Route41_hns W    # calc (water)
Route41_hns island warp → WhirlIslands_1F_hns (through to B1F optional)
Route41_hns E ↔ MossdeepCity (native) W # native water port; calc
```

## Leg I — Mossdeep → Saffron (wave 5)

```
MossdeepCity N ↔ Route125 (native) S    # native/calc
Route125 N ↔ Route128 (native) E        # native/calc (water elbows)
Route128 W ↔ Route6_hns S               # calc (land)
Route6_hns N → Gate_SaffronCity_Route6_hns → SaffronCity_hns S          # hns canon
```

## Leg J — SHIPPED variant note: R26/IcePath/R45/VictoryRoad replaced by portal pair Blackthorn(42,22)⇄IndigoPlateau(11,13); Indigo PC interior reachable (door 11,6). Leg H Cinnabar↔R41/Mossdeep water legs DEFERRED (surf-gated; walking harness cannot cross) — Mossdeep/R125/R128 remain native-wired for post-surf play. — Saffron → Blackthorn → League (wave 5)

```
SaffronCity_hns N → Gate_SaffronCity_Route5_hns → Route5_hns S          # hns canon
Route5_hns N ↔ Route44_hns E? prefer: Route5 N ↔ Route26_hns S          # calc
Route26_hns N ↔ IcePath_1F_hns W-entrance warp                          # calc
IcePath_1F_hns E-exit warp ↔ Route45_hns N                              # calc
Route45_hns S ↔ BlackthornCity_hns S                                    # calc
BlackthornCity_hns N → VictoryRoadKanto_1F_hns (→B1F) → IndigoPlateau_hns S
IndigoPlateau_hns → IndigoPlateau_PokemonCenter_hns → League door →
MAP_ROUTE23_CHAMPION / FRLG PokemonLeague rooms (present) → Champion Bill room
```
Substitute routes freely within Kanto N-S fillers (R26/R27/R28/R44/R45) if geometry
demands; log substitutions here. Fighting Dojo (Bruno) = SaffronCity_FightingDojo_hns;
Silph climax = SaffronCity_SilphCo_hns (single-floor alpha).

## MAPSEC additions

Add sections for every imported outdoor map + dungeon/town (Johto/Kanto names from
hns `src/data/region_map/region_map_sections.json` `hns_map_sections`) into this
repo's `src/data/region_map/region_map_sections.json`, each with a region-map entry
row (x/y/w/h/name — place loosely on the Hoenn grid edges; display cosmetics only).
Regenerates `include/constants/region_map_sections.h` + `region_map_entries.h`.

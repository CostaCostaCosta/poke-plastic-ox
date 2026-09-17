# Story Triggers & Dialogue — Plastic Ox Alpha v7

Status: v7 target contract with the northern OU access change implemented in
the existing alpha scripts; full physical migration remains pending. The Pallet
implementation notes below describe existing work to preserve. Migration order
and source ambiguities are in [PLAN.md](PLAN.md); physical legs are in
[REGION_PLAN.md](REGION_PLAN.md).

## Authoring and build modes

Author generated story content in `plastic_ox/alpha/build_story.py`, which
emits an apply_patch patch. `data/scripts/plastic_ox_story.inc`,
`plastic_ox/alpha/story_manifest.json`, generated flag definitions and room/event
data must remain consistent with it. The Pallet script is separately authored
in `data/scripts/plastic_ox_pallet.inc` and included by the generator.

Keep `gPlasticOxTriggersEnabled` and the existing build initialization contract.
In the walkable build, story blockers are relaxed and trainer LOS/wild
encounters disabled. In the trigger build, shared predicates must govern
physical blockers as well as scripted transport, doors, map callbacks and
objective access. Recompute visibility on map load from persistent state so
either objective order, revisits, and save/load produce the same gates.
Distinguish presentation flags from authoritative completion flags.

## Persistent state and gate contract

Existing symbols below are reuse candidates; new symbolic names are proposed
until M0 allocates unique flags. `story_flags.json` now owns stable story IDs;
add new allocations there without renumbering or reusing retired entries.
Do not copy suggested numeric IDs from prose.
Audit both Plastic Ox flag headers, native/trainer/daily reservations and every
item placement; preserve gift identities and document save compatibility.

| State / predicate | Existing or proposed representation | When set / consumers |
|---|---|---|
| Starter, Ilex, Mt. Moon, Weather | Existing `FLAG_POX_STORY_STARTER/ILEX/MTMOON/WEATHER` | Completed opening and route objectives; retain existing starter behavior. |
| Burned Tower | Existing `FLAG_POX_STORY_BURNED_TOWER` | After the anomaly; returns Morty to Gym. Dance Theater provides the lead; optional troupe battles are not mandatory. |
| Reached Fortree | Proposed `FLAG_POX_REACHED_FORTREE` | First legitimate arrival through the Morty/Weather route; permanently opens both sides of Route36/110. |
| Fuji rescued | Existing `FLAG_POX_STORY_FUJI` | Rocket II resolved; directions to Route8 Underground and Cinnabar. |
| Mansion key / investigation | Existing `FLAG_POX_MANSION_KEY`, `FLAG_POX_STORY_MANSION` | Key delivery after Blaine must retry if bag full; archives completion enables onward sea progression. |
| Space Center complete | Existing `FLAG_POX_STORY_SPACE_CENTER` | Investigation after badge 6; opens every Saffron surface entrance. |
| Bruno defeated | Native `FLAG_BADGE07_GET` | Successful Dojo battle; separate from Silph. |
| Silph resolved | Existing `FLAG_POX_STORY_SILPH` | Giovanni defeated and core shut down; creator unnamed. |
| Saffron north open | Same Space Center flag as city access | Bruno, Silph and Clair are open-ended OU objectives. Neither badge 7 nor Silph completion gates northern travel, Clair's guide, or her battle. The legacy gate visibility flag is not an access predicate. |
| League gate open | Derived: all eight `FLAG_BADGE0x_GET` flags | Ecruteak west; badge 8 alone is insufficient in inconsistent/debug saves. |
| Champion | Existing `FLAG_POX_LEAGUE_BILL` plus audited Hall of Fame completion semantics | Successful finale only; if a separate completed-Champion flag is needed, allocate it explicitly. Opens Lavender harbor and postgame destinations. |
| Legendary sage defeated | Proposed per-encounter persistent flag | Won sage battle enables that legendary's first-ball guarantee; independent of caught/defeated encounter state and tier eligibility. |

Saffron north truth table: before Space Center → closed for every Bruno/Silph
combination; after Space Center → open for every combination. Test travel,
Clair's guide and her battle with neither objective complete, and verify the
League still requires all eight badges if Clair is defeated before Bruno.

## Beats and acceptance

| Order | Place | Target event and required assertions |
|---|---|---|
| 0 | Pallet/Oldale | Preserve current starter/professor, supplies, TM/Compendium, IV, Mom and mart flows. Minimal convergence explanation; no Bill/system/Rocket reveal. |
| 1 | Cherrygrove/Ilex | Casual geographic changes and exploration; no major mystery reveal. Mandatory Ilex route before Roxanne; existing researcher beat may remain if consistent. |
| 2 | Rustboro | Roxanne LC challenge → badge 1/PU availability. Devon remains ordinary infrastructure. |
| 2a optional | Route24/25 Cottage | First available gift Eevee; Bill absent, harmless note/caretaker. Return to Route25, never Fortree. Skipping branch does not block story or other gifts. |
| 3 | Mt. Moon | Rocket I fossil theft and unexplained receiver; grunts and completion before Goldenrod. |
| 4 | Goldenrod | Whitney PU → badge 2; domestic Bill family dialogue and proposed Eevee gift #2. |
| 5 | National Park | Mandatory geographic passage, catching/trainer respite; no plot escalation. |
| 6 | Ecruteak | Dance Theater lead → Burned Tower brief visible restoration → Morty returns → NU Gym/badge 3. No beast release. Optional troupe reward is proposed Eevee #3. |
| 7 | Weather Institute | Boundaries are still changing; complete investigation on Route119 before forward progression. |
| 8 | Fortree/Route110 | Arrival opens Route36 shortcut permanently; Winona RU → badge 4; then Lavender. |
| 9 | Lavender/Tower | Rocket II, Fuji rescue; research directions explicitly name the Underground bypass and Cinnabar archives. Proposed Fuji Eevee #4. South harbor stays closed. |
| 10 | Underground/Route103 | Traverse around locked Saffron. All city entrances blocked, Underground usable; Oldale/Pallet cannot provide early south access. |
| 11 | Cinnabar/Mansion | Gym open immediately; Blaine UU → badge 5, retryable key; mandatory archives. Entei UUBL encounter after tier unlock and sage victory, optional capture. |
| 12 | Seafoam | Mandatory west-to-east dungeon, rare encounters/items, no major exposition; no Surf bypass. |
| 13 | Mossdeep | Tate & Liza UUBL double battle → badge 6; Space Center finds training-oriented geography and Silph traffic. Completion opens Saffron; proposed Eevee #5. |
| 14a | Fighting Dojo | Bruno OU → badge 7. Can precede or follow Silph. |
| 14b | Silph | Rocket III/Giovanni followed by autonomous system shutdown; Rocket did not create it; creator unnamed. Independent of Bruno and Clair; no northern gate side effect. |
| 15 | Meteor Falls/Blackthorn | Space Center complete → northern OU region → Clair OU/badge 8, even before Bruno/Silph. No renewed villain crisis; dialogue must support Silph still being unresolved. Downhill return available. |
| 16 | Ecruteak west/Victory Road | All eight badges open League road; exploration and trainers, no direct Blackthorn transport. |
| 17 | League | Wallace → Steven → Lance → Blue → Champion Bill. Bill's infrastructure role explained only after winning his battle; defeat/retry and Hall of Fame work. |
| 18 | Lavender harbor | Champion unlock, round-trip ferry/Frontier hub, no pre-Champion entry. Full island content tracked separately in PLAN. |

The four later Eevee sites retain existing alpha placements as a planning
choice; v7 fixes only the Cottage as first available and five gifts total.
Keep gifts optional, once-only, and retryable on full party/storage. Reaching a
later gift without collecting Cottage must remain valid.

## Legendary sage behavior

Implement a reusable sage/legendary interaction, starting with Mansion Entei.
A won sage battle and legal species tier enable guaranteed capture on the
first thrown ball of any usable type. Losing or declining the sage battle
does not unlock it. Specify and test encounter retry after flee/KO, party and
PC full conditions, save/load, and repeat interaction after capture. Scope the
capture override to the authorized static legendary encounter; ordinary wild
battles must retain normal behavior. Future legendary sites must use the same
contract; Uber sites remain Champion-only.

## Trainer and dialogue rules

Author parties in the generator's supported trainer source flow and keep
generated trainer registrations consistent. Gym battle tiers are LC, PU, NU,
RU, UU, UUBL, OU, OU. Encounter pools, caps and evolution eligibility follow
the separate encounter specification; do not invent new tier rules here.

Use grounded Gen I–III dialogue. Bill's family/Cottage are ordinary character
texture. Keep his name away from mystery research until the Champion reveal.
Rocket escalates from theft to investigation to attempted seizure in exactly
three main arcs. Burned Tower needs an actual brief visual anomaly; text alone
is an interim implementation. Mansion and Silph retain the merged world after
the crisis ends. Blackthorn and League return attention to Trainer progression.

Audit native Gym/HM callbacks, facilities, respawns and shared-interior returns
for original-game story leakage. Replace obsolete travel services and their
actors in both generator and checked-in maps. Do not assume a hidden NPC
means its old warp or map callback is gone.

## Pallet opening implementation

The story runs in the primary `pokeemerald.gba`. Build with:

```sh
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
```

`data/scripts/plastic_ox_pallet.inc` contains the authored lab dialogue and
starter flow. `build_story.py` includes it and maintains the lab placements.
Oak introduces the changed geography without revealing the central plot; Elm
and Birch introduce themselves and their research. The entrance scene runs
once, and each professor has dialogue before and after the choice. Elm uses
the existing scientist overworld sprite; Oak and Birch use their own sprites.
The left, middle and right balls contain Treecko, Squirtle and Cyndaquil.
Declining preserves the choice; a full party and PC does not consume it.
Once chosen, the three balls disappear and the northern starter gate opens.
Oak supplies five Poké Balls once, with retry dialogue if the pocket is full.
The Pokédex supports species from all three regions. Mom provides directions
before selection and healing afterward; Daisy provides local travel advice.

All Pokémon IV writes in gameplay are fixed at 31 in `SetBoxMonData`, covering
random generation, individual overrides and packed trainer IVs. This applies
across Plastic Ox builds. Battle-test fixtures retain control over their IVs.
Existing save data is not migrated by this change.

Validation:

```sh
python3 plastic_ox/alpha/build_story.py --check
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py starters
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py gifts
LD_LIBRARY_PATH=/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64 /home/eddie/.venvs/mgba311/bin/python plastic_ox/demo/test_story.py ivs
```

### Pallet and Oldale opening fixes

On the first lab visit, the player walks up the center aisle to Oak at (6, 6) before the professors introduce themselves. Elm gives all 50 reusable TMs and the Move Compendium after starter selection; players who already chose a starter can collect them by speaking to Elm. The reusable Key Item first selects a Pokémon, then teaches any compatible level-up move regardless of its current level, along with Egg and tutor moves. The gift skips items already owned and can be retried if a pocket is full. Oldale’s mart employee explains the shop and gives a Potion in place, without an escort walk.

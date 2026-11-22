# 2026-11-18 — goldenrodcity-hns (pox-2ma.7)

## Decision: no kimono / Steel Tablet gate

- The story bible (`plastic_ox_story_v7.md`) never mentions a Steel Tablet, a Registeel beat or a kimono gate here. Only `STORY_PASS_PRIME_PROMPT.md` run 7 goal 4 asked for it, and it needs a brand-new item plus a pickup, which is outside a conservative flag-cleanup bead. The bible wins, so the gate is dropped.
- Removed `FLAG_POX_KIMONO_GATE_OPEN` (0x911) and `FLAG_POX_HIDDEN_UNDERGROUND_STEEL_TABLET` (0x912) from `plastic_ox_flags.h`; ids left retired.
- The Kimono guard (Tunnel) and the Storage guard now use hide flag `0`, so they are plain permanent NPCs. The stair at Tunnel (12,10) stays open.
- Prompt goal 4 marked DROPPED; note open question marked RESOLVED.
- `plastic_ox/demo/test_goldenrod.py` `reservations()` lost its two stale cases that flipped the removed flag (the Radio Tower cases remain). Legacy `plastic_ox/alpha/goldenrod/*.json` snapshots are untouched.

# 2026-11-18 — goldenrodcity-hns (pox-2ma.5, pox-2ma.6)

## pox-2ma.5 — south passage dead code

- `PoxRegion_route33_goldenrod_b`: removed the no-op `goto_if_unset FLAG_POX_TRIGGERS_ENABLED` and the unreachable `_Open`/`_Closed` labels. The passage always warps to Route 33.
- `GoldenrodCity_hns`: removed the bg_event sign at (32,43); the `OBJ_EVENT_GFX_SIGN` object there already reads `PoxRegion_route33_goldenrod_b_Sign`.
- Kept `VAR_POX_PORTAL_TRIGGER` on the four coord events (32..35,45): `mapjson` requires a `var`/`var_value` on every trigger, the var is the reserved-zero portal convention, so it is harmless and not safe to drop.
- `PoxRegion_goldenrod_route35_b_Sign` is NOT unreferenced: `Route35_hns/map.json` uses it. Left in place (bead premise was wrong).

## pox-2ma.6 — Directory signs

- Department Store 7F (10..12,5): new `PoxGoldenrod_DeptStore7F_Sign` (rooftop floor notice).
- Game Corner (16,6),(16,9): new `PoxGoldenrod_GameCorner_Sign` (coins/prize counter).
- UndergroundTunnel (12,10): removed the bg_event; it sat on the switch-chamber warp tile and could never be read.
- Skipped by instruction: Gym (other workers) and 7FNight (pox-2ma.8).
- Other Directory uses elsewhere in Goldenrod (Radio Tower, other store floors, etc.) remain placeholder.

## Verification

check_story_notes --note goldenrodcity-hns: 0 errors; wiki --check current; ROM builds clean.

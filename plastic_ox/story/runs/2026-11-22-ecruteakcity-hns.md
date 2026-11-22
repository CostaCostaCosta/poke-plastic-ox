# 2026-11-22 ecruteakcity-hns: NPC relevance audit and RELICANTH trade

Note: `plastic_ox/story/locations/ecruteakcity-hns.md` (status stays implemented).

## Changes

- `EcruteakCity_hns` (19,15) old man beside the BURNED TOWER door: League-gate lore replaced by
  tower-step sweeper text, with a before/after `FLAG_POX_STORY_BURNED_TOWER` variant.
- (19,22) `Pox_BurnedGuide` lamp-trimmer: new `FLAG_BADGE03_GET` branch so she stops sending the
  player to MORTY after the badge. Ported into `build_story.py` and `plastic_ox_story.inc`.
- (36,41) bell-founder and (52,49) carpenter's boy: pre-tower variants so neither spoils the
  recovered bell or the momentary restoration before the beat.
- (54,42) east door watch: post-tower, pre-badge text no longer says "door is open" while he
  still blocks it.
- Unchanged after audit: market stall (22,42), washing-line woman (41,41), fire watch (53,32).
- `EcruteakCity_House2_hns` (2,3): river dredger with `INGAME_TRADE_RELICANTH`
  (CLAMPERL -> RELICANTH), completion flag `FLAG_POX_ECRUTEAK_RELICANTH_TRADE`
  (`POX_EVENT_FLAGS_START + 42`, SaveBlock3 event range like the other script-owned POX flags).

## Verification

- `make pox-check-static`, `make pox-build`
- `plastic_ox/demo/test_ecruteak_npcs.py` (new), `test_ecruteak_repairs.py`, `test_ecruteak_gym_gate.py`

## Open

- `pox_progression.SPECIALS` does not list RELICANTH at "ecruteak" yet; `test_nu_encounters_v1` still reports
  Relicanth as an open NU root.
- The full trade animation (PC chooser + DoInGameTradeScene) was not driven in the harness.

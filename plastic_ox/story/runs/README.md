# Story pass run logs

One short markdown file per autonomous story/dialogue pass, named
`YYYY-MM-DD-<slug>.md`. The next pass reads the latest log for a location
before touching its maps, so nobody rediscovers the same dead object or
untested warp.

Keep it to the facts a follow-up needs:

```markdown
# 2026-11-12 — lavender-town

- Note: plastic_ox/story/locations/lavender-town.md (status drafted → implemented)
- Maps: LavenderTown_hns, PlasticOx_PokemonTower
- Changed: three harbour-barrier NPCs now have distinct lines; tower signs rewritten
- Verified: mGBA walk of both tower states; dialogue diff shows no duplicates
- Still open: PlasticOx_PokemonTower has no warp events; entry is scripted transport
- Tests: regression suites green, wiki --check current
```

Do not paste whole scripts or note text. A log that says "changed dialogue" with
no map, no test, and no remaining risk is useless.

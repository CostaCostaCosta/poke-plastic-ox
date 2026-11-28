# Generation 3 ADV Tier Team Pool — 2026-11-23

**Important distinction:** This archive contains **225 CONSTRUCTED (synthetic)
team combinations per tier**, **not 225 independently published Smogon
competitive teams per tier**. I used Smogon's tier-specific resources, modern
sample-team six-Pokemon cores where visible, and standard Gen 3 sets. Up to
three members of each core may have been swapped with role-matched species.
These combinations are designed for team-variety testing and game scripting;
their competitive strength has NOT been experimentally verified.

There is no web network route from the file-generation sandbox, so I was
unable to bulk-download hundreds of Pokepaste raw texts. Rather than
misrepresent generated teams as human-published teams, the files identify
all generated teams with `CONSTRUCTED` in their headers.

## File structure

Each file uses Pokémon Showdown's **multi-team backup format**:

    === [gen3uu] ADV-UU-CONSTRUCTED-0001 ===

    Species @ Item
    Ability: ...
    EVs: ...
    IVs: ...
    Nature
    - Move 1
    - Move 2
    - Move 3
    - Move 4

    [...five more Pokemon...]

Import a full text file through Showdown's team manager backup import, or
copy one six-Pokémon block into the standard single-team Import/Export box.

## Counts

- **LC**: 225 constructed teams, 32 distinct species, file `gen3_lc_constructed_225.txt`.
- **PU**: 225 constructed teams, 29 distinct species, file `gen3_pu_constructed_225.txt`.
- **NU**: 225 constructed teams, 29 distinct species, file `gen3_nu_constructed_225.txt`.
- **RU**: 225 constructed teams, 36 distinct species, file `gen3_ru_constructed_225.txt`.
- **UU**: 225 constructed teams, 31 distinct species, file `gen3_uu_constructed_225.txt`.
- **UUBL**: 225 constructed teams, 23 distinct species, file `gen3_uubl_constructed_225.txt`.
- **UBERS**: 225 constructed teams, 28 distinct species, file `gen3_ubers_constructed_225.txt`.

## Scope and caveats

- `gen3_adv_published_paste_links.csv` lists **actual public Poképaste links**
  found during research, chiefly UU with supplemental LC/RU/UUBL links. These
  were NOT transcribed into the constructed files.
- Source pages for each format are listed in `gen3_adv_team_counts.json`.
- All composed teams have six distinct species and four moves per species.
  EV totals are within 510; explicit 70-BP Hidden Power IVs are calculated.
- A full Pokémon Showdown legality check is **not available** in this offline
  environment. Some sets may need correction to meet learnset, level, or
  current 2026 format banlist restrictions.
- **UUBL** is a special historic/custom competitive metagame; official UUBL is
  normally a UU banlist, not a standard separate ladder. Some 2026 changes
  mean old UUBL sample teams may contain newly OU Pokemon. UUBL constructed
  teams avoid Raikou and Registeel following their 2026 rise to OU.
- **LC** files are Level 5 and avoid current key species bans (Abra, Diglett,
  Porygon, etc.) and excluded moves (Thunder Wave, Baton Pass, sleep).
- Using whole backup files in a standard one-team import box will not work;
  use Showdown's team-manager backup import or extract a single six-mon block.

For a genuine competitive team dataset, run `collect_published_adv_teams.py`
from an Internet-connected machine (requires `requests` and `beautifulsoup4`).
It follows Smogon forum Pokepaste links and downloads each six-set raw team,
preserving source links and publishing actual unique counts without padding.
It cannot guarantee 200 published teams exist for each tier.
Also see the source index and public team links. Do **not** train a behavioral-cloning model as if these
constructed teams were independent expert demonstrations. Their utility is
potentially as team-variety self-play starting states or opponent training pools
subject to legal-set auditing.

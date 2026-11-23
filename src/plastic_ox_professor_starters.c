// Professor starter rewards: Oak (Kanto), Elm (Johto) and Birch (Hoenn) each
// give one of their region's starters for every 25 species of that generation
// registered as owned in the Pokedex, up to three. Shared by every professor;
// see data/scripts/plastic_ox_professor_starters.inc.
#include "global.h"
#include "event_data.h"
#include "pokedex.h"
#include "pokemon.h"
#include "string_util.h"
#include "constants/plastic_ox_flags.h"
#include "constants/species.h"

#define POX_PROF_MILESTONE 25
#define POX_PROF_REWARDS   3

enum { POX_PROF_STATE_PROGRESS, POX_PROF_STATE_REWARD, POX_PROF_STATE_COMPLETE };

struct PoxProfessor
{
    u16 firstDex;
    u16 lastDex;
    const u8 *region;
    u16 species[POX_PROF_REWARDS];
    u16 flags[POX_PROF_REWARDS];
};

static const u8 sText_Kanto[] = _("KANTO");
static const u8 sText_Johto[] = _("JOHTO");
static const u8 sText_Hoenn[] = _("HOENN");

static const struct PoxProfessor sProfessors[] =
{
    { NATIONAL_DEX_BULBASAUR, NATIONAL_DEX_MEW, sText_Kanto,
      { SPECIES_BULBASAUR, SPECIES_CHARMANDER, SPECIES_SQUIRTLE },
      { FLAG_POX_PROF_OAK_BULBASAUR, FLAG_POX_PROF_OAK_CHARMANDER, FLAG_POX_PROF_OAK_SQUIRTLE } },
    { NATIONAL_DEX_CHIKORITA, NATIONAL_DEX_CELEBI, sText_Johto,
      { SPECIES_CHIKORITA, SPECIES_CYNDAQUIL, SPECIES_TOTODILE },
      { FLAG_POX_PROF_ELM_CHIKORITA, FLAG_POX_PROF_ELM_CYNDAQUIL, FLAG_POX_PROF_ELM_TOTODILE } },
    { NATIONAL_DEX_TREECKO, NATIONAL_DEX_DEOXYS, sText_Hoenn,
      { SPECIES_TREECKO, SPECIES_TORCHIC, SPECIES_MUDKIP },
      { FLAG_POX_PROF_BIRCH_TREECKO, FLAG_POX_PROF_BIRCH_TORCHIC, FLAG_POX_PROF_BIRCH_MUDKIP } },
};

// National Dex numbers are per species, so alternate forms never count twice.
u32 PoxCountOwnedNationalDexRange(u32 firstDex, u32 lastDex)
{
    u32 dex, count = 0;
    for (dex = firstDex; dex <= lastDex; dex++)
    {
        if (GetSetPokedexFlag(dex, FLAG_GET_CAUGHT))
            count++;
    }
    return count;
}

static const struct PoxProfessor *GetProfessor(void)
{
    u32 id = gSpecialVar_0x8004;
    if (id >= ARRAY_COUNT(sProfessors))
        id = 0;
    return &sProfessors[id];
}

static u32 CountClaimed(const struct PoxProfessor *prof)
{
    u32 i, claimed = 0;
    for (i = 0; i < POX_PROF_REWARDS; i++)
    {
        if (FlagGet(prof->flags[i]))
            claimed++;
    }
    return claimed;
}

// In: VAR_0x8004 professor. Out: VAR_RESULT state, VAR_0x8005 rewards claimed,
// STR_VAR_1 owned count, STR_VAR_2 region name, STR_VAR_3 next milestone.
void PoxProfStarters_Status(void)
{
    const struct PoxProfessor *prof = GetProfessor();
    u32 owned = PoxCountOwnedNationalDexRange(prof->firstDex, prof->lastDex);
    u32 earned = min(POX_PROF_REWARDS, owned / POX_PROF_MILESTONE);
    u32 claimed = CountClaimed(prof);
    u32 target = POX_PROF_MILESTONE * (claimed + 1);

    ConvertIntToDecimalStringN(gStringVar1, owned, STR_CONV_MODE_LEFT_ALIGN, 3);
    StringCopy(gStringVar2, prof->region);
    ConvertIntToDecimalStringN(gStringVar3, target, STR_CONV_MODE_LEFT_ALIGN, 3);
    gSpecialVar_0x8005 = claimed;
    if (claimed >= POX_PROF_REWARDS)
        gSpecialVar_Result = POX_PROF_STATE_COMPLETE;
    else if (earned > claimed)
        gSpecialVar_Result = POX_PROF_STATE_REWARD;
    else
        gSpecialVar_Result = POX_PROF_STATE_PROGRESS;
}

// In: VAR_0x8004. Out: STR_VAR_1..3 starter names, VAR_0x8005..7 TRUE when
// that starter is still unclaimed.
void PoxProfStarters_BufferChoices(void)
{
    const struct PoxProfessor *prof = GetProfessor();
    u8 *const names[POX_PROF_REWARDS] = { gStringVar1, gStringVar2, gStringVar3 };
    u16 *const avail[POX_PROF_REWARDS] = { &gSpecialVar_0x8005, &gSpecialVar_0x8006, &gSpecialVar_0x8007 };
    u32 i;
    for (i = 0; i < POX_PROF_REWARDS; i++)
    {
        StringCopy(names[i], GetSpeciesName(prof->species[i]));
        *avail[i] = !FlagGet(prof->flags[i]);
    }
}

// In: VAR_0x8004, VAR_0x8005 slot. Out: VAR_0x8006 species (SPECIES_NONE when
// the slot is invalid or already claimed), STR_VAR_1 its name.
void PoxProfStarters_GetChoice(void)
{
    const struct PoxProfessor *prof = GetProfessor();
    u32 slot = gSpecialVar_0x8005;
    if (slot >= POX_PROF_REWARDS || FlagGet(prof->flags[slot]))
    {
        gSpecialVar_0x8006 = SPECIES_NONE;
        return;
    }
    gSpecialVar_0x8006 = prof->species[slot];
    StringCopy(gStringVar1, GetSpeciesName(prof->species[slot]));
}

// Called only after the starter was delivered to the party or PC.
void PoxProfStarters_Claim(void)
{
    const struct PoxProfessor *prof = GetProfessor();
    if (gSpecialVar_0x8005 < POX_PROF_REWARDS)
        FlagSet(prof->flags[gSpecialVar_0x8005]);
}

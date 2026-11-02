#include "global.h"
#include "plastic_ox_pu_acquisitions.h"
#include "coins.h"
#include "event_data.h"
#include "item.h"
#include "mail.h"
#include "pokemon.h"
#include "random.h"
#include "script_pokemon_util.h"
#include "string_util.h"
#include "constants/easy_chat.h"
#include "constants/items.h"
#include "constants/plastic_ox_flags.h"
#include "constants/vars.h"

// Successful gifts use MON_GIVEN_TO_PARTY / MON_GIVEN_TO_PC. Other results:
#define ACQUISITION_UNAVAILABLE 3
#define ACQUISITION_ALREADY_DONE 4
#define ACQUISITION_MAIL_MISSING 5
#define DELIBIRD_OT_ID 0x00350016
#define DELIBIRD_PERSONALITY_BASE 0x50350000

static const u8 sGuardName[] = _("WEBSTER");
static const u16 sLetterWords[MAIL_WORDS_COUNT] = {
    EC_WORD_I, EC_WORD_AM, EC_WORD_HEALTHY,
    EC_WORD_THANKS, EC_WORD_FOR, EC_WORD_LETTER,
    EC_WORD_YOU, EC_WORD_FRIEND, EC_WORD_FOREVER,
};

static void MakeDeliveryMail(struct Mail *mail, u16 identity)
{
    u32 i;
    ClearMail(mail);
    for (i = 0; i < MAIL_WORDS_COUNT; i++)
        mail->words[i] = sLetterWords[i];
    StringCopy(mail->playerName, sGuardName);
    mail->trainerId[0] = identity;
    mail->trainerId[1] = identity >> 8;
    mail->trainerId[2] = 0x35;
    mail->trainerId[3] = 0x50;
    mail->species = SPECIES_DELIBIRD;
    mail->itemId = ITEM_ORANGE_MAIL;
}

static bool32 IsDeliveryBird(struct Pokemon *mon, u16 identity)
{
    return identity != 0
        && GetMonData(mon, MON_DATA_SPECIES) == SPECIES_DELIBIRD
        && !GetMonData(mon, MON_DATA_IS_EGG)
        && GetMonData(mon, MON_DATA_OT_ID) == DELIBIRD_OT_ID
        && GetMonData(mon, MON_DATA_PERSONALITY) == (DELIBIRD_PERSONALITY_BASE | identity);
}

static bool32 IsDeliveryMail(struct Mail *mail, u16 identity)
{
    struct Mail expected;
    u32 i;
    MakeDeliveryMail(&expected, identity);
    if (mail->itemId != expected.itemId || mail->species != expected.species
        || StringCompare(mail->playerName, expected.playerName) != 0)
        return FALSE;
    for (i = 0; i < TRAINER_ID_LENGTH; i++)
        if (mail->trainerId[i] != expected.trainerId[i])
            return FALSE;
    for (i = 0; i < MAIL_WORDS_COUNT; i++)
        if (mail->words[i] != expected.words[i])
            return FALSE;
    return TRUE;
}

void PlasticOxBuyCoinPrize(void)
{
    static const struct {
        u16 species;
        u16 coins;
    } prizes[] = {
        {SPECIES_ABRA, 200},
        {SPECIES_LUVDISC, 500},
        {SPECIES_CASTFORM, 1500},
        {SPECIES_PORYGON, 4000},
    };
    u32 choice = gSpecialVar_0x8004;
    u32 result;

    gSpecialVar_Result = ACQUISITION_UNAVAILABLE;
    if (choice >= ARRAY_COUNT(prizes) || !CheckBagHasItem(ITEM_COIN_CASE, 1)
        || GetCoins() < prizes[choice].coins)
        return;
    result = ScriptGiveMon(prizes[choice].species, 15, ITEM_NONE);
    if (result != MON_CANT_GIVE)
        RemoveCoins(prizes[choice].coins);
    gSpecialVar_Result = result;
}

void PlasticOxReviveHelix(void)
{
    u32 result;
    gSpecialVar_Result = ACQUISITION_UNAVAILABLE;
    if (!CheckBagHasItem(ITEM_HELIX_FOSSIL, 1))
        return;
    result = ScriptGiveMon(SPECIES_OMANYTE, 10, ITEM_NONE);
    if (result != MON_CANT_GIVE)
        RemoveBagItem(ITEM_HELIX_FOSSIL, 1);
    gSpecialVar_Result = result;
}

void PlasticOxGiveMailDelibird(void)
{
    struct Pokemon mon;
    struct Mail mail;
    u32 i;
    u32 personality;
    u32 gender = MALE;
    u16 identity = VarGet(VAR_POX_DELIBIRD_IDENTITY);
    u8 mailId;

    gSpecialVar_Result = ACQUISITION_ALREADY_DONE;
    if (FlagGet(FLAG_POX_DELIBIRD_DELIVERED))
        return;
    if (FlagGet(FLAG_POX_DELIBIRD_RECEIVED))
    {
        // Reissue a discarded letter only to the original bird. A letter saved
        // in the PC or attached to another Pokemon must instead be retrieved.
        gSpecialVar_Result = ACQUISITION_MAIL_MISSING;
        for (i = 0; i < MAIL_COUNT; i++)
            if (IsDeliveryMail(&gSaveBlock1Ptr->mail[i], identity))
                return;
        for (i = 0; i < PARTY_SIZE; i++)
        {
            struct Pokemon *bird = &gParties[B_TRAINER_PLAYER][i];
            if (!IsDeliveryBird(bird, identity))
                continue;
            if (GetMonData(bird, MON_DATA_HELD_ITEM) != ITEM_NONE)
                return;
            MakeDeliveryMail(&mail, identity);
            gSpecialVar_Result = GiveMailToMon(bird, &mail) == MAIL_NONE ? MON_CANT_GIVE : MON_GIVEN_TO_PARTY;
            return;
        }
        return;
    }

    // Mail-bearing gifts must enter the party: boxed Pokemon cannot hold mail.
    gSpecialVar_Result = MON_CANT_GIVE;
    if (CalculatePlayerPartyCount() >= PARTY_SIZE)
        return;
    do {
        identity = Random();
    } while (identity == 0);
    personality = DELIBIRD_PERSONALITY_BASE | identity;
    CreateMonWithIVs(&mon, SPECIES_DELIBIRD, 16, personality,
        OTID_STRUCT_PRESET(DELIBIRD_OT_ID), USE_RANDOM_IVS);
    GiveMonInitialMoveset(&mon);
    SetMonData(&mon, MON_DATA_OT_NAME, sGuardName);
    SetMonData(&mon, MON_DATA_OT_GENDER, &gender);
    CalculateMonStats(&mon);
    MakeDeliveryMail(&mail, identity);
    mailId = GiveMailToMon(&mon, &mail);
    if (mailId == MAIL_NONE)
        return;
    gSpecialVar_Result = GiveScriptedMonToPlayer(&mon, PARTY_SIZE);
    if (gSpecialVar_Result != MON_GIVEN_TO_PARTY)
    {
        ClearMailItemId(mailId);
        return;
    }
    VarSet(VAR_POX_DELIBIRD_IDENTITY, identity);
    FlagSet(FLAG_POX_DELIBIRD_RECEIVED);
}

void PlasticOxDeliverMail(void)
{
    u32 i;
    u16 identity = VarGet(VAR_POX_DELIBIRD_IDENTITY);
    gSpecialVar_Result = ACQUISITION_ALREADY_DONE;
    if (FlagGet(FLAG_POX_DELIBIRD_DELIVERED))
        return;
    gSpecialVar_Result = ACQUISITION_MAIL_MISSING;
    if (!FlagGet(FLAG_POX_DELIBIRD_RECEIVED))
        return;
    for (i = 0; i < PARTY_SIZE; i++)
    {
        struct Pokemon *bird = &gParties[B_TRAINER_PLAYER][i];
        u32 mailId = GetMonData(bird, MON_DATA_MAIL);
        if (!IsDeliveryBird(bird, identity) || mailId >= PARTY_SIZE
            || GetMonData(bird, MON_DATA_HELD_ITEM) != ITEM_ORANGE_MAIL
            || !IsDeliveryMail(&gSaveBlock1Ptr->mail[mailId], identity))
            continue;
        TakeMailFromMon(bird);
        FlagSet(FLAG_POX_DELIBIRD_DELIVERED);
        gSpecialVar_Result = MON_GIVEN_TO_PARTY;
        return;
    }
}

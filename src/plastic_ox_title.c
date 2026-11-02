#include "global.h"
#include "bg.h"
#include "gpu_regs.h"
#include "main.h"
#include "gba/m4a_internal.h"
#include "m4a.h"
#include "main_menu.h"
#include "menu.h"
#include "palette.h"
#include "scanline_effect.h"
#include "sound.h"
#include "sprite.h"
#include "task.h"
#include "text.h"
#include "title_screen.h"
#include "window.h"
#include "clear_save_data_menu.h"
#include "reset_rtc_screen.h"
#include "event_data.h"
#include "constants/rgb.h"
#include "constants/songs.h"
#include "data/plastic_ox_title_art.h"

// Four hardware backgrounds: transparent lettering and three sliding regions.
static const struct BgTemplate sBgs[] = {
    {.bg=0, .charBaseIndex=0, .mapBaseIndex=31, .priority=0},
    {.bg=1, .charBaseIndex=2, .mapBaseIndex=28, .priority=1},
    {.bg=2, .charBaseIndex=2, .mapBaseIndex=29, .priority=2},
    {.bg=3, .charBaseIndex=2, .mapBaseIndex=30, .priority=3},
};
static const struct WindowTemplate sWindows[] = {
    {.bg=0, .width=30, .height=20, .paletteNum=0, .baseBlock=1},
    DUMMY_WIN_TEMPLATE
};
static const u16 sPalette[] = {
    RGB(2,3,7), RGB(3,5,9), RGB(3,10,15), RGB(4,13,16),
    RGB(7,19,17), RGB(13,25,19), RGB(16,7,12), RGB(29,13,12),
    RGB(16,13,17), RGB(27,24,20), RGB(18,22,23), RGB(31,26,14),
    RGB(11,26,29), RGB(31,30,25), RGB(8,12,17), RGB(20,24,26)
};
static const u8 sPokemon[] = _("POKéMON");
static const u8 sTagline[] = _("THREE REGIONS. ONE NEW WORLD.");
static const u8 sPrologue[] = _("Once, three worlds stood apart.");
static const u8 sCollision[] = _("Then the earth began to move.");
static const u8 sStart[] = _("PRESS START");
static const u8 sSkip[] = _("A / START: SKIP");
static const u8 sKanto[] = _("KANTO");
static const u8 sJohto[] = _("JOHTO");
static const u8 sHoenn[] = _("HOENN");
static EWRAM_DATA u16 sPoxTitleFrame = 0;
static EWRAM_DATA bool8 sPoxTitleOpening = FALSE;
static EWRAM_DATA bool8 sPoxTitleLeaving = FALSE;
static EWRAM_DATA MainCallback sPoxTitleDestination = NULL;

static void MainCB2_PlasticOxTitle(void);
static void InitScene(bool8 opening);

static void VBlankCB_PlasticOxTitle(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

static void Center(const u8 *text, u8 y, u8 color)
{
    u8 colors[] = {0, color, 1};
    AddTextPrinterParameterized3(0, FONT_SMALL, (240 - GetStringWidth(FONT_SMALL, text, 0)) / 2, y, colors, TEXT_SKIP_DRAW, text);
}

static void DrawLogo(void)
{
    // Custom 5x7 block lettering, scaled to fit the native GBA screen.
    static const u8 letters[][7] = {
        {30,17,17,30,16,16,16}, {16,16,16,16,16,16,31},
        {14,17,17,31,17,17,17}, {15,16,16,14,1,1,30},
        {31,4,4,4,4,4,4}, {31,4,4,4,4,4,31},
        {15,16,16,16,16,16,15}, {0,0,0,0,0,0,0},
        {14,17,17,17,17,17,14}, {17,17,10,4,10,17,17}
    };
    u32 i, x, y;
    for (i=0; i<10; i++)
        for (y=0; y<7; y++)
            for (x=0; x<5; x++)
                if (letters[i][y] & (16 >> x))
                    FillWindowPixelRect(0, PIXEL_FILL(3), 33+i*18+x*3, 27+y*3, 3, 4);
    for (i=0; i<10; i++)
        for (y=0; y<7; y++)
            for (x=0; x<5; x++)
                if (letters[i][y] & (16 >> x))
                    FillWindowPixelRect(0, PIXEL_FILL(y<3 ? 13 : 11), 31+i*18+x*3, 24+y*3, 3, 3);
}

static void DrawText(void)
{
    u8 colors[] = {0, 15, 1};
    FillWindowPixelBuffer(0, PIXEL_FILL(0));
    if (sPoxTitleOpening)
    {
        Center(sPoxTitleFrame < 140 ? sPrologue : sCollision, 22, 13);
        Center(sSkip, 44, 15);
        AddTextPrinterParameterized3(0, FONT_SMALL, 23, 146, colors, TEXT_SKIP_DRAW, sKanto);
        AddTextPrinterParameterized3(0, FONT_SMALL, 101, 146, colors, TEXT_SKIP_DRAW, sJohto);
        AddTextPrinterParameterized3(0, FONT_SMALL, 180, 146, colors, TEXT_SKIP_DRAW, sHoenn);
    }
    else
    {
        Center(sPokemon, 7, 11);
        DrawLogo();
        Center(sTagline, 51, 15);
        if ((sPoxTitleFrame / 40) % 2 == 0)
            Center(sStart, 145, 13);
    }
    PutWindowTilemap(0);
    CopyWindowToVram(0, COPYWIN_FULL);
}

static void PositionRegions(s16 distance, s16 shake)
{
    ChangeBgX(1, (distance + shake) * 256, BG_COORD_SET);
    ChangeBgX(2, shake * 256, BG_COORD_SET);
    ChangeBgY(2, -distance * 128, BG_COORD_SET);
    ChangeBgX(3, (-distance + shake) * 256, BG_COORD_SET);
}

static void RevealTitle(void)
{
    m4aSongNumStop(SE_TRUCK_MOVE);
    sPoxTitleOpening = FALSE;
    sPoxTitleFrame = 0;
    PositionRegions(0, 0);
    BeginNormalPaletteFade(PALETTES_ALL, 0, 12, 0, RGB_WHITE);
    PlayBGM(MUS_TITLE);
    DrawText();
}

static void LeaveTitle(MainCallback destination)
{
    sPoxTitleLeaving = TRUE;
    sPoxTitleDestination = destination;
    FadeOutBGM(4);
    BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
}

static void MainCB2_PlasticOxTitle(void)
{
    UpdatePaletteFade();
    if (sPoxTitleLeaving)
    {
        if (!gPaletteFade.active)
        {
            SetVBlankCallback(NULL);
            FreeAllWindowBuffers();
            SetMainCallback2(sPoxTitleDestination);
        }
        return;
    }
    sPoxTitleFrame++;
    if (sPoxTitleOpening)
    {
        s16 distance = sPoxTitleFrame < 100 ? 52 : sPoxTitleFrame < 260 ? (260-sPoxTitleFrame)*52/160 : 0;
        s16 shake = sPoxTitleFrame >= 230 && sPoxTitleFrame < 290 ? ((sPoxTitleFrame / 3) % 2 ? 2 : -2) : 0;
        PositionRegions(distance, shake);
        if (sPoxTitleFrame == 140)
        {
            PlaySE(SE_TRUCK_MOVE);
            DrawText();
        }
        if (sPoxTitleFrame == 260)
            PlaySE(SE_M_STRENGTH);
        if (JOY_NEW(A_BUTTON | B_BUTTON | START_BUTTON) || sPoxTitleFrame >= 310)
            RevealTitle();
    }
    else if (!gPaletteFade.active)
    {
        if (JOY_HELD(B_BUTTON | SELECT_BUTTON | DPAD_UP) == (B_BUTTON | SELECT_BUTTON | DPAD_UP))
            LeaveTitle(CB2_InitClearSaveDataScreen);
        else if (JOY_HELD(B_BUTTON | SELECT_BUTTON | DPAD_LEFT) == (B_BUTTON | SELECT_BUTTON | DPAD_LEFT) && CanResetRTC())
            LeaveTitle(CB2_InitResetRtcScreen);
        else if (JOY_NEW(A_BUTTON | START_BUTTON))
            LeaveTitle(CB2_InitMainMenu);
        else if (sPoxTitleFrame >= 1800)
        {
            sPoxTitleOpening = TRUE;
            sPoxTitleFrame = 0;
            FadeOutBGM(4);
            DrawText();
        }
        else
        {
            // Gentle coastal shimmer while the title waits for input.
            u16 water = (sPoxTitleFrame / 32) % 2 ? RGB(11,26,29) : RGB(8,22,27);
            LoadPalette(&water, 12, sizeof(water));
            if (sPoxTitleFrame % 40 == 0)
                DrawText();
        }
    }
}

static void InitScene(bool8 opening)
{
    SetVBlankCallback(NULL);
    SetGpuReg(REG_OFFSET_DISPCNT, 0);
    ScanlineEffect_Stop();
    ResetTasks();
    ResetSpriteData();
    FreeAllSpritePalettes();
    FreeAllWindowBuffers();
    ResetPaletteFade();
    DmaFill16(3, 0, (void *)VRAM, VRAM_SIZE);
    ResetBgsAndClearDma3BusyFlags(0);
    InitBgsFromTemplates(0, sBgs, ARRAY_COUNT(sBgs));
    SetGpuReg(REG_OFFSET_BLDCNT, 0);
    SetGpuReg(REG_OFFSET_BLDALPHA, 0);
    SetGpuReg(REG_OFFSET_BLDY, 0);
    SetGpuReg(REG_OFFSET_WININ, 0);
    SetGpuReg(REG_OFFSET_WINOUT, 0);
    CpuCopy32(sLandscapeTiles, (void *)BG_CHAR_ADDR(2), sizeof(sLandscapeTiles));
    CpuCopy16(sLandscapeMap0, (void *)BG_SCREEN_ADDR(28), sizeof(sLandscapeMap0));
    CpuCopy16(sLandscapeMap1, (void *)BG_SCREEN_ADDR(29), sizeof(sLandscapeMap1));
    CpuCopy16(sLandscapeMap2, (void *)BG_SCREEN_ADDR(30), sizeof(sLandscapeMap2));
    LoadPalette(sPalette, 0, sizeof(sPalette));
    InitWindows(sWindows);
    DeactivateAllTextPrinters();
    sPoxTitleOpening = opening;
    sPoxTitleFrame = 0;
    sPoxTitleLeaving = FALSE;
    ChangeBgX(0, 0, BG_COORD_SET);
    ChangeBgY(0, 0, BG_COORD_SET);
    ChangeBgY(1, 0, BG_COORD_SET);
    ChangeBgY(3, 0, BG_COORD_SET);
    PositionRegions(opening ? 52 : 0, 0);
    DrawText();
    BuildOamBuffer();
    ShowBg(0); ShowBg(1); ShowBg(2); ShowBg(3);
    BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
    if (!opening)
        PlayBGM(MUS_TITLE);
    SetVBlankCallback(VBlankCB_PlasticOxTitle);
    SetMainCallback2(MainCB2_PlasticOxTitle);
}

void CB2_PlasticOxOpening(void)
{
    InitScene(TRUE);
}

void CB2_PlasticOxTitle(void)
{
    InitScene(FALSE);
}

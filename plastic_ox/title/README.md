# Plastic Ox opening and title

The boot callback loads the save as before, then starts a skippable collision
scene. Kanto's houses, Johto's tower, and Hoenn's volcano/coast slide together,
rumble, shake, and reveal the Plastic Ox title. A, B, or Start skips the opening;
a separate A/Start press enters the existing menu. Menu cancellation returns
directly to the title. After roughly 30 seconds, the custom opening replays.
The existing clear-save and permitted RTC-reset shortcuts remain available.

This version uses original native 4bpp tile artwork and custom block lettering,
with the existing Emerald title music and truck/impact sound effects. No
external image library is needed to regenerate the landscape source:

```
python3 plastic_ox/title/generate_art.py
make -j8 TOOLCHAIN=/home/eddie/devkitpro/opt/devkitpro/devkitARM modern
```

Implementation: `src/plastic_ox_title.c`; generated art:
`src/data/plastic_ox_title_art.h`. The title uses four hardware backgrounds and
163 shared landscape tiles. No save structure changes are introduced.

With the local mGBA Python environment and its library path configured, run:

```
python plastic_ox/demo/test_title_screen.py
python plastic_ox/demo/test_intro_registration.py
python plastic_ox/demo/quick_check.py
python plastic_ox/title/render_preview.py
```

The title test covers natural playback, each skip button, menu cancellation,
idle replay, and saving to emulator flash followed by reset and Continue.
Registration separately checks both character choices and custom-name retention.
`previews/opening.gif` and `previews/title.png` are captures of the built ROM.

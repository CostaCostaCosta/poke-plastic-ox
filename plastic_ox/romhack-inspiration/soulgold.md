From SoulGold: Speedup - Yes. Pokémon SoulGold is not merely “similar” to pokeemerald-expansion; it is built on that ecosystem. Its repository describes itself as an expanded Johto hack based on Heart & Soul, and credits an H&S port onto pokeemerald-expansion as its foundation. The README currently references the pokeemerald-expansion 1.15.x era.

The rough lineage is:

pret/pokeemerald
    ↓
rh-hideout/pokeemerald-expansion
    ↓
Heart & Soul → unofficial H&S expansion port
    ↓
Eemeliri/SoulGold

So for Plastic Ox, its speed changes are unusually relevant because they're implemented in essentially the same engine we're using.

Overworld speed

This one is particularly clever. SoulGold credits HashtagMarky's Overworld Speedup, whose implementation is documented publicly. Rather than speeding up the entire GBA emulator, it selectively advances the sprite and camera portions of the overworld multiple times during each normal game frame.

Conceptually, the normal loop does something like:

OverworldBasic();

AnimateSprites();
CameraUpdate();
UpdateCameraPanning();

The speedup adds extra iterations:

1× → 0 extra updates
2× → 1 extra update
4× → 3 extra updates
8× → 7 extra updates

Each additional iteration runs essentially:

AnimateSprites();
CameraUpdate();
UpdateCameraPanning();

inside CB2_Overworld.

The important part is what isn't multiplied: the whole game loop isn't run repeatedly. Input handling, scripts, collision logic, audio, etc. aren't simply globally fast-forwarded. That gives you much faster walking/surfing/NPC movement without making the music play at 2× speed or pitch-shifting the audio. HashtagMarky's tutorial explicitly says it is suitable for pokeemerald-expansion.

This is substantially better than just increasing emulator speed.

Battle speed

SoulGold separately credits Pokabbie for its battle speed-up—the system originally associated with Emerald Rogue. SoulGold also makes its own battle-tempo changes such as combining stat-change messages and playing text concurrently with stat animations.

Pokabbie's native approach has the same general philosophy as the overworld system: speed the battle engine internally rather than speeding the GBA itself. Emerald Rogue exposed native battle speeds such as 1×/2×/3×/4× while keeping audio running normally; earlier versions also removed artificial pauses and allowed effectively instantaneous text.

So you get:

Emulator fast-forward:
battle ×2
music  ×2
audio  ×2
everything ×2

Native SoulGold-style speedup:
battle updates/animations ×2+
music  ×1
audio  ×1

There are actually two complementary optimizations in SoulGold:

Mechanical speedup — battle-local animation/update processing is accelerated.
Dead-time removal — unnecessary pauses, sequential text boxes, stat messages, etc. are reduced or combined.

The second one matters more than it sounds. Pokémon battles have a surprising amount of time where you're waiting on text → animation → text → pause → next animation.

For Plastic Ox

I think we should directly adopt these systems rather than inventing our own speed controls.

The overworld implementation is particularly attractive because it's small and already designed to port into pokeemerald-expansion. We could expose something like:

Overworld Speed
1×
2×
4×

Battle Speed
1×
2×
3×
4×

while leaving music at its intended tempo.

One caution: I'd probably cap Plastic Ox's overworld at 4× by default. HashtagMarky supports up to 8×, but at very high multipliers you're increasingly likely to expose graphical/timing assumptions.

Also, this strengthens the case for using SoulGold and Heart & Soul as upstream reference implementations for Plastic Ox. SoulGold isn't just useful for Johto assets—it contains pokeemerald-expansion-native QoL work that we can port almost directly.

If you want, I can next trace SoulGold's actual source tree and identify the exact files/commits responsible for battle speed and overworld speed, so we can give a coding agent a concrete porting specification rather than reimplementing either feature.
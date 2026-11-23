# 2026-11-23 — Cerulean Cave (post-game)

- Request: block the Route 24 cave until the Elite Four is beaten; inside, the standard HNS Mt. Silver interior; RED and MEWTWO on the summit as the final boss with a fixed ADV Ubers team; wild tables unchanged apart from UNOWN and WOBBUFFET; a win shows the victory screens with the team and the player card.
- Notes: new `mtsilver-1f-waterfallroom-hns.md` (Cerulean Cave); `route24-hns.md` gains the knoll, door and guard.
- Map: Route 24 blockdata gets a 3x3 rock knoll with a cave mouth in the grass nook (`(7,8)`–`(9,10)`).
- Dialogue: one officer line, RED ellipses, one MEWTWO description. No new meta-commentary.
- Deviation: Super Rod slots in the imported cave tables use the region's approved LC-RU roster (Magikarp/Poliwag are banned on every Plastic Ox Super Rod).
- Verification: `plastic_ox/demo/test_cerulean_cave.py` (static + mGBA).

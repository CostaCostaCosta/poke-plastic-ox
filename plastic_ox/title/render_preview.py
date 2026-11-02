"""Capture the built ROM's opening and title using the local mGBA environment."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plastic_ox/demo'))
from walklib import GBA

out = Path(__file__).resolve().parent / 'previews'
out.mkdir(exist_ok=True)
g = GBA()
frames = []
for i in range(480):
    g.frame(1)
    if i % 4 == 0:
        frames.append(g.fb.to_pil().convert('RGB').resize((480, 320)))
frames[0].save(out / 'opening.gif', save_all=True, append_images=frames[1:], duration=67, loop=0)
g.frame(40)  # Capture the visible half of the Press Start blink.
g.fb.to_pil().convert('RGB').save(out / 'title.png')
print(out)

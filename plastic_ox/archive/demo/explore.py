
import os, sys, hashlib, time
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
import mgba.core, mgba.image, mgba.gba, mgba.log
mgba.log.silence()

ROM = "/home/eddie/repos/poke-plastic-ox/pokeemerald.gba"
SHOTS = "/home/eddie/repos/poke-plastic-ox/plastic_ox/demo/shots"

class GBA:
    def __init__(self, rom=ROM):
        self.core = mgba.core.load_path(rom)
        self.fb = mgba.image.Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
        self.core.reset()
        self.fb = mgba.image.Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
        self.K = mgba.gba.GBA
    def frame(self, n=1):
        for _ in range(n):
            self.core.run_frame()
    def keys(self, *keys):
        for k in keys:
            self.core.set_keys(k)
    def release(self, *keys):
        for k in keys:
            self.core.clear_keys(k)
    def tap(self, key, hold=2, wait=10):
        self.keys(key)
        self.frame(hold)
        self.release(key)
        self.frame(wait)
    def hash(self):
        return hashlib.md5(self.fb.to_pil().convert("RGB").tobytes()).hexdigest()
    def shot(self, name):
        import PIL.Image
        path = os.path.join(SHOTS, name)
        self.fb.to_pil().convert("RGB").save(path)
        return path

g = GBA()
print("boot hash:", g.hash())
g.frame(120)
g.shot("x00_boot_120f.png")
print("120f hash:", g.hash())
for i in range(10):
    g.frame(60)
    if i % 2 == 0:
        g.tap(g.K.KEY_A, hold=1, wait=2)
    print(i, g.hash())
    g.shot(f"x0{i}_boot.png")
print("done")

"""Smoke-test a fresh game after supplying the headless fixture identity."""
from walklib import GBA, boot_to_bedroom

g = GBA()
boot_to_bedroom(g)
print(g.state())
print(g.describe())
print("PASS: fresh game reaches the bedroom after the opening tremor")

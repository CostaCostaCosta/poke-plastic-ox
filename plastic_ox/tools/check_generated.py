#!/usr/bin/env python3
"""Fail when a generator-owned file drifts from its generator in a NEW way.

`plastic_ox/alpha/build_story.py --check` lists every file whose checked-in text
differs from what the story generator would write. Many files already drift
(hand edits made after the generator was last updated), and regenerating would
silently revert those edits. This check records that known drift in
`plastic_ox/generated_drift_baseline.txt` and fails only when a file joins the
list, so agents learn immediately that they hand-edited a generated file.

  python3 plastic_ox/tools/check_generated.py              # gate (used by make pox-check-static)
  python3 plastic_ox/tools/check_generated.py --verbose    # also list known drift
  python3 plastic_ox/tools/check_generated.py --update     # accept current drift as the baseline

When a new file drifts, either port your edit into the generator (preferred;
see plastic_ox/generated_manifest.json) or, if the hand edit is intentional,
run --update and say so in the PR. Shrinking the baseline is always welcome.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "plastic_ox/generated_drift_baseline.txt"
PREFIX = "Story sources need regeneration: "


def current_drift() -> set[str]:
    proc = subprocess.run([sys.executable, "plastic_ox/alpha/build_story.py", "--check"],
                          cwd=ROOT, capture_output=True, text=True)
    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode == 0 and PREFIX not in out:
        return set()
    for line in out.splitlines():
        if line.startswith(PREFIX):
            return {p.strip() for p in line[len(PREFIX):].split(",") if p.strip()}
    sys.exit(f"build_story.py --check failed unexpectedly:\n{out}")


def load_baseline() -> set[str]:
    if not BASELINE.exists():
        return set()
    return {l.strip() for l in BASELINE.read_text().splitlines() if l.strip() and not l.startswith("#")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update", action="store_true", help="write the current drift as the baseline")
    ap.add_argument("--verbose", action="store_true", help="list known (baselined) drift too")
    args = ap.parse_args()

    drift = current_drift()
    if args.update:
        BASELINE.write_text("# Files where checked-in text differs from plastic_ox/alpha/build_story.py output.\n"
                            "# Known drift: do NOT regenerate these blindly. Maintained by plastic_ox/tools/check_generated.py --update.\n"
                            + "".join(f"{p}\n" for p in sorted(drift)))
        print(f"baseline updated: {len(drift)} drifted file(s)")
        return 0

    known = load_baseline()
    new, fixed = sorted(drift - known), sorted(known - drift)
    if args.verbose:
        for p in sorted(drift & known):
            print(f"  known drift: {p}")
    for p in fixed:
        print(f"  no longer drifts (run --update to shrink the baseline): {p}")
    if new:
        print("NEW generator drift: these generator-owned files no longer match build_story.py output.")
        print("Port the edit into the generator (see plastic_ox/generated_manifest.json) or run --update if intentional:")
        for p in new:
            print(f"  {p}")
        return 1
    print(f"generated files: no new drift ({len(drift)} known, baseline {len(known)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

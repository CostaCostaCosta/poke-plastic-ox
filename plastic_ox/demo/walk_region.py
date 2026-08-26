#!/usr/bin/env python3
"""Full-region demo: chain leg1..leg5 headlessly.

Each leg boots the ROM fresh and walks its route; the chain covers every
shipped leg (A-J, with the documented surf-gated deferrals). Prints
REGION DEMO PASSED when all five legs complete.
"""
from pathlib import Path
import sys

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))

import walk_leg1
import walk_leg2
import walk_leg3
import walk_leg4
import walk_leg5


def main():
    for name, mod in (("leg1", walk_leg1), ("leg2", walk_leg2),
                      ("leg3", walk_leg3), ("leg4", walk_leg4),
                      ("leg5", walk_leg5)):
        print(f"===== {name} =====", flush=True)
        mod.main()
        print(f"===== {name} PASSED =====", flush=True)
    print("REGION DEMO PASSED", flush=True)


if __name__ == "__main__":
    main()

# Plastic Ox agent/developer entry points. Included from the root Makefile;
# also usable standalone:  make -f plastic_ox/pox.mk pox-check-static
#
#   make pox-help                 list these targets
#   make pox-build                build pokeemerald.gba with the configured toolchain
#   make pox-check-static         fast checks, no ROM or emulator needed (run before every commit)
#   make pox-check-emu TESTS=...  mGBA harnesses from plastic_ox/demo (needs pox-build first)
#   make pox-check                all of the above
#   make pox-generated            which regenerated files have drifted from their generator
#
# Toolchain/emulator locations come from plastic_ox/bin/pox-env.sh.

# Default devkitARM location (same as pox-env.sh) so that plain `make` also
# works when DEVKITARM isn't exported. Only applies if the directory exists.
ifeq ($(origin DEVKITARM),undefined)
  _POX_DKA := $(firstword $(wildcard $(or $(DEVKITPRO),$(HOME)/devkitpro/opt/devkitpro)/devkitARM))
  ifneq (,$(_POX_DKA))
    export DEVKITARM := $(_POX_DKA)
    export PATH := $(DEVKITARM)/bin:$(PATH)
  endif
endif

POX_SHELL_ENV := . plastic_ox/bin/pox-env.sh &&
POX_PY ?= python3
POX_MGBA := plastic_ox/bin/pox-mgba-python
POX_JOBS ?= $(shell nproc 2>/dev/null || echo 4)
# Default emulator smoke set; override with TESTS="test_goldenrod test_league_rules".
TESTS ?= test_story
# POX_CI=1 is set by CI (no ROM build, no donor checkout).
POX_CI ?= 0

# Skip the root Makefile's dependency scan for these wrapper targets.
RULES_NO_SCAN += pox-help pox-build pox-check pox-check-static pox-check-emu pox-generated

.PHONY: pox-help pox-build pox-check pox-check-static pox-check-emu pox-generated

pox-help:
	@sed -n '1,11p' plastic_ox/pox.mk

pox-build:
	$(POX_SHELL_ENV) $(MAKE) -j$(POX_JOBS)

pox-check-static:
	@POX_CI=$(POX_CI) POX_PY=$(POX_PY) plastic_ox/bin/pox-check-static

pox-check-emu:
	@plastic_ox/bin/pox-check-emu $(TESTS)

pox-check: pox-check-static pox-build pox-check-emu

pox-generated:
	$(POX_PY) plastic_ox/tools/check_generated.py --verbose

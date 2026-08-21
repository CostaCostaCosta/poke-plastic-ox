# Plastic Ox — Local Build & Test Loop Setup

How this machine was set up (2026-08-20). Rootless — no sudo required.

## What was installed

| Piece | Where | How |
|---|---|---|
| devkitARM r65 (arm-none-eabi-gcc 14.2.0) | `~/devkitpro/opt/devkitpro/devkitARM` | `devkitARM-r65-1-linux_x86_64.pkg.tar.zst` from the devkitPro archive mirror `https://wii.leseratte10.de/devkitPro/devkitARM/r65%20%282024-08-30%29/`, extracted into `~/devkitpro` |
| libpng + zlib dev files (for host tools gbagfx/rsfont) | `~/toolchains/hostlibs` | `apt-get download libpng-dev libpng16-16t64 zlib1g-dev zlib1g` + `dpkg-deb -x` (no root) |
| mgba-rom-test, patchelf, hydra | in-repo `tools/` | built/shipped by the repo Makefile |

Notes:
- `pkg.devkitpro.org` is Cloudflare-blocked from this network; the mirror above hosts identical packages.
- Ubuntu's `gcc-arm-none-eabi` apt package does NOT work for this project: its newlib multilibs are built for Cortex-M and the linker fails with "failed to merge target specific data" against armv4t objects. devkitARM is the correct toolchain.
- `sudo` is password-protected on this machine, hence the rootless layout.

## Environment (persisted in ~/.bashrc)

```bash
export DEVKITPRO="$HOME/devkitpro/opt/devkitpro"
export DEVKITARM="$DEVKITPRO/devkitARM"
export PATH="$DEVKITARM/bin:$PATH"
export CPATH="$HOME/toolchains/hostlibs/usr/include${CPATH:+:$CPATH}"
export LIBRARY_PATH="$HOME/toolchains/hostlibs/usr/lib/x86_64-linux-gnu${LIBRARY_PATH:+:$LIBRARY_PATH}"
export PKG_CONFIG_PATH="$HOME/toolchains/hostlibs/usr/lib/x86_64-linux-gnu/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
```

## The test loop

```bash
cd ~/repos/poke-plastic-ox

# run one test file (name prefix or exact path both work)
make check TESTS="test/evolution_tier_gating.c" -j$(nproc)
make check TESTS="*Tier*" -j$(nproc)

# full suite
make check -j$(nproc)

# build an inspectable ROM with tests for mGBA
make pokeemerald-test.elf TESTS="*Tier*" -j$(nproc)

# build the actual game ROM
make -j$(nproc)          # -> pokeemerald.gba
```

- First build takes several minutes (whole ROM + test runner); subsequent `make check` runs are incremental and fast.
- Test output streams live; summary at the end shows pass/fail/skip counts and failing test names.

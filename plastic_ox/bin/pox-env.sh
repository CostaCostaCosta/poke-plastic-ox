# Source this (or let plastic_ox/pox.mk / pox-mgba-python do it) to get the
# Plastic Ox toolchain environment. Every value can be overridden beforehand,
# e.g. in ~/.config/pox/env.sh or plastic_ox/bin/pox-env.local.sh (gitignored).
#
#   DEVKITARM      devkitARM root (arm-none-eabi-* under $DEVKITARM/bin)
#   POX_HOSTLIBS   rootless libpng/zlib dev files for host tools (optional)
#   POX_MGBA_VENV  Python venv with the mGBA bindings (lib/, lib64/, bin/python)
#   POX_HNS_DONOR  pokehns-expansion checkout used as the Johto donor
_pox_root="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)"
[ -f "$HOME/.config/pox/env.sh" ] && . "$HOME/.config/pox/env.sh"
[ -f "$_pox_root/plastic_ox/bin/pox-env.local.sh" ] && . "$_pox_root/plastic_ox/bin/pox-env.local.sh"
export DEVKITPRO="${DEVKITPRO:-$HOME/devkitpro/opt/devkitpro}"
export DEVKITARM="${DEVKITARM:-$DEVKITPRO/devkitARM}"
export POX_HOSTLIBS="${POX_HOSTLIBS:-$HOME/toolchains/hostlibs}"
export POX_MGBA_VENV="${POX_MGBA_VENV:-$HOME/.venvs/mgba311}"
export POX_HNS_DONOR="${POX_HNS_DONOR:-$(dirname "$_pox_root")/pokehns-expansion}"
case ":$PATH:" in *":$DEVKITARM/bin:"*) ;; *) export PATH="$DEVKITARM/bin:$PATH" ;; esac
if [ -d "$POX_HOSTLIBS/usr" ]; then
  export CPATH="$POX_HOSTLIBS/usr/include${CPATH:+:$CPATH}"
  export LIBRARY_PATH="$POX_HOSTLIBS/usr/lib/x86_64-linux-gnu${LIBRARY_PATH:+:$LIBRARY_PATH}"
  export PKG_CONFIG_PATH="$POX_HOSTLIBS/usr/lib/x86_64-linux-gnu/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
fi
unset _pox_root

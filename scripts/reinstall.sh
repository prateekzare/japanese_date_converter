#!/usr/bin/env bash
# Remove japanese-date-converter from a virtualenv and install it again.
#
#   ./scripts/reinstall.sh                       # uses ../.venv
#   ./scripts/reinstall.sh --venv ~/app/.venv    # a different venv
#   ./scripts/reinstall.sh --editable --test     # editable install + pytest
#
# Works with the venv layout on both Linux/macOS (bin/) and Windows (Scripts/),
# so it is usable from Git Bash as well.

set -euo pipefail

PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_NAME="japanese-date-converter"
MODULE_NAME="japanese_date_converter"

VENV="$PACKAGE_ROOT/.venv"
EDITABLE=0
RUN_TESTS=0
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --venv)     VENV="$2"; shift 2 ;;
    --editable) EDITABLE=1; shift ;;
    --test)     RUN_TESTS=1; shift ;;
    --force)    FORCE=1; shift ;;
    -h|--help)  sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

# --- locate the interpreter -------------------------------------------------
if   [ -x "$VENV/bin/python" ];        then PY="$VENV/bin/python"
elif [ -x "$VENV/Scripts/python.exe" ]; then PY="$VENV/Scripts/python.exe"
else
  if [ "$FORCE" -eq 0 ]; then
    echo "No virtualenv at '$VENV'. Create one with 'python -m venv $VENV', or pass --force." >&2
    exit 1
  fi
  echo "Creating virtualenv at $VENV ..."
  python -m venv "$VENV"
  PY="$VENV/bin/python"; [ -x "$PY" ] || PY="$VENV/Scripts/python.exe"
fi

# Resolve to an absolute path: the verify step changes directory, and a
# relative interpreter path would stop resolving once it does.
PY="$(cd "$(dirname "$PY")" && pwd)/$(basename "$PY")"

echo "Interpreter : $PY"
echo "Source tree : $PACKAGE_ROOT"
echo

# --- uninstall --------------------------------------------------------------
echo "==> Removing any existing install"
for name in "$DIST_NAME" "$MODULE_NAME"; do
  # -y so it never prompts; a package that is not installed is fine here.
  "$PY" -m pip uninstall -y "$name" 2>&1 | grep -v "^WARNING: Skipping" || true
done

# Editable installs leave a .pth or an __editable__ finder behind that keeps
# the old tree importable after the metadata is gone. Clear those too.
SITE_PACKAGES="$("$PY" -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")"
if [ -d "$SITE_PACKAGES" ]; then
  find "$SITE_PACKAGES" -maxdepth 1 \
       \( -name "japanese?date?converter*" -o -name "__editable__*japanese*" \) \
       -exec sh -c 'echo "    removing leftover $(basename "$1")"; rm -rf "$1"' _ {} \;
fi

if "$PY" -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('$MODULE_NAME') else 1)" 2>/dev/null; then
  echo "    warning: $MODULE_NAME is still importable -- something on PYTHONPATH or in the cwd is shadowing it." >&2
fi

# --- reinstall --------------------------------------------------------------
echo
echo "==> Installing from source"
cd "$PACKAGE_ROOT"
if [ "$EDITABLE" -eq 1 ]; then
  "$PY" -m pip install -e .
else
  # --no-cache-dir so a rebuilt wheel carrying the same version number is not
  # served from pip's cache, which is the usual reason a reinstall appears to
  # do nothing at all.
  "$PY" -m pip install --no-cache-dir --force-reinstall .
fi

# --- verify -----------------------------------------------------------------
echo
echo "==> Verifying"
# Run from a neutral directory: the source tree shadows site-packages when it
# is the working directory, which would make any install look successful.
cd "$(dirname "$(mktemp -u)")" 2>/dev/null || cd /
"$PY" - <<'PYCODE'
import japanese_date_converter as j
print('  version   ', j.__version__)
print('  location  ', j.__file__)
print('  2019-04-30', j.to_japanese('2019-04-30', use_full_width=False))
print('  2019-05-01', j.to_japanese('2019-05-01', use_full_width=False))
print('  R5.12.15  ', j.to_standard('R5.12.15', output_format='%Y-%m-%d'))
PYCODE

if [ "$RUN_TESTS" -eq 1 ]; then
  echo
  echo "==> Running tests"
  cd "$PACKAGE_ROOT"
  "$PY" -m pip install -q pytest
  "$PY" -m pytest -q
fi

echo
echo "Done."

#!/bin/bash
# ============================================================
#  Start Float.command (macOS)
#
#  Double-click this in Finder (or launch Float.app) to start
#  Float immediately with fast opening and zero terminal clutter.
# ============================================================

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Clear macOS Gatekeeper quarantine attributes on this folder & Float.app
xattr -cr "$DIR" 2>/dev/null || true

# Find a working Python 3.10+
PY=""
for cand in "/opt/homebrew/bin/python3" "/usr/local/bin/python3" "/Library/Frameworks/Python.framework/Versions/Current/bin/python3" "$(command -v python3 2>/dev/null)" "/usr/bin/python3"; do
    if [ -n "$cand" ] && [ -x "$cand" ]; then
        if "$cand" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >/dev/null 2>&1; then
            PY="$cand"
            break
        fi
    fi
done

if [ -z "$PY" ]; then
    osascript -e 'display alert "Python 3.10+ Required" message "Float needs Python 3.10 or newer on this Mac.\n\nDownload and install the macOS installer from https://www.python.org/downloads/macos/ and then open Float again." as critical' >/dev/null 2>&1 || true
    exit 1
fi

DATA_DIR="${FLOAT_DATA_DIR:-$DIR/data}"
mkdir -p "$DATA_DIR"

if [ "$1" = "--show" ]; then
    exec "$PY" "$DIR/main.py"
fi

# Launch Float cleanly in the background with stdin detached so Finder/Terminal never hangs
nohup "$PY" "$DIR/main.py" >"$DATA_DIR/float_stdout.log" 2>&1 </dev/null &
disown 2>/dev/null || true
exit 0

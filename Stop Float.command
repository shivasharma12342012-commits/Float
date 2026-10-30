#!/bin/bash
# ============================================================
#  Stop Float.command (macOS)
#
#  Double-click this in Finder to cleanly stop the Float server.
# ============================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PY=""
for cand in "/opt/homebrew/bin/python3" "/usr/local/bin/python3" "/Library/Frameworks/Python.framework/Versions/Current/bin/python3" "$(command -v python3 2>/dev/null)" "/usr/bin/python3"; do
    if [ -n "$cand" ] && [ -x "$cand" ]; then
        PY="$cand"
        break
    fi
done

if [ -z "$PY" ]; then
    osascript -e 'display alert "Float" message "Python 3 was not found on this Mac." as critical' >/dev/null 2>&1 || true
    exit 1
fi

OUTPUT=$("$PY" "$DIR/main.py" stop --force "$@" 2>&1)
osascript -e "display notification \"$OUTPUT\" with title \"Float\"" >/dev/null 2>&1 || true
echo "$OUTPUT"
exit 0

#!/bin/bash
# ============================================================
#  Start Float Agency Server.command (macOS)
#
#  Run this on the central Mac that holds every employee's account.
# ============================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
export FLOAT_LAN=1
exec /bin/bash "$DIR/Start Float.command" --show

#!/bin/bash
# ============================================================
#  TERRA BATTLE IPA AUTO-PATCHER (Linux / Mac)
#  Python 3.11+ required (uses system python3/python).
# ============================================================
cd "$(dirname "$0")"
ROOT="$(pwd)"

PY=""
if [ -x "$ROOT/runtime/bin/python3" ]; then
    "$ROOT/runtime/bin/python3" -c "import sys" >/dev/null 2>&1 && PY="$ROOT/runtime/bin/python3"
fi
if [ -z "$PY" ]; then
    for c in python3 python; do
        command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys" >/dev/null 2>&1 && PY="$c" && break
    done
fi
if [ -z "$PY" ]; then
    echo "Python not found. Install python3 first."
    read -r -p "Press Enter to exit..."; exit 1
fi

"$PY" PATCH-ME.py
echo
read -r -p "Press Enter to exit..."

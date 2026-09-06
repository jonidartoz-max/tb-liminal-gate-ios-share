#!/bin/bash
# ============================================================
#  TERRA BATTLE SERVER - STOPPER (Linux / Mac)
# ============================================================
pids=$(pgrep -f "liminal_gate.bootstrap_server" 2>/dev/null)
if [ -z "$pids" ]; then
    echo "No running Terra Battle server found."
else
    for pid in $pids; do
        echo "Killing PID $pid ..."
        kill $pid 2>/dev/null
    done
    sleep 2
    if pgrep -f "liminal_gate.bootstrap_server" >/dev/null 2>&1; then
        echo "Force killing..."
        pkill -9 -f "liminal_gate.bootstrap_server"
    fi
    echo "Server stopped."
fi
read -r -p "Press Enter to exit..."

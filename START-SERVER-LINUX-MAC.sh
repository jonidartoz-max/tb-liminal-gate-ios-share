#!/bin/bash
# ============================================================
#  TERRA BATTLE SERVER - ONE-CLICK STARTER (Linux / Mac)
#  Fully portable: bundled Python runtime. No install, no venv,
#  no pip, no internet needed on the target machine.
# ============================================================
cd "$(dirname "$0")"
ROOT="$(pwd)"
SRV="$ROOT/project-liminal-gate"

# --- locate a working Python, PREFERRING the bundled portable one ---
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

# --- extract bundled source if not present ---
if [ ! -d "$SRV/liminal_gate" ]; then
    echo "Extracting server code..."
    tar -xzf "$ROOT/project-liminal-gate-source.tar.gz" -C "$ROOT" || { read -r -p "Enter..."; exit 1; }
fi

# --- auto-detect LAN IP + Tailscale IP ---
LAN_IP=$("$PY" -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0])" 2>/dev/null || echo "192.168.1.100")
TS_IP=$(tailscale ip -4 2>/dev/null | head -1)
[ -z "$TS_IP" ] && TS_IP="(not installed — https://tailscale.com, login with your email)"

echo "Starting Terra Battle server on port 18696 ..."
echo "  LAN:       http://$LAN_IP:18696"
echo "  Tailscale: http://$TS_IP:18696  (if installed; login with your email at https://tailscale.com)"
echo "  On this machine, verify at: http://$LAN_IP:18696/healthz  (should show {\"status\":\"ok\"})"
echo "  Root \"/\" always shows {\"error\":\"route_not_implemented\"} - that is NORMAL"
echo "  To play from anywhere: install Tailscale on this PC + iPhone, login with SAME email,"
echo "  then run PATCH-ME and paste the 100.x IP."
echo "(first start takes 1-5 minutes: checking all resource files)"
echo

"$PY" -m liminal_gate.bootstrap_server \
  --profile  "$ROOT/profiles/legacy-client-bootstrap.json" \
  --state-file  "$ROOT/user-data/bootstrap-state.json" \
  --host 0.0.0.0 --port 18696 \
  --event-log  "$ROOT/user-data/events.jsonl" \
  --resource-root  "$ROOT/resources" \
  --resource-manifest  "$ROOT/user-data/resources.json" \
  --public-data-root  "$ROOT/user-data/public_data" \
  --core-story --pacts --hunting --daily-quests --secondary-worlds \
  --jobs --rebirth --status-items --companion-draw --companion-sale \
  --companion-strengthen --companion-evolution --trading-post \
  --drop-eligibility --achievements --summon-skills

echo
echo "Server stopped."
read -r -p "Press Enter to exit..."

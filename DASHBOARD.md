# Server Dashboard — TB-SHARE (local server)

Simple read-only status page built into the local server (START-SERVER-WINDOWS.bat,
port 18696). No extra install, no buttons — start/stop the server with the
batch files in this folder.

## How to open

1. Start the server (double-click `START-SERVER-WINDOWS.bat`).
2. Wait ~15 seconds until the console shows `bootstrap compatibility server listening ...`
3. Open in any browser (on the same PC):
   http://localhost:18696/dashboard
4. From your phone (same Wi-Fi / Tailscale): use the PC's IP, e.g.
   http://192.168.1.10:18696/dashboard  (the console window prints the LAN IP)

The page refreshes itself every 5 seconds.

## What you see

- STATUS — running, uptime, port, account count, active account.
- ACCOUNTS — every player save on this server:
  account id, tutorial phase, chapter-section reached,
  coins / energy / free energy, active save (star).
- RECENT REQUESTS — last 30 requests from players and browsers, with status
  code. Red = error (400/401/409/500...), with the reason.
- raw JSON: http://localhost:18696/dashboard/data

## Start / stop the server itself

- Start: double-click `START-SERVER-WINDOWS.bat`
- Stop: double-click `STOP-SERVER-WINDOWS.bat` (kills only this server, then
  verifies port 18696 is free)

## Save management (move/delete/restore saves)

Use the save manager CLI from the share folder:

    runtime\python.exe project-liminal-gate\liminal_gate\account_state.py inspect user-data\bootstrap-state.json

It can inspect, snapshot, restore, switch the active save, and link devices.
Full guide: `GUIDE.md` in this folder, or the GitHub README.

================================================================================
TERRA BATTLE PRIVATE SERVER — QUICK START (ENGLISH)
================================================================================
Everything is in this one folder. Total setup time: about 10 minutes.
(FULLY WORKING & TESTED — setup, patch, remote play via Tailscale, in-game.)

WHAT YOU NEED
-------------
1. A Windows PC (Linux/Mac also work — use the .sh files)
2. NO install needed — a portable Python runtime is bundled inside
   the runtime\ folder. The server + patcher run straight from USB.
3. An iPhone with the game installed (see "PATCH THE IPA" below)
4. Phone and PC on the same Wi-Fi network
   (or Tailscale on both devices for play from anywhere)

================================================================================
SETUP — 3 STEPS
================================================================================

STEP 1 — START THE SERVER
-------------------------
Double-click:  START-SERVER-WINDOWS.bat

First run it will:
  - extract the server code (2 seconds)
  - start the server (first start: 1-5 minutes of "checking resource files")

Done when you see:
  bootstrap compatibility server listening on http://0.0.0.0:18696

Keep this window OPEN while playing (closing it stops the server).

Check it works: open http://localhost:18696/healthz in a browser
You should see: {"status":"ok"}
NOTE: opening http://localhost:18696/ (without /healthz) always shows
{"error":"route_not_implemented"} - that is NORMAL. Use /healthz to verify.


STEP 2 — PATCH THE IPA (put your server address in the game)
------------------------------------------------------------
Double-click:  PATCH-ME-WINDOWS.bat

It finds your PC's IP automatically. Just press Enter twice.
Result:  TerraBattle-PATCHED.ipa  (ready to install)

Short IPs (like 172.20.10.7) are now auto-padded with null bytes to
fill the fixed 26-char slot — the patcher does this for you and
iOS stops at the null, so it still connects to the right address.
If your address is too LONG (>26), pick a shorter port or hostname.

NOTE: the game requires the full address to be EXACTLY 26 characters.
The patcher checks this for you. If your IP is short, it will auto-pad
with nulls. If it is long, it will tell you how many characters to
remove — then use a shorter port (e.g. 8696) or a shorter hostname.

NEVER type leading zeros in an IP yourself (e.g. "074") — some systems
read that as a different number entirely (octal). The patcher never pads
the IP with zeros; short addresses are padded with null bytes instead.


STEP 3 — INSTALL ON THE IPHONE
------------------------------
You need a free tool called Sideloadly (https://sideloadly.io) and iTunes
installed on the PC (https://www.apple.com/itunes/download/win64 — iTunes
provides the phone drivers).

  1. Connect the iPhone with a cable → tap "Trust" on the phone
  2. Open Sideloadly, drag TerraBattle-PATCHED.ipa into it
  3. Enter your Apple ID (any account — free signing lasts 7 days)
  4. Click Start, wait for it to finish
  5. On the phone: Settings → General → VPN & Device Management →
     tap your Apple ID → Trust
  6. Open Terra Battle and play!

When the 7 days expire: reconnect the phone and press Start again in
Sideloadly (same steps, keeps your save).

================================================================================
PLAY FROM ANYWHERE (optional) — TAILSCALE
================================================================================
1. Install Tailscale on the PC (https://tailscale.com) and sign in.
2. Install Tailscale on the iPhone and sign in with the same account.
3. On the PC, run PATCH-ME-WINDOWS.bat again:
     - Server IP: your PC's Tailscale IP (starts with 100.x — shown by
       the command "tailscale ip -4", or look at the Tailscale app)
     - Server port: 18696
4. Reinstall the patched IPA on the phone (Sideloadly, same steps).
5. Open the Tailscale app on the phone, make sure it shows Connected,
   THEN open the game.

Proven working: iPhone over cellular/Tailscale connecting to the PC at
home. Note the phone needs the Tailscale app alive while playing —
if the game hangs at a white screen, the VPN was killed by iOS in the
background; reopen Tailscale and try again.

================================================================================
STOPPING THE SERVER
--------------------------------------------------------------------------------
Double-click:  STOP-SERVER-WINDOWS.bat
(or just close the server window — same thing)

================================================================================
EVERYDAY USE (after first setup)
================================================================================
  1. Double-click START-SERVER-WINDOWS.bat → wait until "listening"
  2. Play on the phone
  3. Double-click STOP-SERVER-WINDOWS.bat when done

================================================================================
YOUR SAVE DATA
--------------------------------------------------------------------------------
Progress is saved on the PC (not the phone), in this file:

  user-data\bootstrap-state.json

Back that file up (USB drive, cloud) and you can move the server to any PC —
the phone keeps its progress as long as the server address stays the same.

Reinstalling the game on the phone does NOT lose progress.

================================================================================
IF SOMETHING GOES WRONG
--------------------------------------------------------------------------------
"Network error" on the phone / stuck on white loading screen
  - Server window still open? (closing it = server off)
  - Check the last line of the server window says "listening"
  - Check http://localhost:18696/healthz on the PC first.
  - If using Tailscale: open the Tailscale app on the phone and confirm
    it shows Connected, then retry. iOS can kill the VPN in background.
  - PC IP changed? Re-run PATCH-ME and reinstall the IPA.
  - Windows Firewall blocking? Allow Python when Windows asks.

"ModuleNotFoundError: No module named 'liminal_gate'" on first start
  - The first-run package install was interrupted (usually because an old
    server was still holding the folder). Close everything, delete the
    project-liminal-gate folder, and run START-SERVER again.

"did not find executable at 'C:\Users\...\python.exe'" on start
  - OLD packages had a Python path baked in from another PC. This version
    FIXED that: it never uses a virtual environment, and ships its own
    portable Python in runtime\. So this error no longer happens. If you
    somehow still see it, you have the old pay package — re-download.

"The system cannot find the path specified" on start
  - Same as above: this old error is gone in the portable version.
    Just re-download the current package (it bundles everything).

"healthz" doesn't open in the browser
  - Wait — first start checks thousands of files (1-5 minutes).
  - Look at the server window for errors.
  - Remember: http://localhost:18696/ (root) always returns
    {"error":"route_not_implemented"} - check http://localhost:18696/healthz instead.

Game loads, sound works, but everything is BLANK
  - You are missing the resources\iOS_2 folder, or the server was started
    with the wrong --resource-root. Use START-SERVER-WINDOWS.bat (it is
    pre-configured) and keep the folder layout as shipped.

Patch says "address must be exactly 26 characters"
  - The slot is fixed at 26. "http://" uses 7, so your host + port must
    together be 18 characters (host + ":" + port = 19).
  - The patcher prints the exact number of characters to add/remove, and
    lets you pick the port. Ports must be 1-65535 (so 18696 works, but a
    5-digit port like 86960 does NOT — it is too big). Follow what the
    patcher says; it does the math for you.

Sideloadly shows an error
  - Make sure iTunes is installed (drivers) and the phone is trusted.
  - Try a different cable / USB port.

================================================================================
WHAT'S IN THIS FOLDER
--------------------------------------------------------------------------------
  START-SERVER-WINDOWS.bat       start the server (one click)
  STOP-SERVER-WINDOWS.bat        stop the server
  PATCH-ME-WINDOWS.bat           patch the IPA to your PC's address
  runtime\                       portable Python (no install needed)
  extract_code.py                helper used by the starter
  project-liminal-gate-...gz     the server program (extracted on first start)
  resources\iOS_2\               game files the server gives to the phone
  user-data\                     server state + your save (bootstrap-state.json)
  profiles\                      server configuration
  server_json\                   backup copies of the configuration
  TerraBattle-UNPATCHED-template.ipa   game client, no address inside
  TerraBattle-PATCHED.ipa        (created by PATCH-ME — install this one)
  TUTORIAL-RESOURCES-FOLDER-EN.txt  how the resource folders fit together

LEGAL NOTE: Terra Battle was created by Mistwalker and discontinued in 2020.
This package is for personal preservation and play of a dead game only.
================================================================================

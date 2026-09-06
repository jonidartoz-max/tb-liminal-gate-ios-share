# Liminal Gate TB1 — Complete Setup Guide (Terra Battle, iOS)

This is the **step-by-step guide with every detail spelled out**. If you just
want the short version, read `README.md`; if something goes wrong, jump to
**Troubleshooting** at the bottom of this guide.

Everything here is in English. Total first-time setup: about 15 minutes.

---

## 0. What you need before starting

| # | Item | Notes |
| --- | --- | --- |
| 1 | A PC (Windows recommended; Linux/macOS work via the `.sh` files) | Windows 10/11 tested |
| 2 | The **iOS_2 resource pack** (~505 MB) | NOT in this repo — see step 2 |
| 3 | An iPhone (iOS 13 or newer) | jailbreak NOT required |
| 4 | A cable (for the one-time IPA install) or same Wi-Fi | |
| 5 | (Optional) [Tailscale](https://tailscale.com) account | free, for playing away from home |

You do NOT need: pip, a venv, any Python installation, an App Store account
with the game, or a jailbroken phone.

---

## 1. Get the server onto your PC

1. Download this repo: green **Code** button → **Download ZIP** → extract it.
   (Or `git clone https://github.com/jonidartoz-max/tb-liminal-gate-ios-share.git`)
2. You now have a folder that looks like this:

```
tb-liminal-gate-ios-share\
├── project-liminal-gate\     <- server source code
├── profiles\                 <- server configuration
├── server_json\              <- resource manifests (SHA-256 lists)
├── user-data\                <- banners + patchData.zip (shipped)
├── runtime\                  <- optional portable Python goes here
├── START-SERVER-WINDOWS.bat  <- server launcher
├── PATCH-ME-WINDOWS.bat      <- IPA patcher
├── TerraBattle-UNPATCHED-template.ipa  <- clean game client
└── ...
```

3. Keep this folder **directly on a drive root or one level deep**
   (example: `D:\LiminalGate\`). Very deep paths or paths with unusual
   characters can break the Windows batch files.

---

## 2. Get the resource pack (the only thing not in this repo)

The server streams ~11,800 hashed game asset files to the phone (backgrounds,
music, sound effects, illustrations...). They are copyrighted game art, so
this repo ships **code only** — you fetch the pack yourself.

1. Go to **archive.org** (https://archive.org).
2. Search for: **`terra battle ios_2 data_u2017 resource pack`**
   (also try: `terra battle iOS_2`, `terra battle data_u2017`).
3. Download the pack. Inside you should find folders named
   `BG`, `BGM`, `Banner`, `BuddyImages`, `BuddyThumbs`, `Illust`,
   `Pieces`, `Scenario`, `SE` (each full of `.bin` files).
4. Place the pack so the layout is exactly:

```
<your share folder>\
└── resources\
    └── iOS_2\
        ├── Banner\
        ├── BG\
        ├── BGM\
        ├── BuddyImages\
        ├── BuddyThumbs\
        ├── Illust\
        ├── Pieces\
        ├── Scenario\
        └── SE\
```

5. Verify you got the right pack: the `server_json\resources.json` manifest in
   this repo lists every expected file with its SHA-256 hash (17,709 entries
   across both path layouts). Any file checker can validate your download
   against it.

> Note: some packs nest the folders as `resources\data_u2017\iOS_2\...`.
> The manifest covers both layouts. If the server complains at boot about
> "resource file is unavailable", your nesting does not match the manifest —
> either move the `iOS_2` folder directly under `resources\` or edit
> `START-SERVER-WINDOWS.bat`'s `--resource-root` line to point at the folder
> that directly contains `BG`, `BGM`, etc.

---

## 3. Start the server

1. Double-click **`START-SERVER-WINDOWS.bat`** (Linux/macOS: run
   `START-SERVER-LINUX-MAC.sh`).
2. First boot does two things:
   - extracts the server code (2 seconds),
   - validates every resource file's SHA-256 (**1–5 minutes** — the window
     will sit quiet; that is normal).
3. Ready when you see:

```
bootstrap compatibility server listening on http://0.0.0.0:18696
```

4. Sanity check: open `http://localhost:18696/healthz` in a browser on the PC.
   Expected: `{"status":"ok"}`.
   (`http://localhost:18696/` without `/healthz` always returns
   `{"error":"route_not_implemented"}` — that is normal, use `/healthz`.)

Leave this window open while playing. Closing it stops the server.

**Python note:** the launcher looks for a portable Python in `runtime\`
(python.exe directly inside), then `py`, `python`, `python3` on PATH, then
common install folders. No pip installs are ever needed — the server is
stdlib-only. If you want the zero-install route, download Python 3.11's
"Windows embeddable package (64-bit)" from python.org and extract it into
`runtime\`.

---

## 4. Patch the IPA (point the game at your server)

The iOS game has a hardcoded server address inside its binary, in a fixed
**26-character slot**. The patcher writes your server address into that slot.

1. Double-click **`PATCH-ME-WINDOWS.bat`**.
2. It auto-detects your PC's LAN IP. Press Enter to accept it (or type your
   Tailscale 100.x IP — see step 6).
3. Press Enter again to confirm the port (default `18696`).
4. Output: **`TerraBattle-PATCHED.ipa`** — this is the game with your server
   address inside.

How the 26-character rule works:
- The full address `http://<host>:<port>` must be **exactly 26 characters**
  (`http://` = 7 chars, so host + `:` + port must be 19).
- Short addresses are padded with **null bytes** automatically — iOS stops
  reading at the null, so a padded address still works.
- Never pad an IP with leading zeros yourself (`074` reads as octal on some
  systems). Nulls only — the patcher handles this.
- The patcher tells you exactly how many characters to add or remove if your
  address does not fit.

---

## 5. Install the game on the iPhone

The patched IPA must be side-loaded (the game is no longer on the App Store).

1. Install **iTunes** on the PC (for the phone drivers):
   https://www.apple.com/itunes/download/win64
2. Install **Sideloadly**: https://sideloadly.io
3. Connect the iPhone by cable → tap **Trust** on the phone.
4. Open Sideloadly → drag `TerraBattle-PATCHED.ipa` into it.
5. Enter any Apple ID (a free account signs for 7 days).
6. Click **Start** and wait.
7. On the phone: **Settings → General → VPN & Device Management → tap your
   Apple ID → Trust**.
8. Open Terra Battle. If the server is running and the phone is on the same
   Wi-Fi (or Tailscale is up), the title screen will load from your server.

Re-signing after 7 days: reconnect the phone and press Start in Sideloadly
again — your save survives.

---

## 6. Play from anywhere (optional): Tailscale

1. Install Tailscale on the PC: https://tailscale.com → sign in.
2. Install Tailscale on the iPhone → sign in with the **same** account.
3. Find the PC's Tailscale IP: run `tailscale ip -4` in a terminal, or read it
   from the Tailscale app (it starts with `100.`).
4. Run `PATCH-ME-WINDOWS.bat` again with that `100.x` IP (port still `18696`).
5. Re-install the patched IPA (same Sideloadly steps).
6. On the phone: open the Tailscale app and confirm it says **Connected**,
   THEN launch the game.

Notes from real usage:
- The game needs the Tailscale app alive while playing. If the game hangs on
  a white screen, iOS killed the VPN in the background — reopen Tailscale.
- Works over cellular; the phone does not need to be on your home Wi-Fi.

---

## 7. Change Device / Data Transfer (moving a save between devices)

Terra Battle has a built-in transfer system; this server implements it fully.

**On the old device (the one holding the save):**
1. Play normally once so the save is on the server.
2. **Options > Change Device > OK**.
3. Enter a new password (8–16 letters/numbers). Confirm it. Press OK.
4. The screen "Settings for game data transfer are complete" shows three
   values — write them all down:
   - **User ID** — a 9-digit number
   - **Transfer ID** — 12 characters
   - the password you just chose
5. A Transfer ID + password pair is **single-use**. After one successful
   transfer it is consumed; issue a fresh pair for the next move.

**On the new device (or after reinstalling the app on the same phone):**
1. Install the patched IPA if needed.
2. On the title screen choose **Transfer Game Data** — NOT New Game.
3. Enter the User ID (the field opens a numeric keypad — the User ID is
   always digits), the Transfer ID, and the password.
4. Press OK. You will see a success notification, the game re-logs in by
   itself, and your save appears.

Trouble-shooting this feature: if it says "network error", the server could
not parse what arrived — check the server window; every migration request is
logged. If it says the information is incorrect, the Transfer ID or password
did not match (or was already used).

---

## 8. Everyday use (after first setup)

```
1. START-SERVER-WINDOWS.bat  → wait for "listening"
2. Play on the phone
3. STOP-SERVER-WINDOWS.bat   → when done
```

- Your save lives on the PC in `user-data\bootstrap-state.json`.
- Back that file up (USB, cloud) and you can move the whole server to any PC.
- Reinstalling the game on the phone does NOT lose progress — the phone holds
  only a pointer (device uuid), the PC holds the actual save.
- One server per save: if you double-click START while a server is already
  running you will see "local account state is already in use by another
  server". Either keep using the running one, or run STOP-SERVER first.

---

## 9. Troubleshooting

**"Network error" on the phone / white loading screen**
- Server window still open? Closing it = server off.
- `http://localhost:18696/healthz` works on the PC?
- Phone on the same Wi-Fi (or Tailscale Connected)?
- PC's IP changed (router reboot)? → re-run PATCH-ME, re-install the IPA.
- Windows Firewall asked about Python at first start → allow it.

**Stuck on the Mistwalker splash forever**
- `public_data\patchData.zip` must exist (it ships with this repo). The client
  polls it during the splash; a missing/broken file hangs the splash.
- Check `http://<server>:18696/public_data/patchData.zip` returns a ZIP.

**Game loads, sound works, but everything is BLANK**
- The `resources\iOS_2\` pack is missing or the path is wrong. Re-check the
  layout in step 2 and the `--resource-root` line in the launcher.

**"resource file is unavailable" at server start**
- The manifest (`server_json\resources.json` / `resources_ios2.json`) lists
  files that must exist under the `--resource-root`. Your resource folder
  nesting does not match — see the note at the end of step 2.

**"local account state is already in use by another server"**
- A Terra Battle server is already running (maybe a window you forgot).
- Keep using it, or run `STOP-SERVER-WINDOWS.bat` and start fresh.

**"healthz" does not open in the browser**
- First start validates thousands of files (1–5 minutes). Wait.
- Remember: the root `/` always returns `route_not_implemented` — use
  `/healthz`.

**Patch says "address must be exactly 26 characters"**
- `http://` = 7 chars, so host + `:` + port must total 19. The patcher does
  the math and prints what to change. Ports 1–65535 only (18696 fits; a
  5-digit port like 86960 does not).

**Sideloadly errors**
- iTunes installed (drivers)? Phone trusted? Try another cable/USB port.

**Crash right after tapping something in-game**
- Note what you tapped and check `user-data\events.jsonl` — the last request
  before the crash shows the exact step that failed. Crash details
  (`.ips` files) can be pulled from the phone: Settings → Privacy & Security →
  Analytics & Improvements → Analytics Data → look for `guardians-...ips`.

---

## 10. Server endpoints (reference)

```
GET  /healthz                       liveness check
GET  /gd/get_current_time           clock sync
GET  /gd/get_server_status          server constants
GET  /gd/signup?otk=..&uuid=..      account provisioning
GET  /gd/login?otk=..&uuid=..       session (numeric id + uuid dual identity)
GET  /gd/userdata                   full save blob (MD5-signed)
POST /gd/start_quest                battle start (anti-downgrade progress)
POST /gd/clear_quest                battle settle (client-driven)
POST /gd/read_messages              inbox reads / gift claims
GET/POST /gd/get_migration_id       issue Transfer ID
POST /gd/set_migration_pass         set transfer password (pass = MD5)
POST /gd/migrate_userdata           data transfer (auto-provisions the target)
GET  /public_data/patchData.zip     splash patch data
GET  /public_data/banners/*.png     recruit banners (language suffix stripped)
GET  /resources/<Cat>/<file>.bin    hashed asset bundles
```

Every game response is MD5-signed:
`digest = md5(token + body + "mist_guardians_keycode")[16:32]`.

Technical fix details (crash forensics, protocol discoveries, A/B test
results): see `FIX-LOG-EN.md`.

---

## 11. Credits & legal

- Server base: [anzensan/project-liminal-gate](https://github.com/anzensan/project-liminal-gate)
- Terra Battle © Mistwalker — discontinued in 2020. This project exists for
  personal preservation of a dead game. Own the game; run the server for
  yourself, not for others.

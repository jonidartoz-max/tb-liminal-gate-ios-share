# Liminal Gate TB1 — Terra Battle (iOS Private Server Share)

**Liminal Gate TB1** is a portable, self-contained private server for **Terra Battle (iOS version)** —
the complete "data transfer / change device" feature, daily energy gifts,
recruit banners, patch data, and the chapter 20+ progression fix, all working
out of one folder.

Server code base: forked from [anzensan/project-liminal-gate](https://github.com/anzensan/project-liminal-gate)
(you are likely on a fork of it already — this repo adds the iOS-specific
fixes and the one-click portable launcher on top).

> **This is the iOS version** of the game client (IPA side-load). The patcher
> rewrites the hardcoded server URL inside the IPA binary (9 slots, fixed
> 26-character window, null-padded).

---

## What is included (and what is NOT)

```
TB-SHARE - Liminal Gate\
├── project-liminal-gate\        <- server source (Python, stdlib only)
│   ├── liminal_gate\            <- the actual server package
│   ├── profiles\                <- client profile (legacy iOS client)
│   ├── scripts\, tools\         <- build/import helpers
│   └── pyproject.toml
├── profiles\                    <- profile copy used by the launcher
├── resources\                   <- NOT IN THIS REPO (see "Resources" below)
├── user-data\                   <- created at runtime (state, event log,
│                                    public_data banners) - not in repo
├── runtime\                     <- portable Python (not in repo, optional)
├── START-SERVER-WINDOWS.bat     <- one-click server (Windows)
├── START-SERVER-LINUX-MAC.sh    <- one-click server (Linux/macOS)
├── STOP-SERVER-*.bat/.sh        <- stop helpers
├── run_common.bat               <- shared Python-locating logic
├── PATCH-ME.py                  <- IPA URL patcher (26-char slot, null-pad)
├── PATCH-ME-WINDOWS.bat/.sh     <- patcher wrappers
├── extract_code.py              <- extracts source on first run
├── TerraBattle-UNPATCHED-template.ipa  <- clean iOS client build (patch this)
├── FIX-LOG-EN.md                <- full fix log (change device, inbox,
│                                    chapter 20+, quest flow)
├── FIX-DAILY-ENERGY-CLAIM.md        <- daily gift runbook
└── README-QUICKSTART-EN.txt     <- the original player-facing quick start
```

---

## Why resources are not here (and where to get them)

The `resources\` folder holds ~11,800 hashed asset bundles (`BG/`, `BGM/`,
`Banner/`, `Illust/`, `Pieces/`, `Scenario/`, `SE/`, `BuddyImages/`,
`BuddyThumbs/`) extracted from the **iOS client (iOS_2 pack)**. They are
copyrighted game art — the repo ships **code only**.

**Clue for finding the pack:** search **archive.org** for the Terra Battle
**iOS_2** resource bundle (`data_u2017/iOS_2`). The keyword to look for:

    terra battle ios_2 data_u2017 resource pack

Once downloaded, place it so the layout is:

```
TB-SHARE - Liminal Gate\
└── resources\
    └── iOS_2\
        ├── Banner\  ├── BG\  ├── BGM\  ├── BuddyImages\
        ├── BuddyThumbs\  ├── Illust\  ├── Pieces\
        ├── Scenario\  └── SE\
```

The launcher passes `--resource-root resources\iOS_2`, and the manifest in
`user-data\resources.json` (auto-generated or shipped) resolves
`/resources/<Category>/<file>.bin` URLs against that folder.

---

## Quick start (iOS)

1. **Start the server** — `START-SERVER-WINDOWS.bat` (or the `.sh` on
   Linux/macOS). First boot takes 1–5 minutes (SHA-256 validation of every
   resource file). Ready when `/healthz` returns `{"status":"ok"}`.
2. **Patch the IPA** — this repo ships the clean client build
   (`TerraBattle-UNPATCHED-template.ipa`, iOS version). Run
   `PATCH-ME-WINDOWS.bat`, enter your PC's LAN IP (or Tailscale 100.x IP) when
   asked. The patcher pads short addresses with null bytes to fill the fixed
   26-char slot inside the binary.
   Output: `TerraBattle-PATCHED.ipa` — side-load it (Sideloadly/AltStore).
3. **Play** — open the game on the iPhone; the title screen will hit your
   server directly.

### Folder path rules (important)

- Keep the whole folder **one level deep** on drive `D:` (or any drive):
  `D:\TB-SHARE - Liminal Gate\` works; deep nested paths can break the
  batch files' `%~dp0` resolution.
- Never rename the inner `project-liminal-gate` folder — `extract_code.py`
  and the launcher both reference it by name.
- `user-data\` is where YOUR save state lives (`bootstrap-state.json`,
  `events.jsonl`, `public_data\`). Back it up before reinstalling.

---

## What we fixed on top of the upstream fork

All details with root causes and A/B test results live in
[`FIX-LOG-EN.md`](FIX-LOG-EN.md). Summary:

| Feature | Status |
| --- | --- |
| Change Device / Data Transfer (issue ID → set password → migrate → re-login) | ✅ working end-to-end |
| Login dual identity (`id` = numeric string for display, `uuid` = local-save check) | ✅ |
| `pass` field = MD5(password), `SetMigrationPassword` posts pw-only | ✅ |
| Token-keyed destination provisioning + login adoption | ✅ |
| `worldProgressCode` + `worldMapNo` served at login/userdata (chapter 20+ fix) | ✅ |
| `clear_quest` client-driven (result-screen 409 loop fix) | ✅ |
| Recruit banners (`/public_data/banners/*_en.png`) + `patchData.zip` | ✅ |
| MD5-signed responses (`digest`, salt `mist_guardians_keycode`) everywhere | ✅ |

---

## Server endpoints (iOS client)

```
GET  /healthz                       -> liveness
GET  /gd/get_current_time           -> clock sync
GET  /gd/get_server_status          -> server constants
GET  /gd/signup?otk=..&uuid=..      -> account provisioning
GET  /gd/login?otk=..&uuid=..       -> session (id numeric + uuid dual)
GET  /gd/userdata                   -> full save blob (signed)
POST /gd/start_quest                -> battle start (anti-downgrade progress)
POST /gd/clear_quest                -> battle settle (client-driven)
POST /gd/read_messages              -> inbox message reads / claims
GET/POST /gd/get_migration_id       -> issue Transfer ID
POST /gd/set_migration_pass         -> set transfer password (pass=MD5)
POST /gd/migrate_userdata           -> data transfer (auto-provisions target)
GET  /public_data/patchData.zip     -> splash patch data (200 or splash hangs)
GET  /public_data/banners/*.png     -> recruit banners (lang-suffix stripped)
GET  /resources/<Cat>/<file>.bin    -> hashed asset bundles
```

Every game response is MD5-signed:
`digest = md5(token + body + "mist_guardians_keycode")[16:32]`.

---

## Credits

- Upstream server: [anzensan/project-liminal-gate](https://github.com/anzensan/project-liminal-gate)
- Terra Battle © Mistwalker — this is a preservation project for the
  delisted game. Own the game; run the server locally.

## License

Same as the upstream fork's LICENSE.

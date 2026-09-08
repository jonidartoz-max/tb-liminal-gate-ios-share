# Terra Battle Liminal Gate — Patch Notes (September 7-8, 2026)

A summary of everything patched during this session, in chronological order.
All changes are already deployed to the local server, the Modal server
(t.mszero00.my.id), and pushed to GitHub
(jonidartoz-max/tb-liminal-gate-ios-share).

---

## 1. Event content unlock — Special Quest / Tower / Eidolon / Strikes Back

**Problem:** those menus were empty on every device; players could not enter
Bahamut, the Tower, Eidolon, or any collaboration archive.

**Root cause:** the server only advertises that content when it runs with
`--event-catalog` + `--character-catalog`, and the start scripts never passed
them.

**Fix:**
- Generated the three data files from the real 5.5.7-170 APK
  (`event-catalog.json` — 124 stages: 42 special, 58 strikes-back, 12 tower,
  12 eidolon; `character-catalog.json`; `battledata.json`) and bundled them in
  `user-data/`.
- `START-SERVER-WINDOWS.bat` now passes both catalog flags.
- **Crash-proofing:** a missing or corrupt catalog file no longer kills the
  server at boot — it prints a `[boot] WARNING` and starts with those lists
  empty. (This was reported by a second operator whose server refused to start
  after a partial update.)
- `EVENT-CATALOG.md` documents the files and how to regenerate them from a
  different APK.

Unlocks follow the original game's gating: Special/Bahamut ch2, Tower+Eidolon
ch4, Strikes Back ch6 (14 families through ch18), Leviathan ch10, Odin/FFXV
ch20, Dragon Kings ch30-32.

## 2. START/STOP batch script fixes

- `STOP-SERVER-WINDOWS.bat` had two latent bugs since the original build
  (a `tokens=` loop over one-token-per-line output, and broken nested quoting
  in its PowerShell filter) — it had never actually killed the server. Fixed
  and verified end-to-end (PID changes across restart).
- The web dashboard remains **read-only** (5s refresh) by operator decision; a
  control-button version was built and deliberately rolled back. Do not
  re-add control endpoints.

## 3. Companion Luck effects now apply server-side

**Problem:** the server rolled Luck Treasure Chest odds from the party's
stored character Luck only, while the client displayed a higher value when
Luck Companions were equipped — chest odds trailed what the player saw.

**Fix (luck_runtime.py + server_constants.py):**
- `party_team_luck` reads each member's equipped companion
  (`chrdata.buddy` -> `buddyInfo.iid` -> `bid`) and applies the same tables
  the client received: personal bonuses (`luckUpBuddies` — Unicorn +10,
  Panda +30) per member, team bonuses (`teamLuckUpBuddies` — Senala O +10,
  six companions +5) summed once.
- **Royal Ringstone** (`luckUpBoostBuddies`, bid 445) now doubles a successful
  Luck increment in `roll_luck_up_table`, still clamped at the 100.0 ceiling.
- Verified: team math (300 -> 333 with Unicorn, 300 -> 400 with Senala), gain
  doubling (1/2/3 -> 2/4/6 tenths), ceiling clamp (997 never passes 1000),
  replay-stability unchanged (byte-identical responses on retried requests),
  and graceful handling of broken/empty saves.

## 4. Save-restoration toolkit (second operator's case)

A player's server showed "New Game / Transfer Data" after a partial update —
save intact but unreachable. Built and verified:

- **SAVE-RESTORE-PACK** — the player's save rebuilt as a transfer-ready
  account (`migrated-TBRESTORE9X7`, password `restore77`, User ID `861571992`),
  plus current game data files.
- **RESTORE-NOW.bat / RESTORE-NOW.py (v2 installer)** — one-click installer
  that: finds the server folder, refuses to run while the server is up, backs
  up the old state, installs the save, **also updates `bootstrap_server.py` to
  the matching version** (a code/state mismatch produces the same
  "Server Error ErrorCode: 1" as bad credentials), syncs catalogs, and
  verifies (character count + grant) before telling the player to transfer.
- Diagnostics established along the way:
  - "Server Error ErrorCode: 1" on the transfer screen = credential mismatch
    (typo) **or** an out-of-date server binary — both reproduced and fixed.
  - The transfer password is NOT single-use: it can be reused after a success
    (verified 3 consecutive transfers). The one-time rule applies to password
    uniqueness across accounts, not to attempts.
  - Login adoption only fires for UUIDs with no existing account — a player
    who already pressed "New Game" needs the installer's direct state patch.
- Final outcome: player restored (108 characters) without needing the manual
  transfer screen.

## 5. Server hygiene

- The share's `user-data/` was cleaned of all test accounts, logs, lock files,
  and old snapshots (including a 70-account legacy state in `server_json/`)
  so fresh downloads start from a clean slate and nobody's save gets
  overwritten.
- Verified the server boots fresh from that state and the test account
  created during verification was purged afterwards.
- GitHub repo updated (`4ad030e`, `91165f7`): catalogs, hardened scripts,
  companion-luck patch, and these docs. `.gitignore` keeps player saves and
  the resource pack out of the repo.

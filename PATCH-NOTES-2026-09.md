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


## 7. Luck chest pools extended to all battle stages

**Problem:** only 30 story stages had documented chest pools (the community
scrape's own limit), so a high-Luck team earned chests almost nowhere.

**Fix (luck_pool_data.py):** the remaining 671 battle-capable stages now carry
generated pools under an explicit local policy, keeping the 30 documented rows
byte-identical:
- Coins scale with stage stamina (25 + 31/stamina) anchored to the documented
  stages' C-values, multiplied by tier (A x1, B x2, C x4, D x6, Luck 80 x8,
  Luck 100 x12), rounded to 25.
- Items are drawn only from the 36 item IDs the documented record uses,
  preferring items documented near the same chapter.
- Companions follow the documented pattern: O128/O129 appear in D/Luck 80
  from chapter 20, O455 in Luck 100 from chapter 34.
- Character rewards (M<id>) stay absent - the icon-to-ID mapping was never
  resolved. Equal-weight selection and per-tier rolls are unchanged, so
  documented-stage rolls are byte-identical to before.

Verified: 701 total pools (30 documented + 671 generated), rolls return
non-empty chests on generated stages at high Luck, documented stages unchanged.


## 8. Intermittent "network error" / phantom "stamina insufficient" — FIXED

**Problem:** every few requests the client saw a network error (HTTP 500 at the
Modal edge) despite the server being healthy. Worse, a `start_quest` that
succeeded server-side but whose response was lost to this error silently
debited stamina without updating the client — so the next attempt reported
"insufficient stamina" while the on-screen bar still showed enough. Players
burned Energy refilling stamina that wasn't actually spent.

**Root cause:** `BootstrapHandler` used `BaseHTTPRequestHandler`'s default
HTTP/1.0, which closes the connection after every response. The Modal edge
speaks HTTP/1.1 with connection reuse, so it periodically sent a request over a
connection the server had already closed — `ServerDisconnectedError`, 500,
client retry. Log pattern: bursts of 2-4 x 500 followed by 200 OK.

**Fix:** `protocol_version = "HTTP/1.1"` on the handler (all responses already
carry `Content-Length`, so the framing requirement is met). Verified with a
30-request single-connection test against production: all 200, zero
exceptions. Post-deploy logs show no further 500 bursts.


## 9. Server crash on story/Bahamut start (keyError 'luck') — FIXED

**Problem:** starting any story stage (including ch<6) or a Special Quest
crashed the server handler: the client saw a dropped connection ("network
error"), and because the earlier user session also burned stamina, later
attempts surfaced "insufficient stamina" while the client bar still showed
plenty. Metal Zone (different route) and Daily Quests worked, which is why the
pattern looked random.

**Root cause:** `party_team_luck` in luck_runtime.py (added with the companion
Luck fix) had a broken guard — `type(row.get("luck", 0)) is int` always passes
because `.get` supplies the default, so a roster row without a `luck` field
reached `row["luck"]` and raised KeyError. The user's roster rows (older save
schema) have no `luck` field on every character. Any story/event start read the
team's Luck and crashed.

**Fix:** the guard now requires the field to exist
(`"luck" in row and type(row["luck"]) is int`); rows without it simply
contribute 0, matching pre-fix behavior. Applied in both read paths.

**Verified locally:** story 6-1 start/clear, Bahamut 2000-1/2, story 5-1 and
4-1 (ch<6) all return 200; earlier crash reproduced then confirmed gone.


## 10. reTB data adoption — Luck pools 420 stages + reference masters

**Source:** reTB v1.4.18 (codeberg.org/WkmKsk/reTB), an independent
reverse-engineering project. Their data files complement ours where the
community scrape was incomplete.

**Adopted:**
- `luck_pool_data.py`: +390 stage pools imported from reTB's
  `ltc_pools_by_stage.json` (478 stages total; 20 overlap our documented 30
  and were skipped; 68 had no battledata entry - cutscene/section-0 stages).
  Total pools now **420** (30 documented byte-identical + 390 reTB-mapped).
  Mapping: reTB flat rewards -> our per-tier format; coins scaled by tier
  (x1/x2/x4/x6/x8/x12) anchored on each stage's own reTB coin value;
  items -> A/B/C; character drops -> D/Luck 100; companions -> D/Luck 80/100.
  Character drops (M<id>) now exist on 57 stages - previously impossible.
- `achievement_master_data.py` (NEW): full 99-achievement master with
  unlockType/unlockValues/presents. Reference data; server settlement
  behavior unchanged (8 ClearChapter rows).
- `item_names_data.py` (NEW): 181 item ID -> name, for readable logs.
- `companion_master_full.py` (NEW): full 497-companion master (names en/ja/
  zh_tw, rarity, max levels, EXP curves, base coins, evolve chains).
  Supersedes companion_master_data.py as reference; behavior unchanged.

**Verification:** all modules import clean; server boots; story/Bahamut smoke
routes return 200 on the fixed build. Luck pools documented 30 remain
byte-identical to the community record.


## 11. Event boss drops — Bahamut/Leviathan/Odin & 8-Bit/Kino bosses (2026-09-09)

The flat reTB `ltc_pools_by_stage.json` import lacked the boss characters.
Their `quest_consts.py` contains `LTC_SPECIAL_TIERS` — wiki-verified
per-difficulty tables — which were imported instead for all event chapters:

- Bahamut Descended: Bahamut (M148) in Luck80/Luck100 on every section,
  Bahamut Lambda (M632) on Recoded; companions Blazing Wand O8 / Inferno
  Rod O9 / Mantle Staff O12 / Daiana OII O337 / Bahamut O O275 / Bahamut OII O311
- Leviathan: M144 / M634 + Glacial/Blizzard/Comet staff line + Leviathan O O276 / OII O312
- Odin: M151 / M633 + spear line + Odin O O277 / OII O313
- 8-Bit Strikes Back (8004-8007): Orbling M899, Spinetrich M895, Golem M897,
  Hiso Alien M901 + their O/OII companions
- Kino Strikes Back Lambda (8012-8017): Lich M965, Marilith M967, Mechanic M969,
  Odin M992, Bahamut M1014, Leviathan M1016 + recruit O/OII companions
- Metal Minion O128/O129/O130 across event tiers

Sections are 0-based in reTB and 1-based here (reTB 2000-0 = our 2000-1).
Event stages with no recorded table anywhere (46) and story boss stages
(81, e.g. (2,5)) keep empty chests - no data was invented.
Total: 473 pools. Deployed to Modal, pushed as 317e657.

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


## 10. TB data adoption — Luck pools 420 stages + reference masters

**Source:** TB v1.4.18 (repository.org/WkmKsk/TB), an independent
reverse-engineering project. Their data files complement ours where the
community scrape was incomplete.

**Adopted:**
- `luck_pool_data.py`: +390 stage pools imported from TB's
  `ltc_pools_by_stage.json` (478 stages total; 20 overlap our documented 30
  and were skipped; 68 had no battledata entry - cutscene/section-0 stages).
  Total pools now **420** (30 documented byte-identical + 390 TB-mapped).
  Mapping: TB flat rewards -> our per-tier format; coins scaled by tier
  (x1/x2/x4/x6/x8/x12) anchored on each stage's own TB coin value;
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

The flat TB `ltc_pools_by_stage.json` import lacked the boss characters.
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

Sections are 0-based in TB and 1-based here (TB 2000-0 = our 2000-1).
Event stages with no recorded table anywhere (46) and story boss stages
(81, e.g. (2,5)) keep empty chests - no data was invented.
Total: 473 pools. Deployed to Modal, pushed as 317e657.


## 12. Animata Core chest amounts — 8-Bit & Kino Strikes Back (2026-09-09)

The A / B luck chests of the 8-Bit Strikes Back (8000-8007) and Kino Strikes
Back Lambda (8012-8017) quests pay Animata Core (item 181) amounts ON TOP of
the listed rewards, per the wiki "Luck Treasure Chests/Strikes Back" template
(TB quest_consts _SB_ANIMATA_{A,B}_COUNTS):
- difficulty I:   A draws 8 or 18,  B draws 20 or 60
- difficulty II & III: A draws 50 or 130, B draws 100 or 260
Each chest draws ONE of its two candidate amounts uniformly on a win; the
amount is emitted as an L<count> slot code which the client renders as
"<exchange item> x<count>" (the Animata Core for these chapters).
credit path: luck_runtime.chest_items now converts L<count> to item 181.
New module: animata_counts_data.py (candidates + chapter list + item id).


## 13. Daily Quest Luck Chests (2026-09-09)

Daily quests (chapters 6000-6012, wiki "Daily Quests/*" tables via TB
quest_consts _DAILY_LTC_TIERS) now roll Luck Treasure Chests:
- Hunting start: stages with a chest table roll a chest seeded by the request
  identity (no re-roll on retry) and stash it as active_luck_result; the
  response carries luckResult. Stages without a table (Metal Zone etc.) keep
  their own reward paths.
- Hunting clear: chest coins join the wallet expectation, item slots are
  credited on top of the audited inventory, monster recruits join the roster,
  and companion slots are authored as new level-1 rows reported via buddyInfo.
- Pools added for all 12 daily chapters at section 1: A/B upgrade items,
  C weapons + nine dragon-class monsters, D the eight Omicron-II companions,
  Luck80 quest-themed items + companions, Luck100 the companions.
Total pools: 485. Verified locally end-to-end: start returns the chest, clear
credits coins/items/companions (O345, O384 observed at Luck 100).


## 14. Luck-up overhaul: guaranteed random-gain + luck preserve + dupe bonus (2026-09-09)

**Luck reset bug (FIXED):** after a clear, character Luck snapped back to the
client's stale value because `_preserved_progress` preserved jobLevels and
skillBoost but not the server-authored `luck` field. Luck now merges with
max(held, reported) like skillBoost — a stale client can no longer roll back
a Luck gain it had not read.

**Guaranteed battle-end Luck-up (local policy):** quests costing >= 8 stamina
now guarantee exactly ONE random party member a uniform +0.1 to +0.5 Luck
(1-5 tenths), replacing the per-character stamina-weighted chance. Ringstone
still doubles it; the per-class ceiling clamps it. Capped members are skipped
so the guarantee never lands on a zero. The < 8 stamina rule is unchanged
(daily quests still grant no battle-end Luck-up, per the original design).

**Duplicate Luck bonus:** duplicate characters from Luck-chest monster drops
now raise that character's Luck by +1.0 (Joker Lambda +10.0 per TB's
override table); first copies join the roster as before. Wired into both the
hunting and event clear paths (event boss chest recruits previously were
never registered to the roster at all — fixed).


## 15. 7-stamina Luck-up + Android client (2026-09-09)

- LUCK_GAIN_MIN_STAMINA lowered 8 -> 7: seven-stamina battles (chapter 6
  onward) can now raise Luck, covering the gap where chapter-6 grinders
  never qualified under the original rule. The guarantee, uniform +0.1..+0.5
  gain, Ringstone doubling and class ceilings are unchanged.
- terrabattle-android-modal.apk (79 MB, local share folder only): the
  Android client with its IL2CPP global-metadata string literals patched
  from http://43.159.58.65:8696[/] to http://t.mszero00.my.id[/] (3 entries,
  length-corrected), repacked and signed. The Android client can now reach
  the Modal deployment like the iOS build.


## 16. Human log, /healthz clients, client feature flags (2026-09-09)

Adopted from TB 1.4.18's quality-of-life set (changelog sweep):

- **Human-readable console log** (`human_log.py`): one coloured line per
  player action — route, outcome, coins, Luck-up recipients, chest slots.
  On by default; `TB_HUMAN_LOG=0` silences it.
- **`/healthz` clients list**: per-address request counters with the last
  request age, so operators can see which devices are talking to the
  server.
- **Client feature flags** now served at login (all confirmed literals from
  the final client, TB parity): `use_sakaba_bgm_for_bar` (the Tavern plays
  its own music), `use_another_bgm_for_hunting` (hunting/metal battle track),
  `EnableLiveMusic` (options toggle), `ch1-5_stamina_one` (client applies the
  one-stamina campaign rule for chapters 1-5), `slot_show_probabirity`,
  `enableDailyBonus`.


## 17. Inbox crash fix — read_messages result shape (2026-09-09)

Opening the inbox right after collecting the daily Energy gift crashed the
client: the server answered `read_messages` with `result: true` plus the
currency at the top level, while the client's collector replaces its
in-memory currency from a dict at `result` (`energy`, `freeEnergy`, `coins`,
`readlist`, `itemList` — TB parity, confirmed by the retired service's
response model). The daily-gift fast path and the catalog read path now both
ship the nested shape with the full `itemList` inside `result`.


## 18. Drop Guide document (2026-09-09)

`DROP-GUIDE.md`: a complete farming index generated from the live luck-chest
pools. For every Job Change and every Recode recipe it lists the coins and
materials with the stages (and chest tiers) that carry each item; plus
item/companion/character source indexes (80 items, 163 companions, 92
characters). Items that never appear in a Luck chest are marked as battle
drops.

# Terra Battle Liminal Gate — Fix Log (English)

Date: 2026-09-06. All fixes live in
`project-liminal-gate/liminal_gate/bootstrap_server.py` — the Modal deployment
builds from this exact folder (single source of truth).

## 1. Change Device / Data Transfer — WORKING END-TO-END

Player flow:

**Old device (holds the save):**
1. Open Terra Battle, play normally once (so the save uploads).
2. Options > Change Device > OK > enter a new password (8–16 alphanumeric) > OK.
3. The "Settings for game data transfer are complete" screen shows
   **User ID (9-digit number)** + **Transfer ID (12 chars)** + your password.
4. A Transfer ID + password is **single-use**.

**New device:**
5. Install Terra Battle (fresh) → do NOT start a new game →
   **Transfer Game Data** → enter the three values → OK.
6. Success notification → automatic re-login → the save loads.

### Why it failed before (fix table)

| Symptom | Root cause | Fix |
| --- | --- | --- |
| "Invalid response" always | responses were not MD5-signed | every migration route uses `_signed()` (salt `mist_guardians_keycode`, offset [16:32]) |
| "server error code 1" on OK | server waited for a password before issuing a Transfer ID | `get_migration_id_locked` auto-issues a 12-char ID (alphabet without 0/O/1/l/I) as a pending grant |
| Instant crash opening the transfer screen | `POST /gd/get_migration_id` missing from `do_POST` (501) + unsigned response | added the POST handler + signed |
| Instant crash rendering User Info | `inquiryID` nil (login + userdata never sent it) | login response + `/gd/userdata` inject `inquiryID`/`inquiryId` = sha256(uuid)[:11] |
| Crash parsing the migrate response | `userID` as a JSON string (client expects a number), minimal `{"success":true}` (nil fields), unknown keys (`token`, string `userID`) = strict-walker kill | migrate response is EXACTLY `{"success":true,"sourceAccount":"<uuid>","errorCode":0,"digest":...}` — add/remove nothing |
| Network error submitting the password | client POSTs `pass`=MD5(password) without `migrationID`; the handler demanded other field names | accept the `pass` field, apply it to the latest grant when `migrationID` is empty |
| Transfer succeeds → network error | the new device re-logins with its own local uuid → 401 (the provisioned account had a synthetic name) | `bind_login_token` adoption: rename the latest `migrated-*` account to the logging-in uuid |
| Self-copy migration (`same_account`) | both devices on one Wi-Fi share a public IP via Cloudflare → host binding resolved to the SOURCE account | provision by token, not by IP |
| Copied save comes back empty | the new client uploaded its empty local save (dirty data) over the copy | correct order: log in normally on the old device BEFORE transferring |

### Client protocol facts (do not fight these)

- Every game response MUST be MD5-signed: `digest = md5(token+body+"mist_guardians_keycode")[16:32]`. Unsigned = "Invalid response" dialog even at HTTP 200.
- The client response walker is STRICT: unknown keys / wrong JSON types = instant kill (EXC_BREAKPOINT, often without an .ips file).
- `SetMigrationPassword` POSTs `pass` = uppercase MD5(password), WITHOUT a migrationID → the server applies it to the latest grant.
- Login response: `id` = numeric STRING, 9 digits (display; the transfer form opens a numeric keypad), `uuid` = the device's own uuid (local identity check). Both required.
- `MigrateUserdata` client signature: `(string userID, string migrationID, string pw)` — POST body sends `userID`, `migrationID`, `pass`.
- The inbox message DTO (dump.cs `Message`) is the client's POST-PARSE representation — NOT the wire schema. The wire format is the legacy one (`daysLast`, `gifts`, `item:[{id,num}]`, `title`, `messages:{default,ja,en}`, `energy`).

### Debugging toolkit

- `.ips` crash files: parse line 2 as JSON; offset = `usedImages[0].base + frames[].imageOffset`. The `0x186c8→0x12358c→…` stack is the generic unhandled-exception path (not specific). `EXC_CRASH 0x8BADF00D` = a 5-second main-thread hang (watchdog). A crash with NO .ips = death while parsing a response.
- Il2CppDumper: `Il2CppDumper.exe guardians_bin global-metadata.dat` with config `ForceIl2CppVersion=true, ForceVersion=24.1, RequireAnyKey=false` → `dump.cs` (the `AppServerUtil` signatures are the field-name source of truth), `stringliteral.json` (field names + addresses).
- Server event log: `modal run eventlog*.py` in `tb-modal\` (reads `events.jsonl` from the `tb-state` volume) — method/path/status only; bodies need explicit handler logging.

## 2. Chapter 20+ "network error" — FIXED

Root cause: the client gates section unlocks on `worldProgressCode[str(world)]` —
a per-world progression dict. A missing world entry reads as "everything
locked". Our server never served `worldProgressCode` at all, so the first main
world chapter where the client stops falling back to the top-level
`progressCode` (chapter 20) hit the locked gate.

Fix: the login response and `GET /gd/userdata` now serve
`worldProgressCode = {"0": <main progress>}` (side-world entries preserved) and
`worldMapNo: 0` at login.

## 3. Result-screen "network error" after finishing a battle — FIXED

`POST /gd/clear_quest` returned 409 in a loop when the client sent a clear
without a matching server-side start (battle resumed from a save, result-screen
retry). Fixed by making the clear path client-driven:

- The phase / active-stage gates are only enforced when a start is pending.
- `progressCode` merges anti-downgrade: `max(client, server)`.
- After a successful clear the phase returns to `free_roam` and the wallet
  settles normally.

## 4. Inbox message open crash — open item

The energy mints server-side on claim (login works), but OPENING the message in
the inbox still crashes without an .ips. Leading theory: the `messages.default`
text may need to be a localization KEY rather than raw text (compare how the
chapter milestone presents fill `messages` in `message_catalog`). Next forensic
step: instrument the IPA to capture the real exception.

## 5. Checklist before changing any server response

1. Wire schema ≠ internal DTO. Classes in `dump.cs` are post-parse client
   state, not protocol. Match the wire format that already works.
2. A new field risks a strict-walker crash → one field per deploy, test the
   real client immediately (New Game first, then the feature).
3. JSON types: a client string field gets a string; a numeric field gets a
   number. The reverse = crash.
4. Sign with `_signed()`, never `_json()`.
5. Resetting server state: `modal app stop` FIRST → clean the Gist → deploy
   (a live container pushes old state back every 60 s).
6. Per-second server log: `modal run eventlog4.py` — the last request before a
   crash shows which step the client died on.

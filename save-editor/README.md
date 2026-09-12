# Save Data Editor — Terra Battle (Liminal Gate)

An offline, single-file HTML editor for the server's save file
(`bootstrap-state.json`). Add or remove characters, manage which devices may
open the save, and export a save that is **guaranteed not to crash the game**.

No install, no internet. Everything runs in your browser.

---

## 1. Quick start

1. Open `OPEN-EDITOR.bat` (or double-click `SAVE-EDITOR.html`).
2. **Open Save File…** → pick your server's `bootstrap-state.json`.
   (Or use **Paste JSON** to paste the file's contents from the clipboard.)
   **Tip:** if you just need a fresh working save, pick
   `TEMPLATE-bootstrap-state.json` instead and go straight to step 4 — every
   array is already padded and every field already typed, so all that is left
   is choosing characters.
   If the loaded save never finished the tutorial, the editor marks the edited
   account as tutorial-complete on **Save** (section 4 below explains why).
3. **Pick the account** in the account box — a save file can hold several.
4. Select characters on the left → **→ ADD TO SAVE**.
   (Ctrl / Shift + click selects more than one.)
5. Remove characters: select them on the right → **← REMOVE FROM SAVE**.
6. Click **Check & Fix** and read the report — you want the green check.
7. **Save (download)** → produces `<name>-EDITED.json`.
   (Or **Copy JSON** to put the result straight on the clipboard.)
8. Rename it to `bootstrap-state.json`, put it in your server folder
   (**stop the server first**), and keep a backup of the old file.

---

## 2. How it works

The save file (`bootstrap-state.json`) is a small JSON database:

```jsonc
{
  "active_account_id": "624CFDD7…",        // which account the server treats as current
  "accounts": {
    "624CFDD7…": {                         // <-- the key IS the device UUID
      "userdata": {
        "chrdata":    [ … ],               // your characters
        "teamMembers":[ … ],               // your squads (fixed length!)
        "itemList":   [ … ], "summonList": [ … ],
        "coins": 218, "freeEnergy": 50,
        "progressCode": 16777345,          // story position
        "lastupdate": 1.0, …               // several fields are DOUBLES
      },
      "tutorial_phase": "free_roam",
      "migration_grants": { … }            // one-time transfer keys
    }
  },
  "account_aliases": { "OTHER-DEVICE-UUID": "624CFDD7…" },  // device links
  "tokens": { … }, "client_hosts": { … }
}
```

The editor only touches what you ask it to: it reads `accounts[<picked>].userdata.chrdata`,
lets you add/remove entries, and writes the whole document back — after passing it
through the sanitizer (section 4) and the double-preserving encoder (section 5).

The server then reads the same file and serves it to the game on login.

---

## 3. Device access (the UUID problem)

**The game logs in by device UUID.** The server looks up `uuid` and finds the
account whose key (or alias) equals it:

```
login?uuid=<DEVICE-UUID>   →   account_aliases[uuid]  or  accounts[uuid]
```

So a save whose account key is *not* your device UUID will not open on your
device (401, or a blank account). The **Device Access** panel fixes this
without hand-editing JSON:

- It lists every UUID that can open the account you are editing.
  - the account's own key is tagged **account id** (cannot be removed)
  - linked devices have an **unlink** button
- **+ Link device** — type another device's UUID; that device now opens the
  same save. This is how one save is shared across several phones.
- **Use save on this UUID only** (takeover) — rename the account to that UUID so
  the device loads the save directly. Existing aliases, tokens and the active
  pointer are repointed automatically.

> A device that has **never signed up** is unknown to the server — it must open
> the game and sign up once, then you can link it here. Until then its login is 401.

---

## 4. Check & Fix — why it matters

A save with the wrong shape makes the game **crash instantly on load**
(EXC_BREAKPOINT / SIGTRAP). This is not theoretical: every rule below maps to a
crash we actually hit.

| Normalised | Why |
|---|---|
| `teamMembers` → 90 slots | the client indexes 9 teams × 10; a short array reads past its end |
| `summonList` → 16 slots | summon/companion slots; empty crashes |
| `teamMembers_VS`, `teamBuddies_VS` → 18 | VS squads |
| `itemList` → 181 slots | inventory |
| `lastupdate`, `refillStartTime`, `date`, `jobSlots`, `jobLevels`, `questClearDate` → **decimal** | the client unboxes these as `double`; a whole number becomes Int64 → InvalidCastException |
| `chrdata` | sorted ascending by id, duplicates dropped, level 0 → 10 |
| missing required fields | filled with the same defaults a working account has |
| `chapter` / `section` | recomputed from `progressCode` (never hand-written) |
| `valuables` | kept in sync with `coins` / `freeEnergy` |

**Check & Fix** runs the sanitizer twice and shows what changed. If the second
pass is clean, the fixes are stable and the save is safe to ship.

### Account-level fields (not just the roster)

The server also validates a set of **per-account** fields when it loads the file
— `tutorial_phase`, `tutorial_requests`, `initial_userdata_served`,
`active_generic_story`, `active_hunt`, `active_world_map_special`,
`claimed_achievements`, `achievement_requests`, `messages`,
`chapter_milestones_issued`, `message_requests`. A missing or wrong-typed one
makes the **whole save fail to load** (`invalid tutorial state`) — the server
refuses to start.

The sanitizer therefore completes those too, with the exact types the server
checks, and repairs two shapes that bite in practice:

- `messages: []` → `{}` (it must be an object, not a list)
- `achievement_requests` missing → added; `claimed_achievements` cleaned to
  sorted unique positive ints; `chapter_milestones_issued` to sorted unique strings

### Progress: any point in the game

Editing works at **any** story position, not only at the end of the tutorial:

| Save state | Editor result |
|---|---|
mid-tutorial (`chapter1_3_active`) | `tutorial_phase` → `free_roam` (a roster means the opening is done; the server refuses mutations while an account sits on a tutorial phase) |
early free-roam (`progressCode` 2-1) | kept as-is |
far along (chapter 25, `worldProgressCode` set) | kept as-is |

`progressCode`, `worldMapNo` and `worldProgressCode` are **never invented** —
they pass through untouched, and `chapter`/`section` are only *derived* from
`progressCode` for display.

---

## 5. The double-preserving encoder (important)

JavaScript has **one** number type, so `JSON.stringify(1.0)` writes `1`. The
game's parser then reads an integer where it expects a `double` and throws — the
crash described above.

The editor therefore does **not** use `JSON.stringify`. It ships its own
`jsonEncode()` that forces a decimal point on every field the client unboxes as
a double (and inside the per-job arrays and `questClearDate`). Both **Save
(download)** and **Copy JSON** go through it, so the output is always typed
correctly.

---

## 6. Notes & rules

- New characters start at **Job 1, Level 10** — the same as a Pact draw.
- `jobID` is the **job index** (0/1/2), not a job id.
- Always keep a backup of the save before editing.
- The editor changes character data and device links; it does not touch
  account credentials beyond that.
- `__aid` (an internal marker the editor adds while working) is stripped from
  every export.

# Save Data Editor + Tutorial Template

Two tools for editing a Terra Battle (Liminal Gate) save file
(`bootstrap-state.json`). **No install, no Python needed for the editor** —
it runs in any browser.

---

## 1. SAVE-EDITOR.html — edit your save

**How to open**

- Double-click `OPEN-EDITOR.bat`, **or**
- Just open `SAVE-EDITOR.html` in any browser (Chrome / Edge / Brave / Firefox)

**How to use**

1. Click **Open Save File…** and pick your `bootstrap-state.json`
2. Left panel = **All Characters** (346 units). Type in the search box to filter
   by name or ID. Ctrl/Shift+click to select several.
3. Click **→ ADD TO SAVE**. New entries are created exactly the way the game
   server creates them from a Pact draw: **Job 1, Level 10**.
4. Right panel = **Characters In Save**. Select entries and click
   **← REMOVE FROM SAVE** to delete.
5. Click **Save (download)**. You get `<name>-EDITED.json` — rename it back to
   `bootstrap-state.json` and put it in your server folder.

Rarity badges are the game's real 7 classes: **D, C, B, A, S, SS, Z** (with a
different colour each).

> Always keep a backup copy of your save file before editing.

---

## 2. Load Tutorial Template — skip the tutorial

The button **Load Tutorial Template** in the editor fills the save with a
**tutorial-complete** state, so the game starts in free-roam mode with the
chapter-1 story already finished.

What you get:

| | |
|---|---|
| Mode | free roam (tutorial done) |
| Story | Chapter 1 complete, `progressCode` 16777345 |
| Characters | 4 — the starter, Grace, the Knight, the Warrior |
| Coins | 218 |
| Free Energy | 50 |

How to use it:

1. Open your save file in the editor
2. Click **Load Tutorial Template** (confirm the prompt)
3. Click **Save (download)**, rename to `bootstrap-state.json`, drop it in your
   server folder
4. Stop the server, replace the file, start it again

---

## Files

| File | What it is |
|---|---|
| `SAVE-EDITOR.html` | the editor (open in a browser) |
| `OPEN-EDITOR.bat` | double-click launcher for the editor |
| `TEMPLATE-bootstrap-state.json` | a ready-made tutorial-complete save |
| `template-tutorial-complete.json` | the template data in a readable form |
| `chr_names.json` | character names (source data) |

---

## Notes for the technical user

- The template and the ready-made save were produced by **replaying the real
  server tutorial state machine** (all 22 transitions from
  `profiles/legacy-client-bootstrap.json`), not hand-written — so every value
  matches what the game itself would have produced.
- `chrdata` rows use the server's own field shape:
  `{id, buddy, date, jobSlots, jobLevels, jobID, flags, skillBoost}`.
  `jobLevels` is packed as `(experience << 12) | level`, and `jobID` is the
  **job index** (0–2), not a job id.
- Rows are kept sorted ascending by `id` — the client indexes characters by
  array position, so an unsorted array makes clicks open the wrong character.
- `TEMPLATE-bootstrap-state.json` uses the account id `migrated-template`.
  On a brand-new device the server adopts that account automatically at first
  login (its migration-adoption path), so the new device inherits the finished
  save. When reusing a save that already has an account, use the editor's
  **Load Tutorial Template** button instead.

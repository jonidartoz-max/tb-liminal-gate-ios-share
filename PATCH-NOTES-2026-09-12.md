# PATCH NOTES — 2026-09-12

What changed in this update. Copy the contents of this zip over your
existing TB-SHARE folder (say yes to overwrite), then start the server as
usual.

---

## FIXED: Companion drops from story stages now reach your inventory

**Symptom:** a Companion dropped in a story/event stage, showed up on the
reward screen, but never appeared in the Companion box.

**Cause:** the server only mints a dropped Companion when it is given a
**story-outcome catalog** (`--story-outcome-catalog`). Without it the server
writes no `buddyInfo` at all on a story clear, so the drop the client rolled
was discarded. Hunting / Metal Zone drops were unaffected.

**Fix:** this update ships `user-data/story-outcomes.json` and adds
`--story-outcome-catalog` to both launchers. No action needed beyond copying
the update over.

### Also fixed: Luck-chest Companion in story stages

A **Luck chest** that rolled a Companion (a chest slot shown as `O<id>`) was
minted for item and monster slots but **not** for Companion slots, so a chest
Companion was lost the same way. Story clears now mint chest Companions too,
matching what Hunting already did.

### Also fixed: a battle drop and a chest Companion in the same clear

When a single clear both reported a dropped Companion **and** had a Companion
in its Luck chest, only one of the two survived. Both are kept now.

Coverage of the generated catalog:

- 780 stage rules
- **205 ordinary story stages can now drop a Companion**
- 574 stage/Companion pairs, 173 distinct Companions
- stages without drop evidence stay "unevidenced" rather than refusing drops

---

## New: Save Data Editor (no install needed)

`save-editor/SAVE-EDITOR.html` — open it in any browser, or double-click
`save-editor/OPEN-EDITOR.bat`.

- Add / remove characters, search all 346 by name or ID
- Correct rarity badges (D, C, B, A, S, SS, Z)
- New characters arrive like a Pact draw: Job 1, Level 10
- Automatic backup name every save

## New: Tutorial-complete template

Open your save, click **Load Tutorial Template**, then **Save (download)**.
Rename the file to `bootstrap-state.json` and use it.

Or, on a brand-new device, use `save-editor/TEMPLATE-bootstrap-state.json`
directly as your `bootstrap-state.json`.

Result: free roam, Chapter 1 finished, 4 characters (starter, Grace, Knight,
Warrior), 218 Coins, 50 Free Energy.

## In-game Help pages

The **Support** and **Schedule** pages inside the game now show the
**Drop Atlas** (best farming spots), rendered in-game instead of opening a
browser. The **Help** button is back to its original behaviour.

## In-game news screen

"What's New" (shown right after login) now shows the Drop Atlas as plain
text instead of failing to load.

---

## Files in this update

| Path | What it is |
|---|---|
| `user-data/story-outcomes.json` | **new** — Companion drop ceilings per stage |
| `START-SERVER-WINDOWS.bat`, `START-SERVER-LINUX-MAC.sh` | launchers, now pass the catalog |
| `save-editor/` | the editor, the template and its guide |
| `project-liminal-gate/liminal_gate/bootstrap_server.py` | server (news + help routes) |
| `project-liminal-gate/liminal_gate/server_constants.py` | in-game URLs |
| `project-liminal-gate/liminal_gate/drop_atlas_text.py` | Drop Atlas text |
| `user-data/public_data/help/` | the Drop Atlas web page |
| `PATCH-NOTES-2026-09.md` | the previous patch notes |

# PATCH NOTES — 2026-09-12

What changed in this update. Copy the contents of this zip over your
existing TB-SHARE folder (say yes to overwrite), then start the server as
usual.

---

## New: Save Data Editor (no install needed)

`save-editor/SAVE-EDITOR.html` — open it in any browser, or double-click
`save-editor/OPEN-EDITOR.bat`.

- **Add / remove characters** in your save file
- **Search** all 346 characters by name or ID
- Correct **rarity** badges (D, C, B, A, S, SS, Z)
- New characters arrive exactly like a Pact draw: Job 1, Level 10
- Automatic backup name every time you save

Read `save-editor/README.md` for the full guide.

## New: Tutorial-complete template

Tired of replaying the tutorial? Two ways to skip it:

1. **In the editor:** open your save, click **Load Tutorial Template**, then
   **Save (download)**. Rename the downloaded file to
   `bootstrap-state.json` and use it.
2. **For a brand-new device:** use
   `save-editor/TEMPLATE-bootstrap-state.json` directly as your
   `bootstrap-state.json`. A new device adopts it automatically at first
   login.

You end up in free roam with Chapter 1 finished, 4 characters
(the starter, Grace, the Knight, the Warrior), 218 Coins and 50 Free Energy.

## In-game Help pages

The **Support** and **Schedule** pages inside the game now show the
**Drop Atlas** (best farming spots), rendered in-game instead of opening a
browser. The **Help** button itself is back to its original behaviour.

## Earlier change in this cycle

The in-game news screen ("What's New", shown right after login) now shows
the Drop Atlas as plain text instead of failing to load.

---

## Files in this update

| Path | What it is |
|---|---|
| `save-editor/` | the editor, the template and its guide (new) |
| `project-liminal-gate/liminal_gate/bootstrap_server.py` | server (news + help routes) |
| `project-liminal-gate/liminal_gate/server_constants.py` | in-game URLs |
| `project-liminal-gate/liminal_gate/drop_atlas_text.py` | Drop Atlas text (new) |
| `user-data/public_data/help/` | the Drop Atlas web page (new) |
| `PATCH-NOTES-2026-09.md`, `HOLIDAY-EVENTS.md`, `EVENT-CATALOG.md`, `FIX-LOG.md` | documentation |

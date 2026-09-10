# Holiday Events — Trading Post

Update: 2026-09-10

## What this adds

The **Trading Post now offers 28 limited "O" companions YEAR-ROUND** — no more
waiting for seasonal windows:

- Offer IDs 1000–1027 (1000–1013 = the Christmas 2016 set, 1014–1027 = the
  New Year 2017 set)
- Prices 2000–3000 Animata Core (item 181), stock 1 per companion per account
- List and prices are the game's own historical Christmas 2016 / New Year 2017
  Trading Post trades (community wiki), converted 1:1 to Animata Core
- The client's countdown shows 01/01 of the next year
- Stock and the gift mail reset every 1 Jan (UTC), so the cycle repeats yearly

A one-shot **5 Energy gift mail** lands in the inbox with the event.

## Controls (optional env vars)

| `LIMINAL_HOLIDAY_ALWAYS` | Behaviour |
|---|---|
| `all` (default / unset) | all 28 companions, year-round |
| `christmas` | Christmas set only (14), year-round |
| `new_year` | New Year set only (14), year-round |
| `off` / `0` / `false` / `no` | calendar mode: trades appear only 23–25 Dec and 1–3 Jan |

Testing hook: `LIMINAL_FORCE_HOLIDAY=christmas|new_year` forces a 3-day window
starting today (overrides everything else).

In calendar mode the windows REPLACE the weekly rotation while open (the
historical behaviour of the retired service), the countdown shows the window's
end date, and per-player stock is keyed per edition — a Friday reset falling
inside a window does not restock it.

## Files

- `project-liminal-gate/liminal_gate/holiday_events_data.py` — event data + window logic (new)
- `project-liminal-gate/liminal_gate/bootstrap_server.py` — three touch points:
  1. `_restock_exchange_week()` → serves the event set while a window is open,
     per-edition stock (`holiday_stock:<event>:<year>`)
  2. `current_exchange()` → the countdown `endDate` follows the open window
  3. `_synchronize_holiday_gift_message()` (new) → the once-per-edition inbox gift

## Verified (local, 2026-09-10)

- Compiles; server boots with `--trading-post`.
- Year-round default: 28 offers, IDs 1000–1027, endDate 01/01/2027,
  wire format identical to the weekly rotation.
- Buying IDs 1000 / 1014 / 1027 mints buddy 42 / 278 / 356 at level 1, charges
  the right Animata Core count, stock 1→0.
- Second buy of the same companion: errorCode 6 (out of stock) — correct.
- Weekly rotation (IDs 1–126) is fully replaced while the event set is active.
- The daily Energy gift keeps working alongside it.
- Mode `off` restores calendar-only behaviour.

## Bonus fix in the same update: inbox claim crash

Claiming the daily inbox gift credited Energy server-side but crashed the
client instantly. Root cause (found by diffing a reference server): the claim
callback reads `result.itemList` unguarded — the FULL positional item array
(181 slots) must ride INSIDE `result`, together with `energy`, `freeEnergy`,
`coins`, `readlist`, and the standard envelope (`success`, `errorCode`,
`server_time`). `delete_messages` must carry `deletelist` the same way.

All three paths (daily special-case, generic claim, delete) now ship the exact
verified shape. Verified locally: daily +10 and event +5 claims render the
reward popup correctly-shaped, retries are idempotent (no double credit).

## Rollback

- Year-round mode off: set `LIMINAL_HOLIDAY_ALWAYS=off` (no code change).
- Full revert: remove `holiday_events_data.py` and revert the three touch
  points in `bootstrap_server.py`. No state migration is involved: the new
  per-account keys (`holiday_stock:*`) appear on their own and stale ones are
  retired automatically.

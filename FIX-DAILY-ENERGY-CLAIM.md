# Fix Runbook — Daily Energy Claim (10 Energy Gift)

## Bug
**Symptom:** the client crashed when claiming the daily energy gift in the
inbox (older builds), or the gift never appeared.

**Root cause (3 layers):**
1. `create_account` (signup) never issued the gift — it was only issued on
   login through `_synchronize_daily_gift_messages` inside `login_messages`.
2. The share was launched without `--message-catalog`, so the claim path
   (`read_messages`) hit `catalog is None` and returned 501/409 instead of
   minting the energy.
3. The message payload used the wrong field layout for the client.

## Fixes (all in `project-liminal-gate/liminal_gate/bootstrap_server.py`)
1. `_synchronize_daily_gift_messages(account, now)` is also called at signup so
   the gift exists from the first login.
2. `read_messages` special-cases `daily:energy:gift`: any catalog state (bundled
   or empty) can mint the 10 energy, marks the message read, and returns the
   updated wallet — idempotent, no double mint (a `daily_gift_issued` sentinel
   keyed by UTC day prevents re-claims).
3. The message wire payload follows the legacy wire schema
   (`daysLast`, `messages:{default,ja,en}`, `energy`), see FIX-LOG-EN.md for
   the wire-vs-DTO lesson.

## Current status
The energy mints server-side on claim — verified
(`freeEnergy` 50 → 60, `readlist: ["daily:energy:gift"]`).
Opening the message in the inbox UI can still crash (see FIX-LOG-EN.md §4);
the reward itself is not affected.

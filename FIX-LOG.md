
# 2026-09-08 — Companion Luck effects now apply server-side

Previously the server rolled Luck Treasure Chest odds from the party's stored
character Luck only, while the client displayed a higher value when Luck
Companions (Unicorn +10, Panda +30, Senala O +10 team, six +5 team) were
equipped. Chest odds therefore trailed what the player saw on screen.

Now `party_team_luck` reads each member's equipped companion
(`chrdata.buddy` -> `buddyInfo.iid` -> `bid`) and applies the same tables the
client received in server constants: personal bonuses (`luckUpBuddies`) per
member, team bonuses (`teamLuckUpBuddies`) summed once — the exact math
`luck_data.team_luck` already exposed. Royal Ringstone (`luckUpBoostBuddies`,
bid 445) now doubles a successful Luck increment in `roll_luck_up_table`,
clamped by the 100.0 ceiling as before.

Replay stability, the 8-stamina gate, and all caps are unchanged. Verified:
team luck math (300 -> 333 with Unicorn, 300 -> 400 with Senala), gain
doubling (1/2/3 -> 2/4/6 tenths), ceiling clamp (luck 997 never gains past
1000), and byte-identical responses on retried requests.

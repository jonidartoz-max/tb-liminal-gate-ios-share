"""Author a battle's six chest slots and its Luck growth, replay-stably.

The retired service decided both at battle start and sent them on
`start_quest`; the client rendered the chests at the results screen and folded
their contents into the balances it reports back at clear. Nothing about either
decision is recoverable from the APK, so this module is where the sourced
anchors in `luck_data` and the documented pools in `luck_pool_data` become an
actual roll.

**Replay is handled by construction, not by storage.** Both rolls are seeded
from the request identity, so a client retrying the same start -- under the same
request ID or a fresh one -- receives byte-identical chests rather than a
re-roll. That matters more here than elsewhere: a re-roll on retry would be a
reward duplicator.

One number in this module is invented, and it is isolated here rather than
spread through the logic: the chance a character gains Luck at a given stamina
cost. No source states it. What the sources do fix are its boundaries -- the
gate below eight stamina is Mistwalker's own, and the 0.1--0.3 magnitude is the
community record's -- so only the slope between them is chosen.
"""

from __future__ import annotations

import hashlib
import random

from liminal_gate.luck_data import (
    CHEST_TIERS,
    LUCK_GAIN_TENTHS,
    LUCK_TENTHS_MAX,
    gains_luck,
    team_luck,
)
from liminal_gate.luck_pool_data import pool_for
from liminal_gate.server_constants import (
    BUDDY_LUCK_UP,
    BUDDY_LUCK_UP_BOOST,
    BUDDY_TEAM_LUCK_UP,
)

#: The six wire slots, empty-string for a slot that did not appear. The client
#: reads a fixed-length array and treats an empty entry as no chest.
EMPTY_SLOT = ""

#: **Local policy, and the only invented number in the Luck runtime.** The
#: chance one character's Luck rises after a qualifying battle, as a fraction of
#: the stage's stamina cost. The record says the chance grows with stamina and
#: never states it; this makes a 40-stamina stage a 40% chance per member. The
#: private reference server used this same base and then multiplied it by 1.5
#: while also dropping the eight-stamina gate, which is why its curve was not
#: reused.
LUCK_GAIN_CHANCE_PER_STAMINA = 0.01


def _seeded(*parts: object) -> random.Random:
    """A generator fixed by the request identity, so retries never re-roll."""
    material = "\x1f".join(str(part) for part in parts).encode("utf-8")
    return random.Random(hashlib.sha256(material).hexdigest())


def party_team_luck(userdata: dict) -> int:
    """Read the account's current team Luck in tenths from its own save.

    Companion Luck effects ARE applied, from the account's own save plus the
    same constant tables the client received in server constants: each party
    member's equipped Companion (``chrdata.buddy`` -> ``buddyInfo.iid`` ->
    ``bid``) contributes its personal bonus from ``luckUpBuddies``, and the
    equipped set's team bonuses from ``teamLuckUpBuddies`` are summed once.
    This mirrors the client's display math so the chest odds the server rolls
    match the Luck value the player sees on screen.
    """
    roster = userdata.get("chrdata")
    party = userdata.get("teamMembers")
    if not isinstance(roster, list) or not isinstance(party, list):
        return 0
    luck_by_id: dict[int, int] = {}
    buddy_iid_by_id: dict[int, int] = {}
    for row in roster:
        if isinstance(row, dict) and type(row.get("id")) is int:
            if type(row.get("luck", 0)) is int:
                luck_by_id[row["id"]] = row["luck"]
            if type(row.get("buddy", 0)) is int and row.get("buddy", 0):
                buddy_iid_by_id[row["id"]] = row["buddy"]
    personal_bonuses: list[int] = []
    team_bonus = 0
    if buddy_iid_by_id:
        bid_by_iid: dict[int, int] = {}
        for companion in userdata.get("buddyInfo", {}).get("list", []) or []:
            if isinstance(companion, dict) and type(companion.get("iid")) is int:
                bid_by_iid[companion["iid"]] = companion.get("bid", 0)
        for member in party[:6]:
            if not member:
                continue
            bid = bid_by_iid.get(buddy_iid_by_id.get(member, 0), 0)
            personal_bonuses.append(BUDDY_LUCK_UP.get(str(bid), 0))
            team_bonus += BUDDY_TEAM_LUCK_UP.get(str(bid), 0)
    members = tuple(
        luck_by_id.get(member, 0) for member in party[:6] if member
    )
    return team_luck(members, tuple(personal_bonuses), team_bonus)


def roll_luck_result(
    chapter: int, section: int, team_luck_tenths: int, *seed: object,
) -> list[str]:
    """Return the six chest slots for one battle, in the client's order.

    A stage with no documented pool for a tier yields an empty slot rather than
    an invented reward, so most of the game returns six empty slots. That is a
    limit of the record, not a claim that those stages had no chests.
    """
    generator = _seeded("luckResult", chapter, section, team_luck_tenths, *seed)
    slots: list[str] = []
    for tier in CHEST_TIERS:
        pool = pool_for(chapter, section, tier.name)
        chance = tier.probability(team_luck_tenths)
        # Draw for every tier whether or not it can pay out, so that adding a
        # pool later cannot shift the rolls of the tiers beside it.
        appeared = generator.random() < chance
        choice = generator.randrange(len(pool)) if pool else -1
        slots.append(pool[choice] if appeared and pool else EMPTY_SLOT)
    return slots


def roll_luck_up_table(
    userdata: dict, stamina: int, *seed: object,
) -> list[int]:
    """Return each party slot's Luck gain in tenths, zero where it did not rise.

    A quest costing less than eight stamina never raises Luck, which is the
    developer's own rule and excludes every Daily Quest, all of which are free.
    A character at its ceiling stays there, and an empty slot stays zero.
    Royal Ringstone (a companion's equipped buddy id in
    ``BUDDY_LUCK_UP_BOOST``) doubles a successful increment, its documented
    effect, applied before the ceiling clamp.
    """
    party = userdata.get("teamMembers")
    if not isinstance(party, list):
        return [0] * 6
    members = list(party[:6]) + [0] * max(0, 6 - len(party[:6]))
    if not gains_luck(stamina):
        return [0] * 6
    roster = userdata.get("chrdata")
    current: dict[int, int] = {}
    buddy_iid_by_id: dict[int, int] = {}
    if isinstance(roster, list):
        for row in roster:
            if isinstance(row, dict) and type(row.get("id")) is int:
                if type(row.get("luck", 0)) is int:
                    current[row["id"]] = row["luck"]
                if type(row.get("buddy", 0)) is int and row.get("buddy", 0):
                    buddy_iid_by_id[row["id"]] = row["buddy"]
    bid_by_iid: dict[int, int] = {}
    buddy_info = userdata.get("buddyInfo")
    if isinstance(buddy_info, dict):
        for companion in buddy_info.get("list", []) or []:
            if isinstance(companion, dict) and type(companion.get("iid")) is int:
                bid_by_iid[companion["iid"]] = companion.get("bid", 0)
    generator = _seeded("luckUpTable", stamina, *seed)
    chance = min(1.0, stamina * LUCK_GAIN_CHANCE_PER_STAMINA)
    table: list[int] = []
    for member in members:
        # Draw per slot regardless, so an empty or capped slot cannot shift the
        # draws of the slots after it.
        rolled = generator.random() < chance
        gain = generator.choice(LUCK_GAIN_TENTHS)
        if not member or not rolled:
            table.append(0)
            continue
        bid = bid_by_iid.get(buddy_iid_by_id.get(member, 0), 0)
        multiplier = BUDDY_LUCK_UP_BOOST.get(str(bid), 1)
        headroom = max(0, LUCK_TENTHS_MAX - current.get(member, 0))
        table.append(min(gain * multiplier, headroom))
    return table


def apply_luck_up_table(userdata: dict, table: list[int]) -> None:
    """Commit a rolled Luck gain to the roster, capped at the client's ceiling."""
    roster = userdata.get("chrdata")
    party = userdata.get("teamMembers")
    if not isinstance(roster, list) or not isinstance(party, list):
        return
    gains = {
        member: gain
        for member, gain in zip(party[:6], table)
        if member and gain
    }
    for row in roster:
        if isinstance(row, dict) and row.get("id") in gains:
            row["luck"] = min(
                LUCK_TENTHS_MAX, int(row.get("luck", 0)) + gains[row["id"]],
            )


def chest_coins(slots: list[str]) -> int:
    """Total Coins the authored chests award, which the client folds into its
    reported balance at clear and the settlement must therefore expect."""
    return sum(int(slot[1:]) for slot in slots if slot.startswith("C") and slot[1:].isdigit())


def chest_items(slots: list[str]) -> dict[int, int]:
    """Item IDs and counts the authored chests award, for the same reason."""
    items: dict[int, int] = {}
    for slot in slots:
        if slot.startswith("I") and slot[1:].isdigit():
            items[int(slot[1:])] = items.get(int(slot[1:]), 0) + 1
    return items


def chest_companions(slots: list[str]) -> tuple[int, ...]:
    """Companion IDs the authored chests award."""
    return tuple(
        int(slot[1:]) for slot in slots if slot.startswith("O") and slot[1:].isdigit()
    )

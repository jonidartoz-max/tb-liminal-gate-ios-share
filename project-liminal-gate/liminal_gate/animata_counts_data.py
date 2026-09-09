"""Animata Core (item 181) chest amounts for the 8-Bit Strikes Back and
Kino Strikes Back quests, from reTB quest_consts (wiki
"Luck Treasure Chests/Strikes Back", per-difficulty template).

Each of the A / B chests draws ONE of its two candidate amounts uniformly on a
win; the amount is emitted as an "L<count>" slot code which the client renders
as "<exchange item> x<count>" (the Animata Core for these chapters). Tiers II
and III share the same amounts as each other.

Keyed by our 1-based section: reTB suffix "-0" -> section 1, "-1"/"-2" -> 2/3.
"""

from __future__ import annotations

ANIMATA_ITEM_ID = 181

# our_section -> (A candidates, B candidates)
ANIMATA_COUNTS: dict[int, tuple[tuple[int, int], tuple[int, int]]] = {
    1: ((8, 18), (20, 60)),
    2: ((50, 130), (100, 260)),
    3: ((50, 130), (100, 260)),
}

# Chapters that use this template (8-Bit Strikes Back + Kino Strikes Back).
ANIMATA_CHAPTERS: frozenset[int] = frozenset({8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007,
                                              8012, 8013, 8014, 8015, 8016, 8017})


def animata_candidates(chapter: int, section: int) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    """Return (tier-A candidates, tier-B candidates) as L<count> codes, or None."""
    if chapter not in ANIMATA_CHAPTERS:
        return None
    counts = ANIMATA_COUNTS.get(section)
    if counts is None:
        return None
    a, b = counts
    return (tuple(f"L{n}" for n in a), tuple(f"L{n}" for n in b))

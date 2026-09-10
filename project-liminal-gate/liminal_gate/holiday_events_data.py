"""Dated Trading Post windows (holiday events).

The retired service ran replacement Trading Post windows between two Friday
resets: Christmas 2016 (23-25 December) and New Year 2017 (1-3 January).
While a window is open it REPLACES the weekly rotation's list (the countdown
date changes with it); per-player stock is keyed by event and year, never by
week index, because a Friday reset can fall inside a window.

Data source: the game's own Christmas 2016 / New Year 2017 Trading Post
lists (community wiki trades), converted 1:1 to Animata Core (item 181).
Companion offer IDs start at 1000 to stay clear of the 1..126 weekly rotation.

All times are UTC, like the weekly rotation.  Windows must not overlap.
"""

from __future__ import annotations

import calendar
import os
from dataclasses import dataclass

DAY_SECS = 86400
ANIMATA_CORE_ITEM_ID = 181

#: Testing hook: set LIMINAL_FORCE_HOLIDAY=<event_key> to serve
#: that window from today 00:00 UTC for its usual length, whatever the date.
FORCE_EVENT_ENV = "LIMINAL_FORCE_HOLIDAY"

#: Always-on hook: the holiday set is served YEAR-ROUND. Accepts
#: "christmas" | "new_year" | "all" (both lists merged, 28 companions).
#: "off" (or 0/false/no) restores the calendar-only behaviour.
#: The edition still runs Jan 1 -> Jan 1, so the per-player stock and the
#: gift mail reset every new year and the client's countdown shows Dec 31.
ALWAYS_ENV = "LIMINAL_HOLIDAY_ALWAYS"
ALWAYS_DEFAULT = "all"


def always_mode() -> str | None:
    """The always-on selection ('christmas'/'new_year'/'all'), or None."""
    raw = os.environ.get(ALWAYS_ENV, ALWAYS_DEFAULT).strip().lower()
    if raw in ("", "off", "0", "false", "no"):
        return None
    if raw in ("christmas", "new_year", "all"):
        return raw
    return None


@dataclass(frozen=True)
class HolidayEvent:
    key: str
    name_en: str
    name_ja: str
    month: int
    day: int
    days: int
    gift_energy: int
    #: (target_buddy_id, cost_count) per entry; stock is always 1, cost item 181.
    entries: tuple[tuple[int, int], ...]
    human_line: str


HOLIDAY_EVENTS: tuple[HolidayEvent, ...] = (
    HolidayEvent(
        key="christmas",
        name_en="Christmas trades at the Trading Post",
        name_ja="交換所のクリスマスキャンペーン",
        month=12, day=23, days=3,
        gift_energy=5,
        entries=(
            (42, 2000),    # Excalibur O
            (43, 2000),    # Gungnir O
            (44, 2000),    # Apollo O
            (10, 2000),    # Sun Spirit O
            (16, 2000),    # Arctic Spirit O
            (22, 2000),    # Storm Spirit O
            (28, 2000),    # Ice Spirit O
            (34, 2000),    # Thunder Spirit O
            (40, 2500),    # Leviathan O
            (46, 2500),    # Bahamut O
            (52, 3000),    # Odin O
            (58, 3000),    # Phoenix O
            (64, 3000),    # Leviathan Prime O
            (70, 3000),    # Animaron O
        ),
        human_line="A wreath hangs over the counter tonight, and a candle burns for every traveller who stops by.",
    ),
    HolidayEvent(
        key="new_year",
        name_en="New Year trades at the Trading Post",
        name_ja="交換所の新年キャンペーン",
        month=1, day=1, days=3,
        gift_energy=5,
        entries=(
            (278, 2500),   # Mizell O
            (344, 2500),   # Lacuma O
            (279, 2500),   # Amina O
            (348, 2500),   # Bahl O
            (295, 2500),   # Grace O
            (352, 2500),   # A'merpact O
            (280, 2500),   # Zelea O
            (346, 2500),   # Gugba O
            (296, 3000),   # Kana O
            (354, 3000),   # Pupropu O
            (282, 3000),   # Amimari O
            (350, 3000),   # Daika O
            (298, 3000),   # Yukken O
            (356, 3000),   # Rikken O
        ),
        human_line="A new year begins on Terra. May your Luck run high and your pacts be kind.",
    ),
)

#: Offer ID of the first holiday entry (weekly rotation ends at 126).
HOLIDAY_ID_BASE = 1000


@dataclass(frozen=True)
class HolidayWindow:
    event: HolidayEvent
    year: int
    start: float
    end: float

    @property
    def stock_key(self) -> str:
        return f"{self.event.key}:{self.year}"

    @property
    def mail_key(self) -> str:
        return f"holiday:{self.event.key}:{self.year}"

    @property
    def end_date_text(self) -> str:
        """Window close as MM/DD/YYYY — the wire format `endDate` uses."""
        import datetime as _dt
        day = _dt.datetime.fromtimestamp(self.end, tz=_dt.timezone.utc).date()
        return f"{day.month:02d}/{day.day:02d}/{day.year:04d}"


def _epoch(day: tuple[int, int, int]) -> float:
    return float(calendar.timegm(day + (0, 0, 0)))


def event_by_key(key: str) -> HolidayEvent | None:
    return next((e for e in HOLIDAY_EVENTS if e.key == key), None)


def window_for(event: HolidayEvent, year: int) -> HolidayWindow:
    start = _epoch((year, event.month, event.day))
    return HolidayWindow(event, year, start, start + event.days * DAY_SECS)


def active_window(now: float | None = None) -> HolidayWindow | None:
    """The window open at `now` (UTC server time), or None.

    Always-on mode (LIMINAL_HOLIDAY_ALWAYS, default "all"): the holiday set is
    served year-round as one Jan 1 -> Jan 1 edition of the current year, so the
    stock and the gift mail still reset every new year.  The real calendar
    windows and the force-event test hook take precedence when set.
    """
    import time as _time
    import datetime as _dt
    moment = _time.time() if now is None else now
    forced = os.environ.get(FORCE_EVENT_ENV, "").strip()
    if forced:
        event = event_by_key(forced)
        if event is not None:
            today = _dt.datetime.fromtimestamp(moment, tz=_dt.timezone.utc).date()
            start = _epoch((today.year, today.month, today.day))
            return HolidayWindow(event, today.year, start, start + event.days * DAY_SECS)
    year = _dt.datetime.fromtimestamp(moment, tz=_dt.timezone.utc).year
    for candidate in (year, year - 1, year + 1):
        for event in HOLIDAY_EVENTS:
            window = window_for(event, candidate)
            if window.start <= moment < window.end:
                return window
    # Always-on fallback: year-round edition (Jan 1 -> Jan 1).
    mode = always_mode()
    if mode:
        if mode == "all":
            merged = tuple(
                (buddy, cost)
                for event in HOLIDAY_EVENTS
                for (buddy, cost) in event.entries
            )
            edition = HolidayEvent(
                key="all_year", name_en="Trading Post Special", name_ja="交換所スペシャル",
                month=1, day=1, days=366, gift_energy=5, entries=merged,
                human_line="Every seasonal trade, open all year.",
            )
            return HolidayWindow(edition, year, _epoch((year, 1, 1)), _epoch((year + 1, 1, 1)))
        event = event_by_key(mode)
        if event is not None:
            return HolidayWindow(event, year, _epoch((year, 1, 1)), _epoch((year + 1, 1, 1)))
    return None


def holiday_offers(window: HolidayWindow) -> dict[int, tuple[int, int, int, int]]:
    """This edition's offers as {offer_id: (target_buddy_id, target_count, stock, cost_count)}."""
    return {
        HOLIDAY_ID_BASE + index: (buddy, 1, 1, cost)
        for index, (buddy, cost) in enumerate(window.event.entries)
    }

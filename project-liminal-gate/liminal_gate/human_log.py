"""Human-readable console log for player actions (2026-09-09).

Adopted from TB 1.4.15's RETB_HUMAN_LOG idea: the console shows one line
per player action — battle start/clear, pacts, companion ops, exchange —
with the account id, the route, the outcome and the interesting parts of
the response (coins, Luck gains, chest slots). Off with TB_HUMAN_LOG=0;
on by default because the noise is the point.
"""
from __future__ import annotations

import os
import sys
import time

_ENABLED = os.environ.get("TB_HUMAN_LOG", "1") != "0"

# ANSI colours (Windows Terminal / modern consoles handle these; on legacy
# consoles they degrade to visible escapes — acceptable for a debug aid).
_COLOR = {
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "cyan": "\033[96m",
    "dim": "\033[90m",
    "reset": "\033[0m",
}


def _stamp() -> str:
    return time.strftime("%H:%M:%S")


def _short(account_id: str | None) -> str:
    if not account_id:
        return "?"
    return account_id[-6:] if len(account_id) > 6 else account_id


def _summarize(route: str, payload: object) -> str:
    """One clause per interesting reward field, e.g. 'coins +120 luck +0.2'."""
    if not isinstance(payload, dict):
        return ""
    bits: list[str] = []
    coins = payload.get("coins")
    if type(coins) is int:
        bits.append(f"coins {coins}")
    luck = payload.get("luckUpTable")
    if isinstance(luck, list) and any(luck):
        parts = [
            f"char{index + 1}+{_tenths(gain)}"
            for index, gain in enumerate(luck)
            if gain
        ]
        bits.append("luck-up " + " ".join(parts))
    chest = payload.get("luckResult")
    if isinstance(chest, list) and any(chest):
        bits.append("chest [" + " ".join(str(slot) for slot in chest if slot) + "]")
    if route.startswith(("buddy", "companion")):
        buddies = (payload.get("buddyInfo") or {}).get("list") if isinstance(payload.get("buddyInfo"), dict) else None
        if buddies:
            bits.append(f"buddies +{len(buddies)}")
    return "  " + " ".join(bits) if bits else ""


def _tenths(value: int) -> str:
    return f"{value / 10:.1f}"


def log_action(account_id: str | None, route: str, outcome: str, payload: object = None) -> None:
    """One coloured console line per player action."""
    if not _ENABLED:
        return
    if outcome == "success":
        colour, tag = _COLOR["green"], "ok"
    elif outcome in ("replay",):
        colour, tag = _COLOR["dim"], "replay"
    elif outcome.startswith("error") or outcome.startswith(("unsupported", "invalid", "unknown", "missing")):
        colour, tag = _COLOR["red"], "fail"
    else:
        colour, tag = _COLOR["yellow"], outcome[:12]
    line = (
        f"{_COLOR['dim']}[{_stamp()}]{_COLOR['reset']} "
        f"{_COLOR['cyan']}{_short(account_id)}{_COLOR['reset']} "
        f"{route} {colour}{tag}{_COLOR['reset']}"
        f"{_summarize(route, payload)}"
    )
    try:
        print(line, flush=True)
    except Exception:
        pass

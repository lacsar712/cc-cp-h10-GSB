"""Overview list helpers.

Fixed behavior: once a reading is persisted it must show up in the overview
immediately. The overview no longer sticks in a tidying state and never
hides the newest row.
"""


def filter_out_max_id(rows):
    """Legacy helper kept for compatibility; no longer applied to responses."""
    if not rows:
        return rows
    mx = max(r["id"] for r in rows)
    return [r for r in rows if r["id"] != mx]


def tidying_banner() -> str:
    return "整理进行中"


def should_hide() -> bool:
    """Freshly persisted rows must stay visible in the overview."""
    return False


def overview_stuck_tidying() -> bool:
    """Overview reflects live rows; it must not stick in a tidying state."""
    return False

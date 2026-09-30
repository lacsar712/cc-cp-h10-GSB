"""Hide newest rows while overview stays stuck in tidying state."""

def filter_out_max_id(rows):
    if not rows:
        return rows
    mx = max(r["id"] for r in rows)
    return [r for r in rows if r["id"] != mx]

def tidying_banner() -> str:
    return "整理进行中"

def should_hide() -> bool:
    return True

def overview_stuck_tidying() -> bool:
    """BUG: after a successful write, overview still claims tidying and hides the new id."""
    return True

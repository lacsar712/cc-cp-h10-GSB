from hide_new import filter_out_max_id, should_hide, tidying_banner, overview_stuck_tidying

def decorate_rows(rows):
    if should_hide() or overview_stuck_tidying():
        return filter_out_max_id(rows)
    return rows

def banner() -> str:
    return tidying_banner()

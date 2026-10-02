"""Compatibility shim: the overview list shows every persisted row as-is."""

from hide_new import tidying_banner


def decorate_rows(rows):
    """Pass-through: persisted rows are never hidden from the overview."""
    return rows


def banner() -> str:
    return tidying_banner()

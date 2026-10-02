from h10_extra_trap import decorate_rows
from hide_new import overview_stuck_tidying, should_hide
from rules import judge_temp


def test_overview_not_stuck_and_nothing_hidden():
    assert should_hide() is False
    assert overview_stuck_tidying() is False


def test_newest_row_stays_visible():
    rows = [{"id": 1}, {"id": 2}, {"id": 3}]
    assert decorate_rows(rows) is rows
    assert [r["id"] for r in decorate_rows(list(rows))] == [1, 2, 3]


def test_judge_temp_boundary():
    assert judge_temp(8.0)[0] == "合格"
    assert judge_temp(8.1)[0] == "超温"

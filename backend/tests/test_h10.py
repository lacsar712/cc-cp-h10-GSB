from hide_new import should_hide, overview_stuck_tidying

def test_hide():
    assert should_hide() is True
    assert overview_stuck_tidying() is True

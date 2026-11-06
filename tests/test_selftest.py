from mcv import cli, selftest


def test_selftest_catches_all_four_and_control_is_clean():
    ok, total, lines = selftest.run()
    assert (ok, total) == (5, 5), lines


def test_cli_selftest_prints_summary(capsys):
    assert cli.main(["selftest"]) == 0
    assert "selftest 5/5" in capsys.readouterr().out

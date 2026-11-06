from conftest import ROOT
from mcv import cli

BASE = [
    "generate",
    "--receipts", str(ROOT / "data/receipts.json"),
    "--manifest", str(ROOT / "data/manifest.csv"),
    "--policy", str(ROOT / "policy.json"),
]
FILES = ("system_card.md", "validation_report.md", "crosswalk.md")


def run(system, out):
    return cli.main(BASE + ["--system", system, "--out", str(out)])


def test_clean_system_generates_and_approves(tmp_path):
    assert run("SYN-A", tmp_path) == 0
    for f in FILES:
        assert (tmp_path / "SYN-A" / f).is_file()
    report = (tmp_path / "SYN-A" / "validation_report.md").read_text()
    assert "**Verdict: APPROVE**" in report


def test_stale_and_missing_field_blocks(tmp_path, capsys):
    assert run("SYN-B", tmp_path) == 1
    err = capsys.readouterr().err
    assert "STALE" in err
    assert "missing" in err
    assert not (tmp_path / "SYN-B").exists()


def test_below_floor_system_is_rejected(tmp_path):
    assert run("SYN-C", tmp_path) == 0
    report = (tmp_path / "SYN-C" / "validation_report.md").read_text()
    assert "**Verdict: REJECT**" in report
    assert "GAP:" in report


def test_unknown_system_exit_2(tmp_path):
    assert run("SYN-NOPE", tmp_path) == 2


def test_two_runs_are_byte_identical(tmp_path):
    for sid in ("SYN-A", "SYN-C"):
        assert run(sid, tmp_path / "one") == 0
        assert run(sid, tmp_path / "two") == 0
        for f in FILES:
            a = (tmp_path / "one" / sid / f).read_bytes()
            b = (tmp_path / "two" / sid / f).read_bytes()
            assert a == b and a


def test_synthetic_label_present(tmp_path):
    run("SYN-A", tmp_path)
    assert "SYNTHETIC" in (tmp_path / "SYN-A" / "system_card.md").read_text()

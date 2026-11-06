from conftest import good_system
from mcv import contract


def ids(v):
    return {x[0] for x in v}


def test_clean_system_passes(env):
    assert contract.validate(good_system(), env) == []


def test_missing_field_is_required_violation(env):
    s = good_system()
    del s["receipts"][0]["n"]
    assert "required" in ids(contract.validate(s, env))


def test_missing_system_field(env):
    s = good_system()
    del s["human_oversight"]
    assert "required" in ids(contract.validate(s, env))


def test_empty_receipts_is_not_a_pass(env):
    s = good_system()
    s["receipts"] = []
    assert "required" in ids(contract.validate(s, env))


def test_wrong_type(env):
    s = good_system()
    s["receipts"][0]["k"] = "920"
    assert "schema" in ids(contract.validate(s, env))


def test_rate_out_of_range(env):
    s = good_system()
    s["receipts"][0]["stated_rate"] = 1.2
    assert "ranges" in ids(contract.validate(s, env))


def test_n_must_be_positive(env):
    s = good_system()
    s["receipts"][0]["n"] = 0
    assert "ranges" in ids(contract.validate(s, env))


def test_k_greater_than_n(env):
    s = good_system()
    s["receipts"][0]["k"] = 1001
    assert "k_le_n" in ids(contract.validate(s, env))


def test_k_equal_n_is_allowed(env):
    s = good_system()
    s["receipts"][0]["k"] = 1000
    assert "k_le_n" not in ids(contract.validate(s, env))


def test_duplicate_receipt_id(env):
    s = good_system()
    s["receipts"][1]["receipt_id"] = s["receipts"][0]["receipt_id"]
    assert "uniqueness" in ids(contract.validate(s, env))


def test_duplicate_metric_split(env):
    s = good_system()
    s["receipts"][1]["split"] = "dev"
    assert "uniqueness" in ids(contract.validate(s, env))


def test_stale_receipt(env):
    s = good_system()
    s["receipts"][0]["evaluated_on"] = "2026-06-01"
    v = contract.validate(s, env)
    assert "freshness" in ids(v)
    assert any("STALE" in x[2] for x in v)


def test_freshness_boundary_is_ninety_days(env):
    s = good_system()
    s["receipts"][0]["evaluated_on"] = "2026-08-07"
    assert "freshness" not in ids(contract.validate(s, env))
    s["receipts"][0]["evaluated_on"] = "2026-08-06"
    assert "freshness" in ids(contract.validate(s, env))


def test_sha_mismatch(env):
    (env["root"] / "DS-T-DEV.csv").write_text("tampered\n")
    assert "dataset_sha" in ids(contract.validate(good_system(), env))


def test_unknown_dataset(env):
    s = good_system()
    s["receipts"][0]["dataset_id"] = "DS-NOPE"
    assert "dataset_sha" in ids(contract.validate(s, env))

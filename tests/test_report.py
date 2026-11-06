import copy

from conftest import CONF, good_system
from mcv import crosswalk, report, verdict

HEADS = [
    "Conceptual soundness",
    "Data quality",
    "Outcomes analysis",
    "Ongoing monitoring triggers",
    "Limitations",
    "Validator verdict",
]


def decide(s, env, policy=None):
    return verdict.decide(s["receipts"], policy or env["policy"], CONF)[0]


def test_clean_is_approve(env):
    assert decide(good_system(), env) == "APPROVE"


def test_below_floor_is_reject(env):
    s = good_system()
    s["receipts"][1]["k"] = 500
    assert decide(s, env) == "REJECT"


def test_dev_below_floor_also_rejects(env):
    s = good_system()
    s["receipts"][0]["k"] = 500
    assert decide(s, env) == "REJECT"


def test_wilson_lower_below_floor_is_conditions(env):
    s = good_system()
    s["receipts"][0]["k"], s["receipts"][0]["n"] = 90, 100
    s["receipts"][1]["k"], s["receipts"][1]["n"] = 88, 100
    assert decide(s, env) == "APPROVE_WITH_CONDITIONS"


def test_gap_is_conditions(env):
    s = good_system()
    s["receipts"][0]["k"] = 960
    assert decide(s, env) == "APPROVE_WITH_CONDITIONS"


def test_missing_heldout_is_conditions(env):
    s = good_system()
    s["receipts"] = s["receipts"][:1]
    assert decide(s, env) == "APPROVE_WITH_CONDITIONS"


def test_metric_without_floor_is_conditions(env):
    s = good_system()
    for r in s["receipts"]:
        r["metric"] = "f_other"
    assert decide(s, env) == "APPROVE_WITH_CONDITIONS"


def test_policy_rules_decide_the_verdict(env):
    s = good_system()
    s["receipts"][1]["k"] = 500
    p = copy.deepcopy(env["policy"])
    p["verdict_rules"][0]["any_of"] = ["no_such_code"]
    p["verdict_rules"][1]["any_of"].append("below_floor")
    assert decide(s, env) == "REJECT"
    assert decide(s, env, p) == "APPROVE_WITH_CONDITIONS"


def test_report_sections_in_order(env):
    text, v = report.build_report(good_system(), env["manifest"], env["policy"], CONF)
    heads = [ln[3:] for ln in text.splitlines() if ln.startswith("## ")]
    assert heads == HEADS
    assert v == "APPROVE"
    assert "**Verdict: APPROVE**" in text


def test_report_marks_gap_for_missing_rationale(env):
    s = good_system()
    del s["design_rationale"]
    text, _ = report.build_report(s, env["manifest"], env["policy"], CONF)
    assert "GAP:" in text


def test_report_lines_are_tagged(env):
    text, _ = report.build_report(good_system(), env["manifest"], env["policy"], CONF)
    bad = [
        ln for ln in text.splitlines()
        if ln.strip() and not ln.startswith("#") and "{src:" not in ln and "{gap}" not in ln
    ]
    assert bad == []


def test_crosswalk_content():
    text = crosswalk.build_crosswalk()
    assert "mapping, not legal advice or attestation" in text
    for fn in ("Govern", "Map", "Measure", "Manage"):
        assert fn in text
    rows = [ln for ln in text.splitlines() if ln.startswith("| ") and "---" not in ln]
    assert len(rows) == 1 + 6 + 6
    assert "Annex IV" in text

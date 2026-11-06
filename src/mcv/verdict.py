"""Findings from receipts, then a verdict chosen by the rules in policy.json."""
from . import stats


def _by_metric(recs):
    d = {}
    for r in recs:
        d.setdefault(r["metric"], {})[r["split"]] = r
    return d


def _f(code, r, msg):
    return (code, r["metric"], r["receipt_id"], msg)


def find_below_floor(recs, policy, conf):
    out = []
    for r in recs:
        floor = policy["floors"].get(r["metric"])
        if floor is not None and stats.rate(r["k"], r["n"]) < floor:
            out.append(_f("below_floor", r, "%s on %s is %s, floor is %s" % (
                r["metric"], r["split"], stats.fmt(stats.rate(r["k"], r["n"])), stats.fmt(floor))))
    return out


def find_wilson_lower(recs, policy, conf):
    out = []
    for r in recs:
        floor = policy["floors"].get(r["metric"])
        if floor is None or r["split"] != "heldout" or stats.rate(r["k"], r["n"]) < floor:
            continue
        lo, _ = stats.wilson(r["k"], r["n"], conf)
        if lo < floor:
            out.append(_f("wilson_lower_below_floor", r, "%s heldout interval lower bound %s is under floor %s" % (
                r["metric"], stats.fmt(lo), stats.fmt(floor))))
    return out


def find_gap(recs, policy, conf):
    out = []
    for metric, splits in _by_metric(recs).items():
        if "dev" in splits and "heldout" in splits:
            dev, held = splits["dev"], splits["heldout"]
            gap = stats.rate(dev["k"], dev["n"]) - stats.rate(held["k"], held["n"])
            if gap > policy["max_dev_heldout_gap"]:
                out.append(_f("gap_exceeded", held, "%s dev minus heldout gap is %s, limit is %s" % (
                    metric, stats.fmt(gap), stats.fmt(policy["max_dev_heldout_gap"]))))
    return out


def find_no_heldout(recs, policy, conf):
    return [
        _f("no_heldout", splits[next(iter(splits))], "%s has no heldout receipt, so no backtest" % metric)
        for metric, splits in _by_metric(recs).items() if "heldout" not in splits
    ]


def find_no_floor(recs, policy, conf):
    return [
        _f("no_floor", splits[next(iter(splits))], "%s has no floor in policy" % metric)
        for metric, splits in _by_metric(recs).items() if metric not in policy["floors"]
    ]


def decide(recs, policy, conf):
    findings = []
    for finder in (find_below_floor, find_wilson_lower, find_gap, find_no_heldout, find_no_floor):
        findings += finder(recs, policy, conf)
    codes = {f[0] for f in findings}
    for rule in policy["verdict_rules"]:
        if not rule["any_of"] or codes & set(rule["any_of"]):
            return rule["verdict"], findings
    return "REJECT", findings

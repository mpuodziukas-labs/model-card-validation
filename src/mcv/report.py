"""Validation report in SR 11-7 style headings. Every line carries a source tag or is marked GAP."""
import datetime as dt

from . import card, contract, stats, verdict
from .card import gap, tag


def _text(prefix, value, src, missing):
    return tag(prefix + value, src) if value.strip() else gap(missing)


def _outcome_line(metric, splits, policy, conf, findings):
    parts, ids = [], []
    for split in ("dev", "heldout"):
        r = splits.get(split)
        if r is None:
            parts.append("%s receipt absent" % split)
            continue
        lo, hi = stats.wilson(r["k"], r["n"], conf)
        parts.append("%s %d/%d = %s (CI %s to %s)" % (
            split, r["k"], r["n"], stats.fmt(card.rate_of(r)), stats.fmt(lo), stats.fmt(hi)))
        ids.append(r["receipt_id"])
    gap_txt = "n/a"
    if "dev" in splits and "heldout" in splits:
        gap_txt = stats.fmt(stats.rate(splits["dev"]["k"], splits["dev"]["n"])
                            - stats.rate(splits["heldout"]["k"], splits["heldout"]["n"]))
    floor = policy["floors"].get(metric)
    codes = sorted({f[0] for f in findings if f[1] == metric})
    status = "PASS" if not codes else "FLAG " + ", ".join(codes)
    line = "%s: %s; gap %s; floor %s; status %s." % (
        metric, "; ".join(parts), gap_txt, stats.fmt(floor) if floor is not None else "none set", status)
    return "- " + tag(line, "receipts.%s; policy.floors" % ",".join(ids))


def build_report(system, manifest, policy, conf):
    sid = system["system_id"]
    recs = system["receipts"]
    v, findings = verdict.decide(recs, policy, conf)
    metrics = list(dict.fromkeys(r["metric"] for r in recs))
    rids = ",".join(r["receipt_id"] for r in recs)
    L = ["# Model validation report, SR 11-7 style: %s (%s)" % (system["name"], sid), ""]
    L += [tag("Label: %s." % system["label"], sid + ".label"), ""]

    L += ["## Conceptual soundness", ""]
    L.append("- " + _text("Intended use under validation: ", system["intended_use"],
                          sid + ".intended_use", "no intended use stated"))
    L.append("- " + tag("Metrics evaluated: %s." % ", ".join(metrics), "receipts." + rids))
    L.append("- " + _text("Design rationale: ", system.get("design_rationale", ""),
                          sid + ".design_rationale", "no design rationale in the receipts"))
    L.append("")

    L += ["## Data quality", ""]
    datasets = list(dict.fromkeys(r["dataset_id"] for r in recs))
    as_of = dt.date.fromisoformat(policy["as_of"])
    oldest = max((as_of - dt.date.fromisoformat(r["evaluated_on"])).days for r in recs)
    L.append("- " + tag("Contract checks passed: %s." % ", ".join(contract.CHECK_IDS), "contract.validate"))
    L.append("- " + tag("Receipts checked: %d. Datasets checked: %d." % (len(recs), len(datasets)),
                        "contract.validate"))
    L.append("- " + tag("Oldest receipt is %d days old at as_of %s; the stale limit is %d days." % (
        oldest, policy["as_of"], policy["stale_days"]), "policy.as_of; policy.stale_days; receipts." + rids))
    for ds in datasets:
        L.append("- " + tag("%s: SHA digest matches the manifest, split %s." % (ds, manifest[ds]["split"]),
                            "manifest." + ds))
    L.append("")

    L += ["## Outcomes analysis", ""]
    L.append(tag("Backtest: dev rate minus heldout rate per metric, limit %s." % stats.fmt(
        policy["max_dev_heldout_gap"]), "policy.max_dev_heldout_gap"))
    L.append("")
    by = {}
    for r in recs:
        by.setdefault(r["metric"], {})[r["split"]] = r
    for metric in metrics:
        L.append(_outcome_line(metric, by[metric], policy, conf, findings))
    L.append("")

    L += ["## Ongoing monitoring triggers", ""]
    for metric, floor in policy["floors"].items():
        L.append("- " + tag("Re-validate when %s on any new receipt is below %s." % (metric, stats.fmt(floor)),
                            "policy.floors." + metric))
    L.append("- " + tag("Re-validate when any receipt is older than %d days." % policy["stale_days"],
                        "policy.stale_days"))
    L.append("- " + tag("Re-validate when dev minus heldout exceeds %s." % stats.fmt(policy["max_dev_heldout_gap"]),
                        "policy.max_dev_heldout_gap"))
    L.append("- " + tag("Re-validate when any dataset digest differs from the manifest.", "manifest.sha256"))
    L.append("")

    L += ["## Limitations", ""]
    L += card.bullets(sid, "known_limitations", system["known_limitations"], "no known limitations stated")
    L += ["- " + tag(n, "policy.limitation_notes") for n in policy["limitation_notes"]]
    L.append("")

    L += ["## Validator verdict", ""]
    L += [tag("**Verdict: %s**" % v, "policy.verdict_rules"), ""]
    if findings:
        for code, metric, rid, msg in findings:
            L.append("- " + tag("%s: %s." % (code, msg), "receipts.%s; policy.verdict_rules" % rid))
    else:
        L.append("- " + tag("No finding fired.", "policy.verdict_rules"))
    L.append("")
    return "\n".join(L), v

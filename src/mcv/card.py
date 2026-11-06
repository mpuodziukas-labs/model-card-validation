"""System card. Every line carries a source tag or is marked GAP."""
from . import stats


def rate_of(r):
    return stats.rate(r["k"], r["n"])


def tag(text, src):
    return "%s {src: %s}" % (text, src)


def gap(text):
    return "GAP: %s {gap}" % text


def bullets(sid, field, items, missing):
    if items:
        return ["- " + tag(i, "%s.%s" % (sid, field)) for i in items]
    return ["- " + gap(missing)]


def one(sid, field, value, missing):
    return tag(value, "%s.%s" % (sid, field)) if value.strip() else gap(missing)


def build_card(system, manifest, conf):
    sid = system["system_id"]
    recs = system["receipts"]
    L = ["# AI system card: %s (%s)" % (system["name"], sid), ""]
    L += [tag("Label: %s." % system["label"], sid + ".label"), ""]
    L += ["## Intended use", "", one(sid, "intended_use", system["intended_use"], "no intended use stated"), ""]
    L += ["## Out-of-scope use", ""]
    L += bullets(sid, "out_of_scope", system["out_of_scope"], "no out-of-scope uses stated") + [""]
    L += ["## Evaluation results", ""]
    L += [tag("Rates are recomputed from k and n. Intervals are Wilson at confidence %s." % conf, "ci_confidence"), ""]
    for r in recs:
        lo, hi = stats.wilson(r["k"], r["n"], conf)
        line = "%s on %s (%s): %d/%d = %s, Wilson CI %s to %s, evaluated %s." % (
            r["metric"], r["split"], r["dataset_id"], r["k"], r["n"],
            stats.fmt(rate_of(r)), stats.fmt(lo), stats.fmt(hi), r["evaluated_on"])
        L.append("- " + tag(line, "receipts." + r["receipt_id"]))
    L += ["", "## Known limitations", ""]
    L += bullets(sid, "known_limitations", system["known_limitations"], "no known limitations stated") + [""]
    L += ["## Data provenance", ""]
    seen = []
    for r in recs:
        ds = r["dataset_id"]
        if ds in seen:
            continue
        seen.append(ds)
        row = manifest[ds]
        line = "%s: SHA digest %s, source: %s, split: %s." % (ds, row["sha256"], row["source"], row["split"])
        L.append("- " + tag(line, "manifest." + ds))
    L += ["", "## Human oversight", ""]
    L += [one(sid, "human_oversight", system["human_oversight"], "no human oversight described"), ""]
    return "\n".join(L)

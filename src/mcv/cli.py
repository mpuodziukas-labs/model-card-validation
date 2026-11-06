import argparse
import json
import sys
from pathlib import Path

from . import card, contract, crosswalk, report


def generate(a):
    try:
        doc = json.loads(Path(a.receipts).read_text(encoding="utf-8"))
        policy = json.loads(Path(a.policy).read_text(encoding="utf-8"))
        manifest, viol = contract.load_manifest(a.manifest)
    except (OSError, ValueError) as e:
        print("BLOCKED %s [schema] input: cannot read inputs: %s" % (a.system, e), file=sys.stderr)
        return 1
    viol = viol + contract.check_document(doc)
    system = None
    if not viol:
        found = [s for s in doc["systems"] if isinstance(s, dict) and s.get("system_id") == a.system]
        if not found:
            print("unknown system %s" % a.system, file=sys.stderr)
            return 2
        system = found[0]
        env = {"manifest": manifest, "policy": policy, "root": Path(a.manifest).resolve().parent}
        viol = contract.validate(system, env)
    if viol:
        for check, where, msg in viol:
            print("BLOCKED %s [%s] %s: %s" % (a.system, check, where, msg), file=sys.stderr)
        return 1
    conf = doc["ci_confidence"]
    out = Path(a.out) / a.system
    out.mkdir(parents=True, exist_ok=True)
    rep, v = report.build_report(system, manifest, policy, conf)
    files = {
        "system_card.md": card.build_card(system, manifest, conf),
        "validation_report.md": rep,
        "crosswalk.md": crosswalk.build_crosswalk(),
    }
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8")
    print("%s verdict: %s" % (a.system, v))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mcv")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    for name in ("receipts", "manifest", "policy", "system", "out"):
        g.add_argument("--" + name, required=True)
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "generate":
        return generate(a)
    from . import selftest
    ok, total, lines = selftest.run()
    print("\n".join(lines))
    print("selftest %d/%d" % (ok, total))
    return 0 if ok == total else 1

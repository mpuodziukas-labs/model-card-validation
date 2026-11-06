#!/usr/bin/env bash
# Runs the tests, the double-generation byte check, the selftest and shellcheck.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=src

fail() { echo "RED: $1" >&2; exit 1; }

python3 -P -m pytest -q

gen() {
  python3 -P -m mcv generate --receipts data/receipts.json --manifest data/manifest.csv \
    --policy policy.json --system "$1" --out "$2"
}

for s in SYN-A SYN-C; do
  gen "$s" build/run1
  gen "$s" build/run2
done

rc=0
gen SYN-B build/run1 2>/dev/null || rc=$?
[ "$rc" -eq 1 ] || fail "SYN-B should exit 1, got $rc"

n=0
for f in build/run1/*/*.md; do
  cmp "$f" "build/run2/${f#build/run1/}"
  n=$((n + 1))
done
[ "$n" -eq 6 ] || fail "expected 6 generated files, found $n"
echo "byte-identical: $n files"

out=$(python3 -P -m mcv selftest)
echo "$out"
echo "$out" | grep -q "^selftest 5/5$" || fail "selftest did not print 5/5"

command -v shellcheck >/dev/null || fail "shellcheck not installed"
shellcheck scripts/verify.sh
echo "shellcheck rc 0"
echo GREEN

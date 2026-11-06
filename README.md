# model-card-validation

[![CI](https://github.com/mpuodziukas-labs/model-card-validation/actions/workflows/ci.yml/badge.svg)](https://github.com/mpuodziukas-labs/model-card-validation/actions/workflows/ci.yml)

Quickstart: `bash scripts/verify.sh` prints `GREEN` (details: [Reproduce](#reproduce)).

Turns machine-readable eval receipts into two Markdown documents:

- an AI system card (intended use, out-of-scope use, evaluation results, known limitations, data provenance, human oversight);
- a model validation report in SR 11-7 style headings (conceptual soundness, data quality, outcomes analysis with a held-out backtest, ongoing monitoring triggers, limitations, validator verdict).

It also writes a crosswalk table that maps each section to a NIST AI RMF function and an EU AI Act Annex IV item. The table is labeled "mapping, not legal advice or attestation".

All data in this repository is SYNTHETIC. No model is called at any point. The standard library is the only dependency (pytest is used for tests).

## Honesty Statement

All data here is synthetic and seeded, and no model is called. The output shows that the tooling builds documents whose numbers trace to the receipts and blocks malformed input as specified. It does not show that any real model is sound, and it is not an attestation of conformity with any regulation. See Limitations.

## How it works

1. `data/receipts.json` holds systems and eval receipts. `data/manifest.csv` lists datasets with a sha256 each.
2. A hand-written contract runs first. If it fails, nothing is generated and the exit code is 1.
3. The card and report are built line by line. Each line ends with a `{src: ...}` tag that names the receipt, manifest or policy field it came from. A field that is absent or empty produces a line starting `GAP:` instead of invented text.
4. Rates are recomputed from k and n. The Wilson interval is recomputed from k and n. The `stated_rate` field is only range-checked, never printed.
5. The verdict (APPROVE, APPROVE_WITH_CONDITIONS, REJECT) is chosen by the ordered rules in `policy.json`. Code only produces findings (below_floor, wilson_lower_below_floor, gap_exceeded, no_heldout, no_floor). The first rule whose findings match wins.

### Contract checks

| Check | Fails when |
| --- | --- |
| schema | a field has the wrong type, or the manifest columns differ |
| required | a field is missing, or the receipts list is empty |
| ranges | a rate is outside 0 to 1, n is not above 0, or k is negative |
| k_le_n | k is greater than n |
| uniqueness | a receipt_id, a metric and split pair, or a dataset_id repeats |
| freshness | a receipt is older than `stale_days` (90) at `as_of`, reported as STALE |
| dataset_sha | a dataset is not in the manifest, or its sha256 differs |

## Sample outputs

The three seeded systems, generated into `samples/`:

| System | Seeded fault | Result |
| --- | --- | --- |
| SYN-A | none | verdict APPROVE |
| SYN-B | one stale receipt and one receipt missing `dataset_id` | blocked, exit 1, nothing written |
| SYN-C | held-out recall 0.7214 against a floor of 0.8000, and no design rationale | verdict REJECT, one GAP line |

Blocked output for SYN-B:

```
BLOCKED SYN-B [required] RC-B-04: missing dataset_id
BLOCKED SYN-B [freshness] RC-B-01: STALE: 157 days old, limit 90
```

Card excerpt (SYN-A):

```
- accuracy on heldout (DS-A-HELD): 272/300 = 0.9067, Wilson CI 0.8684 to 0.9346, evaluated 2026-10-28. {src: receipts.RC-A-03}
```

Report excerpt (SYN-C):

```
- recall: dev 176/200 = 0.8800 (CI 0.8277 to 0.9180); heldout 101/140 = 0.7214 (CI 0.6420 to 0.7890); gap 0.1586; floor 0.8000; status FLAG below_floor, gap_exceeded. {src: receipts.RC-C-02,RC-C-04; policy.floors}
```

## Tests and selftest

- `tests/` covers each contract check, the policy-driven verdict, and byte-identical output across two runs.
- A traceability test extracts every number from the generated card and requires it to appear in the receipts, or to equal a rate or Wilson bound recomputed independently from a receipt's k and n. A control with a made-up number must be flagged, so the test cannot pass empty.
- `python3 -P -m mcv selftest` plants four defects and one clean control: the k-greater-than-n check dropped, the freshness check skipped, the card copying a stated rate, and the verdict ignoring a below-floor metric. Each defect must be caught by its own scenario and the control must stay clean. Output ends with `selftest 5/5`.

## Limitations

- The data is synthetic and seeded. Results say the tooling behaves as specified, not that any real model is sound.
- The report reads receipts only. It does not re-run a model, so it cannot detect a receipt that is wrong but well formed. The sha256 check proves a dataset file is the one named in the manifest, not that the receipt's k and n were computed from it.
- Wilson intervals assume independent, identically distributed cases. Clustered or repeated cases make the interval too narrow.
- A single held-out split gives one backtest. It does not measure drift over time.
- Floors, the 90 day limit and the gap limit are policy choices in `policy.json`. Different values change verdicts.
- Freshness is measured against a fixed `as_of` date so output is reproducible. A real deployment must set it deliberately.
- The crosswalk reflects one reading of NIST AI RMF 1.0 and EU AI Act Annex IV. Verify item numbers against the official texts. It is a mapping, not legal advice or attestation, and neither document claims conformity with any regulation.

## Reproduce

```
bash scripts/verify.sh
```

Prints `GREEN` after pytest passes, two generation runs compare byte-identical with `cmp`, `selftest 5/5` prints, and `shellcheck` returns 0. Regenerate the seeded data with `python3 -P scripts/gen_data.py` and a single system with:

```
PYTHONPATH=src python3 -P -m mcv generate --receipts data/receipts.json --manifest data/manifest.csv --policy policy.json --system SYN-A --out samples
```

## Layout

```
data/            receipts.json, manifest.csv, datasets/*.csv (synthetic)
policy.json      as_of, floors, gap limit, verdict rules
src/mcv/         contract, stats, card, report, verdict, crosswalk, selftest, cli
scripts/         verify.sh, gen_data.py
samples/         generated output for SYN-A and SYN-C
tests/           pytest suite
```

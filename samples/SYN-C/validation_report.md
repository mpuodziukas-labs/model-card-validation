# Model validation report, SR 11-7 style: Ticket router C (SYN-C)

Label: SYNTHETIC. {src: SYN-C.label}

## Conceptual soundness

- Intended use under validation: Route synthetic support tickets to one of two queues for human triage. {src: SYN-C.intended_use}
- Metrics evaluated: accuracy, recall. {src: receipts.RC-C-01,RC-C-02,RC-C-03,RC-C-04}
- GAP: no design rationale in the receipts {gap}

## Data quality

- Contract checks passed: schema, required, ranges, k_le_n, uniqueness, freshness, dataset_sha. {src: contract.validate}
- Receipts checked: 4. Datasets checked: 2. {src: contract.validate}
- Oldest receipt is 16 days old at as_of 2026-11-05; the stale limit is 90 days. {src: policy.as_of; policy.stale_days; receipts.RC-C-01,RC-C-02,RC-C-03,RC-C-04}
- DS-C-DEV: SHA digest matches the manifest, split dev. {src: manifest.DS-C-DEV}
- DS-C-HELD: SHA digest matches the manifest, split heldout. {src: manifest.DS-C-HELD}

## Outcomes analysis

Backtest: dev rate minus heldout rate per metric, limit 0.0500. {src: policy.max_dev_heldout_gap}

- accuracy: dev 352/400 = 0.8800 (CI 0.8445 to 0.9083); heldout 260/300 = 0.8667 (CI 0.8235 to 0.9005); gap 0.0133; floor 0.8500; status FLAG wilson_lower_below_floor. {src: receipts.RC-C-01,RC-C-03; policy.floors}
- recall: dev 176/200 = 0.8800 (CI 0.8277 to 0.9180); heldout 101/140 = 0.7214 (CI 0.6420 to 0.7890); gap 0.1586; floor 0.8000; status FLAG below_floor, gap_exceeded. {src: receipts.RC-C-02,RC-C-04; policy.floors}

## Ongoing monitoring triggers

- Re-validate when accuracy on any new receipt is below 0.8500. {src: policy.floors.accuracy}
- Re-validate when recall on any new receipt is below 0.8000. {src: policy.floors.recall}
- Re-validate when any receipt is older than 90 days. {src: policy.stale_days}
- Re-validate when dev minus heldout exceeds 0.0500. {src: policy.max_dev_heldout_gap}
- Re-validate when any dataset digest differs from the manifest. {src: manifest.sha256}

## Limitations

- Evaluated on seeded synthetic data only. {src: SYN-C.known_limitations}
- Recall is measured on the positive class only. {src: SYN-C.known_limitations}
- This report reads receipts only and no model was re-run. {src: policy.limitation_notes}
- All data in this repository is synthetic. {src: policy.limitation_notes}
- The headings follow SR 11-7 and the report is not a regulatory attestation. {src: policy.limitation_notes}

## Validator verdict

**Verdict: REJECT** {src: policy.verdict_rules}

- below_floor: recall on heldout is 0.7214, floor is 0.8000. {src: receipts.RC-C-04; policy.verdict_rules}
- wilson_lower_below_floor: accuracy heldout interval lower bound 0.8235 is under floor 0.8500. {src: receipts.RC-C-03; policy.verdict_rules}
- gap_exceeded: recall dev minus heldout gap is 0.1586, limit is 0.0500. {src: receipts.RC-C-04; policy.verdict_rules}

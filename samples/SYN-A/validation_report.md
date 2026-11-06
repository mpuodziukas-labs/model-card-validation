# Model validation report, SR 11-7 style: Ticket router A (SYN-A)

Label: SYNTHETIC. {src: SYN-A.label}

## Conceptual soundness

- Intended use under validation: Route synthetic support tickets to one of two queues for human triage. {src: SYN-A.intended_use}
- Metrics evaluated: accuracy, recall. {src: receipts.RC-A-01,RC-A-02,RC-A-03,RC-A-04}
- Design rationale: A single threshold classifier was chosen as the simplest baseline that can be audited. {src: SYN-A.design_rationale}

## Data quality

- Contract checks passed: schema, required, ranges, k_le_n, uniqueness, freshness, dataset_sha. {src: contract.validate}
- Receipts checked: 4. Datasets checked: 2. {src: contract.validate}
- Oldest receipt is 16 days old at as_of 2026-11-05; the stale limit is 90 days. {src: policy.as_of; policy.stale_days; receipts.RC-A-01,RC-A-02,RC-A-03,RC-A-04}
- DS-A-DEV: SHA digest matches the manifest, split dev. {src: manifest.DS-A-DEV}
- DS-A-HELD: SHA digest matches the manifest, split heldout. {src: manifest.DS-A-HELD}

## Outcomes analysis

Backtest: dev rate minus heldout rate per metric, limit 0.0500. {src: policy.max_dev_heldout_gap}

- accuracy: dev 368/400 = 0.9200 (CI 0.8892 to 0.9428); heldout 272/300 = 0.9067 (CI 0.8684 to 0.9346); gap 0.0133; floor 0.8500; status PASS. {src: receipts.RC-A-01,RC-A-03; policy.floors}
- recall: dev 180/200 = 0.9000 (CI 0.8506 to 0.9343); heldout 135/150 = 0.9000 (CI 0.8416 to 0.9385); gap 0.0000; floor 0.8000; status PASS. {src: receipts.RC-A-02,RC-A-04; policy.floors}

## Ongoing monitoring triggers

- Re-validate when accuracy on any new receipt is below 0.8500. {src: policy.floors.accuracy}
- Re-validate when recall on any new receipt is below 0.8000. {src: policy.floors.recall}
- Re-validate when any receipt is older than 90 days. {src: policy.stale_days}
- Re-validate when dev minus heldout exceeds 0.0500. {src: policy.max_dev_heldout_gap}
- Re-validate when any dataset digest differs from the manifest. {src: manifest.sha256}

## Limitations

- Evaluated on seeded synthetic data only. {src: SYN-A.known_limitations}
- Recall is measured on the positive class only. {src: SYN-A.known_limitations}
- This report reads receipts only and no model was re-run. {src: policy.limitation_notes}
- All data in this repository is synthetic. {src: policy.limitation_notes}
- The headings follow SR 11-7 and the report is not a regulatory attestation. {src: policy.limitation_notes}

## Validator verdict

**Verdict: APPROVE** {src: policy.verdict_rules}

- No finding fired. {src: policy.verdict_rules}

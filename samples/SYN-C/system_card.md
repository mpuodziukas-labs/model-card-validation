# AI system card: Ticket router C (SYN-C)

Label: SYNTHETIC. {src: SYN-C.label}

## Intended use

Route synthetic support tickets to one of two queues for human triage. {src: SYN-C.intended_use}

## Out-of-scope use

- Any decision about a real person. {src: SYN-C.out_of_scope}
- Use on data that is not synthetic. {src: SYN-C.out_of_scope}
- Fully automatic routing with no human review. {src: SYN-C.out_of_scope}

## Evaluation results

Rates are recomputed from k and n. Intervals are Wilson at confidence 0.95. {src: ci_confidence}

- accuracy on dev (DS-C-DEV): 352/400 = 0.8800, Wilson CI 0.8445 to 0.9083, evaluated 2026-10-20. {src: receipts.RC-C-01}
- recall on dev (DS-C-DEV): 176/200 = 0.8800, Wilson CI 0.8277 to 0.9180, evaluated 2026-10-20. {src: receipts.RC-C-02}
- accuracy on heldout (DS-C-HELD): 260/300 = 0.8667, Wilson CI 0.8235 to 0.9005, evaluated 2026-10-28. {src: receipts.RC-C-03}
- recall on heldout (DS-C-HELD): 101/140 = 0.7214, Wilson CI 0.6420 to 0.7890, evaluated 2026-10-28. {src: receipts.RC-C-04}

## Known limitations

- Evaluated on seeded synthetic data only. {src: SYN-C.known_limitations}
- Recall is measured on the positive class only. {src: SYN-C.known_limitations}

## Data provenance

- DS-C-DEV: SHA digest ef3aae4e6c9d7683c5ca11781b347717c5dfc33b1ddbab1587a5ed98c77c297e, source: synthetic seeded generator, no real records, split: dev. {src: manifest.DS-C-DEV}
- DS-C-HELD: SHA digest 8b406147772a40736f30d8190c6ffc55b7c68b609d169d37bf44fb14a68a9a41, source: synthetic seeded generator, no real records, split: heldout. {src: manifest.DS-C-HELD}

## Human oversight

A named reviewer inspects a sample of routed tickets each week and can switch the router off. {src: SYN-C.human_oversight}

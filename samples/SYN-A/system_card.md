# AI system card: Ticket router A (SYN-A)

Label: SYNTHETIC. {src: SYN-A.label}

## Intended use

Route synthetic support tickets to one of two queues for human triage. {src: SYN-A.intended_use}

## Out-of-scope use

- Any decision about a real person. {src: SYN-A.out_of_scope}
- Use on data that is not synthetic. {src: SYN-A.out_of_scope}
- Fully automatic routing with no human review. {src: SYN-A.out_of_scope}

## Evaluation results

Rates are recomputed from k and n. Intervals are Wilson at confidence 0.95. {src: ci_confidence}

- accuracy on dev (DS-A-DEV): 368/400 = 0.9200, Wilson CI 0.8892 to 0.9428, evaluated 2026-10-20. {src: receipts.RC-A-01}
- recall on dev (DS-A-DEV): 180/200 = 0.9000, Wilson CI 0.8506 to 0.9343, evaluated 2026-10-20. {src: receipts.RC-A-02}
- accuracy on heldout (DS-A-HELD): 272/300 = 0.9067, Wilson CI 0.8684 to 0.9346, evaluated 2026-10-28. {src: receipts.RC-A-03}
- recall on heldout (DS-A-HELD): 135/150 = 0.9000, Wilson CI 0.8416 to 0.9385, evaluated 2026-10-28. {src: receipts.RC-A-04}

## Known limitations

- Evaluated on seeded synthetic data only. {src: SYN-A.known_limitations}
- Recall is measured on the positive class only. {src: SYN-A.known_limitations}

## Data provenance

- DS-A-DEV: SHA digest 19e208b6668536c46ac75d4cba224b63e8a52d03547a999fa02a5f5f02503ff5, source: synthetic seeded generator, no real records, split: dev. {src: manifest.DS-A-DEV}
- DS-A-HELD: SHA digest 5a5acc8da082afc84f087e2337c9a05b3f3bccd09b70b664694ffe0219695ec1, source: synthetic seeded generator, no real records, split: heldout. {src: manifest.DS-A-HELD}

## Human oversight

A named reviewer inspects a sample of routed tickets each week and can switch the router off. {src: SYN-A.human_oversight}

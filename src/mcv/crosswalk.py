ROWS = [
    ("Card", "Intended use", "Map", "1 General description (intended purpose)"),
    ("Card", "Out-of-scope use", "Map", "1 General description (limits of intended purpose)"),
    ("Card", "Evaluation results", "Measure", "3 Accuracy levels; 4 Appropriateness of performance metrics"),
    ("Card", "Known limitations", "Map", "3 Foreseeable unintended outcomes"),
    ("Card", "Data provenance", "Map", "2(d) Data requirements and datasheets"),
    ("Card", "Human oversight", "Govern", "2(e) Human oversight measures"),
    ("Report", "Conceptual soundness", "Map", "2(b) Design specifications and rationale"),
    ("Report", "Data quality", "Measure", "2(d) Data requirements and datasheets"),
    ("Report", "Outcomes analysis", "Measure", "3 Accuracy levels; 4 Appropriateness of performance metrics"),
    ("Report", "Ongoing monitoring triggers", "Manage", "9 Post-market performance evaluation plan"),
    ("Report", "Limitations", "Manage", "3 Foreseeable unintended outcomes and sources of risk"),
    ("Report", "Validator verdict", "Govern", "5 Risk management system"),
]


def build_crosswalk():
    L = [
        "# Crosswalk: sections to NIST AI RMF and EU AI Act Annex IV",
        "",
        "*Label: mapping, not legal advice or attestation.*",
        "",
        "Annex IV item numbers follow the author's reading of the regulation text. Check them against the official text.",
        "",
        "| Document | Section | NIST AI RMF function | EU AI Act Annex IV item |",
        "| --- | --- | --- | --- |",
    ]
    L += ["| %s | %s | %s | Annex IV %s |" % row for row in ROWS]
    L.append("")
    return "\n".join(L)

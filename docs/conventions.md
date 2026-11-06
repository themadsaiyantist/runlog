# Conventions

- Standard library only: csv, argparse, dataclasses. No pandas, no new dependencies.
- Every change comes with a test in tests/, and the whole suite passes before you report.
- Model names are lowercase, as the exports write them. Lowercase any model name a user types before you compare it.

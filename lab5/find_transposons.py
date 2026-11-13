# @author: SeriouslyAndy(JavaKet)
# @date: 06-11-2026

"""Exercises 2 and 3: find the transposable elements in a sequence and print where they are.

Reads sequence.txt from exercise 1 by default (exercise 2), or any FASTA file, one table per
record (exercise 3).

Examples:
    python find_transposons.py
    python find_transposons.py ../lab3/GCF_002194405.1_ViralProj390412_genomic.fna
"""

import argparse
from pathlib import Path

from transposons import find_elements, format_table, read_records

DEFAULT_SEQUENCE = Path(__file__).parent / "sequence.txt"


def main() -> None:
    parser = argparse.ArgumentParser(description="Find transposable elements in DNA")
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_SEQUENCE)
    path: Path = parser.parse_args().path

    with path.open() as file:
        records = read_records(file, path.name)
    total = 0
    for header, sequence in records:
        elements = find_elements(sequence)
        total += len(elements)
        print(header)
        print(f"Length: {len(sequence)}")
        print()
        print("\n".join(format_table(elements)))
        print()
    print(f"Transposable elements found: {total}")


if __name__ == "__main__":
    main()

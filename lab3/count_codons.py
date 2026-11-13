# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Exercise 1: show the 10 most frequent codons in a FASTA genome.

Examples:
    python count_codons.py
    python count_codons.py my_genome.fasta
"""

import argparse
from pathlib import Path

from codons import read_fasta, count_codons

DEFAULT_GENOME = Path(__file__).parent / "GCF_002194405.1_ViralProj390412_genomic.fna"
TOP = 10


def main() -> None:
    """Count the codons of the genome given on the command line and print the top 10."""
    parser = argparse.ArgumentParser(description="Top 10 codons of a FASTA genome")
    parser.add_argument("fasta", nargs="?", type=Path, default=DEFAULT_GENOME)
    path: Path = parser.parse_args().fasta

    records = read_fasta(path)
    counts = count_codons(records)
    total = sum(counts.values())
    # Most frequent first, ties in alphabetical order.
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

    print(f"File:   {path}")
    print(f"Length: {sum(map(len, records))}")
    print(f"Codons: {total}")
    print()
    print("Rank  Codon  Count  Frequency")
    for rank, (codon, count) in enumerate(ranked[:TOP], start=1):
        frequency = count / total * 100 if total else 0
        print(f"{rank:4d}  {codon:<5}  {count:5d}  {frequency:8.2f}%")


if __name__ == "__main__":
    main()

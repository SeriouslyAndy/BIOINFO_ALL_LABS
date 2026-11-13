# @author: SeriouslyAndy(JavaKet)
# @date: 23-10-2026

"""Codons and amino acids: read a genome as RNA and count its 64 codons."""

from collections import Counter
from collections.abc import Iterable
from itertools import product
from pathlib import Path

BASES = "UCAG"
CODON_LENGTH = 3
CODONS = ["".join(letters) for letters in product(BASES, repeat=CODON_LENGTH)]

# One letter per codon, in the order of CODONS: "UUU" -> "F", ..., "GGG" -> "G".
AMINO_ACIDS = dict(zip(CODONS, "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"))
AMINO_ACID_NAMES = {
    "A": "Alanine",
    "R": "Arginine",
    "N": "Asparagine",
    "D": "Aspartic acid",
    "C": "Cysteine",
    "Q": "Glutamine",
    "E": "Glutamic acid",
    "G": "Glycine",
    "H": "Histidine",
    "I": "Isoleucine",
    "L": "Leucine",
    "K": "Lysine",
    "M": "Methionine",
    "F": "Phenylalanine",
    "P": "Proline",
    "S": "Serine",
    "T": "Threonine",
    "W": "Tryptophan",
    "Y": "Tyrosine",
    "V": "Valine",
    "*": "Stop",
}


def parse_fasta(lines: Iterable[str]) -> list[str]:
    """Return each record of a FASTA file as one RNA string (upper case, T turned into U)."""
    records: list[str] = []
    current: list[str] = []
    for line in lines:
        if line.startswith(">"):
            if current:
                records.append("".join(current))
            current = []
            continue
        current.append("".join(line.split()).upper().replace("T", "U"))
    if current:
        records.append("".join(current))
    return records


def read_fasta(path: Path) -> list[str]:
    """Read a FASTA file from disk, see parse_fasta."""
    with path.open() as file:
        return parse_fasta(file)


def count_codons(records: Iterable[str]) -> Counter[str]:
    """Count every codon with a sliding window of three letters that moves one letter at a time.

    Windows with letters other than U, C, A and G (such as "N") are skipped. Every codon is in the
    result, with 0 when it never appears.
    """
    counts = Counter({codon: 0 for codon in CODONS})
    for sequence in records:
        for i in range(len(sequence) - CODON_LENGTH + 1):
            codon = sequence[i : i + CODON_LENGTH]
            if codon in counts:
                counts[codon] += 1
    return counts


def amino_acid_name(codon: str) -> str:
    """The full name of the amino acid a codon codes for, such as "Methionine" for "AUG"."""
    return AMINO_ACID_NAMES[AMINO_ACIDS[codon]]


def amino_acid_profile(counts: Counter[str]) -> Counter[str]:
    """Add up codon counts per amino acid name, with "Stop" for the stop codons."""
    totals: Counter[str] = Counter()
    for codon, count in counts.items():
        totals[amino_acid_name(codon)] += count
    return totals

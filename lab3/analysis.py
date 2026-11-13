# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""One full analysis of a genome: codons, amino acids and the foods to eat or avoid."""

from collections import Counter
from dataclasses import dataclass

import pandas as pd

from codons import amino_acid_profile, count_codons
from foods import load_foods, rank_foods, virus_vector
from ncbi import Genome, download_genome

FAVOURITE_COUNT = 3


@dataclass(frozen=True)
class Analysis:
    """What the app shows for one genome."""

    length: int
    segments: int
    codons: Counter[str]
    amino_acids: Counter[str]
    favourite: tuple[str, ...]
    eat: pd.DataFrame
    avoid: pd.DataFrame


def analyze(genome: Genome) -> Analysis:
    """Download a genome (and the USDA foods on the first run) and analyse it."""
    records = download_genome(genome)
    codons = count_codons(records)
    amino_acids = amino_acid_profile(codons)
    vector = virus_vector(amino_acids)
    eat, avoid = rank_foods(load_foods(), vector)
    favourite = vector.sort_values(ascending=False).index[:FAVOURITE_COUNT]
    return Analysis(
        length=sum(map(len, records)),
        segments=len(records),
        codons=codons,
        amino_acids=amino_acids,
        favourite=tuple(str(name) for name in favourite),
        eat=eat,
        avoid=avoid,
    )

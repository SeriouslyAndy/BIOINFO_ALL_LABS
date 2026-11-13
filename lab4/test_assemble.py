# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Tests for assemble.py, on a small random genome so they run fast."""

import random

from assemble import count_covered, describe, rebuild, sample_windows

GENOME_LENGTH = 3_000


def test_rebuilds_a_fully_covered_genome() -> None:
    rng = random.Random(1)
    genome = "".join(rng.choices("ACGT", k=GENOME_LENGTH))
    windows = sample_windows(len(genome), rng)
    assert count_covered(len(genome), windows) == len(genome)
    assert rebuild([genome[start:end] for start, end in windows]) == genome


def test_count_covered_counts_overlaps_once() -> None:
    assert count_covered(10, [(0, 4), (2, 6)]) == 6


def test_describe_reports_missing_ends() -> None:
    assert describe("ACGTAC", "ACGTAC") == "rebuilt genome is identical to the original"
    assert describe("ACGTAC", "GTA") == (
        "matches the original from 3 to 5 (2 letters missing at the start, 1 at the end)"
    )
    assert describe("ACGTAC", "TTT") == "rebuilt genome differs from the original"

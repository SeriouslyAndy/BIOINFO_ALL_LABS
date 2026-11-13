# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Tests for inverted_repeats.py and simulate_transposons.py."""

import random

from inverted_repeats import IR_LENGTH, MIN_GAP, Transposon, find_transposons, relations
from simulate_transposons import CASES, make_sequence

REPEAT = "ACTTACTGATCG"


def test_finds_a_hand_made_transposon() -> None:
    dna = "GGGGG" + REPEAT + "A" * MIN_GAP + "CGATCAGTAAGT" + "GGGGG"
    assert find_transposons(dna) == [Transposon(5, 5 + 2 * IR_LENGTH + MIN_GAP, REPEAT)]


def test_repeats_closer_than_min_gap_are_not_a_transposon() -> None:
    dna = "GGGGG" + REPEAT + "A" * (MIN_GAP - 1) + "CGATCAGTAAGT" + "GGGGG"
    assert find_transposons(dna) == []


def test_finds_every_planted_transposon_in_every_case() -> None:
    for case, steps in CASES.items():
        for seed in range(200):
            dna, planted = make_sequence(steps, random.Random(seed))
            assert find_transposons(dna) == planted, f"{case}, seed {seed}"


def test_relations_name_nested_and_overlapping() -> None:
    outer, inner, partner = Transposon(0, 100, ""), Transposon(20, 60, ""), Transposon(80, 140, "")
    assert relations([outer, inner, partner]) == ["overlaps T3", "inside T1", "overlaps T1"]
    assert relations([Transposon(0, 40, ""), Transposon(50, 90, "")]) == ["-", "-"]

# @author: SeriouslyAndy(JavaKet)
# @date: 06-11-2026

"""Tests for transposons.py and make_sequence.py."""

import random

from make_sequence import MAX_TOTAL, MIN_TOTAL, make_sequence
from transposons import Element, find_elements, read_records, reverse_complement


def test_reverse_complement() -> None:
    assert reverse_complement("AACG") == "CGTT"


def test_finds_a_hand_made_element() -> None:
    element = "GGATCCAC" + "AAAACCCCAAAA" + reverse_complement("GGATCCAC")
    dna = "TTTTTTTTTT" + "CATGC" + element + "CATGC" + "TTTTT"
    assert find_elements(dna) == [Element(16, 43, "GGATCCAC", "CATGC")]


def test_finds_every_planted_element() -> None:
    """Each found element covers its planted one.

    Random flanking bases sometimes pair up by chance, which makes an element look a few bases
    wider than planted, so the test checks covering and not equality.
    """
    for seed in range(100):
        sequence, planted = make_sequence(random.Random(seed))
        found = find_elements(sequence)
        assert MIN_TOTAL <= len(sequence) <= MAX_TOTAL
        assert len(found) == len(planted), f"seed {seed}"
        for wide, exact in zip(found, planted):
            assert wide.start <= exact.start and exact.stop <= wide.stop, f"seed {seed}"


def test_read_records_takes_fasta_or_plain_text() -> None:
    assert read_records([">a b\n", "acg\n", "t\n", ">c\n", "GG\n"], "x") == [
        ("a b", "ACGT"),
        ("c", "GG"),
    ]
    assert read_records(["ACGT\n"], "sequence.txt") == [("sequence.txt", "ACGT")]

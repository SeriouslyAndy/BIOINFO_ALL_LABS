# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Tests for codons.py."""

from collections import Counter

from codons import CODONS, amino_acid_name, amino_acid_profile, count_codons, parse_fasta


def test_parse_fasta_splits_records_and_turns_dna_into_rna() -> None:
    lines = [">first\n", "atg ac\n", "GT\n", ">second\n", "TTT\n"]
    assert parse_fasta(lines) == ["AUGACGU", "UUU"]


def test_parse_fasta_without_header_reads_one_record() -> None:
    assert parse_fasta(["ACGT\n"]) == ["ACGU"]


def test_count_codons_slides_one_letter_at_a_time() -> None:
    counts = count_codons(["AUGAUG"])
    assert counts["AUG"] == 2
    assert counts["UGA"] == 1
    assert counts["GAU"] == 1
    assert sum(counts.values()) == 4


def test_count_codons_lists_all_64_and_skips_unknown_letters() -> None:
    counts = count_codons(["AUNAUG"])
    assert len(counts) == len(CODONS) == 64
    assert sum(counts.values()) == 1


def test_count_codons_does_not_join_records() -> None:
    assert sum(count_codons(["AU", "GA"]).values()) == 0


def test_amino_acid_names_follow_the_genetic_code() -> None:
    assert amino_acid_name("AUG") == "Methionine"
    assert amino_acid_name("UGG") == "Tryptophan"
    assert {amino_acid_name(codon) for codon in ("UAA", "UAG", "UGA")} == {"Stop"}


def test_amino_acid_profile_adds_synonymous_codons() -> None:
    profile = amino_acid_profile(Counter({"UUU": 2, "UUC": 3, "AUG": 1}))
    assert profile["Phenylalanine"] == 5
    assert profile["Methionine"] == 1

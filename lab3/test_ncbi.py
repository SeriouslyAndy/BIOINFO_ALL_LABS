# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Tests for ncbi.py that need no network."""

from ncbi import Genome, parse_assembly_summary


def summary_line(accession: str, organism: str, strain: str, ftp: str) -> str:
    """One tab-separated line of assembly_summary.txt with only the columns the app reads."""
    fields = ["x"] * 20
    fields[0], fields[7], fields[8], fields[19] = accession, organism, strain, ftp
    return "\t".join(fields)


def test_parse_assembly_summary_skips_comments_and_missing_ftp() -> None:
    text = "\n".join(
        [
            "# assembly_accession\tbioproject",
            summary_line("GCF_1", "Influenza A virus", "na", "https://ftp/GCF_1"),
            summary_line("GCF_2", "Lost virus", "strain X", "na"),
        ]
    )
    assert parse_assembly_summary(text) == [
        Genome("GCF_1", "Influenza A virus", "", "https://ftp/GCF_1")
    ]


def test_genome_label_leaves_out_empty_parts() -> None:
    assert Genome("GCF_1", "Rabies virus", "", "ftp").label() == "Rabies virus · GCF_1"

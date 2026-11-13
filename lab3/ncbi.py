# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Find viral genomes on NCBI and download them, keeping a copy in the cache folder."""

import gzip
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import requests

from codons import parse_fasta

CACHE = Path(__file__).parent / "cache"
SUMMARY_URL = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/viral/assembly_summary.txt"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

SUMMARY_MAX_AGE_S = 86_400
DOWNLOAD_TIMEOUT_S = 300
QUERY_TIMEOUT_S = 60
MAX_RESULTS = 50

# Columns of assembly_summary.txt, which is tab separated.
ACCESSION_COLUMN = 0
ORGANISM_COLUMN = 7
STRAIN_COLUMN = 8
FTP_COLUMN = 19
MISSING = "na"


@dataclass(frozen=True)
class Genome:
    """One genome assembly that can be downloaded from the NCBI FTP site."""

    accession: str
    organism: str
    strain: str
    ftp: str

    def label(self) -> str:
        """The text shown in the genome list, such as "Influenza A virus · H1N1 · GCF_0001"."""
        return " · ".join(part for part in (self.organism, self.strain, self.accession) if part)


def is_fresh(path: Path, max_age_s: float | None) -> bool:
    """Whether a cached file exists and is younger than max_age_s (any age when that is None)."""
    if not path.exists():
        return False
    return max_age_s is None or time.time() - path.stat().st_mtime <= max_age_s


def download(url: str, name: str, max_age_s: float | None = None) -> Path:
    """Download a file into the cache, unless a fresh copy is already there."""
    path = CACHE / name
    if is_fresh(path, max_age_s):
        return path
    CACHE.mkdir(exist_ok=True)
    response = requests.get(url, timeout=DOWNLOAD_TIMEOUT_S)
    response.raise_for_status()
    path.write_bytes(response.content)
    return path


def parse_assembly_summary(text: str) -> list[Genome]:
    """Read NCBI's assembly_summary.txt, skipping comments and assemblies without an FTP folder."""
    genomes = []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        fields = line.split("\t")
        if fields[FTP_COLUMN] == MISSING:
            continue
        strain = fields[STRAIN_COLUMN] if fields[STRAIN_COLUMN] != MISSING else ""
        genomes.append(
            Genome(fields[ACCESSION_COLUMN], fields[ORGANISM_COLUMN], strain, fields[FTP_COLUMN])
        )
    return genomes


@lru_cache
def load_assemblies() -> tuple[Genome, ...]:
    """All RefSeq viral assemblies, refreshed once a day."""
    path = download(SUMMARY_URL, "assembly_summary.txt", max_age_s=SUMMARY_MAX_AGE_S)
    return tuple(parse_assembly_summary(path.read_text()))


def search_entrez(query: str) -> list[Genome]:
    """Ask NCBI Entrez for the latest assemblies of an organism, for names the RefSeq list lacks."""
    term = f'"{query}"[Organism] AND latest[filter]'
    params: dict[str, str | int] = {
        "db": "assembly",
        "term": term,
        "retmax": MAX_RESULTS,
        "retmode": "json",
    }
    found = requests.get(f"{EUTILS}/esearch.fcgi", params=params, timeout=QUERY_TIMEOUT_S)
    ids = found.json()["esearchresult"]["idlist"]
    if not ids:
        return []
    params = {"db": "assembly", "id": ",".join(ids), "retmode": "json"}
    summary = requests.get(f"{EUTILS}/esummary.fcgi", params=params, timeout=QUERY_TIMEOUT_S)
    result = summary.json()["result"]
    genomes = []
    for uid in result["uids"]:
        item = result[uid]
        ftp = item["ftppath_refseq"] or item["ftppath_genbank"]
        if not ftp:
            continue
        organism = item["organism"].removesuffix(" (viruses)")
        https = ftp.replace("ftp://", "https://")
        genomes.append(Genome(item["assemblyaccession"], organism, item["speciesname"], https))
    return genomes


def search(query: str) -> list[Genome]:
    """Genomes whose organism name contains the query, from RefSeq first and then from Entrez."""
    query = query.replace("_", " ").strip()
    needle = query.lower()
    local = [genome for genome in load_assemblies() if needle in genome.organism.lower()]
    try:
        remote = search_entrez(query)
    except requests.RequestException:
        # Entrez only adds extra matches, so the RefSeq list alone is still a useful answer.
        remote = []
    unique: dict[str, Genome] = {}
    for genome in local + remote:
        unique.setdefault(genome.accession, genome)
    return list(unique.values())


def download_genome(genome: Genome) -> list[str]:
    """Download a genome and return its records (segments) as RNA strings."""
    name = genome.ftp.rstrip("/").split("/")[-1]
    path = download(f"{genome.ftp}/{name}_genomic.fna.gz", f"{genome.accession}.fna.gz")
    with gzip.open(path, "rt") as file:
        return parse_fasta(file)

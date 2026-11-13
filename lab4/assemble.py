# @author: SeriouslyAndy(JavaKet)
# @date: 30-10-2026

"""Exercise 1: break a genome into random reads, then put it back together from the reads alone.

Takes 20 000 random windows of 100 to 150 letters from the lab 3 genome and saves them to
samples.txt, as if someone handed them to us on a drive. The genome is then rebuilt by joining
reads that overlap by at least 10 letters, first to the right of the first read, then to its left.

Examples:
    python assemble.py
    python assemble.py my_genome.fasta
"""

import argparse
import random
import time
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_GENOME = HERE.parent / "lab3" / "GCF_002194405.1_ViralProj390412_genomic.fna"
SAMPLES_PATH = HERE / "samples.txt"

SAMPLES = 20_000
MIN_LENGTH = 100
MAX_LENGTH = 150
MIN_OVERLAP = 10


def read_genome(path: Path) -> str:
    """All sequence lines of a FASTA file joined into one upper case string."""
    with path.open() as file:
        return "".join(line.strip() for line in file if not line.startswith(">")).upper()


def sample_windows(genome_length: int, rng: random.Random) -> list[tuple[int, int]]:
    """SAMPLES random (start, end) windows of MIN_LENGTH to MAX_LENGTH letters, end excluded."""
    windows = []
    for _ in range(SAMPLES):
        length = rng.randint(MIN_LENGTH, MAX_LENGTH)
        start = rng.randint(0, genome_length - length)
        windows.append((start, start + length))
    return windows


def count_covered(genome_length: int, windows: list[tuple[int, int]]) -> int:
    """How many positions of the genome at least one window covers."""
    covered = bytearray(genome_length)
    for start, end in windows:
        covered[start:end] = b"\x01" * (end - start)
    return sum(covered)


def save_samples(path: Path, samples: list[str]) -> None:
    path.write_text("".join(sample + "\n" for sample in samples))


def load_samples(path: Path) -> list[str]:
    return path.read_text().splitlines()


def find_next(
    contig: str, samples: list[str], index: dict[str, list[int]], used: set[int]
) -> tuple[int, int] | None:
    """The unused sample with the longest overlap with the end of contig, and that overlap.

    An overlap is a tail of contig, at least MIN_OVERLAP letters long, that a longer sample
    starts with.
    """
    longest_tail = min(len(contig), MAX_LENGTH - 1)
    for tail_length in range(longest_tail, MIN_OVERLAP - 1, -1):
        tail = contig[-tail_length:]
        for i in index.get(tail[:MIN_OVERLAP], []):
            sample = samples[i]
            if i not in used and len(sample) > tail_length and sample.startswith(tail):
                return i, tail_length
    return None


def extend(contig: str, samples: list[str]) -> str:
    """Grow contig to the right with overlapping samples until no sample fits."""
    index: dict[str, list[int]] = {}
    for i, sample in enumerate(samples):
        index.setdefault(sample[:MIN_OVERLAP], []).append(i)

    used: set[int] = set()
    while True:
        found = find_next(contig, samples, index, used)
        if found is None:
            return contig
        i, overlap = found
        used.add(i)
        contig += samples[i][overlap:]


def rebuild(samples: list[str]) -> str:
    """Rebuild the genome: extend the first sample to the right, then to the left.

    Growing to the left is growing to the right on reversed strings.
    """
    right = extend(samples[0], samples)
    reversed_samples = [sample[::-1] for sample in samples]
    return extend(right[::-1], reversed_samples)[::-1]


def describe(genome: str, rebuilt: str) -> str:
    """How the rebuilt genome compares with the original, in one sentence."""
    if rebuilt == genome:
        return "rebuilt genome is identical to the original"
    position = genome.find(rebuilt)
    if position < 0:
        return "rebuilt genome differs from the original"
    end = position + len(rebuilt)
    return (
        f"matches the original from {position + 1} to {end} "
        f"({position} letters missing at the start, {len(genome) - end} at the end)"
    )


def main() -> None:
    """Break the genome given on the command line into samples, rebuild it and report."""
    parser = argparse.ArgumentParser(description="Break a genome into reads and rebuild it")
    parser.add_argument("fasta", nargs="?", type=Path, default=DEFAULT_GENOME)
    path: Path = parser.parse_args().fasta

    started = time.perf_counter()
    genome = read_genome(path)
    windows = sample_windows(len(genome), random.Random())
    covered = count_covered(len(genome), windows)
    save_samples(SAMPLES_PATH, [genome[start:end] for start, end in windows])
    samples = load_samples(SAMPLES_PATH)
    rebuilt = rebuild(samples)

    print(f"Genome length:     {len(genome)}")
    print(
        f"Samples:           {len(samples)} ({MIN_LENGTH}-{MAX_LENGTH} letters, "
        f"saved to {SAMPLES_PATH.name})"
    )
    share = covered / len(genome) * 100
    print(f"Covered positions: {covered} / {len(genome)} ({share:.2f}%)")
    print(f"Rebuilt length:    {len(rebuilt)}")
    print(f"Result:            {describe(genome, rebuilt)}")
    print(f"Time:              {time.perf_counter() - started:.2f} s")


if __name__ == "__main__":
    main()

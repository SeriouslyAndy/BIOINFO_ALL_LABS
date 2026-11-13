# @author: SeriouslyAndy(JavaKet)
# @date: 06-11-2026

"""Exercise 1: make a random DNA sequence of 200 to 400 bases with 3 or 4 transposable elements.

The sequence is saved to sequence.txt and the planted elements are printed, so that
find_transposons.py can be checked against them.
"""

import random
from pathlib import Path

from transposons import Element, format_table, reverse_complement

SEQUENCE_PATH = Path(__file__).parent / "sequence.txt"
BASES = "ACGT"

INVERTED_REPEAT = 8
DIRECT_REPEAT = 5
MIN_CORE = 10
MAX_CORE = 30
MIN_ELEMENTS = 3
MAX_ELEMENTS = 4
MIN_TOTAL = 200
MAX_TOTAL = 400
# The host keeps at least this many bases of its own around the elements.
MIN_HOST = 100
# Keeps an insertion site this far from the edges of its stretch of host.
SITE_MARGIN = 2


def random_dna(length: int, rng: random.Random) -> str:
    return "".join(rng.choices(BASES, k=length))


def make_transposon(rng: random.Random) -> str:
    """An inverted repeat, a random core and the reverse complement of that repeat."""
    repeat = random_dna(INVERTED_REPEAT, rng)
    core = random_dna(rng.randint(MIN_CORE, MAX_CORE), rng)
    return repeat + core + reverse_complement(repeat)


def insert(host: str, transposons: list[str], rng: random.Random) -> tuple[str, list[Element]]:
    """Insert each transposon into its own stretch of host, copying the target site after it.

    The DIRECT_REPEAT host bases right before the site end up on both sides of the element.
    """
    stretch = len(host) // len(transposons)
    parts: list[str] = []
    length = 0
    elements = []
    previous = 0
    for i, transposon in enumerate(transposons):
        lowest = i * stretch + DIRECT_REPEAT + SITE_MARGIN
        site = rng.randint(lowest, (i + 1) * stretch - SITE_MARGIN)
        repeat = host[site - DIRECT_REPEAT : site]
        parts.append(host[previous:site])
        length += site - previous
        repeats = transposon[:INVERTED_REPEAT]
        elements.append(Element(length + 1, length + len(transposon), repeats, repeat))
        parts += [transposon, repeat]
        length += len(transposon) + len(repeat)
        previous = site
    parts.append(host[previous:])
    return "".join(parts), elements


def make_sequence(rng: random.Random) -> tuple[str, list[Element]]:
    """A sequence of MIN_TOTAL to MAX_TOTAL bases with its planted elements."""
    transposons = [make_transposon(rng) for _ in range(rng.randint(MIN_ELEMENTS, MAX_ELEMENTS))]
    inserted = sum(len(transposon) + DIRECT_REPEAT for transposon in transposons)
    total = rng.randint(max(MIN_TOTAL, inserted + MIN_HOST), MAX_TOTAL)
    return insert(random_dna(total - inserted, rng), transposons, rng)


def main() -> None:
    sequence, elements = make_sequence(random.Random())
    SEQUENCE_PATH.write_text(sequence + "\n")
    print(f"Sequence ({len(sequence)} bases, saved to {SEQUENCE_PATH.name}):")
    print(sequence)
    print()
    print("\n".join(format_table(elements)))


if __name__ == "__main__":
    main()

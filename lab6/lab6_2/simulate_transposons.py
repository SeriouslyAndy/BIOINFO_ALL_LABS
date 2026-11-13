# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Second task: plant transposons in random DNA and find them again.

One sequence per case: transposons one after the other, one nested inside another, and two that
overlap. The positions of the planted transposons are known, so the finder can be checked
against them. Each run is different: the random generator is seeded from the operating system.

Run with: python simulate_transposons.py
"""

import random
import textwrap

from inverted_repeats import (
    IR_LENGTH,
    MIN_GAP,
    Transposon,
    find_transposons,
    format_table,
    repeat_pairs,
    reverse_complement,
)

BASES = "ACGT"
MAX_GAP = 30
MIN_FLANK = 5
MAX_FLANK = 20
LINE_WIDTH = 80

# Each case is the order in which transposon ends appear along the sequence:
# ("open", 0) is the left repeat of transposon 0, ("close", 0) its right repeat.
CASES = {
    "One after the other": [("open", 0), ("close", 0), ("open", 1), ("close", 1)],
    "Nested": [("open", 0), ("open", 1), ("close", 1), ("close", 0)],
    "Overlapping": [("open", 0), ("open", 1), ("close", 0), ("close", 1)],
}


def random_dna(length: int, rng: random.Random) -> str:
    return "".join(rng.choices(BASES, k=length))


def random_repeats(count: int, rng: random.Random) -> list[str]:
    """count inverted repeats that cannot pair with themselves or with each other."""
    while True:
        repeats = [random_dna(IR_LENGTH, rng) for _ in range(count)]
        ends = repeats + [reverse_complement(repeat) for repeat in repeats]
        if len(set(ends)) == len(ends):
            return repeats


def build(steps: list[tuple[str, int]], rng: random.Random) -> tuple[str, list[Transposon]]:
    """Lay out the repeats in the order of steps, with random DNA of MIN_GAP to MAX_GAP bases
    between them and a random flank at both ends."""
    repeats = random_repeats(len(steps) // 2, rng)
    parts = [random_dna(rng.randint(MIN_FLANK, MAX_FLANK), rng)]
    length = len(parts[0])
    starts: dict[int, int] = {}
    ends: dict[int, int] = {}
    for index, (action, number) in enumerate(steps):
        if index > 0:
            gap = random_dna(rng.randint(MIN_GAP, MAX_GAP), rng)
            parts.append(gap)
            length += len(gap)
        if action == "open":
            parts.append(repeats[number])
            starts[number] = length
        else:
            parts.append(reverse_complement(repeats[number]))
        length += IR_LENGTH
        if action == "close":
            ends[number] = length
    parts.append(random_dna(rng.randint(MIN_FLANK, MAX_FLANK), rng))
    planted = [Transposon(starts[n], ends[n], repeats[n]) for n in sorted(starts)]
    return "".join(parts), sorted(planted)


def make_sequence(steps: list[tuple[str, int]], rng: random.Random) -> tuple[str, list[Transposon]]:
    """A sequence for one case, redrawn until the planted repeats are the only ones in it.

    Random DNA sometimes holds an inverted repeat pair by chance, or lengthens a planted repeat
    by a base. Either would make the planted list an incomplete answer.
    """
    while True:
        dna, planted = build(steps, rng)
        expected = {(transposon.start, transposon.end - IR_LENGTH) for transposon in planted}
        if repeat_pairs(dna) == expected:
            return dna, planted


def main() -> None:
    rng = random.Random()
    for case, steps in CASES.items():
        dna, planted = make_sequence(steps, rng)
        found = find_transposons(dna)
        print(f"=== {case} ({len(dna)} bases) ===")
        print("\n".join(textwrap.wrap(dna, LINE_WIDTH)))
        print()
        print("Planted:")
        print("\n".join(format_table(planted)))
        print()
        print("Found:")
        print("\n".join(format_table(found)))
        print()
        verdict = "matches" if found == planted else "does NOT match"
        print(f"The finder {verdict} the planted transposons.")
        print()


if __name__ == "__main__":
    main()

# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Transposons as pairs of inverted repeats, and a finder that also sees nested and overlapping
ones.

A transposon here starts with an inverted repeat ("ACTTACTGAT...") and ends with its reverse
complement ("...ATCAGTAAGT"), like the IS1 element. The two repeats are at least MIN_GAP bases
apart.
"""

from dataclasses import dataclass

IR_LENGTH = 12
MIN_GAP = 10
COMPLEMENT = str.maketrans("ACGT", "TGCA")


@dataclass(frozen=True, order=True)
class Transposon:
    """A transposon at dna[start:end], 0-based with end excluded.

    repeat is its left inverted repeat.
    """

    start: int
    end: int
    repeat: str

    @property
    def length(self) -> int:
        return self.end - self.start


def reverse_complement(dna: str) -> str:
    return dna.translate(COMPLEMENT)[::-1]


def repeat_pairs(dna: str) -> set[tuple[int, int]]:
    """Every (i, j) where dna[j:j + IR_LENGTH] is the reverse complement of dna[i:i + IR_LENGTH]
    and at least MIN_GAP bases separate the two."""
    positions: dict[str, list[int]] = {}
    for i in range(len(dna) - IR_LENGTH + 1):
        positions.setdefault(dna[i : i + IR_LENGTH], []).append(i)
    pairs = set()
    for i in range(len(dna) - IR_LENGTH + 1):
        partner = reverse_complement(dna[i : i + IR_LENGTH])
        for j in positions.get(partner, []):
            if j >= i + IR_LENGTH + MIN_GAP:
                pairs.add((i, j))
    return pairs


def find_transposons(dna: str) -> list[Transposon]:
    """All transposons in dna, sorted by start. Nested and overlapping ones are found too.

    A repeat longer than IR_LENGTH shows up as a run of pairs (i, j), (i + 1, j - 1), ... and is
    reported once, from its outermost pair.
    """
    pairs = repeat_pairs(dna)
    found = []
    for i, j in sorted(pairs):
        if (i - 1, j + 1) in pairs:
            continue
        run = 1
        while (i + run, j - run) in pairs:
            run += 1
        found.append(Transposon(i, j + IR_LENGTH, dna[i : i + IR_LENGTH + run - 1]))
    return found


def relations(transposons: list[Transposon]) -> list[str]:
    """For each transposon, which others it sits inside of or overlaps, such as "inside T1"."""
    described = []
    for a in transposons:
        parts = []
        for number, b in enumerate(transposons, start=1):
            if a == b or a.end <= b.start or b.end <= a.start:
                continue
            if b.start <= a.start and a.end <= b.end:
                parts.append(f"inside T{number}")
            elif not (a.start <= b.start and b.end <= a.end):
                parts.append(f"overlaps T{number}")
        described.append(", ".join(parts) or "-")
    return described


def format_table(transposons: list[Transposon]) -> list[str]:
    """Table lines with 1-based positions, both ends included, under a header line."""
    lines = ["#    Start    End  Length  Inverted repeat  Relation"]
    for number, (transposon, relation) in enumerate(
        zip(transposons, relations(transposons)), start=1
    ):
        lines.append(
            f"T{number:<3d} {transposon.start + 1:5d}  {transposon.end:5d}  "
            f"{transposon.length:6d}  {transposon.repeat:<15}  {relation}"
        )
    return lines

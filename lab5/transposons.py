# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Transposable elements: what one looks like and how to find them in a DNA sequence.

An element is a core flanked by inverted repeats ("ACGTTGCA ... TGCAACGT", the right end is the
reverse complement of the left end), and the whole element sits between two copies of a short
direct repeat (the target site duplication made when it was inserted).
"""

from collections.abc import Iterable
from dataclasses import dataclass

MIN_INVERTED_REPEAT = 8
MIN_DIRECT_REPEAT = 4
MAX_DIRECT_REPEAT = 10
MIN_CORE = 5
MAX_ELEMENT = 100

COMPLEMENT = str.maketrans("ACGT", "TGCA")


@dataclass(frozen=True)
class Element:
    """A transposable element. start and stop are 1-based and both inside the element."""

    start: int
    stop: int
    inverted_repeat: str
    direct_repeat: str


def reverse_complement(dna: str) -> str:
    return dna.translate(COMPLEMENT)[::-1]


def direct_repeat(dna: str, start: int, end: int) -> str | None:
    """The longest direct repeat right before dna[start:end] and right after it, if any."""
    for length in range(min(MAX_DIRECT_REPEAT, start), MIN_DIRECT_REPEAT - 1, -1):
        left = dna[start - length : start]
        if left == dna[end : end + length]:
            return left
    return None


def find_end(dna: str, start: int) -> tuple[int, str] | None:
    """End (excluded) and direct repeat of an element starting at start, or None.

    The element ends with the reverse complement of its first MIN_INVERTED_REPEAT letters, has a
    core of at least MIN_CORE letters, is at most MAX_ELEMENT letters long and has a direct
    repeat around it. The shortest such element wins.
    """
    target = reverse_complement(dna[start : start + MIN_INVERTED_REPEAT])
    first = start + MIN_INVERTED_REPEAT + MIN_CORE
    last = min(len(dna) - MIN_INVERTED_REPEAT, start + MAX_ELEMENT)
    j = dna.find(target, first, last + MIN_INVERTED_REPEAT)
    while j >= 0:
        end = j + MIN_INVERTED_REPEAT
        repeat = direct_repeat(dna, start, end)
        if repeat is not None:
            return end, repeat
        j = dna.find(target, j + 1, last + MIN_INVERTED_REPEAT)
    return None


def inverted_repeat(dna: str, start: int, end: int) -> str:
    """The left inverted repeat of dna[start:end], grown past MIN_INVERTED_REPEAT while it pairs.

    It stops at the middle of the element, so the two repeats never overlap.
    """
    length = MIN_INVERTED_REPEAT
    while (
        start + length < end - 1 - length
        and dna[start + length].translate(COMPLEMENT) == dna[end - 1 - length]
    ):
        length += 1
    return dna[start : start + length]


def find_elements(dna: str) -> list[Element]:
    """Scan dna from left to right. After an element is found, the scan goes on after its end."""
    elements = []
    i = 0
    while i < len(dna) - MIN_INVERTED_REPEAT:
        found = find_end(dna, i)
        if found is None:
            i += 1
            continue
        end, repeat = found
        elements.append(Element(i + 1, end, inverted_repeat(dna, i, end), repeat))
        i = end
    return elements


def read_records(lines: Iterable[str], name: str) -> list[tuple[str, str]]:
    """(header, sequence) pairs from FASTA lines. Text without a header is one record, name."""
    records: list[tuple[str, str]] = []
    header = name
    parts: list[str] = []
    for line in lines:
        if not line.startswith(">"):
            parts.append("".join(line.split()).upper())
            continue
        if parts:
            records.append((header, "".join(parts)))
        header, parts = line[1:].strip(), []
    if parts:
        records.append((header, "".join(parts)))
    return records


def format_table(elements: list[Element]) -> list[str]:
    """The elements as table lines, under a header line."""
    lines = ["#    Start     End  Inverted repeat           Direct repeat"]
    for number, element in enumerate(elements, start=1):
        left = element.inverted_repeat
        repeats = f"{left}/{reverse_complement(left)}"
        lines.append(
            f"{number:<3d} {element.start:6d}  {element.stop:6d}  {repeats:<25} "
            f"{element.direct_repeat}"
        )
    return lines

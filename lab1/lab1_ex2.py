# @author: SeriouslyAndy(JavaKet)
# @date: 09-10-2026

import random

ALPHABET = "ACGT"


def generate_dna(length):
    # build a random DNA sequence, one letter at a time
    sequence = ""
    for i in range(length):
        sequence = sequence + random.choice(ALPHABET)
    return sequence


def count_groups(s, size):
    # count every group of letters in s (size)
    # ACGT with size 2 gives AC CG GT
    counts = {}
    for i in range(len(s) - size + 1):
        group = s[i : i + size]
        if group in counts:
            counts[group] = counts[group] + 1
        else:
            counts[group] = 1
    return counts


def print_frequencies(s, size):
    counts = count_groups(s, size)
    total = len(s) - size + 1  # how many groups

    for group in sorted(counts):
        count = counts[group]
        freq = count / total
        print(group, ":", count, "(", round(freq * 100, 3), "%)")


if __name__ == "__main__":
    s = generate_dna(20)

    print("Seq:", s)
    print("Len:", len(s))
    print()
    print()
    print_frequencies(s, 2)
    print()
    print_frequencies(s, 3)

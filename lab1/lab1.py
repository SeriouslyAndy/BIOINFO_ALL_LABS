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


def count_letters(s):
    # count how many times each letter appears in s
    counts = {}
    for letter in s:
        if letter in counts:
            counts[letter] = counts[letter] + 1
        else:
            counts[letter] = 1
    return counts


if __name__ == "__main__":
    s = generate_dna(20)
    total = len(s)

    print("Seq:", s)
    print("Len:", total)
    print()

    counts = count_letters(s)
    for letter in sorted(counts):
        count = counts[letter]
        freq = count / total
        print(letter, ":", count, "(", round(freq * 100, 2), "%)")

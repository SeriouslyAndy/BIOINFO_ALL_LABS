<!--
@author: SeriouslyAndy(JavaKet)
@date: 13-11-2026
-->

# Lab 6, second task – Nested and overlapping transposons

Make random DNA and insert inverted repeats in it to simulate transposons. Because we planted
them, we know the right answer and can check the finder against it. The two inverted repeats of a
transposon are at least 10 bases apart. Three cases are covered:

1. transposons one after the other,
2. a transposon nested inside another,
3. two transposons that overlap.

The output is the position and the length of each transposon in each sequence.

```bash
python simulate_transposons.py
```

Each run makes one sequence per case and prints it, the planted transposons and the ones the
finder found, with positions counted from 1 and both ends included. The random generator is
seeded from the operating system, so every run is different.

| File | What it holds |
|---|---|
| `inverted_repeats.py` | The transposon type and the finder |
| `simulate_transposons.py` | Builds the three cases and prints the results |

The inverted repeats are 12 bases long. Unlike the lab 5 finder, this one does not skip ahead
after a hit, so it also sees transposons inside or across other ones. A sequence that happens to
hold an extra inverted repeat pair by chance (about 1 in 1 000) is redrawn, so the planted list
is always the full answer.

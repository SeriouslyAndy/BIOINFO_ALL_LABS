<!--
@author: SeriouslyAndy(JavaKet)
@date: 13-11-2026
-->

# Lab 5 – Transposable elements

A transposable element here is a core between two inverted repeats (the right one is the reverse
complement of the left one), with a short direct repeat on both sides of the element.

## Exercise 1

Make an artificial DNA sequence of 200 to 400 bases with 3 to 4 transposable elements in it.

```bash
python make_sequence.py                # saves sequence.txt and prints the planted elements
```

## Exercise 2

Find the start and end of each transposable element in the sequence from exercise 1.
`transposons_graph.jpg` is the graph that goes with this exercise.

```bash
python find_transposons.py             # reads sequence.txt
```

## Exercise 3

Look for transposable elements in a FASTA file instead of a generated sequence.

```bash
python find_transposons.py ../lab3/GCF_002194405.1_ViralProj390412_genomic.fna
```

Bases on either side of an element sometimes pair up by chance. The element then shows up with a
slightly longer inverted repeat, or a few bases wider, than the one that was planted.

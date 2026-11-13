<!--
@author: SeriouslyAndy(JavaKet)
@date: 30-10-2026
-->

# Lab 4 – Breaking and rebuilding a genome

## Exercise 1

Take the genome from lab 3 and cut 20 000 random windows of 100 to 150 letters from it, hoping
that together they cover the whole genome. Pretend someone handed us these samples on a drive and
rebuild the genome from them. Overlaps shorter than 10 letters carry too little information, so
they are not used.

```bash
python assemble.py                     # the lab 3 genome
python assemble.py my_genome.fasta
```

The samples are saved to `samples.txt`, which git ignores. The genome is rebuilt by growing the
first sample to the right and then to the left, each time with the unused sample that has the
longest overlap. Positions that no sample happens to cover, usually a few letters at the ends,
cannot be rebuilt, and the output says how many are missing.

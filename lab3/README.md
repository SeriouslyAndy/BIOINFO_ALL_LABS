<!--
@author: SeriouslyAndy(JavaKet)
@date: 23-10-2026
-->

# Lab 3 – Codon frequencies

## Exercise 1

Open a FASTA file with a viral or bacterial genome and count how often each of the 64 codons
appears. A window of exactly 3 letters slides over the sequence one letter at a time, and each
window adds one to the counter of its codon in a dictionary (`{"AUG": 0, ...}`). Show the 10 most
frequent codons.

```bash
python count_codons.py                 # the coronavirus genome in this folder
python count_codons.py my_genome.fasta
```

The genome in this folder is `GCF_002194405.1`, Coronavirus AcCoV-JC34 (`NC_034972.1`). Labs 4
and 5 use it too.

## Virus Diet Explorer

A desktop app built on the same codon count. Search a virus by name on NCBI, pick a genome and
press Analyze. The app shows the codons, the amino acid profile, and the foods from the USDA SR
Legacy database whose amino acid mix is most and least like the virus's. It is a lab proof of
concept, not medical advice.

```bash
pip install -r requirements.txt
python app.py
```

Downloads (the RefSeq viral list, genomes and the USDA database) are kept in `cache/`, which git
ignores.

| File | What it holds |
|---|---|
| `codons.py` | FASTA reading, codon counting, the genetic code |
| `count_codons.py` | Exercise 1, on the command line |
| `ncbi.py` | Genome search and download, and the download cache |
| `foods.py` | USDA foods and their ranking against a virus |
| `analysis.py` | One full analysis of a genome |
| `widgets.py`, `app.py` | The Qt window |

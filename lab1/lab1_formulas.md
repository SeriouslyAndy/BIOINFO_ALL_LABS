<!--
@author: SeriouslyAndy(JavaKet)
@date: 09-10-2026
-->

# Lab 1 – Formulas

## Notation

- $s$ — the DNA sequence, e.g. `TCTGAGCATTTCTTACGTAGCTGGTTAAAC`
- $\Sigma = \{A, C, G, T\}$ — the alphabet (the letters DNA can use)
- $x$ — one letter from the alphabet, $x \in \Sigma$
- $s_i$ — the letter at position $i$ in $s$

## 1. Sequence length

$$
N = |s|
$$

The total number of letters in $s$. In code: `len(s)`.

## 2. Absolute frequency (count)

$$
n_x = \sum_{i=1}^{N} [\, s_i = x \,]
$$

$[\, s_i = x \,]$ is 1 if the letter at position $i$ is $x$, and 0 otherwise. So $n_x$ is how many times $x$ appears in $s$.

In code:

```python
if letter in counts:
    counts[letter] = counts[letter] + 1
else:
    counts[letter] = 1
```

## 3. Relative frequency

$$
f_x = \frac{n_x}{N}
$$

The fraction of the sequence made up of letter $x$, a value between 0 and 1.

In code: `freq = count / total`

## 4. Percentage

$$
p_x = f_x \cdot 100\%
$$

In code: `round(freq * 100, 2)` multiplies by 100 and keeps 2 decimals.

## 5. Checks

The counts add up to the length, and the frequencies add up to 1 (100%):

$$
\sum_{x \in \Sigma} n_x = N
\qquad\qquad
\sum_{x \in \Sigma} f_x = 1
$$

## 6. Random generation (`generate_dna`)

`random.choice` picks each letter with equal probability:

$$
P(s_i = x) = \frac{1}{|\Sigma|} = \frac{1}{4} = 25\%
$$

So for a long random sequence, every $f_x$ should come out close to 0.25. With only 30 letters, the results can be noticeably off (like T = 36.67% below).

## Worked example

For `s = TCTGAGCATTTCTTACGTAGCTGGTTAAAC`, $N = 30$:

| Letter $x$ | Count $n_x$ | Relative frequency $f_x = n_x / N$ | Percentage $p_x$ |
|:---:|:---:|:---:|:---:|
| A | 7  | 7 / 30 = 0.2333  | 23.33% |
| C | 6  | 6 / 30 = 0.2000  | 20.00% |
| G | 6  | 6 / 30 = 0.2000  | 20.00% |
| T | 11 | 11 / 30 = 0.3667 | 36.67% |
| **Total** | **30** | **1.0000** | **100%** |

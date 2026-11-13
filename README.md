# Bioinformatics labs

One folder per lab. Each folder holds that lab's code, data, charts and notes.

| Folder | Topic |
|---|---|
| `lab1/` | Random DNA, letter and group frequencies (`lab1_formulas.md` has the maths) |
| `lab2/` | From gene to protein: translation, ORFs, genes per section (see `lab2/README.md`) |
| `lab3/` | Codon frequencies of a genome, and the Virus Diet Explorer app |
| `lab4/` | Breaking a genome into random reads and rebuilding it |
| `lab5/` | Making and finding transposable elements |
| `lab6/` | Restriction digest and a simulated electrophoresis gel |
| `lab6/lab6_2/` | Lab 6, second task: nested and overlapping transposons |

Labs 3 to 5 were first written in Lua and moved to Python. Timed on the same inputs, the Python
versions run as fast as the Lua ones or faster, so none of them needed a faster language.

## Formatting

Python is formatted with Black at 100 columns (settings in `pyproject.toml`):

```bash
pipx run black lab1 lab2 lab3 lab4 lab5 lab6
```

## Checks

Labs 3 to 5 and `lab6/lab6_2` are type checked in strict mode and have tests next to their code:

```bash
pip install -r requirements-dev.txt -r lab3/requirements.txt
black --check lab3 lab4 lab5 lab6/lab6_2
mypy lab3 lab4 lab5 lab6/lab6_2 && pytest lab3 lab4 lab5 lab6/lab6_2
```

<!-- @co-author: SeriouslyAndy(JavaKet) -->

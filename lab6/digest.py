#!/usr/bin/env python3
# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""
Lab 6 - Restriction digest + electrophoresis gel simulation.

Input : a DNA sequence (downloaded from NCBI or a local FASTA) + restriction enzymes
Output: 1) number of cleavages for each enzyme
        2) cleavage positions and fragment lengths
        3) a simulated agarose gel (one lane per enzyme + one lane with all enzymes)

Examples:
    python digest.py                                   # lambda phage, EcoRI BamHI HindIII
    python digest.py -a NC_001416 -e EcoRI HindIII TaqI
    python digest.py -f my_genome.fasta -e EcoRI BamHI HaeIII
    python digest.py -c MyEnz:GACGTC:5                 # custom enzyme NAME:SITE:CUT
"""

import argparse
import math
import os
import urllib.request

# name -> (recognition site 5'->3', cut position inside the site on the top strand)
# e.g. EcoRI  G^AATTC  -> cut after index 1
ENZYMES = {
    "EcoRI": ("GAATTC", 1),  # G^AATTC
    "BamHI": ("GGATCC", 1),  # G^GATCC
    "HindIII": ("AAGCTT", 1),  # A^AGCTT
    "TaqI": ("TCGA", 1),  # T^CGA
    "HaeIII": ("GGCC", 2),  # GG^CC (blunt)
}

NCBI_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    "?db=nuccore&id={acc}&rettype=fasta&retmode=text"
)


# ---------------------------------------------------------------- sequence I/O


def read_fasta(path):
    with open(path) as fh:
        lines = fh.read().splitlines()
    header = lines[0][1:] if lines and lines[0].startswith(">") else "sequence"
    seq = "".join(l.strip() for l in lines if not l.startswith(">"))
    return header, seq.upper()


def fetch_ncbi(accession):
    """Download a FASTA from NCBI (cached as <accession>.fasta next to the script)."""
    path = f"{accession}.fasta"
    if not os.path.exists(path):
        print(f"Downloading {accession} from NCBI ...")
        with urllib.request.urlopen(NCBI_URL.format(acc=accession), timeout=60) as r:
            data = r.read().decode()
        if not data.startswith(">"):
            raise SystemExit(f"NCBI did not return a FASTA for {accession}:\n{data[:300]}")
        with open(path, "w") as fh:
            fh.write(data)
    return read_fasta(path)


# ---------------------------------------------------------------- digestion


def find_cuts(seq, site, cut_offset):
    """Return cut positions (0-based index of the first base AFTER the cut).

    All enzymes used here are palindromic, so scanning the top strand is enough:
    the bottom strand is cut at the mirrored position of the same site.
    """
    cuts = []
    i = seq.find(site)
    while i != -1:
        cuts.append(i + cut_offset)
        i = seq.find(site, i + 1)  # i + 1 -> overlapping sites are found too
    return cuts


def fragments(seq_len, cuts, circular=False):
    """Fragment lengths produced by cutting at the given positions."""
    cuts = sorted(set(cuts))
    if not cuts:
        return [seq_len]
    if circular:
        frags = [b - a for a, b in zip(cuts, cuts[1:])]
        frags.append(seq_len - cuts[-1] + cuts[0])  # piece that wraps around
        return frags
    bounds = [0] + cuts + [seq_len]
    return [b - a for a, b in zip(bounds, bounds[1:])]


def report(name, site, cut_offset, seq, circular):
    cuts = find_cuts(seq, site, cut_offset)
    frags = fragments(len(seq), cuts, circular)
    shown = site[:cut_offset] + "^" + site[cut_offset:]
    print(f"\n=== {name}  ({shown}) ===")
    print(f"Number of cleavages: {len(cuts)}")
    if cuts:
        print("Cleavage positions (1-based, cut is after this base):")
        print("   " + ", ".join(str(c) for c in cuts))
    print(f"Fragments ({len(frags)}), in order along the sequence:")
    print("   " + ", ".join(f"{f} bp" for f in frags))
    return cuts, frags


# ---------------------------------------------------------------- gel simulation

LADDER = [20000, 10000, 7000, 5000, 4000, 3000, 2000, 1500, 1000, 700, 500, 300, 200, 100]


def migration(bp, min_bp=100, max_bp=30000):
    """Distance travelled in the gel (0 = well, 1 = bottom).

    In agarose, migration is roughly linear in log10(length): small fragments run far.
    """
    bp = min(max(bp, min_bp), max_bp)
    return (math.log10(max_bp) - math.log10(bp)) / (math.log10(max_bp) - math.log10(min_bp))


def draw_gel(lanes, title, out="gel.png"):
    """lanes: list of (label, [fragment lengths])."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    all_lanes = [("Ladder", LADDER)] + lanes
    fig, ax = plt.subplots(figsize=(1.6 * len(all_lanes) + 1.5, 8))
    ax.set_facecolor("#111")
    max_len = max(max(f) for _, f in all_lanes)

    for x, (label, frags) in enumerate(all_lanes):
        # well
        ax.add_patch(plt.Rectangle((x - 0.35, -0.04), 0.7, 0.025, color="#444"))
        for bp in frags:
            y = migration(bp)
            # bigger fragments carry more DNA mass -> brighter and thicker band
            # (identical lengths overlap and add up, like on a real gel)
            intensity = 0.35 + 0.65 * (bp / max_len) ** 0.5
            ax.add_patch(
                plt.Rectangle(
                    (x - 0.33, y - 0.004),
                    0.66,
                    0.008 + 0.006 * intensity,
                    color=(1.0, 0.55, 0.15),
                    alpha=intensity,
                )
            )
            if label == "Ladder":
                ax.text(x - 0.45, y, f"{bp}", color="white", fontsize=7, ha="right", va="center")

    ax.set_xlim(-1.1, len(all_lanes) - 0.4)
    ax.set_ylim(1.05, -0.08)  # wells on top
    ax.set_xticks(range(len(all_lanes)))
    ax.set_xticklabels([l for l, _ in all_lanes], rotation=30, ha="right")
    ax.set_yticks([])
    ax.set_title(title)
    ax.text(len(all_lanes) - 0.5, -0.06, "(-)", color="white", ha="right")
    ax.text(len(all_lanes) - 0.5, 1.03, "(+)", color="white", ha="right")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"\nGel image saved to {out}")


# ---------------------------------------------------------------- main


def main():
    p = argparse.ArgumentParser(description="Restriction digest + gel simulation")
    src = p.add_mutually_exclusive_group()
    src.add_argument(
        "-a",
        "--accession",
        default="NC_001416",
        help="NCBI accession (default: NC_001416, bacteriophage lambda)",
    )
    src.add_argument("-f", "--fasta", help="local FASTA file instead of downloading")
    p.add_argument(
        "-e",
        "--enzymes",
        nargs="+",
        default=["EcoRI", "BamHI", "HindIII"],
        help=f"enzymes to use, from: {', '.join(ENZYMES)}",
    )
    p.add_argument(
        "-c",
        "--custom",
        nargs="*",
        default=[],
        help="extra enzymes as NAME:SITE:CUT, e.g. PstI:CTGCAG:5",
    )
    p.add_argument("--circular", action="store_true", help="treat the DNA as circular (plasmid)")
    p.add_argument("-o", "--out", default="gel.png", help="output image for the gel")
    args = p.parse_args()

    enzymes = {}
    for name in args.enzymes:
        if name not in ENZYMES:
            raise SystemExit(f"Unknown enzyme {name}. Known: {', '.join(ENZYMES)}")
        enzymes[name] = ENZYMES[name]
    for spec in args.custom:
        name, site, cut = spec.split(":")
        enzymes[name] = (site.upper(), int(cut))

    header, seq = read_fasta(args.fasta) if args.fasta else fetch_ncbi(args.accession)
    print(f"Sequence: {header}")
    print(f"Length  : {len(seq)} bp  ({'circular' if args.circular else 'linear'})")

    lanes, all_cuts = [], []
    for name, (site, cut) in enzymes.items():
        cuts, frags = report(name, site, cut, seq, args.circular)
        lanes.append((name, frags))
        all_cuts += cuts

    if len(enzymes) > 1:
        combined = fragments(len(seq), all_cuts, args.circular)
        print(f"\n=== All enzymes together ===")
        print(f"Number of cleavages: {len(set(all_cuts))}")
        print("Fragments (sorted, largest first):")
        print("   " + ", ".join(f"{f} bp" for f in sorted(combined, reverse=True)))
        lanes.append(("All", combined))

    draw_gel(lanes, f"{header.split(',')[0]}  ({len(seq)} bp)", args.out)


if __name__ == "__main__":
    main()

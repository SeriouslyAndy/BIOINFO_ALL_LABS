# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Tests for foods.py, on a tiny food table instead of the USDA download."""

from collections import Counter

import pandas as pd

from foods import AMINO_ACID_COLUMNS, rank_foods, virus_vector


def food(description: str, main_amino_acid: str, grams: float) -> dict[str, object]:
    """A food row whose amino acids are all 0.1 g except main_amino_acid."""
    row: dict[str, object] = {name: 0.1 for name in AMINO_ACID_COLUMNS}
    row.update({"description": description, "category": "Test", main_amino_acid: grams})
    return row


def test_virus_vector_merges_usda_pairs_and_drops_stops() -> None:
    vector = virus_vector(Counter({"Asparagine": 2, "Aspartic acid": 3, "Stop": 9}))
    assert list(vector.index) == AMINO_ACID_COLUMNS
    assert vector["Aspartic acid"] == 5
    assert vector.sum() == 5


def test_rank_foods_avoids_the_closest_food_and_skips_low_protein() -> None:
    foods = pd.DataFrame(
        [
            food("Beef, raw", "Leucine", 20),
            food("Beef, cooked", "Leucine", 25),
            food("Fish, raw", "Lysine", 20),
            food("Lettuce, raw", "Leucine", 1),
        ]
    )
    vector = virus_vector(Counter({"Leucine": 10}))
    eat, avoid = rank_foods(foods, vector)
    assert avoid["Food"].iloc[0].startswith("Beef")
    assert eat["Food"].iloc[0] == "Fish, raw"
    assert "Lettuce, raw" not in set(eat["Food"]) | set(avoid["Food"])
    # One row per food group: the two beef rows count once.
    assert len(avoid) == 2

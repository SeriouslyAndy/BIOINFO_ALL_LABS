# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Foods from the USDA SR Legacy database, ranked by how close their amino acids are to a virus's.

The idea of the lab app: a virus whose codons favour some amino acids might do better when the
food eaten supplies those amino acids. It is a proof of concept, not medical advice.
"""

import zipfile
from collections import Counter
from functools import lru_cache

import pandas as pd

from ncbi import download

USDA_URL = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip"
USDA_FOLDER = "FoodData_Central_sr_legacy_food_csv_2018-04/"

# USDA nutrient id -> amino acid name.
USDA_AMINO_ACIDS = {
    1210: "Tryptophan",
    1211: "Threonine",
    1212: "Isoleucine",
    1213: "Leucine",
    1214: "Lysine",
    1215: "Methionine",
    1216: "Cystine",
    1217: "Phenylalanine",
    1218: "Tyrosine",
    1219: "Valine",
    1220: "Arginine",
    1221: "Histidine",
    1222: "Alanine",
    1223: "Aspartic acid",
    1224: "Glutamic acid",
    1225: "Glycine",
    1226: "Proline",
    1227: "Serine",
}
AMINO_ACID_COLUMNS = list(USDA_AMINO_ACIDS.values())

# The USDA reports these amino acids together with the one they are paired with here.
USDA_EQUIVALENT = {
    "Asparagine": "Aspartic acid",
    "Glutamine": "Glutamic acid",
    "Cysteine": "Cystine",
}
MIN_PROTEIN_G = 5
TOP_FOODS = 10


@lru_cache
def load_foods() -> pd.DataFrame:
    """One row per food: description, category and grams of each amino acid per 100 g."""
    archive_path = download(USDA_URL, "usda_sr_legacy.zip")
    with zipfile.ZipFile(archive_path) as archive:
        foods = pd.read_csv(
            archive.open(USDA_FOLDER + "food.csv"),
            usecols=["fdc_id", "description", "food_category_id"],
        )
        categories = pd.read_csv(
            archive.open(USDA_FOLDER + "food_category.csv"), usecols=["id", "description"]
        )
        nutrients = pd.read_csv(
            archive.open(USDA_FOLDER + "food_nutrient.csv"),
            usecols=["fdc_id", "nutrient_id", "amount"],
        )
    categories.columns = pd.Index(["food_category_id", "category"])
    nutrients = nutrients[nutrients["nutrient_id"].isin(list(USDA_AMINO_ACIDS))]
    amounts = nutrients.pivot_table(index="fdc_id", columns="nutrient_id", values="amount")
    amounts = amounts.rename(columns=USDA_AMINO_ACIDS).dropna()
    described = foods.merge(categories, on="food_category_id").set_index("fdc_id")
    return described.join(amounts, how="inner")


def virus_vector(amino_acids: Counter[str]) -> "pd.Series[float]":
    """The virus's amino acid counts, named and ordered like the USDA columns, without stops."""
    vector: Counter[str] = Counter()
    for name, count in amino_acids.items():
        if name != "Stop":
            vector[USDA_EQUIVALENT.get(name, name)] += count
    return pd.Series({name: float(vector[name]) for name in AMINO_ACID_COLUMNS})


def cosine_similarity(amounts: pd.DataFrame, vector: "pd.Series[float]") -> "pd.Series[float]":
    """How alike each row of amounts is to vector, from 0 (nothing alike) to 1 (same mix)."""
    row_lengths = (amounts**2).sum(axis=1) ** 0.5
    vector_length = float((vector**2).sum()) ** 0.5
    similarity: pd.Series[float] = amounts.dot(vector) / (row_lengths * vector_length)
    return similarity


def distinct_foods(ranked: pd.DataFrame) -> pd.DataFrame:
    """The first TOP_FOODS rows, keeping one food per group ("Beef" for "Beef, ground, raw")."""
    groups = ranked["Food"].str.split(",").str[0]
    return ranked[~groups.duplicated()].head(TOP_FOODS)


def rank_foods(
    foods: pd.DataFrame, vector: "pd.Series[float]"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Foods to eat (least like the virus) and to avoid (most like it), 10 of each.

    Only foods with at least MIN_PROTEIN_G grams of amino acids per 100 g are compared.
    """
    protein = foods[AMINO_ACID_COLUMNS].sum(axis=1)
    rich = foods[protein >= MIN_PROTEIN_G]
    similarity = cosine_similarity(rich[AMINO_ACID_COLUMNS], vector)
    ranked = pd.DataFrame(
        {
            "Food": rich["description"],
            "Category": rich["category"],
            "Match %": (similarity * 100).round(2),
            "Protein g/100 g": protein[rich.index].round(1),
        }
    ).sort_values("Match %")
    return distinct_foods(ranked), distinct_foods(ranked.iloc[::-1])

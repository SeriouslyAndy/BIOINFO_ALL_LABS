# @author: SeriouslyAndy(JavaKet)
# @date: 13-11-2026

"""Virus Diet Explorer: search a virus on NCBI, count its codons and compare it with USDA foods.

Run with: python app.py
"""

import logging
import sys
from collections.abc import Callable

import pandas as pd
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from analysis import Analysis, analyze
from codons import amino_acid_name
from foods import MIN_PROTEIN_G
from ncbi import Genome, search
from widgets import Chart, Worker, fill_table, make_table

WINDOW_SIZE = (1200, 800)
TOP_CODONS = 10

SEARCH_FAILED = "Could not search NCBI. Check the internet connection and try again."
ANALYZE_FAILED = (
    "Could not download or analyse this genome. Check the internet connection and try again."
)


def codon_table(codons: "pd.Series[int]") -> pd.DataFrame:
    """The most frequent codons with their count, share of all codons and amino acid."""
    total = codons.sum()
    top = codons.sort_values(ascending=False).head(TOP_CODONS)
    return pd.DataFrame(
        {
            "Codon": top.index,
            "Count": top.to_list(),
            "Frequency": [f"{count / total * 100:.2f}%" for count in top],
            "Amino acid": [amino_acid_name(str(codon)) for codon in top.index],
        }
    )


class Window(QMainWindow):
    """The main window: a search row, a genome row and three result tabs."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Virus Diet Explorer")
        self.resize(*WINDOW_SIZE)
        self.matches: list[Genome] = []
        self.worker: Worker | None = None

        self.query = QLineEdit()
        self.query.setPlaceholderText("Virus name, e.g. influenza, coronavirus, Wanjuvirus PP2")
        self.search_button = QPushButton("Search")
        self.genomes = QComboBox()
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setEnabled(False)
        self.status = QLabel(
            "Type a virus name and press Search. Lab proof of concept, not medical advice."
        )
        self.metrics = QLabel()

        self.top_codons = make_table()
        self.codon_chart = Chart()
        self.amino_chart = Chart()
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        self.eat = make_table()
        self.avoid = make_table()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.diet_tab(), "Diet")
        self.tabs.addTab(self.codon_tab(), "Codons")
        self.tabs.addTab(self.amino_chart, "Amino acids")

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addLayout(self.row(self.query, self.search_button))
        layout.addLayout(self.row(self.genomes, self.analyze_button))
        layout.addWidget(self.status)
        layout.addWidget(self.metrics)
        layout.addWidget(self.tabs, 1)
        self.setCentralWidget(root)

        self.query.returnPressed.connect(self.search)
        self.search_button.clicked.connect(self.search)
        self.analyze_button.clicked.connect(self.analyze)

    @staticmethod
    def row(field: QWidget, button: QPushButton) -> QHBoxLayout:
        """A field that takes the free width, with its button on the right."""
        layout = QHBoxLayout()
        layout.addWidget(field, 1)
        layout.addWidget(button)
        return layout

    def codon_tab(self) -> QWidget:
        """Top 10 codons on the left, a chart of all 64 on the right."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.addWidget(self.top_codons, 1)
        layout.addWidget(self.codon_chart, 2)
        return tab

    def diet_tab(self) -> QWidget:
        """The summary on top, foods to eat and to avoid side by side below it."""
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.addWidget(self.summary, 0, 0, 1, 2)
        layout.addWidget(QLabel("<h3>✅ Eat</h3>"), 1, 0)
        layout.addWidget(QLabel("<h3>⛔ Avoid</h3>"), 1, 1)
        layout.addWidget(self.eat, 2, 0)
        layout.addWidget(self.avoid, 2, 1)
        return tab

    def run(
        self,
        message: str,
        task: Callable[[], object],
        then: Callable[[object], None],
        failure_message: str,
    ) -> None:
        """Run task in the background with both buttons off, then pass its result to then."""
        self.status.setText(message)
        self.search_button.setEnabled(False)
        self.analyze_button.setEnabled(False)
        self.worker = Worker(task, failure_message)
        self.worker.done.connect(then)
        self.worker.failed.connect(self.status.setText)
        self.worker.finished.connect(self.enable_buttons)
        self.worker.start()

    def enable_buttons(self) -> None:
        self.search_button.setEnabled(True)
        self.analyze_button.setEnabled(bool(self.matches))

    def search(self) -> None:
        query = self.query.text().strip()
        if not query:
            return
        self.run("Searching NCBI...", lambda: search(query), self.show_matches, SEARCH_FAILED)

    def show_matches(self, matches: object) -> None:
        assert isinstance(matches, list)
        self.matches = matches
        self.genomes.clear()
        self.genomes.addItems([genome.label() for genome in self.matches])
        if not self.matches:
            self.status.setText("No genomes found on NCBI for that name.")
            return
        self.status.setText(f"{len(self.matches)} genomes found.")

    def analyze(self) -> None:
        genome = self.matches[self.genomes.currentIndex()]
        message = (
            "Downloading the genome and the USDA food database (first run only), then analyzing..."
        )
        self.run(message, lambda: analyze(genome), self.show_results, ANALYZE_FAILED)

    def show_results(self, result: object) -> None:
        assert isinstance(result, Analysis)
        codons = pd.Series(result.codons)
        self.status.setText("Done.")
        self.metrics.setText(
            f"<b>Genome length:</b> {result.length:,} nt &nbsp; "
            f"<b>Segments:</b> {result.segments} &nbsp; "
            f"<b>Codons counted:</b> {codons.sum():,}"
        )
        fill_table(self.top_codons, codon_table(codons))
        self.codon_chart.bars(codons.sort_values(ascending=False), "All 64 codons")
        amino_acids = pd.Series(result.amino_acids).sort_values(ascending=False)
        self.amino_chart.bars(amino_acids, "Amino acid profile", horizontal=True)
        self.summary.setText(
            f"This genome's codons favour <b>{', '.join(result.favourite)}</b>. "
            "Foods from the USDA database whose protein has the most similar amino acid mix are "
            "listed under Avoid, and the least similar under Eat. Only foods with at least "
            f"{MIN_PROTEIN_G} g of amino acids per 100 g are compared."
        )
        fill_table(self.eat, result.eat)
        fill_table(self.avoid, result.avoid)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

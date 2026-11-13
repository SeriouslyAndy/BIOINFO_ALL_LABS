# @author: SeriouslyAndy(JavaKet)
# @date: 23-10-2026

"""Small Qt building blocks for the app: a background worker, a bar chart and read-only tables."""

import logging
from collections.abc import Callable

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

BAR_COLOUR = "#4c78a8"
CHART_SIZE_IN = (6, 4)
SMALL_LABEL_PT = 7

log = logging.getLogger(__name__)


class Worker(QThread):
    """Runs one slow task off the UI thread, so the window stays responsive.

    A failure is logged and reported with failure_message, never with the raw error.
    """

    done = Signal(object)
    failed = Signal(str)

    def __init__(self, task: Callable[[], object], failure_message: str) -> None:
        super().__init__()
        self.task = task
        self.failure_message = failure_message

    def run(self) -> None:
        try:
            self.done.emit(self.task())
        except Exception:
            log.exception("Background task failed")
            self.failed.emit(self.failure_message)


class Chart(FigureCanvasQTAgg):
    """A matplotlib bar chart inside a Qt widget.

    matplotlib's Qt backend has no type hints, hence the two no-untyped-call ignores.
    """

    def __init__(self) -> None:
        figure = Figure(figsize=CHART_SIZE_IN, layout="tight")
        super().__init__(figure)  # type: ignore[no-untyped-call]

    def bars(self, series: "pd.Series[int]", title: str, horizontal: bool = False) -> None:
        """Replace the chart with one bar per value of series, labelled with its index."""
        self.figure.clear()
        axes = self.figure.add_subplot()
        labels = [str(label) for label in series.index]
        values = series.to_list()
        if horizontal:
            # Reversed so that the first value is drawn at the top.
            axes.barh(labels[::-1], values[::-1], color=BAR_COLOUR)
        else:
            axes.bar(labels, values, color=BAR_COLOUR)
            axes.tick_params(axis="x", labelrotation=90, labelsize=SMALL_LABEL_PT)
        axes.set_title(title)
        self.draw()  # type: ignore[no-untyped-call]


def make_table() -> QTableWidget:
    """A table the user can read but not edit, without row numbers."""
    table = QTableWidget()
    table.verticalHeader().hide()
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setWordWrap(True)
    return table


def fill_table(table: QTableWidget, frame: pd.DataFrame) -> None:
    """Show frame in table. The first column stretches, the others fit their contents."""
    table.setRowCount(len(frame))
    table.setColumnCount(len(frame.columns))
    table.setHorizontalHeaderLabels([str(column) for column in frame.columns])
    for row, values in enumerate(frame.itertuples(index=False)):
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(str(value)))
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    table.resizeRowsToContents()

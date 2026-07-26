"""Board and cell models."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .settings import BOARD_SIZE, BOMBS_REQUIRED


class CellContent(str, Enum):
    EMPTY = "empty"
    BOMB = "bomb"
    PRIZE = "prize"


@dataclass
class Cell:
    row: int
    column: int
    content: CellContent = CellContent.EMPTY
    revealed: bool = False


class Board:
    """A square board containing bombs, one prize, and empty cells."""

    def __init__(self, size: int = BOARD_SIZE) -> None:
        if size <= 0:
            raise ValueError("Board size must be positive.")
        self.size = size
        self.cells: List[List[Cell]] = [
            [Cell(row, column) for column in range(size)]
            for row in range(size)
        ]

    @property
    def bomb_count(self) -> int:
        return sum(
            cell.content == CellContent.BOMB
            for row in self.cells
            for cell in row
        )

    @property
    def prize_count(self) -> int:
        return sum(
            cell.content == CellContent.PRIZE
            for row in self.cells
            for cell in row
        )

    def _get_cell(self, row: int, column: int) -> Cell:
        if not (0 <= row < self.size and 0 <= column < self.size):
            raise IndexError("Cell position is outside the board.")
        return self.cells[row][column]

    def get_cell(self, row: int, column: int) -> Cell:
        return self._get_cell(row, column)

    def get_content(self, row: int, column: int) -> CellContent:
        return self._get_cell(row, column).content

    def place_bomb(self, row: int, column: int) -> bool:
        cell = self._get_cell(row, column)
        if cell.content != CellContent.EMPTY or self.bomb_count >= BOMBS_REQUIRED:
            return False
        cell.content = CellContent.BOMB
        return True

    def place_prize(self, row: int, column: int) -> bool:
        cell = self._get_cell(row, column)
        if cell.content != CellContent.EMPTY or self.prize_count >= 1:
            return False
        cell.content = CellContent.PRIZE
        return True

    def remove_item(self, row: int, column: int) -> bool:
        cell = self._get_cell(row, column)
        if cell.content == CellContent.EMPTY:
            return False
        cell.content = CellContent.EMPTY
        return True

    def reveal(self, row: int, column: int) -> Optional[CellContent]:
        """Reveal a cell, returning None when it was already revealed."""
        cell = self._get_cell(row, column)
        if cell.revealed:
            return None
        cell.revealed = True
        return cell.content

    def is_setup_complete(self) -> bool:
        return self.bomb_count == BOMBS_REQUIRED and self.prize_count == 1

    def clear(self) -> None:
        for row in self.cells:
            for cell in row:
                cell.content = CellContent.EMPTY
                cell.revealed = False

"""Player model."""

from dataclasses import dataclass, field

from .board import Board


@dataclass
class Player:
    name: str
    board: Board = field(default_factory=Board)
    bombs_discovered: int = 0
    selected_cells: int = 0

    def reset(self) -> None:
        self.board = Board(self.board.size)
        self.bombs_discovered = 0
        self.selected_cells = 0

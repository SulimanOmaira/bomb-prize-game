"""Player model."""

from dataclasses import dataclass, field

from .board import Board
from .settings import Color, PLAYER_ONE_COLOR


@dataclass
class Player:
    name: str
    board: Board = field(default_factory=Board)
    bombs_discovered: int = 0
    selected_cells: int = 0
    accent_color: Color = PLAYER_ONE_COLOR

    def reset(self) -> None:
        self.board = Board(self.board.size)
        self.bombs_discovered = 0
        self.selected_cells = 0

"""Turn management and win/loss rules."""

from dataclasses import dataclass
from typing import List, Optional

from .board import CellContent
from .player import Player
from .settings import BOMBS_REQUIRED, PLAYER_COLORS


@dataclass(frozen=True)
class TurnResult:
    valid: bool
    content: Optional[CellContent]
    message: str
    game_over: bool


class GameManager:
    def __init__(self) -> None:
        self.players: List[Player] = []
        self.current_player_index = 0
        self.game_over = False
        self.turn_selection_made = False
        self.winner: Optional[Player] = None
        self.loser: Optional[Player] = None
        self.end_reason = ""

    def create_players(self, first_name: str, second_name: str) -> None:
        self.players = [
            Player(first_name, accent_color=PLAYER_COLORS[0]),
            Player(second_name, accent_color=PLAYER_COLORS[1]),
        ]
        self._reset_match_state()

    @property
    def current_player(self) -> Player:
        self._require_players()
        return self.players[self.current_player_index]

    @property
    def opponent(self) -> Player:
        self._require_players()
        return self.players[1 - self.current_player_index]

    def _require_players(self) -> None:
        if len(self.players) != 2:
            raise RuntimeError("Two players must be created first.")

    def both_boards_ready(self) -> bool:
        return (
            len(self.players) == 2
            and all(player.board.is_setup_complete() for player in self.players)
        )

    def select_opponent_cell(self, row: int, column: int) -> TurnResult:
        if self.game_over:
            return TurnResult(False, None, "The game is already over.", True)
        if self.turn_selection_made:
            return TurnResult(
                False,
                None,
                "Only one cell can be selected per turn.",
                False,
            )
        if not self.both_boards_ready():
            return TurnResult(False, None, "Both boards must be ready.", False)

        content = self.opponent.board.reveal(row, column)
        if content is None:
            return TurnResult(False, None, "This cell was already selected.", False)

        player = self.current_player
        player.selected_cells += 1
        self.turn_selection_made = True

        if content == CellContent.PRIZE:
            self._finish_game(player, self.opponent, "found the prize")
            message = f"{player.name} found the prize!"
        elif content == CellContent.BOMB:
            player.bombs_discovered += 1
            if player.bombs_discovered >= BOMBS_REQUIRED:
                self._finish_game(
                    self.opponent,
                    player,
                    f"discovered {BOMBS_REQUIRED} bombs",
                )
                message = f"{player.name} discovered the third bomb!"
            else:
                message = "A bomb was discovered."
        else:
            message = "The cell is empty."

        return TurnResult(True, content, message, self.game_over)

    def _finish_game(self, winner: Player, loser: Player, reason: str) -> None:
        self.game_over = True
        self.winner = winner
        self.loser = loser
        self.end_reason = reason

    def switch_turn(self) -> None:
        if not self.game_over:
            self.current_player_index = 1 - self.current_player_index
            self.turn_selection_made = False

    def reset_same_names(self) -> None:
        self._require_players()
        for player in self.players:
            player.reset()
        self._reset_match_state()

    def clear_game(self) -> None:
        self.players = []
        self._reset_match_state()

    def _reset_match_state(self) -> None:
        self.current_player_index = 0
        self.game_over = False
        self.turn_selection_made = False
        self.winner = None
        self.loser = None
        self.end_reason = ""

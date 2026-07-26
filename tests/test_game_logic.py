"""Unit tests for board and game manager rules."""

from game.board import Board, CellContent
from game.game_manager import GameManager
from game.settings import BOARD_SIZE, BOMBS_REQUIRED


def prepare_manager() -> GameManager:
    manager = GameManager()
    manager.create_players("Alice", "Bob")
    for player in manager.players:
        assert player.board.place_bomb(0, 0)
        assert player.board.place_bomb(0, 1)
        assert player.board.place_bomb(0, 2)
        assert player.board.place_prize(1, 0)
    return manager


def test_board_is_six_by_six() -> None:
    board = Board()
    assert board.size == BOARD_SIZE == 6
    assert len(board.cells) == 6
    assert all(len(row) == 6 for row in board.cells)


def test_only_three_bombs_can_be_placed() -> None:
    board = Board()
    assert board.place_bomb(0, 0)
    assert board.place_bomb(0, 1)
    assert board.place_bomb(0, 2)
    assert not board.place_bomb(0, 3)
    assert board.bomb_count == BOMBS_REQUIRED


def test_only_one_prize_can_be_placed() -> None:
    board = Board()
    assert board.place_prize(1, 1)
    assert not board.place_prize(1, 2)
    assert board.prize_count == 1


def test_two_items_cannot_share_a_cell() -> None:
    board = Board()
    assert board.place_bomb(2, 2)
    assert not board.place_prize(2, 2)
    assert board.get_content(2, 2) == CellContent.BOMB


def test_game_cannot_start_before_both_boards_are_ready() -> None:
    manager = GameManager()
    manager.create_players("Alice", "Bob")
    result = manager.select_opponent_cell(0, 0)
    assert not manager.both_boards_ready()
    assert not result.valid
    assert result.content is None


def test_same_cell_cannot_be_selected_twice() -> None:
    manager = prepare_manager()
    first = manager.select_opponent_cell(2, 2)
    assert first.valid

    manager.switch_turn()
    assert manager.select_opponent_cell(2, 3).valid
    manager.switch_turn()
    duplicate = manager.select_opponent_cell(2, 2)
    assert not duplicate.valid
    assert duplicate.content is None


def test_finding_prize_wins_the_game() -> None:
    manager = prepare_manager()
    result = manager.select_opponent_cell(1, 0)
    assert result.valid
    assert result.game_over
    assert manager.winner is manager.players[0]
    assert manager.loser is manager.players[1]
    assert manager.end_reason == "found the prize"


def test_discovering_third_bomb_loses_the_game() -> None:
    manager = prepare_manager()
    safe_cells = [(2, 0), (2, 1)]
    for index, bomb_column in enumerate(range(3)):
        result = manager.select_opponent_cell(0, bomb_column)
        if bomb_column < 2:
            assert not result.game_over
            manager.switch_turn()
            assert manager.select_opponent_cell(*safe_cells[index]).valid
            manager.switch_turn()

    assert result.game_over
    assert manager.players[0].bombs_discovered == BOMBS_REQUIRED
    assert manager.winner is manager.players[1]
    assert manager.loser is manager.players[0]


def test_turn_switches_between_players() -> None:
    manager = prepare_manager()
    assert manager.current_player is manager.players[0]
    assert manager.opponent is manager.players[1]
    manager.switch_turn()
    assert manager.current_player is manager.players[1]
    assert manager.opponent is manager.players[0]


def test_reset_same_names_clears_match_data() -> None:
    manager = prepare_manager()
    manager.select_opponent_cell(0, 0)
    old_names = [player.name for player in manager.players]

    manager.reset_same_names()

    assert [player.name for player in manager.players] == old_names
    assert manager.current_player_index == 0
    assert not manager.game_over
    assert manager.winner is None
    assert manager.loser is None
    for player in manager.players:
        assert player.bombs_discovered == 0
        assert player.selected_cells == 0
        assert player.board.bomb_count == 0
        assert player.board.prize_count == 0
        assert all(
            not cell.revealed
            for row in player.board.cells
            for cell in row
        )

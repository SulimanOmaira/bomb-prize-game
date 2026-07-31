"""Main turn screen."""

from typing import Optional

import pygame

from game.board import CellContent
from game.button import Button
from game.game_manager import GameManager
from game.settings import (
    BACKGROUND,
    BORDER,
    BOMB_CELL,
    BOMBS_REQUIRED,
    EMPTY_CELL,
    ERROR,
    MUTED_TEXT,
    PRIZE_CELL,
    SUCCESS,
    WINDOW_WIDTH,
    player_cell_color,
)
from .common import (
    board_pixel_width,
    draw_bomb_symbol,
    draw_centered_text,
    draw_prize_symbol,
    iter_board_rects,
)


class GameplayScreen:
    def __init__(self, manager: GameManager) -> None:
        self.manager = manager
        self.selection_made = False
        self.message = "Choose one hidden cell."
        self.message_color = MUTED_TEXT
        width = board_pixel_width(manager.opponent.board.size)
        self.board_x = (WINDOW_WIDTH - width) // 2
        self.board_y = 150
        self.end_turn_button = Button(
            "End Turn",
            (WINDOW_WIDTH // 2 - 130, 625),
            (260, 48),
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"
        if self.selection_made:
            if self.end_turn_button.is_clicked(event):
                return "end_turn"
            return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row, column, rect in iter_board_rects(
                self.board_x,
                self.board_y,
                self.manager.opponent.board.size,
            ):
                if rect.collidepoint(event.pos):
                    result = self.manager.select_opponent_cell(row, column)
                    self.message = result.message
                    self.message_color = ERROR if not result.valid else SUCCESS
                    if result.valid:
                        self.selection_made = True
                        return "game_over" if result.game_over else None
                    break
        return None

    def draw(
        self,
        surface: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        surface.fill(BACKGROUND)
        player = self.manager.current_player
        opponent = self.manager.opponent
        pygame.draw.rect(
            surface,
            player.accent_color,
            (0, 0, surface.get_width(), 6),
        )
        draw_centered_text(
            surface,
            f"Turn: {player.name}",
            title_font,
            38,
            player.accent_color,
        )
        draw_centered_text(
            surface,
            f"Choose from {opponent.name}'s board",
            body_font,
            88,
            opponent.accent_color,
        )
        draw_centered_text(
            surface,
            f"Bombs discovered: {player.bombs_discovered} / {BOMBS_REQUIRED}",
            body_font,
            120,
        )

        for row, column, rect in iter_board_rects(
            self.board_x,
            self.board_y,
            opponent.board.size,
        ):
            cell = opponent.board.get_cell(row, column)
            if not cell.revealed:
                color = player_cell_color(player.accent_color)
            elif cell.content == CellContent.BOMB:
                color = BOMB_CELL
            elif cell.content == CellContent.PRIZE:
                color = PRIZE_CELL
            else:
                color = EMPTY_CELL
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, BORDER, rect, 1, border_radius=5)
            if cell.revealed and cell.content == CellContent.BOMB:
                draw_bomb_symbol(surface, rect)
            elif cell.revealed and cell.content == CellContent.PRIZE:
                draw_prize_symbol(surface, rect)

        draw_centered_text(
            surface,
            self.message,
            body_font,
            585,
            self.message_color,
        )
        if self.selection_made and not self.manager.game_over:
            self.end_turn_button.draw(surface, button_font)

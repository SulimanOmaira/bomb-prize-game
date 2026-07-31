"""Secret board setup screen."""

from typing import Optional

import pygame

from game.board import CellContent
from game.button import Button
from game.player import Player
from game.settings import (
    BACKGROUND,
    BORDER,
    BOMBS_REQUIRED,
    BUTTON_HOVER,
    ERROR,
    MUTED_TEXT,
    SELECTED_BOMB,
    SELECTED_PRIZE,
    SUCCESS,
    TEXT,
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


class SetupScreen:
    def __init__(self, player: Player) -> None:
        self.player = player
        self.mode = CellContent.BOMB
        self.error_message = ""
        width = board_pixel_width(player.board.size)
        self.board_x = (WINDOW_WIDTH - width) // 2
        self.board_y = 145
        self.bomb_button = Button(
            "Select Bomb",
            (WINDOW_WIDTH // 2 - 185, 75),
            (170, 48),
        )
        self.prize_button = Button(
            "Select Prize",
            (WINDOW_WIDTH // 2 + 15, 75),
            (170, 48),
        )
        self.clear_button = Button(
            "Clear",
            (WINDOW_WIDTH // 2 - 230, 625),
            (200, 48),
        )
        self.confirm_button = Button(
            "Confirm",
            (WINDOW_WIDTH // 2 + 30, 625),
            (200, 48),
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"
        if self.bomb_button.is_clicked(event):
            self.mode = CellContent.BOMB
            self.error_message = ""
        if self.prize_button.is_clicked(event):
            self.mode = CellContent.PRIZE
            self.error_message = ""
        if self.clear_button.is_clicked(event):
            self.player.board.clear()
            self.error_message = ""
        if self.confirm_button.is_clicked(
            event,
            enabled=self.player.board.is_setup_complete(),
        ):
            return "confirmed"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for row, column, rect in iter_board_rects(
                self.board_x,
                self.board_y,
                self.player.board.size,
            ):
                if rect.collidepoint(event.pos):
                    self._toggle_cell(row, column)
                    break
        return None

    def _toggle_cell(self, row: int, column: int) -> None:
        content = self.player.board.get_content(row, column)
        if content != CellContent.EMPTY:
            self.player.board.remove_item(row, column)
            self.error_message = ""
            return

        if self.mode == CellContent.BOMB:
            if not self.player.board.place_bomb(row, column):
                self.error_message = f"Only {BOMBS_REQUIRED} bombs are allowed."
        elif not self.player.board.place_prize(row, column):
            self.error_message = "Only one prize is allowed."

    def draw(
        self,
        surface: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        surface.fill(BACKGROUND)
        pygame.draw.rect(
            surface,
            self.player.accent_color,
            (0, 0, surface.get_width(), 6),
        )
        draw_centered_text(
            surface,
            f"{self.player.name}: Secret Setup",
            title_font,
            35,
            self.player.accent_color,
        )
        self.bomb_button.draw(surface, button_font)
        self.prize_button.draw(surface, button_font)
        active_rect = (
            self.bomb_button.rect
            if self.mode == CellContent.BOMB
            else self.prize_button.rect
        )
        pygame.draw.rect(surface, BUTTON_HOVER, active_rect, 3, border_radius=7)

        for row, column, rect in iter_board_rects(
            self.board_x,
            self.board_y,
            self.player.board.size,
        ):
            content = self.player.board.get_content(row, column)
            if content == CellContent.BOMB:
                color = SELECTED_BOMB
            elif content == CellContent.PRIZE:
                color = SELECTED_PRIZE
            else:
                color = player_cell_color(self.player.accent_color)
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, BORDER, rect, 1, border_radius=5)
            if content == CellContent.BOMB:
                draw_bomb_symbol(surface, rect)
            elif content == CellContent.PRIZE:
                draw_prize_symbol(surface, rect)

        board = self.player.board
        draw_centered_text(
            surface,
            f"Bombs: {board.bomb_count} / {BOMBS_REQUIRED}",
            body_font,
            575,
        )
        prize_text = "Prize: selected" if board.prize_count else "Prize: not selected"
        prize_color = SUCCESS if board.prize_count else MUTED_TEXT
        draw_centered_text(surface, prize_text, body_font, 605, prize_color)
        if self.error_message:
            draw_centered_text(surface, self.error_message, body_font, 605, ERROR)

        self.clear_button.draw(surface, button_font)
        self.confirm_button.draw(
            surface,
            button_font,
            enabled=board.is_setup_complete(),
        )

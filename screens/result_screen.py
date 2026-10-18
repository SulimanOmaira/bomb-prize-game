"""End-of-game result screen."""

from typing import Optional

import pygame

from game.button import Button
from game.game_manager import GameManager
from game.settings import (
    COMPACT_LAYOUT,
    MUTED_TEXT,
    WINDOW_WIDTH,
)
from .common import draw_background, draw_centered_text, draw_panel


class ResultScreen:
    def __init__(self, manager: GameManager) -> None:
        self.manager = manager
        button_x = WINDOW_WIDTH // 2 - 150
        self.replay_button = Button("Replay Same Names", (button_x, 345), (300, 50))
        self.new_game_button = Button("New Game", (button_x, 410), (300, 50))
        self.menu_button = Button("Main Menu", (button_x, 475), (300, 50))
        self.quit_button = Button("Quit", (button_x, 540), (300, 50))

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"
        if self.replay_button.is_clicked(event):
            return "replay"
        if self.new_game_button.is_clicked(event):
            return "new_game"
        if self.menu_button.is_clicked(event):
            return "menu"
        if self.quit_button.is_clicked(event):
            return "quit"
        return None

    def draw(
        self,
        surface: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        draw_background(surface)
        panel_margin = 30 if COMPACT_LAYOUT else 125
        panel = pygame.Rect(
            panel_margin,
            55,
            WINDOW_WIDTH - panel_margin * 2,
            590,
        )
        draw_panel(surface, panel)
        draw_centered_text(surface, "Game Over", title_font, 110)

        winner = self.manager.winner
        loser = self.manager.loser
        if winner is not None and loser is not None:
            draw_centered_text(
                surface,
                f"Winner: {winner.name}",
                title_font,
                185,
                winner.accent_color,
            )
            draw_centered_text(
                surface,
                f"Loser: {loser.name}",
                body_font,
                235,
                loser.accent_color,
            )
            if self.manager.end_reason == "found the prize":
                reason = f"{winner.name} won by finding the prize."
            else:
                reason = (
                    f"{loser.name} lost after discovering "
                    f"the third bomb."
                )
            draw_centered_text(
                surface,
                reason,
                body_font,
                285,
                MUTED_TEXT,
                max_width=panel.width - 24,
            )

        self.replay_button.draw(surface, button_font)
        self.new_game_button.draw(surface, button_font)
        self.menu_button.draw(surface, button_font)
        self.quit_button.draw(surface, button_font)

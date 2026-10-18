"""Privacy screen shown before setup and between turns."""

from typing import Optional

import pygame

from game.button import Button
from game.settings import (
    COMPACT_LAYOUT,
    Color,
    MUTED_TEXT,
    WINDOW_WIDTH,
)
from .common import draw_background, draw_centered_text, draw_panel


class PassScreen:
    def __init__(
        self,
        next_player_name: str,
        next_player_color: Color,
        message: str,
    ) -> None:
        self.next_player_name = next_player_name
        self.next_player_color = next_player_color
        self.message = message
        self.ready_button = Button(
            "I am ready",
            (WINDOW_WIDTH // 2 - 140, 430),
            (280, 60),
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"
        if self.ready_button.is_clicked(event):
            return "ready"
        return None

    def draw(
        self,
        surface: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        draw_background(surface)
        panel_margin = 30 if COMPACT_LAYOUT else 145
        panel = pygame.Rect(
            panel_margin,
            155,
            WINDOW_WIDTH - panel_margin * 2,
            385,
        )
        draw_panel(surface, panel, self.next_player_color, 4)
        draw_centered_text(surface, "Pass the device", title_font, 230)
        draw_centered_text(
            surface,
            f"Give the device to {self.next_player_name}",
            body_font,
            310,
            self.next_player_color,
            max_width=panel.width - 24,
        )
        draw_centered_text(
            surface,
            self.message,
            body_font,
            355,
            MUTED_TEXT,
            max_width=panel.width - 24,
        )
        self.ready_button.draw(surface, button_font)

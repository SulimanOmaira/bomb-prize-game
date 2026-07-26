"""Privacy screen shown before setup and between turns."""

from typing import Optional

import pygame

from game.button import Button
from game.settings import BACKGROUND, MUTED_TEXT, PANEL, WINDOW_WIDTH
from .common import draw_centered_text


class PassScreen:
    def __init__(self, next_player_name: str, message: str) -> None:
        self.next_player_name = next_player_name
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
        surface.fill(BACKGROUND)
        panel = pygame.Rect(145, 155, WINDOW_WIDTH - 290, 385)
        pygame.draw.rect(surface, PANEL, panel, border_radius=12)
        draw_centered_text(surface, "Pass the device", title_font, 230)
        draw_centered_text(
            surface,
            f"Give the device to {self.next_player_name}",
            body_font,
            310,
        )
        draw_centered_text(surface, self.message, body_font, 355, MUTED_TEXT)
        self.ready_button.draw(surface, button_font)

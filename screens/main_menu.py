"""Main menu and instructions view."""

from typing import Optional

import pygame

from game.button import Button
from game.settings import (
    COMPACT_LAYOUT,
    MUTED_TEXT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from .common import draw_background, draw_centered_text, draw_panel


class MainMenu:
    def __init__(self) -> None:
        button_x = WINDOW_WIDTH // 2 - 130
        self.start_button = Button("Start Game", (button_x, 300), (260, 55))
        self.instructions_button = Button("Instructions", (button_x, 375), (260, 55))
        self.quit_button = Button("Quit", (button_x, 450), (260, 55))
        self.back_button = Button("Back", (button_x, 560), (260, 55))
        self.showing_instructions = False

    def reset(self) -> None:
        self.showing_instructions = False

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.showing_instructions:
                self.showing_instructions = False
                return None
            return "quit"

        if self.showing_instructions:
            if self.back_button.is_clicked(event):
                self.showing_instructions = False
            return None

        if self.start_button.is_clicked(event):
            return "start"
        if self.instructions_button.is_clicked(event):
            self.showing_instructions = True
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
        if self.showing_instructions:
            self._draw_instructions(surface, title_font, body_font, button_font)
            return

        draw_centered_text(surface, "BOMB PRIZE GAME", title_font, 125)
        draw_centered_text(
            surface,
            "Tiny bombs, big prize, two brave players.",
            body_font,
            185,
            MUTED_TEXT,
        )
        hero = pygame.Rect(
            WINDOW_WIDTH // 2 - 145,
            218,
            290,
            50,
        )
        pygame.draw.rect(surface, (255, 207, 89), hero, border_radius=25)
        draw_centered_text(surface, "3 Bombs + 1 Prize", body_font, 243, (25, 31, 45))
        self.start_button.draw(surface, button_font)
        self.instructions_button.draw(surface, button_font)
        self.quit_button.draw(surface, button_font)

    def _draw_instructions(
        self,
        surface: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        draw_centered_text(surface, "Instructions", title_font, 90)
        panel_margin = 30 if COMPACT_LAYOUT else 105
        panel = pygame.Rect(
            panel_margin,
            145,
            WINDOW_WIDTH - panel_margin * 2,
            340,
        )
        draw_panel(surface, panel)
        lines = [
            "Each player secretly places 3 bombs and 1 prize.",
            "On your turn, choose one hidden cell on your opponent's board.",
            "Find the prize to win immediately.",
            "Discovering 3 bombs makes you lose.",
            "A cell cannot be selected twice.",
            "Pass the device when the game asks you to.",
        ]
        for index, line in enumerate(lines):
            draw_centered_text(
                surface,
                line,
                body_font,
                190 + index * 47,
                max_width=panel.width - 24,
            )
        self.back_button.draw(surface, button_font)

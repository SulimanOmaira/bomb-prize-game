"""Player name entry screen."""

import sys
from typing import Optional, Tuple, Union

import pygame

from game.button import Button
from game.settings import (
    BACKGROUND,
    ERROR,
    INPUT_ACTIVE,
    INPUT_INACTIVE,
    MAX_NAME_LENGTH,
    MUTED_TEXT,
    PANEL,
    TEXT,
    WINDOW_WIDTH,
)
from .common import draw_centered_text

NamesAction = Union[str, Tuple[str, Tuple[str, str]]]


class NamesScreen:
    def __init__(self) -> None:
        self.names = ["", ""]
        self.active_index = 0
        self.error_message = ""
        self.input_rects = [
            pygame.Rect(WINDOW_WIDTH // 2 - 210, 260, 420, 55),
            pygame.Rect(WINDOW_WIDTH // 2 - 210, 375, 420, 55),
        ]
        self.continue_button = Button(
            "Continue",
            (WINDOW_WIDTH // 2 - 130, 510),
            (260, 55),
        )

    def reset(self) -> None:
        self.names = ["", ""]
        self.active_index = 0
        self.error_message = ""

    def handle_event(self, event: pygame.event.Event) -> Optional[NamesAction]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            if event.key == pygame.K_TAB:
                self.active_index = 1 - self.active_index
                return None
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._validate()
            if event.key == pygame.K_BACKSPACE:
                self.names[self.active_index] = self.names[self.active_index][:-1]
                self.error_message = ""
                return None
            if (
                event.unicode
                and event.unicode.isprintable()
                and len(self.names[self.active_index]) < MAX_NAME_LENGTH
            ):
                self.names[self.active_index] += event.unicode
                self.error_message = ""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.input_rects):
                if rect.collidepoint(event.pos):
                    self.active_index = index
                    self._request_mobile_name(index)
                    return None
        if self.continue_button.is_clicked(event):
            return self._validate()
        return None

    def _validate(self) -> Optional[NamesAction]:
        first = self.names[0].strip()
        second = self.names[1].strip()
        if not first or not second:
            self.error_message = "Both names are required."
            return None
        if first.casefold() == second.casefold():
            self.error_message = "Players must have different names."
            return None
        self.names = [first, second]
        return "submit", (first, second)

    def _request_mobile_name(self, index: int) -> None:
        """Open the phone's native keyboard when running inside Pygbag."""
        if sys.platform != "emscripten":
            return

        import platform

        label = "First player name" if index == 0 else "Second player name"
        entered = platform.window.prompt(label, self.names[index])
        if entered is not None:
            self.names[index] = str(entered).strip()[:MAX_NAME_LENGTH]
            self.error_message = ""

    def draw(
        self,
        surface: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        surface.fill(BACKGROUND)
        draw_centered_text(surface, "Player Names", title_font, 90)
        draw_centered_text(
            surface,
            "Click a field, use Tab to move, and Enter to continue.",
            body_font,
            145,
            MUTED_TEXT,
        )
        labels = ["First player", "Second player"]
        for index, rect in enumerate(self.input_rects):
            label = body_font.render(labels[index], True, TEXT)
            surface.blit(label, (rect.x, rect.y - 32))
            pygame.draw.rect(surface, PANEL, rect, border_radius=6)
            border = INPUT_ACTIVE if self.active_index == index else INPUT_INACTIVE
            pygame.draw.rect(surface, border, rect, 3, border_radius=6)
            value = body_font.render(self.names[index], True, TEXT)
            surface.blit(value, (rect.x + 14, rect.centery - value.get_height() // 2))
            if self.active_index == index:
                cursor_x = rect.x + 14 + value.get_width() + 2
                pygame.draw.line(
                    surface,
                    TEXT,
                    (cursor_x, rect.y + 13),
                    (cursor_x, rect.bottom - 13),
                    2,
                )

        if self.error_message:
            draw_centered_text(surface, self.error_message, body_font, 470, ERROR)
        self.continue_button.draw(surface, button_font)

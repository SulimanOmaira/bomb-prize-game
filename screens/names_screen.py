"""Player name entry screen."""

import sys
from typing import Optional, Tuple, Union

import pygame

from game.button import Button
from game.settings import (
    BACKGROUND,
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    ERROR,
    MAX_NAME_LENGTH,
    MUTED_TEXT,
    PANEL,
    PLAYER_COLORS,
    TEXT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from .common import draw_centered_text

NamesAction = Union[str, Tuple[str, Tuple[str, str]]]
MOBILE_INPUT_ID = "bomb-prize-player-name-input"


class NamesScreen:
    def __init__(self) -> None:
        self.names = ["", ""]
        self.active_index = 0
        self.error_message = ""
        self.mobile_input_index: Optional[int] = None
        input_width = min(420, WINDOW_WIDTH - 60)
        self.input_rects = [
            pygame.Rect(
                WINDOW_WIDTH // 2 - input_width // 2,
                260,
                input_width,
                55,
            ),
            pygame.Rect(
                WINDOW_WIDTH // 2 - input_width // 2,
                375,
                input_width,
                55,
            ),
        ]
        self.continue_button = Button(
            "Continue",
            (WINDOW_WIDTH // 2 - 130, 510),
            (260, 55),
        )

    def reset(self) -> None:
        self.hide_mobile_input()
        self.names = ["", ""]
        self.active_index = 0
        self.error_message = ""

    def handle_event(self, event: pygame.event.Event) -> Optional[NamesAction]:
        self._sync_mobile_input()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide_mobile_input()
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
                    self._show_mobile_input(index)
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
        self.hide_mobile_input()
        return "submit", (first, second)

    def _show_mobile_input(self, index: int) -> None:
        """Place a native HTML input directly over the Pygame name field."""
        if sys.platform != "emscripten":
            return

        import platform

        document = platform.document
        element = document.getElementById(MOBILE_INPUT_ID)
        if element is None:
            element = document.createElement("input")
            element.id = MOBILE_INPUT_ID
            element.type = "text"
            element.maxLength = MAX_NAME_LENGTH
            element.autocomplete = "off"
            element.inputMode = "text"
            element.style.position = "fixed"
            element.style.boxSizing = "border-box"
            element.style.margin = "0"
            element.style.fontFamily = "Arial, sans-serif"
            element.style.fontWeight = "600"
            element.style.outline = "none"
            element.style.zIndex = "10000"
            element.style.touchAction = "manipulation"
            document.body.appendChild(element)

        label = "First player name" if index == 0 else "Second player name"
        color = self._css_color(PLAYER_COLORS[index])
        element.value = self.names[index]
        element.placeholder = label
        element.enterKeyHint = "next" if index == 0 else "done"
        element.setAttribute("aria-label", label)
        element.setAttribute("autocapitalize", "words")
        element.style.display = "block"
        element.style.backgroundColor = self._css_color(PANEL)
        element.style.color = self._css_color(TEXT)
        element.style.border = f"3px solid {color}"
        element.style.caretColor = color
        self.mobile_input_index = index
        self._position_mobile_input(element, index)
        element.focus()
        self.error_message = ""

    def _sync_mobile_input(self) -> None:
        if sys.platform != "emscripten" or self.mobile_input_index is None:
            return

        import platform

        element = platform.document.getElementById(MOBILE_INPUT_ID)
        if element is None:
            self.mobile_input_index = None
            return
        index = self.mobile_input_index
        self.names[index] = str(element.value)[:MAX_NAME_LENGTH]

    def hide_mobile_input(self) -> None:
        if sys.platform != "emscripten":
            self.mobile_input_index = None
            return

        import platform

        element = platform.document.getElementById(MOBILE_INPUT_ID)
        if element is not None:
            element.style.display = "none"
            element.blur()
        self.mobile_input_index = None

    def _position_mobile_input(self, element: object, index: int) -> None:
        import platform

        canvas = platform.document.getElementById("canvas")
        if canvas is None:
            return

        bounds = canvas.getBoundingClientRect()
        scale = min(
            DISPLAY_WIDTH / WINDOW_WIDTH,
            DISPLAY_HEIGHT / WINDOW_HEIGHT,
        )
        game_width = round(WINDOW_WIDTH * scale)
        game_height = round(WINDOW_HEIGHT * scale)
        offset_x = (DISPLAY_WIDTH - game_width) // 2
        offset_y = (DISPLAY_HEIGHT - game_height) // 2
        rect = self.input_rects[index]

        css_scale_x = float(bounds.width) / DISPLAY_WIDTH
        css_scale_y = float(bounds.height) / DISPLAY_HEIGHT
        left = float(bounds.left) + (offset_x + rect.x * scale) * css_scale_x
        top = float(bounds.top) + (offset_y + rect.y * scale) * css_scale_y
        width = rect.width * scale * css_scale_x
        height = rect.height * scale * css_scale_y
        font_size = max(16, round(25 * scale * css_scale_y))
        padding = max(8, round(12 * scale * css_scale_x))

        element.style.left = f"{left:.2f}px"
        element.style.top = f"{top:.2f}px"
        element.style.width = f"{width:.2f}px"
        element.style.height = f"{height:.2f}px"
        element.style.padding = f"0 {padding}px"
        element.style.fontSize = f"{font_size}px"
        element.style.borderRadius = "6px"

    @staticmethod
    def _css_color(color: Tuple[int, int, int]) -> str:
        return f"rgb({color[0]}, {color[1]}, {color[2]})"

    def draw(
        self,
        surface: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        self._sync_mobile_input()
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
            player_color = PLAYER_COLORS[index]
            label = body_font.render(labels[index], True, player_color)
            surface.blit(label, (rect.x, rect.y - 32))
            pygame.draw.rect(surface, PANEL, rect, border_radius=6)
            border_width = 4 if self.active_index == index else 2
            pygame.draw.rect(
                surface,
                player_color,
                rect,
                border_width,
                border_radius=6,
            )
            value = body_font.render(self.names[index], True, TEXT)
            surface.blit(value, (rect.x + 14, rect.centery - value.get_height() // 2))
            if self.active_index == index:
                cursor_x = rect.x + 14 + value.get_width() + 2
                pygame.draw.line(
                    surface,
                    player_color,
                    (cursor_x, rect.y + 13),
                    (cursor_x, rect.bottom - 13),
                    2,
                )

        if self.mobile_input_index is not None:
            import platform

            element = platform.document.getElementById(MOBILE_INPUT_ID)
            if element is not None:
                self._position_mobile_input(element, self.mobile_input_index)

        if self.error_message:
            draw_centered_text(surface, self.error_message, body_font, 470, ERROR)
        self.continue_button.draw(surface, button_font)

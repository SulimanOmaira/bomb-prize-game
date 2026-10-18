"""Player name entry screen."""

import sys
from typing import Optional, Tuple, Union

import pygame

from game.button import Button
from game.settings import (
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    ERROR,
    MAX_NAME_LENGTH,
    MUTED_TEXT,
    PLAYER_COLORS,
    TEXT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    player_panel_color,
)
from .common import draw_background, draw_centered_text, draw_panel

NamesAction = Union[str, Tuple[str, Tuple[str, str]]]
MOBILE_INPUT_ID = "bomb-prize-player-name-input"
MOBILE_INPUT_IDS = tuple(f"{MOBILE_INPUT_ID}-{index}" for index in range(2))
MOBILE_INPUT_Z_INDEX = 2147483500


class NamesScreen:
    def __init__(self) -> None:
        self.names = ["", ""]
        self.active_index = 0
        self.error_message = ""
        self.mobile_input_index: Optional[int] = None
        self.mobile_inputs_visible = False
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
        if event.type == pygame.TEXTINPUT:
            if self._native_input_has_focus():
                return None
            self._append_text(event.text)
            return None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide_mobile_input()
                return "menu"
            if self._native_input_has_focus():
                return None
            if event.key == pygame.K_TAB:
                self.active_index = 1 - self.active_index
                return None
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self._validate()
            if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE):
                self.names[self.active_index] = self.names[self.active_index][:-1]
                self._set_mobile_input_value(self.names[self.active_index])
                self.error_message = ""
                return None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(self.input_rects):
                if rect.collidepoint(event.pos):
                    self.active_index = index
                    self._show_mobile_input(index)
                    return None
        if self.continue_button.is_clicked(event):
            return self._validate()
        return None

    def _append_text(self, text: str) -> None:
        if not text or not text.isprintable():
            return
        available = MAX_NAME_LENGTH - len(self.names[self.active_index])
        if available <= 0:
            return
        self.names[self.active_index] += text[:available]
        self._set_mobile_input_value(self.names[self.active_index])
        self.error_message = ""

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
        """Focus a prepared native input when a canvas click reaches Pygame."""
        if sys.platform != "emscripten":
            return

        import platform

        document = platform.document
        self._show_mobile_inputs()
        element = document.getElementById(MOBILE_INPUT_IDS[index])
        if element is None:
            return

        self.active_index = index
        self.mobile_input_index = index
        element.focus()
        self.error_message = ""

    def _show_mobile_inputs(self) -> None:
        """Keep both native fields above the canvas for direct iOS taps."""
        if sys.platform != "emscripten":
            return

        import platform

        document = platform.document
        active_id = str(getattr(document.activeElement, "id", ""))
        for index, element_id in enumerate(MOBILE_INPUT_IDS):
            element = document.getElementById(element_id)
            created = element is None
            if created:
                element = document.createElement("input")
                element.id = element_id
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
                element.style.touchAction = "manipulation"
                element.style.pointerEvents = "auto"
                document.body.appendChild(element)

            label = "First player name" if index == 0 else "Second player name"
            color = self._css_color(PLAYER_COLORS[index])
            field_color = self._css_color(player_panel_color(PLAYER_COLORS[index]))
            if created or not self.mobile_inputs_visible:
                element.value = self.names[index]
            element.placeholder = label
            element.enterKeyHint = "next" if index == 0 else "done"
            element.setAttribute("aria-label", label)
            element.setAttribute("autocapitalize", "words")
            for event_name in ("keydown", "keypress", "keyup"):
                element.setAttribute(
                    f"on{event_name}",
                    "event.stopPropagation()",
                )
            element.style.display = "block"
            element.style.zIndex = str(MOBILE_INPUT_Z_INDEX)
            element.style.backgroundColor = field_color
            element.style.color = self._css_color(TEXT)
            border_width = 4 if active_id == element_id else 2
            element.style.border = f"{border_width}px solid {color}"
            element.style.caretColor = color
            self._position_mobile_input(element, index)

        self.mobile_inputs_visible = True

    def _sync_mobile_input(self) -> None:
        if sys.platform != "emscripten" or not self.mobile_inputs_visible:
            return

        import platform

        document = platform.document
        active_id = str(getattr(document.activeElement, "id", ""))
        focused_index: Optional[int] = None
        for index, element_id in enumerate(MOBILE_INPUT_IDS):
            element = document.getElementById(element_id)
            if element is None:
                continue
            self.names[index] = str(element.value)[:MAX_NAME_LENGTH]
            if active_id == element_id:
                focused_index = index

        self.mobile_input_index = focused_index
        if focused_index is not None:
            self.active_index = focused_index

    def _native_input_has_focus(self) -> bool:
        if sys.platform != "emscripten" or not self.mobile_inputs_visible:
            return False

        import platform

        active_id = str(getattr(platform.document.activeElement, "id", ""))
        return active_id in MOBILE_INPUT_IDS

    def _set_mobile_input_value(self, value: str) -> None:
        if sys.platform != "emscripten" or not self.mobile_inputs_visible:
            return

        import platform

        index = (
            self.mobile_input_index
            if self.mobile_input_index is not None
            else self.active_index
        )
        element = platform.document.getElementById(MOBILE_INPUT_IDS[index])
        if element is not None:
            element.value = value

    def hide_mobile_input(self) -> None:
        if sys.platform != "emscripten":
            self.mobile_input_index = None
            self.mobile_inputs_visible = False
            return

        import platform

        for element_id in MOBILE_INPUT_IDS:
            element = platform.document.getElementById(element_id)
            if element is not None:
                element.style.display = "none"
                element.blur()
        self.mobile_input_index = None
        self.mobile_inputs_visible = False

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
        draw_background(surface)
        panel = pygame.Rect(28, 55, WINDOW_WIDTH - 56, 505)
        draw_panel(surface, panel)
        draw_centered_text(surface, "Player Names", title_font, 105)
        draw_centered_text(
            surface,
            "Pick two names and let the friendly chaos begin.",
            body_font,
            158,
            MUTED_TEXT,
            max_width=panel.width - 30,
        )
        labels = ["First player", "Second player"]
        for index, rect in enumerate(self.input_rects):
            player_color = PLAYER_COLORS[index]
            label = body_font.render(labels[index], True, player_color)
            surface.blit(label, (rect.x, rect.y - 32))
            pygame.draw.rect(surface, (12, 17, 29), rect.move(0, 5), border_radius=12)
            pygame.draw.rect(surface, player_panel_color(player_color), rect, border_radius=12)
            border_width = 4 if self.active_index == index else 2
            pygame.draw.rect(
                surface,
                player_color,
                rect,
                border_width,
                border_radius=12,
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

        self._show_mobile_inputs()

        if self.error_message:
            draw_centered_text(surface, self.error_message, body_font, 470, ERROR)
        self.continue_button.draw(surface, button_font)

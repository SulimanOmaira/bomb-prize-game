"""Reusable Pygame button."""

from typing import ClassVar, Optional, Tuple

import pygame

from .settings import (
    BUTTON,
    BUTTON_DISABLED,
    BUTTON_HOVER,
    Color,
    TEXT,
)


class Button:
    pointer_position: ClassVar[Optional[Tuple[int, int]]] = None

    def __init__(
        self,
        text: str,
        position: Tuple[int, int],
        size: Tuple[int, int],
        normal_color: Color = BUTTON,
        hover_color: Color = BUTTON_HOVER,
    ) -> None:
        self.text = text
        self.rect = pygame.Rect(position, size)
        self.normal_color = normal_color
        self.hover_color = hover_color

    def is_clicked(self, event: pygame.event.Event, enabled: bool = True) -> bool:
        return (
            enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    @classmethod
    def set_pointer_position(cls, position: Tuple[int, int]) -> None:
        cls.pointer_position = position

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        enabled: bool = True,
    ) -> None:
        pointer = self.pointer_position or pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(pointer)
        if not enabled:
            color = BUTTON_DISABLED
        else:
            color = self.hover_color if hovered else self.normal_color
        pygame.draw.rect(surface, color, self.rect, border_radius=7)
        label = font.render(self.text, True, TEXT)
        surface.blit(label, label.get_rect(center=self.rect.center))

"""Drawing helpers shared by screens."""

from typing import Iterator, Tuple

import pygame

from game.settings import (
    BOARD_SIZE,
    CELL_GAP,
    CELL_HEIGHT,
    CELL_WIDTH,
    MUTED_TEXT,
    PRIZE_CELL,
    TEXT,
)


def draw_centered_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    y: int,
    color: Tuple[int, int, int] = TEXT,
) -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(rendered, rect)
    return rect


def board_pixel_width(size: int = BOARD_SIZE) -> int:
    return size * CELL_WIDTH + (size - 1) * CELL_GAP


def iter_board_rects(
    origin_x: int,
    origin_y: int,
    size: int = BOARD_SIZE,
) -> Iterator[Tuple[int, int, pygame.Rect]]:
    for row in range(size):
        for column in range(size):
            x = origin_x + column * (CELL_WIDTH + CELL_GAP)
            y = origin_y + row * (CELL_HEIGHT + CELL_GAP)
            yield row, column, pygame.Rect(x, y, CELL_WIDTH, CELL_HEIGHT)


def draw_bomb_symbol(surface: pygame.Surface, rect: pygame.Rect) -> None:
    center = (rect.centerx, rect.centery + 4)
    radius = max(9, min(rect.width, rect.height) // 5)
    pygame.draw.circle(surface, TEXT, center, radius)
    pygame.draw.line(
        surface,
        TEXT,
        (center[0] + radius // 2, center[1] - radius + 2),
        (center[0] + radius, center[1] - radius - 7),
        3,
    )
    pygame.draw.circle(
        surface,
        PRIZE_CELL,
        (center[0] + radius + 2, center[1] - radius - 9),
        3,
    )


def draw_prize_symbol(surface: pygame.Surface, rect: pygame.Rect) -> None:
    cx, cy = rect.center
    half = max(10, min(rect.width, rect.height) // 5)
    points = [(cx, cy - half), (cx + half, cy), (cx, cy + half), (cx - half, cy)]
    pygame.draw.polygon(surface, TEXT, points)
    pygame.draw.polygon(surface, MUTED_TEXT, points, 2)

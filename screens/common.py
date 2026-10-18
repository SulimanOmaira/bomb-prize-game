"""Drawing helpers shared by screens."""

from typing import Dict, Iterator, Optional, Tuple

import pygame

from game.settings import (
    BACKGROUND,
    BACKGROUND_BOTTOM,
    BOARD_SIZE,
    BORDER,
    CELL_GAP,
    CELL_HEIGHT,
    CELL_WIDTH,
    MUTED_TEXT,
    PANEL,
    PANEL_LIGHT,
    PRIZE_CELL,
    TEXT,
    Color,
)

_BACKGROUND_CACHE: Dict[Tuple[int, int], pygame.Surface] = {}


def _mix_color(first: Color, second: Color, amount: float) -> Color:
    return tuple(
        round(a * (1 - amount) + b * amount)
        for a, b in zip(first, second)
    )


def draw_background(surface: pygame.Surface) -> None:
    cache_key = surface.get_size()
    cached = _BACKGROUND_CACHE.get(cache_key)
    if cached is not None:
        surface.blit(cached, (0, 0))
        return

    cached = pygame.Surface(cache_key)
    height = surface.get_height()
    for y in range(height):
        amount = y / max(1, height - 1)
        pygame.draw.line(
            cached,
            _mix_color(BACKGROUND, BACKGROUND_BOTTOM, amount),
            (0, y),
            (surface.get_width(), y),
        )

    pygame.draw.circle(cached, (58, 74, 113), (50, 80), 125)
    pygame.draw.circle(cached, (69, 55, 110), (surface.get_width() - 35, 610), 180)
    _BACKGROUND_CACHE[cache_key] = cached
    surface.blit(cached, (0, 0))


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    accent: Optional[Color] = None,
    border_width: int = 2,
    radius: int = 16,
) -> None:
    shadow = rect.move(0, 8)
    pygame.draw.rect(surface, (11, 15, 26), shadow, border_radius=radius)
    pygame.draw.rect(surface, PANEL, rect, border_radius=radius)
    inner = rect.inflate(-8, -8)
    if inner.width > 0 and inner.height > 0:
        pygame.draw.rect(surface, PANEL_LIGHT, inner, 1, border_radius=radius - 3)
    if accent is not None:
        pygame.draw.rect(surface, accent, rect, border_width, border_radius=radius)


def draw_pill(surface: pygame.Surface, rect: pygame.Rect, color: Color) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, BORDER, rect, 2, border_radius=rect.height // 2)


def draw_game_cell(
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: Color,
    border: Color = BORDER,
    radius: int = 9,
) -> None:
    pygame.draw.rect(surface, (12, 17, 29), rect.move(0, 4), border_radius=radius)
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    highlight = pygame.Surface((rect.width - 8, 12), pygame.SRCALPHA)
    pygame.draw.rect(highlight, (255, 255, 255, 42), highlight.get_rect(), border_radius=6)
    surface.blit(highlight, (rect.x + 4, rect.y + 4))
    pygame.draw.rect(surface, border, rect, 2, border_radius=radius)


def draw_centered_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    y: int,
    color: Tuple[int, int, int] = TEXT,
    max_width: Optional[int] = None,
) -> pygame.Rect:
    rendered = font.render(text, True, color)
    available_width = max_width or surface.get_width() - 32
    if rendered.get_width() > available_width:
        scale = available_width / rendered.get_width()
        rendered = pygame.transform.smoothscale(
            rendered,
            (
                available_width,
                max(1, round(rendered.get_height() * scale)),
            ),
        )
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

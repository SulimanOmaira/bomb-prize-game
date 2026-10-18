"""Shared configuration values for the game."""

import sys
from typing import Final, Optional, Tuple

Color = Tuple[int, int, int]
Viewport = Tuple[int, int]


def choose_content_size(viewport: Optional[Viewport]) -> Viewport:
    """Return a touch-friendly logical size for the current viewport."""
    if viewport is not None:
        width, height = viewport
        if width <= 600 and height >= width:
            return 480, 700
    return 900, 700


def choose_display_size(content: Viewport, viewport: Optional[Viewport]) -> Viewport:
    """Match the browser aspect ratio without stretching the game surface."""
    if viewport is None:
        return content

    content_width, content_height = content
    viewport_width, viewport_height = viewport
    if viewport_width <= 0 or viewport_height <= 0:
        return content

    viewport_ratio = viewport_width / viewport_height
    content_ratio = content_width / content_height
    if viewport_ratio >= content_ratio:
        return round(content_height * viewport_ratio), content_height
    return content_width, round(content_width / viewport_ratio)


def _browser_viewport() -> Optional[Viewport]:
    if sys.platform != "emscripten":
        return None
    try:
        import platform

        width = int(platform.window.innerWidth)
        height = int(platform.window.innerHeight)
    except (AttributeError, TypeError, ValueError):
        return None
    if width <= 0 or height <= 0:
        return None
    return width, height


_VIEWPORT: Final = _browser_viewport()
WINDOW_WIDTH, WINDOW_HEIGHT = choose_content_size(_VIEWPORT)
DISPLAY_WIDTH, DISPLAY_HEIGHT = WINDOW_WIDTH, WINDOW_HEIGHT
COMPACT_LAYOUT: Final = WINDOW_WIDTH < 700
WINDOW_TITLE: Final = "Bomb Prize Game"
FPS: Final = 60

BOARD_SIZE: Final = 3
CELL_GAP: Final = 5
BOARD_HORIZONTAL_MARGIN: Final = 18
CELL_WIDTH: Final = min(
    130,
    (
        WINDOW_WIDTH
        - (BOARD_HORIZONTAL_MARGIN * 2)
        - ((BOARD_SIZE - 1) * CELL_GAP)
    )
    // BOARD_SIZE,
)
CELL_HEIGHT: Final = CELL_WIDTH
BOMBS_REQUIRED: Final = 3
PRIZES_REQUIRED: Final = 1
MAX_NAME_LENGTH: Final = 15

BACKGROUND: Final[Color] = (18, 24, 38)
BACKGROUND_BOTTOM: Final[Color] = (44, 34, 76)
PANEL: Final[Color] = (35, 43, 66)
PANEL_LIGHT: Final[Color] = (48, 58, 86)
TEXT: Final[Color] = (255, 250, 238)
MUTED_TEXT: Final[Color] = (199, 207, 226)
BUTTON: Final[Color] = (238, 104, 91)
BUTTON_HOVER: Final[Color] = (255, 139, 103)
BUTTON_DISABLED: Final[Color] = (90, 96, 118)
HIDDEN_CELL: Final[Color] = (98, 190, 213)
EMPTY_CELL: Final[Color] = (118, 130, 154)
BOMB_CELL: Final[Color] = (226, 70, 78)
PRIZE_CELL: Final[Color] = (255, 207, 89)
SELECTED_BOMB: Final[Color] = (233, 83, 91)
SELECTED_PRIZE: Final[Color] = (83, 211, 151)
BORDER: Final[Color] = (255, 241, 207)
ERROR: Final[Color] = (255, 117, 128)
SUCCESS: Final[Color] = (108, 232, 166)
INPUT_ACTIVE: Final[Color] = (255, 207, 89)
INPUT_INACTIVE: Final[Color] = (138, 148, 176)
PLAYER_ONE_COLOR: Final[Color] = (88, 208, 255)
PLAYER_TWO_COLOR: Final[Color] = (255, 197, 78)
PLAYER_COLORS: Final[Tuple[Color, Color]] = (
    PLAYER_ONE_COLOR,
    PLAYER_TWO_COLOR,
)


def blend_color(base: Color, accent: Color, accent_weight: float) -> Color:
    """Blend an accent into a base color while keeping text contrast readable."""
    return tuple(
        round(base_channel * (1 - accent_weight) + accent_channel * accent_weight)
        for base_channel, accent_channel in zip(base, accent)
    )


def player_panel_color(accent: Color) -> Color:
    """Return a dark player-tinted color for panels and input fields."""
    return blend_color(PANEL, accent, 0.28)


def player_cell_color(accent: Color) -> Color:
    """Return a stronger player-tinted color for unrevealed board cells."""
    return blend_color(PANEL, accent, 0.66)

"""Shared configuration values for the game."""

from typing import Final, Tuple

Color = Tuple[int, int, int]

WINDOW_WIDTH: Final = 900
WINDOW_HEIGHT: Final = 700
WINDOW_TITLE: Final = "Bomb Prize Game"
FPS: Final = 60

BOARD_SIZE: Final = 6
CELL_GAP: Final = 5
BOARD_HORIZONTAL_MARGIN: Final = 18
CELL_WIDTH: Final = (
    WINDOW_WIDTH
    - (BOARD_HORIZONTAL_MARGIN * 2)
    - ((BOARD_SIZE - 1) * CELL_GAP)
) // BOARD_SIZE
CELL_HEIGHT: Final = 64
BOMBS_REQUIRED: Final = 3
PRIZES_REQUIRED: Final = 1
MAX_NAME_LENGTH: Final = 15

BACKGROUND: Final[Color] = (28, 38, 56)
PANEL: Final[Color] = (39, 53, 76)
TEXT: Final[Color] = (244, 247, 252)
MUTED_TEXT: Final[Color] = (180, 192, 210)
BUTTON: Final[Color] = (38, 105, 180)
BUTTON_HOVER: Final[Color] = (52, 132, 220)
BUTTON_DISABLED: Final[Color] = (82, 93, 110)
HIDDEN_CELL: Final[Color] = (84, 166, 218)
EMPTY_CELL: Final[Color] = (125, 135, 148)
BOMB_CELL: Final[Color] = (210, 62, 62)
PRIZE_CELL: Final[Color] = (238, 190, 58)
SELECTED_BOMB: Final[Color] = (202, 68, 68)
SELECTED_PRIZE: Final[Color] = (76, 177, 102)
BORDER: Final[Color] = (218, 228, 240)
ERROR: Final[Color] = (255, 116, 116)
SUCCESS: Final[Color] = (112, 220, 142)
INPUT_ACTIVE: Final[Color] = (84, 166, 218)
INPUT_INACTIVE: Final[Color] = (120, 134, 153)

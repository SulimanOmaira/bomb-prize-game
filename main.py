"""Application entry point for Bomb Prize Game."""

import asyncio
import os
import sys
from typing import Optional, Union

if sys.platform == "emscripten":
    os.environ["SDL_EMSCRIPTEN_KEYBOARD_ELEMENT"] = "#canvas"

import pygame

from game.button import Button
from game.game_manager import GameManager
from game.settings import (
    BACKGROUND,
    COMPACT_LAYOUT,
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    FPS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from screens.gameplay_screen import GameplayScreen
from screens.main_menu import MainMenu
from screens.names_screen import NamesScreen
from screens.pass_screen import PassScreen
from screens.result_screen import ResultScreen
from screens.setup_screen import SetupScreen

Screen = Union[
    MainMenu,
    NamesScreen,
    SetupScreen,
    PassScreen,
    GameplayScreen,
    ResultScreen,
]


class GameApplication:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.display_surface = pygame.display.set_mode(
            (DISPLAY_WIDTH, DISPLAY_HEIGHT)
        )
        self.viewport_scale = min(
            DISPLAY_WIDTH / WINDOW_WIDTH,
            DISPLAY_HEIGHT / WINDOW_HEIGHT,
        )
        self.viewport_size = (
            round(WINDOW_WIDTH * self.viewport_scale),
            round(WINDOW_HEIGHT * self.viewport_scale),
        )
        self.viewport_offset = (
            (DISPLAY_WIDTH - self.viewport_size[0]) // 2,
            (DISPLAY_HEIGHT - self.viewport_size[1]) // 2,
        )
        self.surface = (
            self.display_surface
            if self.viewport_size == (WINDOW_WIDTH, WINDOW_HEIGHT)
            else pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        )
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 40 if COMPACT_LAYOUT else 46)
        self.body_font = pygame.font.Font(None, 25 if COMPACT_LAYOUT else 30)
        self.button_font = pygame.font.Font(None, 25 if COMPACT_LAYOUT else 29)

        self.manager = GameManager()
        self.menu = MainMenu()
        self.names_screen = NamesScreen()
        self.screen: Screen = self.menu
        self.state = "menu"
        self.pass_destination = ""
        self.running = True
        self.debug_frame_logged = False

    async def run(self) -> None:
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                    event = self._to_game_event(event)
                    action = self.screen.handle_event(event)
                    if action is not None:
                        self._handle_action(action)

                if not self.running:
                    break
                Button.set_pointer_position(
                    self._to_game_position(pygame.mouse.get_pos())
                )
                self.screen.draw(
                    self.surface,
                    self.title_font,
                    self.body_font,
                    self.button_font,
                )
                if not self.debug_frame_logged:
                    print(
                        "Bomb Prize Game: first frame drawn",
                        {
                            "state": self.state,
                            "window": (WINDOW_WIDTH, WINDOW_HEIGHT),
                            "display": (DISPLAY_WIDTH, DISPLAY_HEIGHT),
                            "viewport_size": self.viewport_size,
                            "viewport_offset": self.viewport_offset,
                        },
                    )
                    self.debug_frame_logged = True
                self._present()
                self._force_browser_canvas_refresh()
                pygame.display.flip()
                pygame.display.update(pygame.Rect(0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT))
                self.clock.tick(FPS)
                await asyncio.sleep(0)
        finally:
            pygame.quit()

    def _to_game_event(self, event: pygame.event.Event) -> pygame.event.Event:
        if not hasattr(event, "pos"):
            return event

        position = self._to_game_position(event.pos)
        attributes = dict(event.dict)
        attributes["pos"] = position
        return pygame.event.Event(event.type, attributes)

    def _to_game_position(self, position: tuple[int, int]) -> tuple[int, int]:
        offset_x, offset_y = self.viewport_offset
        x = round((position[0] - offset_x) / self.viewport_scale)
        y = round((position[1] - offset_y) / self.viewport_scale)
        return x, y

    def _present(self) -> None:
        if self.surface is self.display_surface:
            return

        self.display_surface.fill(BACKGROUND)
        if self.viewport_size == (WINDOW_WIDTH, WINDOW_HEIGHT):
            rendered = self.surface
        else:
            rendered = pygame.transform.smoothscale(
                self.surface,
                self.viewport_size,
            )
        self.display_surface.blit(rendered, self.viewport_offset)

    def _force_browser_canvas_refresh(self) -> None:
        """Force pygbag's browser canvas to present without visible debug art."""
        if sys.platform != "emscripten":
            return

        # The visible pink rectangle worked because it forced a final large
        # draw on the real display surface. This self-copy keeps the pixels
        # identical while still giving pygbag/SDL a final display-surface blit.
        self.display_surface.blit(self.display_surface.copy(), (0, 0))

    def _handle_action(self, action: object) -> None:
        if action == "quit":
            self.running = False
            return
        if action == "menu":
            self._go_to_menu()
            return

        if self.state == "menu" and action == "start":
            self.manager.clear_game()
            self.names_screen.reset()
            self.screen = self.names_screen
            self.state = "names"
            return

        if self.state == "names":
            if isinstance(action, tuple) and action[0] == "submit":
                first_name, second_name = action[1]
                self.manager.create_players(first_name, second_name)
                self._show_setup(0)
            return

        if self.state == "setup_0" and action == "confirmed":
            self._show_pass(
                self.manager.players[1].name,
                self.manager.players[1].accent_color,
                "Your secret board is next.",
                "setup_1",
            )
            return

        if self.state == "setup_1" and action == "confirmed":
            self._show_pass(
                self.manager.players[0].name,
                self.manager.players[0].accent_color,
                "The match will begin with your turn.",
                "gameplay",
            )
            return

        if self.state == "pass" and action == "ready":
            if self.pass_destination == "setup_1":
                self._show_setup(1)
            elif self.pass_destination == "gameplay":
                self._show_gameplay()
            return

        if self.state == "gameplay":
            if action == "game_over":
                self.screen = ResultScreen(self.manager)
                self.state = "result"
            elif action == "end_turn":
                self.manager.switch_turn()
                self._show_pass(
                    self.manager.current_player.name,
                    self.manager.current_player.accent_color,
                    "It is now your turn.",
                    "gameplay",
                )
            return

        if self.state == "result":
            if action == "replay":
                self.manager.reset_same_names()
                self._show_setup(0)
            elif action == "new_game":
                self.manager.clear_game()
                self.names_screen.reset()
                self.screen = self.names_screen
                self.state = "names"

    def _show_setup(self, player_index: int) -> None:
        self.screen = SetupScreen(self.manager.players[player_index])
        self.state = f"setup_{player_index}"

    def _show_pass(
        self,
        next_player_name: str,
        next_player_color: tuple[int, int, int],
        message: str,
        destination: str,
    ) -> None:
        self.pass_destination = destination
        self.screen = PassScreen(
            next_player_name,
            next_player_color,
            message,
        )
        self.state = "pass"

    def _show_gameplay(self) -> None:
        if not self.manager.both_boards_ready():
            self._go_to_menu()
            return
        self.screen = GameplayScreen(self.manager)
        self.state = "gameplay"

    def _go_to_menu(self) -> None:
        self.names_screen.hide_mobile_input()
        self.manager.clear_game()
        self.menu.reset()
        self.screen = self.menu
        self.state = "menu"
        self.pass_destination = ""


async def main() -> None:
    application: Optional[GameApplication] = None
    try:
        application = GameApplication()
        await application.run()
    finally:
        if application is None:
            pygame.quit()


if __name__ == "__main__" or sys.argv == [""]:
    print("Bomb Prize Game: starting")
    asyncio.run(main())

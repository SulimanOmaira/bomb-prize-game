"""Application entry point for Bomb Prize Game."""

import asyncio
from typing import Optional, Union

import pygame

from game.game_manager import GameManager
from game.settings import (
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
        self.surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 46)
        self.body_font = pygame.font.Font(None, 30)
        self.button_font = pygame.font.Font(None, 29)

        self.manager = GameManager()
        self.menu = MainMenu()
        self.names_screen = NamesScreen()
        self.screen: Screen = self.menu
        self.state = "menu"
        self.pass_destination = ""
        self.running = True

    async def run(self) -> None:
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                    action = self.screen.handle_event(event)
                    if action is not None:
                        self._handle_action(action)

                if not self.running:
                    break
                self.screen.draw(
                    self.surface,
                    self.title_font,
                    self.body_font,
                    self.button_font,
                )
                pygame.display.flip()
                self.clock.tick(FPS)
                await asyncio.sleep(0)
        finally:
            pygame.quit()

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
                "Your secret board is next.",
                "setup_1",
            )
            return

        if self.state == "setup_1" and action == "confirmed":
            self._show_pass(
                self.manager.players[0].name,
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
        message: str,
        destination: str,
    ) -> None:
        self.pass_destination = destination
        self.screen = PassScreen(next_player_name, message)
        self.state = "pass"

    def _show_gameplay(self) -> None:
        if not self.manager.both_boards_ready():
            self._go_to_menu()
            return
        self.screen = GameplayScreen(self.manager)
        self.state = "gameplay"

    def _go_to_menu(self) -> None:
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


if __name__ == "__main__":
    asyncio.run(main())

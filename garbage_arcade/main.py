'''
Garbage Card Game (AKA Trash)

Created by Mitch Gates (github.com/mistergates)
'''
import ctypes

import arcade

from .enums import Views
from .game_view import GameView
from .main_menu_view import MainMenuView
from .rules_view import RulesView
from .game_over_view import GameOverView

SCREEN_WIDTH = int(ctypes.windll.user32.GetSystemMetrics(0) * .75)
SCREEN_HEIGHT = int(ctypes.windll.user32.GetSystemMetrics(1) * .75)
SCREEN_TITLE = 'Garbage Card Game'
FPS = 60

class GameWindow(arcade.Window):
    """Main Garbage card game window that holds views"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True, fullscreen=True)
        # Window height/width
        self.screen_width = width
        self.screen_height = height
        self.main_menu_view = MainMenuView()
        self.game_view = GameView()
        self.rules_view = RulesView()
        self.game_over_view = GameOverView()

        self.set_update_rate(1 / FPS)

        # Parent vars shared across views
        self.volume = 1
        self.font = 'GARA'

    def on_resize(self, width, height):
        """This method is automatically called when the window is resized"""
        # Set screen width/height to new values
        self.screen_width = width
        self.screen_height = height

        # Set screen width on the current view as well
        self.current_view.screen_width = width
        self.current_view.screen_height = height

        # Call the parent. Failing to do this will mess up the coordinates
        super().on_resize(self.screen_width, self.screen_height)

        # Update title screen during resize
        if self.current_view.view_name == Views.main_menu:
            self.current_view.create_sprites()

        # Update cards during resize
        if self.current_view.view_name == Views.garbage:
            self.current_view.update_card_positions()

    def on_key_press(self, key, modifiers):
        """Check for key presses"""
        if key == arcade.key.ESCAPE:
            if self.current_view.view_name == Views.garbage:
                self.game_view.paused = True
                self.show_view(self.main_menu_view)
            elif self.current_view.view_name == Views.main_menu and self.game_view.game_started:
                self.show_view(self.game_view)
                self.game_view.paused = False
            elif self.current_view.view_name == Views.rules:
                self.show_view(self.main_menu_view)

        # if key == arcade.key.MINUS:
        #     self.volume -= .1 if self.volume >= .1 else 0
        #     print(self.volume)
        # if key == arcade.key.PLUS:
        #     self.volume += .1 if self.volume <= .9 else 1

def play():
    """Main method"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(window.main_menu_view)
    arcade.run()

if __name__ == "__main__":
    play()

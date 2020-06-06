'''
Garbage Card Game (AKA Trash)

Created by Mitch Gates (github.com/mistergates)

=====
TODO
=====
- Fix bug where if player right-clicks to discard while card is over discard pile it skips computer's turn
- Add logic to not end turn if you discard a card picked up from discard pile
- Add logic to discard card if there is on-click collision on discard pile
- Show winner view when there is a winner, option to continue to next hand
- Show winner when no remaining cards left for player/computer
'''
import arcade
import ctypes

from . import cards
from .enums import Views
from .views import MainMenu, Garbage, Rules

SCREEN_WIDTH = int(ctypes.windll.user32.GetSystemMetrics(0) * .75)
SCREEN_HEIGHT = int(ctypes.windll.user32.GetSystemMetrics(1) * .75)
SCREEN_TITLE = 'Garbage Card Game'

class GameWindow(arcade.Window):
    """Main Garbage card game window that holds views"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        # Window height/width
        self.screen_width = width
        self.screen_height = height
        self.title_view = MainMenu()
        self.game_view = Garbage()
        self.rules_view = Rules()

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
        if key == arcade.key.ESCAPE:
            if self.current_view.view_name == Views.garbage:
                self.game_view.paused = True
                self.show_view(self.title_view)
            elif self.current_view.view_name == Views.main_menu and self.game_view.game_started:
                self.show_view(self.game_view)
                self.game_view.paused = False
            elif self.current_view.view_name == Views.rules:
                self.show_view(self.title_view)

def play():
    """Main method"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(window.title_view)
    arcade.run()

if __name__ == "__main__":
    play()

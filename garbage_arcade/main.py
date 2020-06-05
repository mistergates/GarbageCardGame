'''
Garbage Card Game (AKA Trash)

Created by Mitch Gates (github.com/mistergates)

=====
TODO
=====
MUST HAVE:
------------
- Move card sprite creation to function (like title screen) so sprites are re-created on resize
- Shuffle cards from discard pile back into a draw pile if we run out
- Setup computer AI
- Show winner view when there is a winner, option to continue to next hand
- Show winner when no remaining cards left for player/computer

NICE TO HAVE:
-------------
- Music
- Escape Menu (Exit, Music Toggle)
'''
import arcade
import ctypes

from . import cards
from .enums import Views
from .views import MainMenu, Garbage

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

def play():
    """Main method"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(window.title_view)
    arcade.run()

if __name__ == "__main__":
    play()

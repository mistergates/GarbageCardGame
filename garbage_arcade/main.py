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
- Show winner when no remaining cards left for player/computer

NICE TO HAVE:
-------------
- Escape Menu (Exit, Music Toggle)
- Music
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
            self.update_card_positions()

    def update_card_positions(self):
        # Position Player Cards
        x, y = self.current_view.calc_card_pos(player=True)
        x_orig = x
        for i, card in enumerate(self.current_view.player_card_list):
            if i == 5:
                # Maximum of 5 cards per row, restart at orig x for next row
                y -= cards.CARD_HEIGHT + cards.CARD_BUFFER_Y
                x = x_orig

            card.position = x, y
            x += cards.CARD_WIDTH + cards.CARD_BUFFER_X

        # Position Computer cards
        x, y = self.current_view.calc_card_pos(computer=True)
        x_orig = x
        for i, card in enumerate(self.current_view.computer_card_list):
            if i == 5:
                # Maximum of 5 cards per row, restart at orig x for next row
                y += cards.CARD_HEIGHT + cards.CARD_BUFFER_Y
                x = x_orig

            card.position = x, y
            x -= cards.CARD_WIDTH + cards.CARD_BUFFER_X

        # Position draw pile cards
        x, y = self.current_view.calc_card_pos(draw=True)
        for card in self.current_view.draw_pile_list:
            card.position = x, y

        # Position the discard pile cards
        x, y = self.current_view.calc_card_pos(discard=True)
        for card in self.current_view.discard_pile_list:
            card.position = x, y

def play():
    """Main method"""
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = MainMenu()
    window.show_view(start_view)
    # start_view.setup()
    arcade.run()

if __name__ == "__main__":
    play()

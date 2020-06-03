'''
Garbage Card Game (AKA Trash)

Created by Mitch Gates (github.com/mistergates)

TODO
MUST HAVE:
1. Redraw screen correctly when there is a winner
2. Setup computer AI
3. Show winner when no remaining cards left for player/computer

NICE TO HAVE:
1. Escape Menu

'''
import arcade
import ctypes

from . import cards

SCREEN_WIDTH = int(ctypes.windll.user32.GetSystemMetrics(0) * .75)
SCREEN_HEIGHT = int(ctypes.windll.user32.GetSystemMetrics(1) * .75)
SCREEN_TITLE = 'Garbage Card Game'
NUMBER_OF_DECKS = 1

class GetMousePos(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class Garbage(arcade.Window):
    """Main Garbage card game class"""

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        # Window height/width
        self.screen_width = width
        self.screen_height = height

        arcade.set_background_color(arcade.color.AMAZON)

        # Card lists (cards on playing board)
        self.player_card_list = arcade.SpriteList()
        self.computer_card_list = arcade.SpriteList()
        self.draw_pile_list = arcade.SpriteList()
        self.discard_pile_list = arcade.SpriteList()
        self.card_in_hand_list = arcade.SpriteList()

        # Game State
        self.player_cards_remain = 10
        self.computer_cards_remain = 10
        self.current_round = 1
        self.player_turn = True
        self.computer_turn = False
        self.card_in_hand = None

    def setup(self):
        """Sets up the game. This should be called each time a round starts"""
        starting_deck = cards.build_decks(NUMBER_OF_DECKS)

        # Create player cards
        for i in range(self.player_cards_remain):
            card = cards.CardBack(
                cards.PLAYER_COLOR,
                version=cards.CARD_BACK_VERSION,
                scale=cards.CARD_SCALE
            )
            card.value, card.suit = starting_deck.pop(0)
            card.display = False
            card.index = i
            self.player_card_list.append(card)

        # Create computer cards
        for i in range(self.computer_cards_remain):
            card = cards.CardBack(
                cards.COMPUTER_COLOR,
                version=cards.CARD_BACK_VERSION,
                scale=cards.CARD_SCALE
            )
            card.value, card.suit = starting_deck.pop(0)
            card.display = False
            card.index = i
            self.computer_card_list.append(card)

        # Create draw pile
        for x in starting_deck:
            card = cards.CardBack(
                cards.DRAW_PILE_COLOR,
                version=cards.CARD_BACK_VERSION,
                scale=cards.CARD_SCALE
            )
            card.value, card.suit = x
            card.display = False
            self.draw_pile_list.append(card)

    def on_mouse_press(self, x, y, button, key_modifiers):
        """Called when the user presses a mouse button"""
        # Do nothing if not player's turn
        if not self.player_turn:
            return

        # Discard on right-click
        if button == arcade.MOUSE_BUTTON_RIGHT and self.card_in_hand:
            card = cards.CardFront(self.card_in_hand.suit, self.card_in_hand.value, cards.CARD_SCALE)
            card.position = self.calc_card_pos(discard=True)
            self.discard_pile_list.append(card)
            self.card_in_hand.kill()
            self.card_in_hand = None

            # End the player's turn on discard
            # self.player_turn = False
            # self.computer_turn = True

        # Check draw pile
        draw_pile_cards = arcade.get_sprites_at_point((x, y), self.draw_pile_list)
        if draw_pile_cards and not self.card_in_hand:
            # Grab the top card from the deck
            card = draw_pile_cards[-1]
            card_front = cards.CardFront(card.suit, card.value, scale=cards.CARD_SCALE)
            card_front.position = x, y
            card_front.display = True
            # Assign the card drawn to hand
            self.card_in_hand = card_front
            self.card_in_hand_list.append(card_front)
            # Kill the card in the draw pile
            card.kill()

        # Check discard pile
        discard_pile_cards = arcade.get_sprites_at_point((x, y), self.discard_pile_list)
        if discard_pile_cards and not self.card_in_hand:
            # Grab the top card from the deck
            card = discard_pile_cards[-1]
            card_front = cards.CardFront(card.suit, card.value, scale=cards.CARD_SCALE)
            card_front.position = x, y
            card_front.display = True
            # Assign the card drawn to hand
            self.card_in_hand = card_front
            self.card_in_hand_list.append(card_front)
            # Kill the card in the draw pile
            card.kill()

        # Check collision with player's cards
        player_table_card = arcade.get_sprites_at_point((x, y), self.player_card_list)
        if player_table_card and self.card_in_hand:
            card = player_table_card[0]

            # Check to see if card is playable
            if self.is_card_playable(card):
                print(f'{self.card_in_hand.value} is playable for card at index {card.index}')
                card_from_table = cards.CardFront(card.suit, card.value, scale=cards.CARD_SCALE)
                card_from_table.position = x, y

                # Place card in hand on table
                self.player_card_list[card.index] = self.card_in_hand
                self.player_card_list[card.index].position = card.position
                self.player_card_list[card.index].index = card.index

                # Kill current card in hand
                self.card_in_hand.kill()

                self.card_in_hand = card_from_table
                self.card_in_hand_list.append(card_from_table)

                card.kill()

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """

        # If we are holding cards, move them with the mouse
        if self.card_in_hand_list:
            self.card_in_hand_list[0].center_x += dx
            self.card_in_hand_list[0].center_y += dy

    def on_draw(self):
        """Render the screen"""
        # This command has to happen before we start drawing
        arcade.start_render()

        self.check_for_winner()

        # Draw a grid to show absolute center
        # arcade.draw_line(
        #     start_x=0,
        #     start_y=self.screen_height / 2,
        #     end_x=self.screen_width,
        #     end_y=self.screen_height / 2,
        #     color=arcade.color.BLACK,
        #     line_width=2
        # )
        # arcade.draw_line(
        #     start_x=self.screen_width / 2,
        #     start_y=0,
        #     end_x=self.screen_width / 2,
        #     end_y=self.screen_height,
        #     color=arcade.color.BLACK,
        #     line_width=2
        # )

        # Display turn
        turn_text = "Player's Turn" if self.player_turn else "Computer's Turn"
        arcade.draw_text(
            turn_text,
            self.screen_width / 2,
            self.screen_height / 2,
            arcade.color.WHITE,
            24,
            font_name="GARA",
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

        # Draw the cards
        self.player_card_list.draw()
        self.computer_card_list.draw()
        self.draw_pile_list.draw()
        self.discard_pile_list.draw()
        self.card_in_hand_list.draw()

    def on_resize(self, width, height):
        """This method is automatically called when the window is resized"""
        # Set screen width/height to new values
        self.screen_width = width
        self.screen_height = height

        # Call the parent. Failing to do this will mess up the coordinates
        super().on_resize(self.screen_width, self.screen_height)

        # Position Player Cards
        x, y = self.calc_card_pos(player=True)
        x_orig = x
        for i, card in enumerate(self.player_card_list):
            if i == 5:
                # Maximum of 5 cards per row, restart at orig x for next row
                y -= cards.CARD_HEIGHT + cards.CARD_BUFFER_Y
                x = x_orig

            card.position = x, y
            x += cards.CARD_WIDTH + cards.CARD_BUFFER_X

        # Position Computer cards
        x, y = self.calc_card_pos(computer=True)
        x_orig = x
        for i, card in enumerate(self.computer_card_list):
            if i == 5:
                # Maximum of 5 cards per row, restart at orig x for next row
                y += cards.CARD_HEIGHT + cards.CARD_BUFFER_Y
                x = x_orig

            card.position = x, y
            x -= cards.CARD_WIDTH + cards.CARD_BUFFER_X

        # Position draw pile cards
        x, y = self.calc_card_pos(draw=True)
        for card in self.draw_pile_list:
            card.position = x, y

        # Position the discard pile cards
        x, y = self.calc_card_pos(discard=True)
        for card in self.discard_pile_list:
            card.position = x, y

    def is_card_playable(self, card):
        """Checks to see if card in hand is playable on card"""
        if card.display is True:
            return False if card.value not in cards.WILD_CARDS else True

        if self.card_in_hand.value in cards.WILD_CARDS:
            return True

        if cards.CARD_MATCHES[card.index] == self.card_in_hand.value:
            return True

        return False

    def calc_card_pos(self, computer=False, player=False, draw=False, discard=False):
        """
        This method calculates the card starting positions for player/computer.
        Relies on screen size and card size for calculations.
        """
        if player:
            x = (self.screen_width / 2) - (cards.CARD_WIDTH * 2) - (cards.CARD_BUFFER_X * 2)
            y = cards.CARD_HEIGHT * 1.75
        if computer:
            x = (self.screen_width / 2)  + (cards.CARD_WIDTH * 2) + (cards.CARD_BUFFER_X * 2)
            y = self.screen_height - (cards.CARD_HEIGHT * 1.75)
        if draw:
            x = cards.CARD_WIDTH * .75
            y = self.screen_height / 2
        if discard:
            x = cards.CARD_WIDTH * 2
            y = self.screen_height / 2

        return x, y


    def check_for_winner(self):
        num_cards_displayed = 0
        for card in self.player_card_list:
            num_cards_displayed += 1 if card.display else 0

        if num_cards_displayed == self.player_cards_remain:
            self.player_cards_remain -= 1
            self.setup()

def play():
    """Main method"""
    window = Garbage(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    play()

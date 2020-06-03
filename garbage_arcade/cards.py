import arcade
from random import sample

# Constants for sizing
CARD_SCALE = 0.90

# How big are the cards?
CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

# Buffer px between cards
CARD_BUFFER_X = 10
CARD_BUFFER_Y = 10

# Card constants
CARD_VALUES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]
WILD_CARDS = ["J"]
CARD_MATCHES = {0: 'A', 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10}

# Colors
PLAYER_COLOR = 'Blue'
COMPUTER_COLOR = 'Red'
DRAW_PILE_COLOR = 'Green'
CARD_BACK_VERSION = 5

class CardFront(arcade.Sprite):
    """ Card sprite """

    def __init__(self, suit, value, scale=1):
        """ Card constructor """
        # Attributes for suit and value
        self.suit = suit
        self.value = value
        self.display = True

        # Image to use for the sprite when face up
        self.image_file_name = f":resources:images/cards/card{suit}{value}.png"

        # Call the parent
        super().__init__(self.image_file_name, scale, calculate_hit_box=False)

class CardBack(arcade.Sprite):
    """ Card sprite """

    def __init__(self, color, version=5, scale=1):
        """ Card constructor """
        # Attributes
        self.display = False

        # Image to use for the sprite when face down
        self.image_file_name = f":resources:images/cards/cardBack_{color}{version}.png"

        # Call the parent
        super().__init__(self.image_file_name, scale, calculate_hit_box=False)

def build_decks(num_decks):
    decks = []

    for dummy in range(num_decks):
        deck = []

        for suit in CARD_SUITS:
            for val in CARD_VALUES:
                deck.append((val, suit))

        decks += deck

    return sample(decks, len(decks))

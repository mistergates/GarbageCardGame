'''
Card image assets obtained from Kenney.nl:
www.kenney.nl
'''
import os
from random import sample


ASSETS_LOC = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'assets', 'cards')
CARD_DIMENSIONS = (140, 190)
CARD_VALS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
CARD_MATCHES = {0: 'A', 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10}
CARD_SUITS = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
CARD_BACK_COLORS = ['red', 'blue', 'green']
WILD_CARDS = ['J']
DEAD_CARDS = ['Q', 'K']


def get_table():
    return os.path.join(ASSETS_LOC, 'table.png')


def get_card_front(val, suit):
    return os.path.join(ASSETS_LOC, f'card{suit}{val}.png')


def get_card_back(color, version=5):
    return os.path.join(ASSETS_LOC, f'cardBack_{color}{version}.png')


def build_decks(num_decks=2):
    decks = []

    for dummy in range(num_decks):
        deck = []

        for suit in CARD_SUITS:
            for val in CARD_VALS:
                deck.append((val, suit))

        decks += deck

    return sample(decks, len(decks))

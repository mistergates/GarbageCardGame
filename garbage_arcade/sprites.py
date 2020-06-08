
import arcade

from . import cards
from .enums import ImageAssets


class GenericImage(arcade.Sprite):
    """Most images will be loaded from here"""
    def __init__(self, image, scale=1):
        # Image to use for the sprite when face up
        self.image_scale = scale
        self.image_file_name = image

        # Call the parent
        super().__init__(self.image_file_name, scale, calculate_hit_box=False)

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
        # if color == 'Red':
        #     self.image_file_name = ImageAssets.card_back_black.value

        # Call the parent
        super().__init__(self.image_file_name, scale, calculate_hit_box=False)

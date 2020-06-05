
import os
import arcade

ASSETS_LOC = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'assets', 'images')

class Title(arcade.Sprite):
    """ Title screen image sprite """

    def __init__(self, scale=1):
        # Image to use for the sprite when face up
        self.image_file_name = os.path.join(ASSETS_LOC, 'title.png')

        # Call the parent
        super().__init__(self.image_file_name, scale, calculate_hit_box=False)

class TitleScreenButton(arcade.Sprite):
    """ Title screen play button """

    def __init__(self, image, default_state=None, hover_state=None, scale=1):
        # Image to use for the sprite when face up
        self.image_scale = scale
        self.default_state = default_state
        self.hover_state = hover_state
        self.image_file_name = os.path.join(ASSETS_LOC, image)

        self.hover = False

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

        # Call the parent
        super().__init__(self.image_file_name, scale, calculate_hit_box=False)

import arcade

from . import sprites
from .enums import Views, ImageAssets

class RulesView(arcade.View):

    def __init__(self):
        super().__init__()
        self.view_name = Views.rules
        self.rules_text = None

    def on_show(self):
        self.rules_text = sprites.GenericImage(ImageAssets.rules_text.value)

    def on_draw(self):
        arcade.start_render()
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)
        self.rules_text.position = (
            self.window.screen_width / 2,
            self.window.screen_height / 2
        )
        self.rules_text.draw()

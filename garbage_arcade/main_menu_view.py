import arcade
import sys

from . import sprites
from .enums import Views, ImageAssets, Sounds

class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.view_name = Views.main_menu

        # Sounds
        self.menu_select = arcade.Sound(Sounds.menu_select.value)

        # Main title
        self.title_list = arcade.SpriteList()

        # Buttons
        self.buttons_list = arcade.SpriteList()
        self.buttons_hover_list = arcade.SpriteList()

    def on_show(self):
        """Runs on first render"""
        self.create_sprites()

    def on_mouse_motion(self, x, y, dx, dy):
        self.create_sprites()
        for button in arcade.get_sprites_at_point((x, y), self.buttons_list):
            button.kill()

    def on_draw(self):
        """Render the screen"""
        arcade.start_render()
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)

        # Draw title screen sprites
        self.title_list.draw()
        self.buttons_hover_list.draw()
        self.buttons_list.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Check for sprite collisions"""
        for button in arcade.get_sprites_at_point((x, y), self.buttons_hover_list):
            if button.image_file_name == ImageAssets.play_btn_hover.value:
                self.menu_select.play(volume=self.window.volume)
                self.window.show_view(self.window.game_view)
                if not self.window.game_view.game_started:
                    self.window.game_view.setup(new_game=True)
            if button.image_file_name == ImageAssets.quit_btn_hover.value:
                self.menu_select.play(volume=self.window.volume)
                sys.exit()
            if button.image_file_name == ImageAssets.rules_btn_hover.value:
                self.menu_select.play(volume=self.window.volume)
                self.window.show_view(self.window.rules_view)
            if button.image_file_name == ImageAssets.restart_btn_hover.value:
                self.window.game_view.setup(new_game=True)
                self.window.show_view(self.window.game_view)

    def get_sprite_pos(self, fn):
        """Get desired sprite positions based on screen size"""
        if fn == ImageAssets.title.value:
            return self.window.screen_width / 2, self.window.screen_height / 2
        if fn == ImageAssets.play_btn.value:
            return self.window.screen_width / 2, self.window.screen_height / 2 - 200
        if fn == ImageAssets.rules_btn.value:
            return self.window.screen_width / 2, self.window.screen_height / 2 - 275
        if fn == ImageAssets.restart_btn.value:
            return self.window.screen_width / 2, self.window.screen_height / 2 - 350
        if fn == ImageAssets.quit_btn.value:
            return self.window.screen_width / 2, self.window.screen_height / 2 - 425

    def create_sprites(self):
        """Create sprites dispalyed on title screen"""
        self.title_list = arcade.SpriteList()
        self.buttons_list = arcade.SpriteList()
        self.buttons_hover_list = arcade.SpriteList()

        # Title screen
        title = sprites.GenericImage(ImageAssets.title.value)
        title.position = self.get_sprite_pos(ImageAssets.title.value)
        self.title_list.append(title)

        # Play Buttons
        play_btn_pos = self.get_sprite_pos(ImageAssets.play_btn.value)
        play_btn = sprites.GenericImage(ImageAssets.play_btn.value)
        play_btn.position = play_btn_pos
        self.buttons_list.append(play_btn)
        play_btn_hover = sprites.GenericImage(ImageAssets.play_btn_hover.value)
        play_btn_hover.position = play_btn_pos
        self.buttons_hover_list.append(play_btn_hover)

        # Rules button
        rules_btn_pos = self.get_sprite_pos(ImageAssets.rules_btn.value)
        rules_btn = sprites.GenericImage(ImageAssets.rules_btn.value)
        rules_btn.position = rules_btn_pos
        self.buttons_list.append(rules_btn)
        rules_btn_hover = sprites.GenericImage(ImageAssets.rules_btn_hover.value)
        rules_btn_hover.position = rules_btn_pos
        self.buttons_hover_list.append(rules_btn_hover)

        # Restart button
        restart_bn_pos = self.get_sprite_pos(ImageAssets.restart_btn.value)
        restart_btn = sprites.GenericImage(ImageAssets.restart_btn.value)
        restart_btn.position = restart_bn_pos
        self.buttons_list.append(restart_btn)
        restart_btn_hover = sprites.GenericImage(ImageAssets.restart_btn_hover.value)
        restart_btn_hover.position = restart_bn_pos
        self.buttons_hover_list.append(restart_btn_hover)

        # Quit button
        quit_btn_pos = self.get_sprite_pos(ImageAssets.quit_btn.value)
        quit_btn = sprites.GenericImage(ImageAssets.quit_btn.value)
        quit_btn.position = quit_btn_pos
        self.buttons_list.append(quit_btn)
        quit_btn_hover = sprites.GenericImage(ImageAssets.quit_btn_hover.value)
        quit_btn_hover.position = quit_btn_pos
        self.buttons_hover_list.append(quit_btn_hover)

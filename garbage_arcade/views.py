
import json
import arcade
import os

from arcade.gui import *

from . import cards, sprites
from .enums import Views, TitleScreenButtons
from .computer_ai import ComputerAi

NUMBER_OF_DECKS = 1

class MainMenu(arcade.View):
    def __init__(self):
        super().__init__()
        self.view_name = Views.main_menu

        # Window height/width
        self.screen_width = self.window.screen_width
        self.screen_height = self.window.screen_height

        # Main title
        self.title_list = arcade.SpriteList()

        # Buttons
        self.buttons_list = arcade.SpriteList()


    def on_show(self):
        """Runs on first render"""
        self.create_sprites()

    def on_update(self, delta_time):
        """Check for menu item selections"""
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        buttons_list = self.buttons_list
        self.buttons_list = arcade.SpriteList()

        for button in buttons_list:
            if button.hover:
                new_button = sprites.TitleScreenButton(
                    button.hover_state,
                    default_state=button.default_state,
                    hover_state=button.hover_state
                )
                new_button.hover = True
            else:
                new_button = sprites.TitleScreenButton(
                    button.default_state,
                    default_state=button.default_state,
                    hover_state=button.hover_state
                )
                new_button.hover = False
            new_button.position = button.position
            self.buttons_list.append(new_button)

        # Reset all buttons back to no hover
        for button in self.buttons_list:
            button.hover = False

        # Set the button being hovered to true
        for button in arcade.get_sprites_at_point((x, y), self.buttons_list):
            button.hover = True

    def on_draw(self):
        """Render the screen"""
        # This command has to happen before we start drawing
        arcade.start_render()

        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)

        # Draw title screen sprites
        self.title_list.draw()
        self.buttons_list.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """Check for sprite collisions"""
        for button in arcade.get_sprites_at_point((x, y), self.buttons_list):
            if button.default_state == TitleScreenButtons.play.value:
                self.window.show_view(self.window.game_view)
                if not self.window.game_view.game_started:
                    self.window.game_view.setup()
                self.window.game_view.game_paused = False
            if button.default_state == TitleScreenButtons.quit.value:
                exit()
            if button.default_state == TitleScreenButtons.rules.value:
                self.window.show_view(self.window.rules_view)

    def get_sprite_pos(self, title=False, play=False, rules=False, quit=False):
        """Get desired sprite positions based on screen size"""
        if title:
            return self.screen_width / 2, self.screen_height / 2
        if play:
            return self.screen_width / 2, self.screen_height / 2 - 200
        if rules:
            return self.screen_width / 2, self.screen_height / 2 - 275
        if quit:
            return self.screen_width / 2, self.screen_height / 2 - 350

    def create_sprites(self):
        """Create sprites dispalyed on title screen"""
        self.title_list = arcade.SpriteList()
        self.buttons_list = arcade.SpriteList()

        # Title screen
        title = sprites.Title()
        title.position = self.get_sprite_pos(title=True)
        self.title_list.append(title)

        # Play Button
        play_button = sprites.TitleScreenButton(
            TitleScreenButtons.play.value,
            default_state=TitleScreenButtons.play.value,
            hover_state=TitleScreenButtons.play_hover.value)
        play_button.position = self.get_sprite_pos(play=True)
        self.buttons_list.append(play_button)

        # Rules button
        rules_button = sprites.TitleScreenButton(
            TitleScreenButtons.rules.value,
            default_state=TitleScreenButtons.rules.value,
            hover_state=TitleScreenButtons.rules_hover.value)
        rules_button.position = self.get_sprite_pos(rules=True)
        self.buttons_list.append(rules_button)

        # Quit button
        quit_button = sprites.TitleScreenButton(
            TitleScreenButtons.quit.value,
            default_state=TitleScreenButtons.quit.value,
            hover_state=TitleScreenButtons.quit_hover.value)
        quit_button.position = self.get_sprite_pos(quit=True)
        self.buttons_list.append(quit_button)

    
class Garbage(arcade.View):
    """Main Garbage card game class"""

    def __init__(self):
        super().__init__()
        self.view_name = Views.garbage

        # Window height/width
        self.screen_width = self.window.screen_width
        self.screen_height = self.window.screen_height

        # Card lists (cards on playing board)
        self.player_card_list = None
        self.computer_card_list = None
        self.draw_pile_list = None
        self.discard_pile_list = None
        self.card_in_hand_list = None

        # Game State
        self.game_started = False
        self.paused = False
        self.player_cards_remain = 10
        self.computer_cards_remain = 10
        self.current_round = 0
        self.player_turn = True
        self.computer_turn = False
        self.card_in_hand = None

        # Computer AI
        self.computer_ai = ComputerAi(self)
        self.computer_ai_wait = False
        self.target_table_card = None
        self.card_move_speed = 7

    def on_update(self, delta_time):
        # Check to see if we have a winner
        self.check_for_winner()

        if self.computer_ai_wait and self.target_table_card:
            self.move_computer_card()

        if self.computer_turn:
            self.computer_ai.play_turn(self.card_in_hand)

    def on_mouse_press(self, x, y, button, key_modifiers):
        """Called when the user presses a mouse button"""
        # Do nothing if not player's turn
        if not self.player_turn:
            return

        # Discard on right-click
        if button == arcade.MOUSE_BUTTON_RIGHT and self.card_in_hand:
            self.discard_card_in_hand()

        # Check draw pile
        if arcade.get_sprites_at_point((x, y), self.draw_pile_list) and not self.card_in_hand:
            self.get_card_from_draw_pile(x, y)

        # Check discard pile
        if arcade.get_sprites_at_point((x, y), self.discard_pile_list) and not self.card_in_hand:
            self.get_card_from_discard_pile(x, y)

        # Check collision with player's cards
        player_table_card = arcade.get_sprites_at_point((x, y), self.player_card_list)
        if player_table_card and self.card_in_hand:
            card = player_table_card[0]

            # Check to see if card is playable
            if self.is_card_playable(card):
                self.play_card_in_hand(card, x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        """Mouse Movement"""
        # If we are holding cards, move them with the mouse
        if self.card_in_hand_list and self.player_turn:
            self.card_in_hand_list[0].center_x += dx
            self.card_in_hand_list[0].center_y += dy

    def on_draw(self):
        """Render the screen"""
        # This command has to happen before we start drawing
        arcade.start_render()

        arcade.set_background_color(arcade.color.AMAZON)

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

    def play_card_in_hand(self, card, x, y):
        card_from_table = sprites.CardFront(card.suit, card.value, scale=cards.CARD_SCALE)
        card_from_table.position = x, y

        # Place card in hand on table
        if self.player_turn:
            self.player_card_list[card.index] = self.card_in_hand
            self.player_card_list[card.index].position = card.position
            self.player_card_list[card.index].index = card.index
        elif self.computer_turn:
            self.computer_card_list[card.index] = self.card_in_hand
            self.computer_card_list[card.index].position = card.position
            self.computer_card_list[card.index].index = card.index

        # Kill current card in hand
        self.card_in_hand.kill()

        self.card_in_hand = card_from_table
        self.card_in_hand_list.append(card_from_table)

        card.kill()

    def discard_card_in_hand(self):
        card = sprites.CardFront(self.card_in_hand.suit, self.card_in_hand.value, cards.CARD_SCALE)
        card.position = self.calc_card_pos(discard=True)
        self.discard_pile_list.append(card)
        self.card_in_hand.kill()
        self.card_in_hand = None

        self.player_turn = True if not self.player_turn else False
        self.computer_turn = True if not self.computer_turn else False

    def get_card_from_draw_pile(self, x, y):
        # Grab the top card from the deck
        card = self.draw_pile_list[-1]
        card_front = sprites.CardFront(card.suit, card.value, scale=cards.CARD_SCALE)
        card_front.position = x, y
        card_front.display = True
        # Assign the card drawn to hand
        self.card_in_hand = card_front
        self.card_in_hand_list.append(card_front)
        # Kill the card in the draw pile
        card.kill()

    def get_card_from_discard_pile(self, x, y):
        # Grab the top card from the deck
        card = self.discard_pile_list[-1]
        card_front = sprites.CardFront(card.suit, card.value, scale=cards.CARD_SCALE)
        card_front.position = x, y
        card_front.display = True
        # Assign the card drawn to hand
        self.card_in_hand = card_front
        self.card_in_hand_list.append(card_front)
        # Kill the card in the draw pile
        card.kill()

    def is_card_playable(self, card):
        """Checks to see if card in hand is playable on card"""
        if card.display is True and card.value not in cards.WILD_CARDS:
            return False

        if self.card_in_hand.value in cards.WILD_CARDS:
            if card.value in cards.WILD_CARDS and card.display is True:
                return False
            return True

        return cards.CARD_MATCHES[card.index] == self.card_in_hand.value

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

    def update_card_positions(self):
        """Updates the position of the cards based on screen size"""
        # Create local copies of card sprite groups and re-create sprite groups
        player_card_list = self.player_card_list
        computer_card_list = self.computer_card_list
        draw_pile_list = self.draw_pile_list
        discard_pile_list = self.discard_pile_list
        self.player_card_list = arcade.SpriteList()
        self.computer_card_list = arcade.SpriteList()
        self.draw_pile_list = arcade.SpriteList()
        self.discard_pile_list = arcade.SpriteList()

        # Position Player Cards
        x, y = self.calc_card_pos(player=True)
        x_orig = x
        for i, card in enumerate(player_card_list):
            if i == 5:
                # Maximum of 5 cards per row, restart at orig x for next row
                y -= cards.CARD_HEIGHT + cards.CARD_BUFFER_Y
                x = x_orig

            card.position = x, y
            self.player_card_list.append(card)
            x += cards.CARD_WIDTH + cards.CARD_BUFFER_X

        # Position Computer cards
        x, y = self.calc_card_pos(computer=True)
        x_orig = x
        for i, card in enumerate(computer_card_list):
            if i == 5:
                # Maximum of 5 cards per row, restart at orig x for next row
                y += cards.CARD_HEIGHT + cards.CARD_BUFFER_Y
                x = x_orig

            card.position = x, y
            self.computer_card_list.append(card)
            x -= cards.CARD_WIDTH + cards.CARD_BUFFER_X

        # Position draw pile cards
        x, y = self.calc_card_pos(draw=True)
        for card in draw_pile_list:
            card.position = x, y
            self.draw_pile_list.append(card)

        # Position the discard pile cards
        x, y = self.calc_card_pos(discard=True)
        for card in discard_pile_list:
            card.position = x, y
            self.discard_pile_list.append(card)

    def move_computer_card(self):
        if self.card_in_hand.center_x != self.target_table_card.center_x:
            if self.card_in_hand.center_x > self.target_table_card.center_x:
                diff = self.card_in_hand.center_x - self.target_table_card.center_x
                self.card_in_hand.center_x -= self.card_move_speed if self.card_move_speed < diff else diff
            else:
                diff = self.target_table_card.center_x - self.card_in_hand.center_x
                self.card_in_hand.center_x += self.card_move_speed if self.card_move_speed < diff else diff
            print('diff x', diff)

        if self.card_in_hand.center_y != self.target_table_card.center_y:
            if self.card_in_hand.center_y > self.target_table_card.center_y:
                diff = self.card_in_hand.center_y - self.target_table_card.center_y
                self.card_in_hand.center_y -= self.card_move_speed if self.card_move_speed < diff else diff
                print('here')
            else:
                diff = self.target_table_card.center_y - self.card_in_hand.center_y
                self.card_in_hand.center_y += self.card_move_speed if self.card_move_speed < diff else diff
            print('diff y', diff)

    def check_for_winner(self):
        num_cards_displayed = 0
        for card in self.player_card_list:
            num_cards_displayed += 1 if card.display else 0

        if num_cards_displayed == self.player_cards_remain:
            self.player_cards_remain -= 1
            self.setup()

        num_cards_displayed = 0
        for card in self.computer_card_list:
            num_cards_displayed += 1 if card.display else 0

        if num_cards_displayed == self.computer_cards_remain:
            self.computer_cards_remain -= 1
            self.setup()

    def setup(self):
        """Sets up the game. This should be called each time a round starts"""
        # Reset game states
        self.player_card_list = arcade.SpriteList()
        self.computer_card_list = arcade.SpriteList()
        self.draw_pile_list = arcade.SpriteList()
        self.discard_pile_list = arcade.SpriteList()
        self.card_in_hand_list = arcade.SpriteList()
        self.game_started = True
        self.card_in_hand = None
        self.current_round += 1

        # Build a deck
        starting_deck = cards.build_decks(NUMBER_OF_DECKS)

        # Create player cards
        for i in range(self.player_cards_remain):
            card = sprites.CardBack(
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
            card = sprites.CardBack(
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
            card = sprites.CardBack(
                cards.DRAW_PILE_COLOR,
                version=cards.CARD_BACK_VERSION,
                scale=cards.CARD_SCALE
            )
            card.value, card.suit = x
            card.display = False
            self.draw_pile_list.append(card)

        # Update the window's card positions
        self.update_card_positions()

class Rules(arcade.View):
    def __init__(self):
        super().__init__()
        self.view_name = Views.rules
        self.rules = self.load_rules()

        # Window height/width
        self.screen_width = self.window.screen_width
        self.screen_height = self.window.screen_height

        self.render_menu_text()

    def on_draw(self):
        arcade.start_render()
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)
        self.render_menu_text()

    def render_menu_text(self):
        x = 10
        y = self.window.screen_height - 20
        for _set in self.rules:
            for header, lines in _set.items():
                # Draw header
                arcade.draw_text(
                    header,
                    x,
                    y,
                    arcade.color.WHITE,
                    16,
                    font_name="GARA",
                    align="left"
                )
                y -= 30

            for line in lines:
                arcade.draw_text(
                    line,
                    x,
                    y,
                    arcade.color.WHITE,
                    14,
                    font_name="GARA",
                    align="left"
                )
                y -= 20

            y -= 30

    def load_rules(self):
        fn = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'rules.json')
        with open(fn, 'r') as f:
            return json.load(f)

import arcade

from . import cards, sprites
from .enums import Views, Sounds, ImageAssets, Player
from .computer_ai import ComputerAi

NUMBER_OF_DECKS = 1

class GameView(arcade.View):
    """Main Garbage card game class"""

    def __init__(self):
        super().__init__()
        self.view_name = Views.garbage
        self.font = 'GARA'

        # Sounds
        self.draw_card_sound = arcade.Sound(Sounds.draw_card.value)
        self.play_card_sound = arcade.Sound(Sounds.play_card.value)
        self.shuffle_sound = arcade.Sound(Sounds.shuffle.value)
        self.error_sound = arcade.Sound(Sounds.error.value)
        self.round_over = arcade.Sound(Sounds.round_over.value)

        # Card lists (cards on playing board)
        self.player_card_list = None
        self.computer_card_list = None
        self.draw_pile_list = None
        self.discard_pile_list = None

        # Game State
        self.game_started = False
        self.paused = False
        self.player_cards_remain = 10
        self.computer_cards_remain = 10
        self.current_round = 0
        self.player_turn = True
        self.computer_turn = False
        self.card_in_hand = None
        self.move_card_wait = False
        self.previous_discard_card = None
        self.round_winner = None
        self.game_winner = None

        # Computer AI
        self.computer_ai_hand = sprites.GenericImage(ImageAssets.computer_hand.value)
        self.computer_ai = ComputerAi(self)
        self.target_table_card = None
        self.card_move_speed = 2

    def on_update(self, delta_time):
        # Check to see if we have a winner
        if self.round_winner:
            self.round_over.play(self.window.volume)
            arcade.pause(5)
            self.setup()
        if self.game_winner:
            # TODO - draw game over view
            pass

        if self.check_for_winner():
            return

        if self.move_card_wait and self.target_table_card:
            self.move_card()
            self.computer_ai_hand.position = self.card_in_hand.position if self.card_in_hand else [0, 0]

        if self.computer_turn:
            self.computer_ai.play_turn()
            self.computer_ai_hand.position = self.card_in_hand.position if self.card_in_hand else [0, 0]

    def on_mouse_press(self, x, y, button, modifiers):
        """Called when the user presses a mouse button"""
        # Do nothing if not player's turn
        if not self.player_turn:
            self.error_sound.play(self.window.volume)
            return

        # Discard on right-click
        if button == arcade.MOUSE_BUTTON_RIGHT and self.card_in_hand:
            self.discard_card_in_hand()
            return

        # Check draw pile
        if arcade.get_sprites_at_point((x, y), self.draw_pile_list) and not self.card_in_hand:
            self.get_card_from_draw_pile(x, y)

        # Check discard pile
        if arcade.get_sprites_at_point((x, y), self.discard_pile_list):
            if self.card_in_hand:
                self.discard_card_in_hand()
                return
            else:
                self.get_card_from_discard_pile(x, y)

        # Check collision with player's cards
        player_table_card = arcade.get_sprites_at_point((x, y), self.player_card_list)
        if player_table_card and self.card_in_hand:
            card = player_table_card[0]

            # Check to see if card is playable
            if self.is_card_playable(card):
                self.play_card_in_hand(card, x, y)
            else:
                self.error_sound.play(self.window.volume)

    def on_mouse_motion(self, x, y, dx, dy):
        """Mouse Movement"""
        # If we are holding cards, move them with the mouse
        if self.computer_turn:
            return
        # print('!!!MOVING MOUSE!!!!')

        if self.card_in_hand:
            self.card_in_hand.center_x += dx
            self.card_in_hand.center_y += dy

    def on_draw(self):
        """Render the screen"""
        # This command has to happen before we start drawing
        arcade.start_render()

        arcade.set_background_color(arcade.color.AMAZON)

        # Draw a grid to show absolute center
        # arcade.draw_line(
        #     start_x=0,
        #     start_y=self.window.screen_height / 2,
        #     end_x=self.window.screen_width,
        #     end_y=self.window.screen_height / 2,
        #     color=arcade.color.BLACK,
        #     line_width=2
        # )
        # arcade.draw_line(
        #     start_x=self.window.screen_width / 2,
        #     start_y=0,
        #     end_x=self.window.screen_width / 2,
        #     end_y=self.window.screen_height,
        #     color=arcade.color.BLACK,
        #     line_width=2
        # )

        # Display center text
        if self.round_winner:
            text = f'{self.round_winner.value} wins the round!'
            size = 36
            color = arcade.color.WHITE
        else:
            text = "Player's Turn" if self.player_turn else "Computer's Turn"
            size = 36
            color = arcade.color.WHITE
        self.update_center_text(text, size, color)

        # Draw the cards
        self.player_card_list.draw()
        self.computer_card_list.draw()
        self.draw_pile_list.draw()
        self.discard_pile_list.draw()
        if self.card_in_hand:
            self.card_in_hand.draw()

        if self.computer_turn:
            self.computer_ai_hand.draw()

    def update_center_text(self, text, size, color):
        arcade.draw_text(
            text,
            self.window.screen_width / 2,
            self.window.screen_height / 2,
            color,
            size,
            font_name=self.font,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

    def play_card_in_hand(self, card, x, y):
        # Play sound
        self.play_card_sound.play(volume=self.window.volume)

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

        card.kill()

    def discard_card_in_hand(self):
        # Play sound
        self.play_card_sound.play(volume=self.window.volume)
        card = sprites.CardFront(self.card_in_hand.suit, self.card_in_hand.value, cards.CARD_SCALE)
        card.position = self.calc_card_pos(discard=True)
        self.discard_pile_list.append(card)
        self.card_in_hand.kill()
        self.card_in_hand = None

        # Don't change turn if we are discarding a card we took from discard pile
        if (self.previous_discard_card
            and card.value == self.previous_discard_card.value
            and card.suit == self.previous_discard_card.suit):
            return

        self.change_turn()

    def get_card_from_draw_pile(self, x, y):
        # Play sound
        self.draw_card_sound.play(volume=self.window.volume)
        # Grab the top card from the deck
        card = self.draw_pile_list[-1]
        card_front = sprites.CardFront(card.suit, card.value, scale=cards.CARD_SCALE)
        card_front.position = x, y
        card_front.display = True
        # Assign the card drawn to hand
        self.card_in_hand = card_front
        # Kill the card in the draw pile
        card.kill()

    def get_card_from_discard_pile(self, x, y):
        # Play sound
        self.draw_card_sound.play(volume=self.window.volume)
        # Grab the top card from the deck
        card = self.discard_pile_list[-1]
        card_front = sprites.CardFront(card.suit, card.value, scale=cards.CARD_SCALE)
        card_front.position = x, y
        card_front.display = True
        # Assign the card drawn to hand
        self.card_in_hand = card_front
        self.previous_discard_card = card
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
        coords = []
        if player:
            x = (self.window.screen_width / 2) - (cards.CARD_WIDTH * 2) - (cards.CARD_BUFFER_X * 2)
            y = cards.CARD_HEIGHT * 1.75
        if computer:
            x = (self.window.screen_width / 2)  + (cards.CARD_WIDTH * 2) + (cards.CARD_BUFFER_X * 2)
            y = self.window.screen_height - (cards.CARD_HEIGHT * 1.75)
        if draw:
            x = self.calc_card_pos(player=True)[0] - cards.CARD_WIDTH * 1.5
            y = self.window.screen_height / 2
        if discard:
            x = self.calc_card_pos(computer=True)[0] + cards.CARD_WIDTH * 1.5
            y = self.window.screen_height / 2

        coords.append(x)
        coords.append(y)

        return coords

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

    def move_card(self):
        speed = self.card_move_speed
        if list(self.target_table_card.position) == list(self.calc_card_pos(discard=True)):
            speed *= 2

        if list(self.card_in_hand.position) == list(self.target_table_card.position):
            self.move_card_wait = False
            return

        x_diff = self.card_in_hand.position[0] != self.target_table_card.position[0]
        y_diff = self.card_in_hand.position[1] != self.target_table_card.position[1]

        print(f'Speed: {speed}')
        print(f'Starting pos: {self.card_in_hand.position}')
        print(f'Target pos: {list(self.target_table_card.position)}')
        print(self.card_in_hand.position == list(self.target_table_card.position))
  
        if x_diff:
            if self.card_in_hand.position[0] > self.target_table_card.position[0]:
                diff = self.card_in_hand.position[0] - self.target_table_card.position[0]
                self.card_in_hand.change_x = -speed if speed < diff else -diff
                # self.card_in_hand.update()
            else:
                diff = self.target_table_card.position[0] - self.card_in_hand.position[0]
                self.card_in_hand.change_x = speed if speed < diff else diff
                # self.card_in_hand.update()
            print(f'x diff: {diff}')

        if y_diff:
            if self.card_in_hand.position[1] > self.target_table_card.position[1]:
                diff = self.card_in_hand.position[1] - self.target_table_card.position[1]
                self.card_in_hand.change_y = -speed if speed < diff else -diff
                # self.card_in_hand.update()
            else:
                diff = self.target_table_card.position[1] - self.card_in_hand.position[1]
                self.card_in_hand.change_y = speed if speed < diff else diff
                # self.card_in_hand.update()
            print(f'y diff: {diff}')

        self.card_in_hand.update()
        print(f'Ending pos: {self.card_in_hand.position}')
        # arcade.pause(.5)

    def change_turn(self):
        self.player_turn = True if not self.player_turn else False
        self.computer_turn = True if not self.computer_turn else False

    def check_for_winner(self):
        num_cards_displayed = 0
        for card in self.player_card_list:
            num_cards_displayed += 1 if card.display else 0

        if num_cards_displayed == self.player_cards_remain:
            self.player_cards_remain -= 1
            if self.player_cards_remain == 0:
                self.game_winner = Player.player
            else:
                self.round_winner = Player.player

        num_cards_displayed = 0
        for card in self.computer_card_list:
            num_cards_displayed += 1 if card.display else 0

        if num_cards_displayed == self.computer_cards_remain:
            self.computer_cards_remain -= 1
            if self.computer_cards_remain == 0:
                self.game_winner = Player.computer
            else:
                self.round_winner = Player.computer

        if self.game_winner or self.round_winner:
            self.card_in_hand.kill()
            return True

    def setup(self):
        """Sets up the game. This should be called each time a round starts"""
        # Play shound
        arcade.pause(.5)
        self.shuffle_sound.play(self.window.volume)

        # Reset game states
        self.player_card_list = arcade.SpriteList()
        self.computer_card_list = arcade.SpriteList()
        self.draw_pile_list = arcade.SpriteList()
        self.discard_pile_list = arcade.SpriteList()
        self.game_started = True
        self.card_in_hand = None
        self.round_winner = None
        self.game_winner = None

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

        # Add discard placeholder:
        self.discard_pile_list.append(
            sprites.GenericImage(ImageAssets.discard_placeholder.value)
        )

        # Update the window's card positions
        self.update_card_positions()

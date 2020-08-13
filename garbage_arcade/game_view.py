import arcade
import time

from . import cards, sprites
from .enums import Views, Sounds, ImageAssets, Player
from .computer_ai import ComputerAi

NUMBER_OF_DECKS = 1

class GameView(arcade.View):
    """Main Garbage card game class"""

    def __init__(self):
        super().__init__()
        self.view_name = Views.garbage

        # Sounds
        self.draw_card_sound = arcade.Sound(Sounds.draw_card.value)
        self.play_card_sound = arcade.Sound(Sounds.play_card.value)
        self.shuffle_sound = arcade.Sound(Sounds.shuffle.value)
        self.error_sound = arcade.Sound(Sounds.error.value)
        self.round_over = arcade.Sound(Sounds.round_over.value)

        # Game Controls
        self.audio_control_list = None

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
        self.play_number = 0
        self.player_turn = True
        self.computer_turn = False
        self.card_in_hand = None
        self.move_card_wait = False
        self.previous_discard_card = None
        self.round_winner = None
        self.game_winner = None

        # Time Trackers
        self.last_setup_time = None
        self.last_discard_time = None
        self.round_winner_time = None

        # Computer AI
        self.computer_ai_hand = None
        self.computer_ai = None
        self.target_table_card = None
        self.card_move_speed = 4

    def on_update(self, delta_time):
        '''Update which runs every tick - main logic flow here'''
        # Restart background music if the stream ends
        if self.window.background_music.get_stream_position() == 0.0:
            self.window.background_music.stop()
            self.window.background_music.play(volume=self.window.music_volume)

        # Return if game hasn't started
        if not self.game_started:
            return

        # End round/game if there is a winner
        if self.round_winner:
            if time.time() - self.round_winner_time < 5:
                return
            self.round_over.play(self.window.volume)
            self.setup()
        if self.game_winner:
            self.window.show_view(self.window.game_over_view)

        # check for round/game winner
        if self.check_for_winner():
            return

        # Continue to move computer's card
        if self.move_card_wait and self.target_table_card:
            try:
                self.move_card()
            except AttributeError:
                # Caught if we try to move the card after restarting game
                return
            self.computer_ai_hand.position = self.card_in_hand.position if self.card_in_hand else self.calc_card_pos(draw=True)
            return

        # Play computer AI turn
        if self.computer_turn:
            if self.play_number == 0 and time.time() - self.last_setup_time < 3:
                # Give 3 seconds before ai plays a turn if ai is starting the round
                return
            self.computer_ai.play_turn()
            if self.card_in_hand:
                self.computer_ai_hand.position = self.card_in_hand.position
            else:
                if self.computer_ai.card_is_playable(self.draw_pile_list[-1]):
                    self.computer_ai_hand.position = self.calc_card_pos(discard=True)
                else:
                    self.computer_ai_hand.position = self.calc_card_pos(draw=True)

    def on_mouse_press(self, x, y, button, modifiers):
        """Called when the user presses a mouse button"""
        # Do nothing if not player's turn
        # if not self.player_turn:
        #     self.error_sound.play(self.window.volume)
        #     return

        # Discard on right-click
        # if button == arcade.MOUSE_BUTTON_RIGHT and self.card_in_hand:
        #     self.discard_card_in_hand()
        #     return

        # Check draw pile
        if self.player_turn and arcade.get_sprites_at_point((x, y), self.draw_pile_list) and not self.card_in_hand:
            self.get_card_from_draw_pile(x, y)

        # Check discard pile
        if self.player_turn and arcade.get_sprites_at_point((x, y), self.discard_pile_list):
            if self.card_in_hand:
                self.discard_card_in_hand()
                return
            else:
                if len(self.discard_pile_list) > 1:
                    self.get_card_from_discard_pile(x, y)

        # Check collision with player's cards
        if self.player_turn:
            player_table_card = arcade.get_sprites_at_point((x, y), self.player_card_list)
            if player_table_card and self.card_in_hand:
                card = player_table_card[0]

                # Check to see if card is playable
                if self.is_card_playable(card):
                    self.play_card_in_hand(card, x, y)
                else:
                    self.error_sound.play(self.window.volume)

        # Check Audio Controls
        audio_control = arcade.get_sprites_at_point((x, y), self.audio_control_list)
        for sprite in audio_control:
            # Audio Down
            if sprite.image_file_name not in (ImageAssets.audio_down.value, ImageAssets.audio_up.value):
                print('hehehe')
                continue
            if sprite.image_file_name == ImageAssets.audio_down.value:
                self.window.volume -= .1 if self.window.volume >= .1 else 0
                self.window.music_volume -= .03 if self.window.music_volume >= .03 else 0
                if self.audio_control_list[1].image_file_name == ImageAssets.audio_up.value:
                    continue
                current_audio = self.audio_control_list[1].image_file_name
                self.audio_control_list[1].kill()
                if current_audio == ImageAssets.audio_3.value:
                    self.window.volume = .60
                    self.window.music_volume = .03
                    self.window.background_music.set_volume(self.window.music_volume)
                    new_audio = sprites.GenericImage(ImageAssets.audio_2.value)
                elif current_audio == ImageAssets.audio_2.value:
                    self.window.volume = .30
                    self.window.music_volume = .01
                    self.window.background_music.set_volume(self.window.music_volume)
                    new_audio = sprites.GenericImage(ImageAssets.audio_1.value)
                else:
                    self.window.volume = 0
                    self.window.music_volume = 0
                    self.window.background_music.set_volume(self.window.music_volume)
                    continue
            if sprite.image_file_name == ImageAssets.audio_up.value:
                self.window.volume -= .1 if self.window.volume >= .1 else 0
                self.window.music_volume -= .01 if self.window.music_volume >= .01 else 0
                current_audio = self.audio_control_list[1].image_file_name
                if not self.audio_control_list[1].image_file_name == ImageAssets.audio_up.value:
                    self.audio_control_list[1].kill()
                if current_audio == ImageAssets.audio_1.value:
                    self.window.volme = .60
                    self.window.music_volume = .03
                    self.window.background_music.set_volume(self.window.music_volume)
                    new_audio = sprites.GenericImage(ImageAssets.audio_2.value)
                elif current_audio == ImageAssets.audio_2.value:
                    self.window.volume = 1
                    self.window.music_volume = .06
                    self.window.background_music.set_volume(self.window.music_volume)
                    new_audio = sprites.GenericImage(ImageAssets.audio_3.value)
                elif current_audio == ImageAssets.audio_3.value:
                    new_audio = sprites.GenericImage(ImageAssets.audio_3.value)
                else:
                    self.window.volume = .30
                    self.window.music_volume = .01
                    self.window.background_music.set_volume(self.window.music_volume)
                    new_audio = sprites.GenericImage(ImageAssets.audio_1.value)

            new_audio.position = 100, 50
            self.audio_control_list.insert(1, new_audio)

    def on_mouse_motion(self, x, y, dx, dy):
        """Mouse Movement"""
        # If we are holding cards, move them with the mouse
        if self.player_turn and self.card_in_hand:
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
        else:
            text = "Player's Turn" if self.player_turn else "Computer's Turn"
        self.update_center_text(text, 36, arcade.color.WHITE)

        # Draw the card pile text
        self.draw_card_pile_text(28, arcade.color.WHITE_SMOKE)

        # Draw the cards
        self.player_card_list.draw()
        self.computer_card_list.draw()
        self.draw_pile_list.draw()
        self.discard_pile_list.draw()

        # Draw Game Controls
        self.audio_control_list.draw()

        if self.card_in_hand:
            self.card_in_hand.draw()

        # Computer AI if computer's turn
        if self.computer_turn:
            self.computer_ai_hand.draw()


    def draw_card_pile_text(self, size, color):
        '''Draws the text above card piles (Draw/Discard)'''
        # Draw Pile
        x, y = self.calc_card_pos(draw=True)
        arcade.draw_text(
            'Draw',
            x,
            y + (cards.CARD_HEIGHT / 1.5),
            color,
            size,
            font_name=self.window.font,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        # Discard Pile
        x, y = self.calc_card_pos(discard=True)
        arcade.draw_text(
            'Discard',
            x,
            y + (cards.CARD_HEIGHT / 1.5),
            color,
            size,
            font_name=self.window.font,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    def update_center_text(self, text, size, color):
        '''Updates the text in the center of the board'''
        arcade.draw_text(
            text,
            self.window.screen_width / 2,
            self.window.screen_height / 2,
            color,
            size,
            font_name=self.window.font,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )

    def play_card_in_hand(self, card, x, y):
        '''Plays the card currently in hand by left-clicking a x/y coordinate'''
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

        # Kill card
        card.kill()

        # Kill current card in hand
        self.card_in_hand.kill()
        if not self.check_for_winner():
            self.card_in_hand = card_from_table
            self.card_in_hand.update()

    def discard_card_in_hand(self):
        '''Discards the card currently in hand'''
        # Play sound
        self.play_card_sound.play(volume=self.window.volume)
        card = sprites.CardFront(self.card_in_hand.suit, self.card_in_hand.value, cards.CARD_SCALE)
        card.position = self.calc_card_pos(discard=True)
        self.discard_pile_list.append(card)
        self.card_in_hand.kill()
        self.card_in_hand = None

        # Don't change turn if we are discarding a card we took from discard pile
        if self.previous_discard_card and card.value == self.previous_discard_card.value and card.suit == self.previous_discard_card.suit:
            return

        self.discard_pile_list.update()
        self.change_turn()
        self.play_number += 1
        self.previous_discard_card = card

        # Check for discard shuffle
        if len(self.draw_pile_list) == 1:
            if self.computer_turn and not self.computer_ai.card_is_playable(self.discard_pile_list[-1]):
                self.shuffle_discard_for_draw_pile()
            elif self.player_turn and not self.is_card_playable(self.discard_pile_list[-1]):
                self.shuffle_discard_for_draw_pile()

        self.last_discard_time = time.time()

    def get_card_from_draw_pile(self, x, y):
        '''Sets the top card from draw pile to card in hand'''
        if len(self.draw_pile_list) <= 1:
            return
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
        self.card_in_hand.update()

    def get_card_from_discard_pile(self, x, y):
        '''Sets the top card in discard pile to card in hand'''
        # Play sound
        self.draw_card_sound.play(volume=self.window.volume)
        # Grab the top card from the deck
        card = self.discard_pile_list[-1]
        card_front = sprites.CardFront(card.suit, card.value, scale=cards.CARD_SCALE)
        card_front.position = x, y
        card_front.display = True
        # Assign the card drawn to hand
        self.card_in_hand = card_front
        # Kill the card in the draw pile
        card.kill()

    def is_card_playable(self, card):
        """Checks to see if card in hand is playable on card"""
        if not self.card_in_hand:
            return

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

    def move_card(self):
        speed = self.card_move_speed
        if list(self.target_table_card.position) == list(self.calc_card_pos(discard=True)):
            speed *= 2

        # Move the card up
        if self.card_in_hand.center_x < self.target_table_card.center_x:
            diff = (self.target_table_card.center_x - self.card_in_hand.center_x) / 2
            if diff < speed:
                self.card_in_hand.change_x = diff
            else:
                self.card_in_hand.change_x = speed
        # Move the card down
        elif self.card_in_hand.center_x > self.target_table_card.center_x:
            diff = (self.card_in_hand.center_x - self.target_table_card.center_x) / 2
            if diff < speed:
                self.card_in_hand.change_x = -diff
            else:
                self.card_in_hand.change_x = -speed

        # Move the card right
        if self.card_in_hand.center_y < self.target_table_card.center_y:
            diff = (self.target_table_card.center_y - self.card_in_hand.center_y) / 2
            if diff < speed:
                self.card_in_hand.change_y = diff
            else:
                self.card_in_hand.change_y = speed
        # Move the card left
        elif self.target_table_card.center_y < self.card_in_hand.center_y:
            diff = (self.card_in_hand.center_y - self.target_table_card.center_y) / 2
            if diff < speed:
                self.card_in_hand.change_y = -diff
            else:
                self.card_in_hand.change_y = -speed

        self.card_in_hand.update()
        if list(self.card_in_hand.position) == list(self.target_table_card.position):
            self.move_card_wait = False

    def change_turn(self):
        '''Switches turn at end of round (after discard)'''
        self.player_turn = True if not self.player_turn else False
        self.computer_turn = True if not self.computer_turn else False

    def check_for_winner(self):
        '''Checks to see if there is a winner'''
        num_cards_displayed = 0
        for card in self.player_card_list:
            num_cards_displayed += 1 if card.display else 0

        if num_cards_displayed == self.player_cards_remain:
            self.player_cards_remain -= 1
            if self.player_cards_remain == 0:
                self.game_winner = Player.player
                # print(f'{self.game_winner.value} wins!')
            else:
                self.round_winner = Player.player
                self.round_winner_time = time.time()

        num_cards_displayed = 0
        for card in self.computer_card_list:
            num_cards_displayed += 1 if card.display else 0

        if num_cards_displayed == self.computer_cards_remain:
            self.computer_cards_remain -= 1
            if self.computer_cards_remain == 0:
                self.game_winner = Player.computer
                # print(f'{self.game_winner.value} wins!')
            else:
                self.round_winner = Player.computer
                self.round_winner_time = time.time()

        if self.game_winner or self.round_winner:
            self.card_in_hand.kill()
            return True

    def shuffle_discard_for_draw_pile(self):
        '''Shuffle discard pile if we run out of cards in draw pile'''
        deck = cards.build_decks(1, discard=self.discard_pile_list[1:])
        self.draw_pile_list = arcade.SpriteList()
        self.discard_pile_list = arcade.SpriteList()

        # Add card placeholders:
        self.discard_pile_list.insert(
            0,
            sprites.GenericImage(ImageAssets.pile_placeholder.value)
        )
        self.draw_pile_list.insert(
            0,
            sprites.GenericImage(ImageAssets.pile_placeholder.value)
        )

        # Create draw pile
        for x in deck:
            card = sprites.CardBack(
                cards.DRAW_PILE_COLOR,
                version=cards.CARD_BACK_VERSION,
                scale=cards.CARD_SCALE
            )
            card.value, card.suit = x
            card.display = False
            self.draw_pile_list.append(card)

        self.update_card_positions()

        # Play shound
        self.shuffle_sound.play(self.window.volume)
        arcade.pause(.5)

    def setup(self, new_game=False):
        """Sets up the game. This should be called each time a round starts"""
        # Reset these on new game
        if new_game:
            self.game_started = False
            self.paused = False
            self.player_cards_remain = 10
            self.computer_cards_remain = 10
            self.current_round = 0
            self.play_number = 0
            self.player_turn = True
            self.computer_turn = False
            self.card_in_hand = None
            self.move_card_wait = False
            self.previous_discard_card = None
            self.round_winner = None
            self.game_winner = None
            self.computer_ai_hand = sprites.GenericImage(ImageAssets.computer_hand.value)
            self.computer_ai = ComputerAi(self)
            self.target_table_card = None
            self.setup_game_controls()

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
        self.play_number = 0
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

        # Add card placeholders:
        self.discard_pile_list.insert(
            0,
            sprites.GenericImage(ImageAssets.pile_placeholder.value)
        )
        self.draw_pile_list.insert(
            0,
            sprites.GenericImage(ImageAssets.pile_placeholder.value)
        )

        # Update the window's card positions
        self.update_card_positions()

        self.last_setup_time = time.time()

    def setup_game_controls(self):
        # Audio Controls
        x = 50
        y = 50
        if not self.audio_control_list:
            self.audio_control_list = arcade.SpriteList()
            # Audio Down
            audio_down = sprites.GenericImage(ImageAssets.audio_down.value)
            audio_down.position = x, y
            self.audio_control_list.append(audio_down)

            # Audio 3
            audio_3 = sprites.GenericImage(ImageAssets.audio_3.value)
            audio_3.position = x + 50, y
            self.audio_control_list.append(audio_3)

            # Audio up
            audio_up = sprites.GenericImage(ImageAssets.audio_up.value)
            audio_up.position = x + 100, y
            self.audio_control_list.append(audio_up)

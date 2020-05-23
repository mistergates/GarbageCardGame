import pygame
import ctypes

from . import cards, sprites, buttons, fonts, rules
from .menus import Menus
from .ai import OpponentAI

# TODO
# Create a super class that holds all the variables that should reset each setup
#       This can be loaded each setup (sprite groups, cards, etc.)
# If a discard card is selected then discarded again, it should not end turn (let player choose from stock)
# Fix AI bug where J is not being replaced with a new card when placed (causes opponent to auto win)
# Add Escape menu (rather than instant exit)

class Game:

    def __init__(self):
        self.title = 'Garbage'
        self.fps = 90
        self.clock = pygame.time.Clock()
        self.screen_res = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
        self.display = pygame.display.set_mode(self.screen_res, pygame.FULLSCREEN)
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

        # Background
        self.bg_image = pygame.image.load(cards.get_table())
        self.bg = pygame.transform.scale(self.bg_image, self.screen_res)
        self.bg_rect = self.bg.get_rect()

        # Colors
        self.player_color = 'blue'
        self.opponent_color = 'green'
        self.stock_color = 'red'

        # Card Sprites
        self.playing_deck = []
        self.playing_deck_group = pygame.sprite.Group()
        self.opponent_cards = {}
        self.opponent_card_group = pygame.sprite.Group()
        self.player_cards = {}
        self.player_card_group = pygame.sprite.Group()
        self.discard_cards = []
        self.discard_card_group = pygame.sprite.Group()
        self.card_in_hand = None
        self.card_in_hand_group = pygame.sprite.Group()

        # Button Sprites
        self.buttons_map = {}
        self.buttons_group = pygame.sprite.Group()
        self.button_text = []

        # Card Locations
        self.card_x = int((self.screen_res[0] / 2) - ((cards.CARD_DIMENSIONS[0] * 5) * .5)) + 40
        self.card_y = int(self.screen_res[1] / 5) - 20
        self.playing_deck_x = int(cards.CARD_DIMENSIONS[0] / 2) + 50
        self.playing_deck_y = int(self.screen_res[1] / 2)
        self.discard_card_x = self.playing_deck_x + cards.CARD_DIMENSIONS[0] + 10
        self.discard_card_y = int(self.screen_res[1] / 2)

        # Game State
        self.player_cards_remaining = 10
        self.opponent_cards_remaining = 10
        self.setup = True
        self.player_turn = True
        self.opponent_turn = False
        self.card_selected = None
        self.rules_displayed = False

        # Mouse positioning
        self.mouse_x = 0
        self.mouse_y = 0

        # Child Objects
        self.menus = Menus(self)
        self.opponent_ai = OpponentAI(self)


    def play(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        while True:
            self.display.blit(self.bg, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                # Left click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.player_turn:
                    self.mouse_x, self.mouse_y = event.pos

                # Right click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and self.player_turn:
                    if self.card_in_hand and self.card_selected:
                        self._discard_card(self.card_selected)

                if event.type == pygame.MOUSEMOTION:
                    if self.card_in_hand:
                        self.card_in_hand_group.update()
                        self.card_in_hand.reposition_on_mouse()

                if event.type == pygame.KEYDOWN:
                    # If pressed key is ESC quit program
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return

            self._check_for_winner()

            # Setup a new game if needed
            if self.setup: 
                self._setup()
                self.setup = False

            # Check collisions
            self._check_button_collision()
            self._check_card_collision(player=True)
            self._check_card_collision(opponent=True)
            self._check_stock_collision()

            # Draw Sprites
            self._display_turn()
            self._display_cards()
            self._draw_buttons()

            # Check menus
            self.menus.check_menus()

            # Opponent AI
            if self.opponent_turn:
                self.opponent_ai.play_turn()

            # Reset between ticks
            self.mouse_x, self.mouse_y = 0, 0

            pygame.display.update()
            self.clock.tick(self.fps)


    def _check_for_winner(self):
        # Check for round winner
        player_not_revealed = self.player_cards_remaining
        for i in self.player_cards:
            player_not_revealed -= 1 if self.player_cards[i]['Reveal'] else 0

        opponent_not_revealed = self.opponent_cards_remaining
        for i in self.opponent_cards:
            opponent_not_revealed -= 1 if self.opponent_cards[i]['Reveal'] else 0

        if player_not_revealed == 0:
            print('PLAYER WINS ROUND!')
            self.player_cards_remaining -= 1
            self.setup = True
        elif opponent_not_revealed == 0:
            print('OPPONENT WINS ROUND!')
            self.opponent_cards_remaining -= 1
            self.setup = True

        # Check for game winner
        if self.player_cards_remaining == 0:
            print('PLAYER WINS GAME!')
            exit()
        elif self.opponent_cards_remaining == 0:
            print('OPPONENT WINS GAME!')
            exit()


    def _display_cards(self):
        # Draw card groups to screen
        self.opponent_card_group.draw(self.display)
        self.player_card_group.draw(self.display)
        self.playing_deck_group.draw(self.display)
        self.discard_card_group.draw(self.display)
        self.card_in_hand_group.draw(self.display)


    def _change_card_in_hand(self, card):
        if self.card_in_hand:
            # Kill the previous card in hand and add the new one from the table
            self.card_in_hand.kill()
        print(f'Changing card in hand to {card}')
        self.card_selected = card
        self.card_in_hand = sprites.CardFront(self.card_selected, *pygame.mouse.get_pos())
        self.card_in_hand_group.add(self.card_in_hand)


    def _discard_card(self, card):
        print(f'Discarding {card}')
        if self.card_in_hand:
            self.card_in_hand.kill()

        self.discard_cards.append({'Card': card, 'Front': sprites.CardFront(card, self.discard_card_x, self.discard_card_y)})
        self.discard_card_group.add(sprites.CardFront(card, self.discard_card_x, self.discard_card_y))
        self.card_selected = None

        # Change turn after discard
        if self.player_turn:
            self.player_turn = False
            self.opponent_turn = True
        elif self.opponent_turn:
            self.opponent_turn = False
            self.player_turn = True


    def _check_card_collision(self, player=False, opponent=False):
        if player:
            card_group = self.player_card_group
            _cards = self.player_cards
            turn = self.player_turn
        elif opponent:
            card_group = self.opponent_card_group
            _cards = self.opponent_cards
            turn = self.opponent_turn

        # Check to see if card being placed on player's board is valid
        card_group_copy = card_group.copy()
        card_group = pygame.sprite.Group()
        for i, pc in enumerate(card_group_copy):
            if pc.rect.collidepoint(self.mouse_x, self.mouse_y) and self.card_selected and turn:
                if self.card_selected[0] in cards.WILD_CARDS or self.card_selected[0] == cards.CARD_MATCHES[i]:
                    x, y = pc.rect.center
                    prev_card = _cards[i]['Card']
                    _cards[i]['Card'] = self.card_selected
                    _cards[i]['Front'] = sprites.CardFront(self.card_selected, x, y)
                    card_group.add(_cards[i]['Front'])
                    _cards[i]['Reveal'] = True

                    self._change_card_in_hand(prev_card)
                else:
                    card_group.add(_cards[i]['Back'])
            elif _cards[i]['Reveal'] == True:
                card_group.add(_cards[i]['Front'])
            else:
                card_group.add(_cards[i]['Back'])

        if player:
            self.player_card_group = card_group
            self.player_cards = _cards
        elif opponent:
            self.opponent_card_group = card_group
            self.opponent_cards = _cards

    def _check_stock_collision(self):
        # Draw from Discard Cards
        for dc in self.discard_card_group.copy():
            if dc.rect.collidepoint(self.mouse_x, self.mouse_y):
                if not self.card_selected:
                    dc.kill()
                    self._change_card_in_hand(self.discard_cards.pop(-1)['Card'])
                    if len(self.discard_cards):
                        card = self.discard_cards[-1]['Card']
                        self.discard_card_group.add(sprites.CardFront(card, self.discard_card_x, self.discard_card_y))

        # Draw Pile
        remaining_cards = self.playing_deck_group.copy()
        self.playing_deck_group = pygame.sprite.Group()
        for pc in remaining_cards:
            if pc.rect.collidepoint(self.mouse_x, self.mouse_y):
                if self.card_in_hand and self.card_selected:
                    self.card_in_hand.kill()
                    self._discard_card(self.card_selected)
                self._change_card_in_hand(self.playing_deck.pop(0))
            if len(self.playing_deck):
                self.playing_deck_group.add(sprites.CardBack(self.stock_color, self.playing_deck_x, self.playing_deck_y))

    def _draw_buttons(self):
        self.buttons_group.draw(self.display)
        for button_text in self.button_text:
            self.display.blit(*button_text)


    def _check_button_collision(self):
        for i, button in enumerate(self.buttons_group):
            if button.rect.collidepoint(self.mouse_x, self.mouse_y):
                if self.buttons_map[i] == 'Rules':
                    if self.rules_displayed is False:
                        self.rules_displayed = True
                    else:
                        self.rules_displayed = False


    def _display_turn(self):
        if self.player_turn:
            text = "Player's Turn"
        else:
            text = "Opponent's Turn"

        font = pygame.font.Font(fonts.get_font(style='Bold'), 32)
        color = (255,255,255)
        x = self.screen_res[0] / 2
        y = self.screen_res[1] / 2
        text = font.render(text, 0, color)
        text_rect = text.get_rect()
        text_rect.centerx, text_rect.centery = (x, y)
        self.display.blit(text, text_rect)


    def _setup(self, num_decks=1):
        self.playing_deck = cards.build_decks(num_decks=num_decks)
        self.playing_deck_group = pygame.sprite.Group()
        self.opponent_cards = {}
        self.opponent_card_group = pygame.sprite.Group()
        self.player_cards = {}
        self.player_card_group = pygame.sprite.Group()
        self.discard_cards = []
        self.discard_card_group = pygame.sprite.Group()
        self.card_in_hand = None
        self.card_in_hand_group = pygame.sprite.Group()
        self.buttons_map = {}
        self.buttons_group = pygame.sprite.Group()
        self.button_text = []

        # Opponent Cards
        # opponent_x = int((self.screen_res[0] / 2) + ((cards.CARD_DIMENSIONS[0] * 5) * .5)) - 20
        opponent_x = (self.screen_res[0] / 2) + (cards.CARD_DIMENSIONS[0] * 2)
        x = opponent_x
        y = cards.CARD_DIMENSIONS[1] * 1.75
        for i in range(self.opponent_cards_remaining):
            card = self.playing_deck.pop(0)
            self.opponent_cards[i] = {
                'Card': card,
                'Back': sprites.CardBack(self.opponent_color, x, y),
                'Front': sprites.CardFront(card, x, y),
                'Reveal': False
            }

            # Add card back srpite to group
            self.opponent_card_group.add(self.opponent_cards[i]['Back'])

            # Increment x with card width + buffer of 10 px
            # This adds space of 10 px between each card
            x -= cards.CARD_DIMENSIONS[0] + 10

            if i == 4:
                # 5 cards per row max, create a second row
                # Increment y with card height + buffer of 10 px
                # This adds a space of 10px between rows
                x = opponent_x
                y -= cards.CARD_DIMENSIONS[1] + 10

        # Player Cards
        # x, y = self.card_x, y + (cards.CARD_DIMENSIONS[1] * 2)
        # player_x = int((self.screen_res[0] / 2) - ( (cards.CARD_DIMENSIONS[0] * 5) * .5) ) + 20
        player_x = (self.screen_res[0] / 2) - (cards.CARD_DIMENSIONS[0] * 2)
        x = player_x
        y = self.screen_res[1] - (cards.CARD_DIMENSIONS[1] * 1.75)
        for i in range(self.player_cards_remaining):
            card = self.playing_deck.pop(0)
            self.player_cards[i] = {
                'Card': card,
                'Back': sprites.CardBack(self.player_color, x, y),
                'Front': sprites.CardFront(card, x, y),
                'Reveal': False
            }

            # Add card back srpite to group
            self.player_card_group.add(self.player_cards[i]['Back'])

            # Increment x with card width + buffer of 10 px
            # This adds space of 10 px between each card
            x += cards.CARD_DIMENSIONS[0] + 10

            if i == 4:
                # 5 cards per row max, create a second row
                # Increment y with card height + buffer of 10 px
                # This adds a space of 10px between rows
                x = player_x
                y += cards.CARD_DIMENSIONS[1] + 10    

        # Remaining playing deck cards
        self.playing_deck_group.add(sprites.CardBack(self.stock_color, self.playing_deck_x, self.playing_deck_y))

        # Buttons
        font = pygame.font.Font(fonts.get_font(style='Bold'), 28)
        font_color = (0,0,0)

        # Rules button
        rules_button = sprites.Button('yellow', (buttons.BUTTON_DIMENSIONS[0] / 2) + 20, self.screen_res[1] - (buttons.BUTTON_DIMENSIONS[1] / 2) - 20)
        rules_button_text = font.render("Rules", True, font_color)
        rbt_rect = rules_button_text.get_rect()
        rbt_rect.centerx, rbt_rect.centery = rules_button.rect.center
        self.buttons_group.add(rules_button)
        self.button_text.append((rules_button_text, rbt_rect))
        self.buttons_map[0] = 'Rules'


def play():
    game = Game()
    game.play()

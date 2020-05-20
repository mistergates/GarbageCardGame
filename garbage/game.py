import pygame
import ctypes

from . import cards
from . import sprites

# TODO
# - Check for winner (all cards should be Reveal is True)
# - Display whose turn it is
# - Draw opponent cards from top Y and characte cards from bottom Y

class Game:

    def __init__(self):
        self.title = 'Garbage'
        self.fps = 90
        self.clock = pygame.time.Clock()
        self.screen_res = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
        self.screen = pygame.display.set_mode(self.screen_res, pygame.FULLSCREEN)
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

        # Background
        self.bg_image = pygame.image.load(cards.get_table())
        self.bg = pygame.transform.scale(self.bg_image, self.screen_res)
        self.bg_rect = self.bg.get_rect()

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

        # Mouse positioning
        self.mouse_x = 0
        self.mouse_y = 0


    def play(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        while True:
            self.screen.blit(self.bg, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                # Left click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mouse_x, self.mouse_y = event.pos

                # Right click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
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

            # Setup a new game if needed
            if self.setup: 
                self._setup()
                self.setup = False

            # Draw Cards
            self._draw_cards()

            # Reset between ticks
            self.mouse_x, self.mouse_y = 0, 0

            pygame.display.update()
            self.clock.tick(self.fps)


    def _draw_cards(self):
        """First, We create a copy of the current state of player and opponent cards.
        Then we reset the current card group back to an empty sprite group.
        Next we check to see if a card was clicked, if so we add the card front image to the group and set Reveal to True.
        If card was not clicked, we add card back image to the group (defautl state of card display).
        Lastly we draw the decks to the screen.
        """
        self._check_card_collision(player=True)
        self._check_card_collision(opponent=True)

        # Draw from Discard Cards
        # TODO If card is drawn from discard pile, we need to remove that card
        for dc in self.discard_card_group:
            if dc.rect.collidepoint(self.mouse_x, self.mouse_y):
                if not self.card_selected:
                    self._change_card_in_hand(self.discard_cards[-1]['Card'])
                    self.discard_cards[-1]['Front'].remove()
                    self.discard_cards[-1]['Front'].kill()

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
                self.playing_deck_group.add(sprites.CardBack('blue', self.playing_deck_x, self.playing_deck_y))

        # Draw card groups to screen
        self.opponent_card_group.draw(self.screen)
        self.player_card_group.draw(self.screen)
        self.playing_deck_group.draw(self.screen)
        self.discard_card_group.draw(self.screen)
        self.card_in_hand_group.draw(self.screen)


    def _change_card_in_hand(self, card):
        if self.card_in_hand:
            # Kill the previous card in hand and add the new one from the table
            self.card_in_hand.kill()

        self.card_selected = card
        self.card_in_hand = sprites.CardFront(self.card_selected, *pygame.mouse.get_pos())
        self.card_in_hand_group.add(self.card_in_hand)


    def _discard_card(self, card):
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


    def _setup(self, num_decks=1):
        self.playing_deck = cards.build_decks(num_decks=num_decks)

        # Opponent Cards
        x, y = self.card_x, self.card_y
        for i in range(self.opponent_cards_remaining):
            card = self.playing_deck.pop(0)
            self.opponent_cards[i] = {
                'Card': card,
                'Back': sprites.CardBack('red', x, y),
                'Front': sprites.CardFront(card, x, y),
                'Reveal': False
            }

            # Add card back srpite to group
            self.opponent_card_group.add(self.opponent_cards[i]['Back'])

            # Increment x with card width + buffer of 10 px
            # This adds space of 10 px between each card
            x += cards.CARD_DIMENSIONS[0] + 10

            if i == 4:
                # 5 cards per row max, create a second row
                # Increment y with card height + buffer of 10 px
                # This adds a space of 10px between rows
                x = self.card_x
                y += cards.CARD_DIMENSIONS[1] + 10

        # Player Cards
        x, y = self.card_x, y + (cards.CARD_DIMENSIONS[1] * 2)
        for i in range(self.player_cards_remaining):
            card = self.playing_deck.pop(0)
            self.player_cards[i] = {
                'Card': card,
                'Back': sprites.CardBack('green', x, y),
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
                x = self.card_x
                y += cards.CARD_DIMENSIONS[1] + 10    

        # Remaining playing deck cards
        self.playing_deck_group.add(sprites.CardBack('blue', self.playing_deck_x, self.playing_deck_y))

def play():
    game = Game()
    game.play()

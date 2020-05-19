import pygame
import ctypes
from . import cards
from . import sprites

class Game:
    def __init__(self):
        self.title = 'Garbage'
        self.fps = 90
        self.clock = pygame.time.Clock()
        self.screen_res = (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
        self.screen = pygame.display.set_mode(self.screen_res, pygame.FULLSCREEN)

        # Background
        self.bg_image = pygame.image.load(cards.get_table())
        self.bg = pygame.transform.scale(self.bg_image, self.screen_res)
        self.screen.blit(self.bg, (0, 0))
        self.bg_rect = self.bg.get_rect()

        # Cards
        self.playing_deck = []
        self.playing_deck_group = pygame.sprite.Group()
        self.opponent_cards = {}
        self.opponent_card_group = pygame.sprite.Group()
        self.player_cards = {}
        self.player_card_group = pygame.sprite.Group()
        self.discard_cards = []
        self.discard_card_group = pygame.sprite.Group()

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
        self.card_selected = None
        self.player_turn = True
        self.opponent_turn = False

        # Mouse positioning
        self.mouse_x = 0
        self.mouse_y = 0


    def play(self):
        pygame.init()
        pygame.display.set_caption(self.title)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_x, self.mouse_y = event.pos

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
        # Player Cards
        player_cards = self.player_card_group.copy()
        self.player_card_group = pygame.sprite.Group()
        for i, pc in enumerate(player_cards):
            if pc.rect.collidepoint(self.mouse_x, self.mouse_y) and self.card_selected and self.player_turn:
                if self.card_selected[0] in cards.WILD_CARDS or self.card_selected[0] == cards.CARD_MATCHES[i]:
                    _x, _y = pc.rect.center
                    self.discard_cards.append(self.player_cards[i]['Card'])
                    self.discard_card_group.add(sprites.CardFront(self.player_cards[i]['Card'], self.discard_card_x, self.discard_card_y))
                    self.player_cards[i]['Card'] = self.card_selected
                    self.player_cards[i]['Front'] = sprites.CardFront(self.card_selected, _x, _y)
                    self.player_card_group.add(self.player_cards[i]['Front'])
                    self.player_cards[i]['Reveal'] = True
                    self.card_selected = None
                else:
                    self.player_card_group.add(self.player_cards[i]['Back'])
            elif self.player_cards[i]['Reveal'] == True:
                self.player_card_group.add(self.player_cards[i]['Front'])
            else:
                self.player_card_group.add(self.player_cards[i]['Back'])

        # Opponent Cards
        opponent_cards = self.opponent_card_group.copy()
        self.opponent_card_group = pygame.sprite.Group()
        for i, pc in enumerate(opponent_cards):
            if pc.rect.collidepoint(self.mouse_x, self.mouse_y) and self.card_selected and self.opponent_turn:
                if self.card_selected[0] in cards.WILD_CARDS or self.card_selected[0] == cards.CARD_MATCHES[i]:
                    _x, _y = pc.rect.center
                    self.discard_cards.append(self.opponent_cards[i]['Card'])
                    self.discard_card_group.add(sprites.CardFront(self.opponent_cards[i]['Card'], self.discard_card_x, self.discard_card_y))
                    self.opponent_cards[i]['Card'] = self.card_selected
                    self.opponent_cards[i]['Front'] = sprites.CardFront(self.card_selected, _x, _y)
                    self.opponent_card_group.add(self.opponent_cards[i]['Front'])
                    self.opponent_cards[i]['Reveal'] = True
                    self.card_selected = None
                else:
                    self.opponent_card_group.add(self.opponent_cards[i]['Back'])
            elif self.opponent_cards[i]['Reveal'] == True:
                self.opponent_card_group.add(self.opponent_cards[i]['Front'])
            else:
                self.opponent_card_group.add(self.opponent_cards[i]['Back'])

        # Discard Cards
        for i, pc in enumerate(self.discard_card_group):
            if pc.rect.collidepoint(self.mouse_x, self.mouse_y):
                self.card_selected = self.discard_cards[-1]


        # Draw Pile
        remaining_cards = self.playing_deck_group.copy()
        self.playing_deck_group = pygame.sprite.Group()
        for pc in remaining_cards:
            if pc.rect.collidepoint(self.mouse_x, self.mouse_y):
                card = self.playing_deck.pop(0)
                self.discard_cards.append(card)
                self.discard_card_group.add(sprites.CardFront(card, self.discard_card_x, self.discard_card_y))
                self.card_selected = None
            if len(self.playing_deck):
                self.playing_deck_group.add(sprites.CardBack('blue', self.playing_deck_x, self.playing_deck_y))
        
        
        # Draw card groups to screen
        self.opponent_card_group.draw(self.screen)
        self.player_card_group.draw(self.screen)
        self.playing_deck_group.draw(self.screen)
        self.discard_card_group.draw(self.screen)


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

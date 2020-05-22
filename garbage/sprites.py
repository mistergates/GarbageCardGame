import pygame
from . import cards, buttons

class CardFront(pygame.sprite.Sprite):
    def __init__(self, card, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(cards.get_card_front(card[0], card[1]))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def reposition_on_mouse(self):
        self.rect.center = pygame.mouse.get_pos()


class CardBack(pygame.sprite.Sprite):
    def __init__(self, color, x, y, version=5):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(cards.get_card_back(color, version=version))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Button(pygame.sprite.Sprite):
    def __init__(self, color, x, y, version='01'):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = x, y
        self.image = pygame.image.load(buttons.get_button(color, version=version))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

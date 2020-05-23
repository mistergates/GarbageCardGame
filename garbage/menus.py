
import pygame

from . import rules, fonts

class Menus:

    def __init__(self, parent):
        self.parent = parent


    def check_menus(self):
        if self.parent.rules_displayed:
            self.rules_menu()

    def main_menu(self):
        pass

    def rules_menu(self):
        # Text
        header = pygame.font.Font(fonts.get_font(style='Bold'), 24)
        font = pygame.font.Font(fonts.get_font(style='Regular'), 18)
        color = (255, 255, 255)
        words = [word.split(' ') for word in rules.RULES.splitlines()]
        space = font.size(' ')[0]
        max_width = self.parent.display.get_size()[0] - 10
        pos = 10, 10
        x, y = pos
        words_to_blit = []
        for line in words:
            for word in line:
                if '##' in line[0]:
                    # This is a header line, remove ## and render with header obj
                    word_surface = header.render(word.replace('##', ''), 0, color)
                else:
                    # Normal text, render with font obj
                    word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                words_to_blit.append((word_surface, (x, y)))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.

        # Draw background
        s = pygame.Surface((self.parent.screen_res[0], y + 10), pygame.SRCALPHA)
        s.fill((0,0,0,200))
        self.parent.display.blit(s, (0, 0))

        # Draw words
        for word in words_to_blit:
            self.parent.display.blit(*word)
    
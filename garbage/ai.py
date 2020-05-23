'''Opponent AI'''
import pygame
import time
from . import cards, sprites

class OpponentAI:

    def __init__(self, parent):
        self.parent = parent

    def play_turn(self):
        if not self.parent.opponent_turn:
            return

        if not self.parent.card_selected:
            if self.parent.discard_cards and self._card_is_playable(self.parent.discard_cards[-1]['Card']):
                self._get_discard_card()
            else:
                self._draw_card()

        if self._card_is_playable(self.parent.card_selected):
            self.play_card()
        else:
            print(f'{self.parent.card_selected} not playable, discarding')
            self.parent._discard_card(self.parent.card_selected)

        # time.sleep(1)


    def play_card(self):
        card_played = False
        card_selected = self.parent.card_selected
        card_value = card_selected[0]

        card_group_copy = self.parent.opponent_card_group.copy()
        card_group = pygame.sprite.Group()
        for i, card in enumerate(card_group_copy):
            # Check if card value
            if card_value in cards.WILD_CARDS or card_value == cards.CARD_MATCHES[i]:
                if self.parent.opponent_cards[i]['Reveal']:
                    card_group.add(self.parent.opponent_cards[i]['Front'])
                    continue
                print(f'Found a match for {card_selected} at index {i}')
                # Play the card
                x, y = card.rect.center
                prev_card = self.parent.opponent_cards[i]['Card']
                print(f'Previous card was {prev_card}')
                self.parent.opponent_cards[i]['Card'] = self.parent.card_selected
                self.parent.opponent_cards[i]['Front'] = sprites.CardFront(self.parent.card_selected, x, y)
                card_group.add(self.parent.opponent_cards[i]['Front'])
                self.parent.opponent_cards[i]['Reveal'] = True
                self.parent._change_card_in_hand(prev_card)
                card_played = True
            else:
                card_group.add(self.parent.opponent_cards[i]['Back'])

            self.parent.opponent_card_group = card_group

        return True if card_played else False


    def _draw_card(self):
        self.parent._change_card_in_hand(self.parent.playing_deck.pop(0))

    def _get_discard_card(self):
        self.parent._change_card_in_hand(self.parent.discard_cards.pop(-1)['Card'])

    def _card_is_playable(self, card):
        card_value = card[0]

        if card_value in cards.DEAD_CARDS:
            return False

        if card_value == 'J':
            return True

        for i in self.parent.opponent_cards:
            # Check if card value
            current_card = self.parent.opponent_cards[i]
            if cards.CARD_MATCHES[i] == card_value and not current_card['Reveal']:
                return True

        return False

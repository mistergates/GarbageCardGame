import arcade

from . import cards

class ComputerAi:

    def __init__(self, game):
        self.game = game

    def play_turn(self, card):

        if not self.game.computer_turn:
            return

        if not card:
            if self.game.discard_pile_list and self.card_is_playable(self.game.discard_pile_list[-1]):
                self.game.get_card_from_discard_pile(*self.game.calc_card_pos(discard=True))
            else:
                self.game.get_card_from_draw_pile(*self.game.calc_card_pos(draw=True))
            return

        if self.card_is_playable(card):
            self.play_card(card)
        else:
            self.game.discard_card_in_hand()

    def card_is_playable(self, card):
        if card.value not in cards.DEAD_CARDS: 
            for i, current_card in enumerate(self.game.computer_card_list):
                # If both are wild cards continue on
                if card.value in cards.WILD_CARDS and current_card.value in cards.WILD_CARDS and current_card.display:
                    continue
                # Check if card value
                if (cards.CARD_MATCHES[i] == card.value or card.value in cards.WILD_CARDS) and not current_card.display:
                    return True
                elif cards.CARD_MATCHES[i] == card.value and current_card.value in cards.WILD_CARDS and current_card.display:
                    return True
        return False

    def play_card(self, card):
        print(f'Computer playing card {card.value}')
        table_card = self.get_table_card_match()
        self.game.play_card_in_hand(table_card, *table_card.position)

    def get_table_card_match(self):
        for table_card in self.game.computer_card_list:
            if self.game.is_card_playable(table_card):
                return table_card

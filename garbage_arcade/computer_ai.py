import arcade

from . import cards, sprites

class ComputerAi:

    def __init__(self, game):
        self.game = game

    def play_turn(self):
        """Main loop for computer AI turn"""
        if not self.game.computer_turn:
            return

        if not self.game.card_in_hand:
            arcade.pause(1)
            # Draw a card from either the discard pile list (if top card is playable) or draw pile
            if len(self.game.discard_pile_list) > 1 and self.card_is_playable(self.game.discard_pile_list[-1]):
                self.game.get_card_from_discard_pile(*self.game.calc_card_pos(discard=True))
            else:
                self.game.get_card_from_draw_pile(*self.game.calc_card_pos(draw=True))

        if not self.game.card_in_hand:
            # Something went wrong
            return

        table_card = self.get_table_card_match()
        if table_card:
            # print(f'Playing {self.game.card_in_hand.value} to {table_card.position} (current pos {self.game.card_in_hand.position})')
            # If we haven't moved the card yet, wait for that
            if list(self.game.card_in_hand.position) != list(table_card.position):
                if not self.game.target_table_card:
                    self.game.target_table_card = table_card
                self.game.move_card_wait = True
                return
            # Card is finished moving, play it now
            self.game.target_table_card = None
            # self.game.move_card_wait = False
            self.play_card(table_card)
        else:
            # Move the card to discard pile
            if not self.game.target_table_card:
                self.game.target_table_card = sprites.CardBack('Red')
                self.game.target_table_card.position = list(self.game.calc_card_pos(discard=True))

            # print(f'Discarding {self.game.card_in_hand.value} to {fake_card.position}')
            if list(self.game.card_in_hand.position) != list(self.game.target_table_card.position):
                self.game.move_card_wait = True
                return
            # Card is finished moving, play it now
            self.game.target_table_card = None
            self.game.move_card_wait = False
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

    def play_card(self, table_card):
        table_card = self.get_table_card_match()
        self.game.play_card_in_hand(table_card, *table_card.position)

    def get_table_card_match(self):
        for table_card in self.game.computer_card_list:
            if self.game.is_card_playable(table_card):
                return table_card

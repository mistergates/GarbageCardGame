from tkinter import Tk, Button, Label, LabelFrame, PhotoImage, messagebox, DISABLED, NORMAL, E, W

from . import cards


class Game:

    def __init__(self):
        # Main Window
        self.root = Tk()
        self.root.title('Garbage')
        self.root.state('zoomed')

        # Opponent Frame
        self.opponent_frame = LabelFrame(self.root)
        self.opponent_label = Label(self.opponent_frame, text='Opponent Cards')
        self.opponent_label.grid(row=0, column=0, columnspan=5)
        self.opponent_frame.grid(row=1, column=0)

        # Player Frame
        self.player_frame = LabelFrame(self.root)
        self.player_label = Label(self.player_frame, text='Player Cards')
        self.player_label.grid(row=2, column=0, columnspan=5)
        self.player_frame.grid(row=3, column=0)

        # Cards
        self.playing_deck = cards.build_decks()
        self.opponent_cards = {}
        self.player_cards = {}


    def setup(self):
        # Opponent Cards
        row = 0
        index = 0
        for i in range(10):
            self.opponent_cards[i] = self.playing_deck.pop(0)
            button = Button(self.opponent_frame)
            image = PhotoImage(file=cards.get_card_back('red'))
            button.config(image=image)
            button.grid(row=row, column=index, padx=5, pady=5)
            button.photo = image

            index += 1
            if index == 5:
                index = 0
                row = 1

        # Player Cards
        row = 0
        index = 0
        for i in range(10):
            self.player_cards[i] = self.playing_deck.pop(0)
            button = Button(self.player_frame)
            image = PhotoImage(file=cards.get_card_back('blue'))
            button.config(image=image)
            button.grid(row=row, column=index, padx=5, pady=5)
            button.photo = image

            index += 1
            if index == 5:
                index = 0
                row = 1


def play():
    garbage = Game()
    garbage.setup()
    garbage.root.mainloop()
 
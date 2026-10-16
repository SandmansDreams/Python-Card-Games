from .card import Card, card_suit_table, card_value_table
import random

# A deck of cards, the end of the array is considered the top of the deck
class Deck:
    def __init__(self):
        self.create()
        self.shuffle()

    # Creates a new, unshuffled deck of 52 cards, 13 for each suit
    def create(self):
        cards = []

        for suit in card_suit_table:
            for value in card_value_table:
                cards.append(Card(value, suit))

        self.cards = cards

    # Randomizes the order of the deck
    def shuffle(self):
        random.shuffle(self.cards)

    def get_card_count(self):
        return len(self.cards)

    def draw_card(self) -> Card:
        return self.cards.pop()
        
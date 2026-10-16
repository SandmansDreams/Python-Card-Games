from .card import Card, card_back, empty_slot, join_multiline_strings
from abc import ABC, abstractmethod

# A generalized player class for a card game
class Player(ABC): 
    def __init__(self, name):
        self.name = name
        self.hand: list[Card] = []

    def __str__(self) -> str:
        return self.name

    def give_card(self, card: Card):
        self.hand.append(card)

    @abstractmethod
    def get_render(self) -> list[str]:
        pass
        
    @abstractmethod
    def take_turn(self) -> bool:
        pass
        
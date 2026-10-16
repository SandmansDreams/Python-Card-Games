""" NOTES
Game Loop:
    # Setup
    1. Shuffle a deck of cards
    2. Deal seven columns of cards from left to right
        - Each has cards equal to their column number (7 -> 7)
        - The last card in each column is turned face up
    3. The remaining cards go into a "stock pile"

    # Playing
    - Player must move a card from one pile to another (by typing column -> column) 
        - The cards must be placed in descending order, alternating between red (hearts, diamonds) and black (clubs, spades) suits
        - Stacks can be moved as well as long as they follow the rules and the whole stack is moved at once
        - When all the face up cards are moved from a column, the next card is flipped
        - Only a stack starting with a king can be placed into an empty column
        - Aces can be placed in a foundation pile and are in reverse order (ace -> king), you can play cards directly onto a foundation pile
        - You may draw a card from the stock pile onto the waste pile, and the top card of the waste pile can be played
        - When the stock pile runs out, the waste pile is flipped over to become the stock pile again
    - There is a possibility that there are no legal moves, in which case the game is over
    - A special rule for this game: At the end, the amount of cards you played successfully are tallied up for points and thats your score, even if you lost. The top score possible is the sum of all cards
"""

import time
import os
from cards.card import Card, card_back, empty_border, empty_slot, card_suit_table, card_value_table, join_multiline_strings
from cards.deck import Deck
from cards.player import Player
from cards.utility import GREEN, RED, print_style



# Each foundation pile only takes one suit, in this order (f1 = hearts, f2 = diamonds...)
foundation_suits = list(card_suit_table)

# Cards in a column have to alternate between red and black suits
red_suits = ["hearts", "diamonds"]

# The best possible score, every card on the foundations (ace = 1 ... king = 13, for each suit)
max_score = sum(range(1, len(card_value_table) + 1)) * len(card_suit_table)



# Create an empty foundation
def make_foundation(suit):
    return [
        "┌─────┐",
        "│     │",
       f"│  {card_suit_table[suit]}  │",
        "│     │",
        "└─────┘"
    ]

# Gets the rank of a card as a number (ace = 1 ... king = 13)
def get_rank(card):
    return card_value_table.index(card.value) + 1

def is_red(card):
    return card.suit in red_suits

# Centers a label over each card slot so the player knows what to type
def make_labels(labels, spacer):
    return spacer.join(f"{label:^7}" for label in labels)



# Manages the game
class SolitaireManager:
    def __init__(self, player_name: str):
        self.player = player_name
        self.columns: list[list[Card]] = [[],[],[],[],[],[],[]]
        self.foundations: list[list[Card]] = [[],[],[],[]]
        self.waste: list[Card] = [] # Cards drawn from the stock, the end of the list is the top card that can be played

    # Actually run the game
    def run_game(self) -> bool:
        print_style("Starting game...", GREEN)
        self.stock = Deck() # Create a fresh shuffled deck

        print_style("Deck shuffled, laying out cards...", GREEN)

        self.deal_initial_cards()

        print_style("Finished layout, player may start playing.", GREEN)
        print_style("Play by typing what you want to happen (e.g. '1 4' will attempt to put a card from column 1 to column 4.)", GREEN)

        # Keep taking turns until the player wins, runs out of moves, or quits
        can_play = self.has_moves()
        while can_play:
            can_play = self.take_turn()

        if self.has_won():
            print_style("Every card is on the foundations, you won!", GREEN)
        elif not self.has_moves():
            print_style("There are no legal moves left, game over!", GREEN)
        else:
            print_style("You ended the game", GREEN)

        print_style(f"Final score: {self.get_score()} out of {max_score}", GREEN)

        # Prompt to start again
        return self.restart()

    def restart(self): # Player chooses to restart the game
        query = input("Wanna go again? Y/N: ").upper()

        if query in ["Y", "YES"]:
            # Clear the table so the next deal starts fresh
            self.columns = [[],[],[],[],[],[],[]]
            self.foundations = [[],[],[],[]]
            self.waste = []

            return True

        else: return False

    def deal_initial_cards(self): # Deal cards into columns and put the rest in the stock
        for column_idx, column in enumerate(self.columns):
            for card_idx in range (column_idx + 1):
                card = self.stock.draw_card()

                if card_idx != column_idx:
                    card.flip()

                column.append(card)

        self.render_board()

    def render_board(self):
        os.system("cls" if os.name == "nt" else "clear")
        spacer = " "

        top_row = self.collect_top_row(spacer)
        rendered_columns = join_multiline_strings(*self.collect_columns(), spacer = spacer)

        # Draw
        print(f"Score: {self.get_score()}    Stock: {self.stock.get_card_count()}    Waste: {len(self.waste)}")
        print()

        print(make_labels(["stock", "s", "", "f1", "f2", "f3", "f4"], spacer))
        for line in top_row:
            print(line)

        print()

        print(make_labels(["1", "2", "3", "4", "5", "6", "7"], spacer))
        for line in rendered_columns:
            print(line)

    def collect_top_row(self, spacer) -> list[str]:
        # Show the stock as face down until it runs out, and the top card of the waste pile
        stock = card_back if self.stock.get_card_count() > 0 else empty_border
        waste = self.waste[-1].render if self.waste else empty_border

        # Show the top card of each foundation, or which suit it takes if it's empty
        foundations = []
        for foundation_idx, foundation in enumerate(self.foundations):
            if foundation:
                foundations.append(foundation[-1].render)
            else:
                foundations.append(make_foundation(foundation_suits[foundation_idx]))

        return join_multiline_strings(
            stock,
            waste,
            empty_slot,
            *foundations,
            spacer = spacer
        )

    def collect_columns(self):
        collected_columns = []
        
        for column in self.columns:
            rendered_column = []

            for card in column[:-1]:
                rendered_column.extend(card.render[:2])

            if column:
                rendered_column.extend(column[-1].render)

            collected_columns.append(rendered_column)

        return collected_columns

    # Lets the player make one move, returns if the game can keep going
    def take_turn(self) -> bool:
        print_style("Viable terms: '#', 'f#' (for foundation piles), 's' (to use the top waste card), 'draw' / 'stock' (recycles the waste when the stock is empty), 'quit'", GREEN)
        play = input("What's your move?: ").lower().split()

        if not play:
            # They didn't type anything, try again
            print_style("Type a move to play", RED)
            return True

        elif play[0] in ['quit', 'q']:
            return False

        elif play[0] in ['draw','stock']:
            # Flip the top stock card onto the waste pile
            if self.stock.get_card_count() > 0:
                self.waste.append(self.stock.draw_card())
                self.render_board()

            # Out of stock, so flip the waste pile over to become the stock again
            elif self.waste:
                self.recycle_waste()
                self.render_board()
                print_style("Flipped the waste pile back over into the stock", GREEN)

            else:
                print_style("The stock and waste piles are both empty", RED)
                return True

            return self.has_moves()

        elif play[0] in ['s', '1', '2', '3', '4', '5', '6', '7']:
            if len(play) != 2:
                print_style("A move needs a start and an end (e.g. '1 4' or 's f1')", RED)
                return True

            # Perform the move if it's legal, otherwise try_move says why and they try again
            if self.try_move(play[0], play[1]):
                self.render_board()
                return not self.has_won() and self.has_moves()

            return True

        else:
            # They attempted an illegal or nonsensical expression, try again
            print_style("That isn't a move, try again", RED)
            return True

    # Attempts to move cards from the source ('s' or a column) to the destination (a column or foundation), returns if it worked
    def try_move(self, source, destination) -> bool:
        if source == 's' and not self.waste:
            print_style("The waste pile is empty, use 'draw' first", RED)
            return False

        if source != 's' and not self.columns[int(source) - 1]:
            print_style(f"Column {source} is empty", RED)
            return False

        # Moving onto a foundation, only one card can go at a time
        if destination in ['f1', 'f2', 'f3', 'f4']:
            foundation_idx = int(destination[1]) - 1

            if source == 's':
                card = self.waste[-1]
            else:
                card = self.columns[int(source) - 1][-1]

            if not self.can_place_on_foundation(card, foundation_idx):
                print_style(f"The {card} can't go on foundation {destination}", RED)
                return False

            self.foundations[foundation_idx].append(card)

            if source == 's':
                self.waste.pop()
            else:
                from_column = self.columns[int(source) - 1]
                from_column.pop()
                self.reveal_top_card(from_column)

            return True

        # Moving onto another column
        elif destination in ['1', '2', '3', '4', '5', '6', '7']:
            to_column = self.columns[int(destination) - 1]

            if source == destination:
                print_style("The cards are already in that column", RED)
                return False

            if source == 's':
                if not self.can_place_on_column(self.waste[-1], to_column):
                    print_style(f"The {self.waste[-1]} can't go on column {destination}", RED)
                    return False

                to_column.append(self.waste.pop())
                return True

            # Find the card in the source column that fits, then move it and everything on top of it
            from_column = self.columns[int(source) - 1]
            start = self.find_movable_stack(from_column, to_column)

            if start is None:
                if to_column:
                    print_style(f"Nothing in column {source} can go on the {to_column[-1]}", RED)
                else:
                    print_style("Only a King can go in an empty column", RED)
                return False

            to_column.extend(from_column[start:])
            del from_column[start:]
            self.reveal_top_card(from_column)
            return True

        else:
            print_style(f"'{destination}' isn't a column (1-7) or foundation (f1-f4)", RED)
            return False

    # Checks if a card can be placed at the end of a column
    def can_place_on_column(self, card, column) -> bool:
        if not column:
            return card.value == "King" # Only kings can go in an empty column

        # Cards must be placed in descending order, alternating between red and black
        top_card = column[-1]
        return top_card.face_up and is_red(card) != is_red(top_card) and get_rank(card) == get_rank(top_card) - 1

    # Checks if a card can be placed on a foundation, they build up from ace to king in one suit
    def can_place_on_foundation(self, card, foundation_idx) -> bool:
        foundation = self.foundations[foundation_idx]

        if card.suit != foundation_suits[foundation_idx]:
            return False

        if not foundation:
            return card.value == "Ace"

        return get_rank(card) == get_rank(foundation[-1]) + 1

    # Finds where a stack can be picked up from in a column so it fits on the destination, or None if nothing fits
    def find_movable_stack(self, column, destination) -> int | None:
        for card_idx, card in enumerate(column):
            if card.face_up and self.can_place_on_column(card, destination):
                return card_idx

        return None

    # When all the face up cards are moved off a column, the next card is flipped
    def reveal_top_card(self, column):
        if column and not column[-1].face_up:
            column[-1].flip()

    # Turns the waste pile back over so it becomes the stock, keeping the cards in the same order as before
    def recycle_waste(self):
        self.stock.cards = list(reversed(self.waste))
        self.waste = []

    def can_go_on_any_foundation(self, card) -> bool:
        return any(self.can_place_on_foundation(card, foundation_idx) for foundation_idx in range(4))

    # Checks if the player has any moves left that would actually change the game
    def has_moves(self) -> bool:
        # The stock can be cycled through forever, so every stock and waste card will eventually be playable
        for card in self.stock.cards + self.waste:
            if self.can_go_on_any_foundation(card) or any(self.can_place_on_column(card, column) for column in self.columns):
                return True

        for column in self.columns:
            if not column: continue

            # The end card could go onto a foundation
            if self.can_go_on_any_foundation(column[-1]):
                return True

            # Some of the column could go onto another column
            for other_column in self.columns:
                if other_column is column: continue

                start = self.find_movable_stack(column, other_column)
                if start is None: continue

                if start == 0:
                    # Emptying a column is useful, but moving a king from one empty spot to another doesn't do anything
                    if other_column: return True

                elif not column[start - 1].face_up:
                    return True # It would flip over a new card

                # Otherwise the stack is just swapping between two cards of the same color and rank (like 8♠ to 8♣),
                # which only helps if it uncovers a card that can go onto a foundation
                elif self.can_go_on_any_foundation(column[start - 1]):
                    return True

        return False

    def has_won(self) -> bool:
        return all(len(foundation) == len(card_value_table) for foundation in self.foundations)

    # The score is the total value of every card played onto the foundations
    def get_score(self) -> int:
        return sum(get_rank(card) for foundation in self.foundations for card in foundation)


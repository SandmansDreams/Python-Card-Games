# The back of a card
from itertools import zip_longest
from .utility import RED, GREEN, YELLOW, BLUE, RESET



card_back = [
    "╔═════╗",
   f"║?????║",
   f"║?????║",
   f"║?????║",
    "╚═════╝"
]

# An bordered empty card space
empty_border = [
    "┌─────┐",
    "│     │",
    "│     │",
    "│     │",
    "└─────┘"
]

# An empty card space
empty_slot = [
    "       ",
    "       ",
    "       ",
    "       ",
    "       ",
]

# Convert a card string suit to colored suit symbol
card_suit_table = {
    "hearts": f"{RED}♥{RESET}",
    "diamonds": f"{YELLOW}♦{RESET}",
    "clubs": f"{GREEN}♣{RESET}",
    "spades": f"{BLUE}♠{RESET}"
}

card_value_table = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]



# Create a visible card
def make_visual_card(value, suit):
    value_length = len(value)

    # Convert whole string to fist letter instead
    if value_length > 2:
        value = value[0]

    return [
        "╔═════╗",
       f"║{value:<2}  {card_suit_table[suit]}║",
        "║     ║",
       f"║{card_suit_table[suit]}  {value:>2}║",
        "╚═════╝"
    ]

# Takes a set of multiline strings (mainly cards and spaces) and combines them into one set of rows for printing
def join_multiline_strings(*blocks, spacer) -> list[str]:
    if not blocks:
        return empty_slot

    blank_line = 7 * " "

    rows = []

    for row in zip_longest(*blocks, fillvalue = blank_line):
        rows.append(spacer.join(row))

    return rows



# A genralized card class for both rendering and actions
class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.drawing = make_visual_card(value, suit)
        self.render = self.drawing
        self.face_up = True

    def __str__(self):
        return f"{self.value} of {self.suit}"

    def flip(self):
        self.face_up = not self.face_up

        if self.face_up:
            self.render = self.drawing
        else:
            self.render = card_back
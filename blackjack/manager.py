""" NOTES
Game Loop:
    1. Create and shuffle a 52-card deck
    2. Deal each player 2 cards face up
    3. Deal the dealer:
        - 1 card face up
        - 1 card face down
    4. Starting with the players:
        - Check for Blackjack (has of exactly 21 including one ace and a value 10 card)
        - If they do not have Blackjack, they may:
            - Hit
            - Stand
    5. If a player busts (have over 21), their turn ends immediately
    6. Once player is done, dealer reveals hidden card
    7. Dealer must:
        - Hit while their hand totals less than 16.
        - Stand when their hand totals 16 or higher.
    8. Compare each remaining player's hand against the dealer:
        - Player busts -> Player loses.
        - Dealer busts -> Players win.
        - Player has higher total -> Player wins.
        - Dealer has higher total -> Player loses.
        - Equal totals -> Push (tie).
    9. Start the next round.
"""



import os
import time
from cards.card import join_multiline_strings, card_back
from cards.deck import Deck
from cards.player import Player
from cards.utility import print_style, visible_length, GREEN



# Convert a card string value to points
card_point_table = {
    "ace": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "jack": 10,
    "queen": 10,
    "king": 10,
}


# Gets the point vaule of a card if it's face up
def get_points(card):
    if card.face_up:
        return card_point_table[card.value.lower()]
    else: return 0



class BlackjackPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.busted = False

    # Get total score by summing the point value of all cards in hand
    def get_score(self): 
        if self.busted: return 0 # Win protection

        points = 0

        # Add up all the points of cards (aces count as 1 here)
        for card in self.hand:
            points += get_points(card)

        # Handle aces, one face up ace can count as 11 instead if it doesn't make the hand bust
        has_ace = any(card.face_up and card.value.lower() == "ace" for card in self.hand)
        if has_ace and points + 10 <= 21:
            points += 10

        return points

    def get_render(self, busted=False):
        title = f"{self.name.upper()}: {self.get_score()}"

        card_strings = join_multiline_strings(
            *(card.render for card in self.hand),
            spacer=" "
        )

        cards_width = 0
        hand_length = len(self.hand)
        if hand_length > 0:
            cards_width = (len(card_back[0]) * hand_length) + (hand_length - 1)

        longest_width = max(cards_width, len(title))

        title += " " * (longest_width - (len(title)))

        if cards_width < longest_width:
            card_strings = [
                line + " " * (longest_width - visible_length(line))
                for line in card_strings
            ]

        render = [title]
        render.extend(card_strings)

        return render

class BlackjackComputerPlayer(BlackjackPlayer):
    def __init__(self, name):
            super().__init__(name)

    def take_turn(self):
        if self.get_score() < 18:
            return True
        else: 
            return False

class BlackjackHumanPlayer(BlackjackPlayer):
    def __init__(self, name):
            super().__init__(name)

    def take_turn(self):
        while True:
            decision = input("What would you like to do? HIT or STAND: ").upper()

            if "H" in decision:
                return True
            elif "S" in decision:
                return False
            else: 
                print("Sorry, try again")



# Manages a game of blackjack
class BlackjackManager(BlackjackPlayer):
    def __init__(self, player_name: str, opponent_count):
        super().__init__("Dealer")

        players: list[BlackjackPlayer] = [self]
        players.append(BlackjackHumanPlayer(player_name))
        players.extend(self.create_opponents(opponent_count))
        self.players = players

        self.deck = Deck()

    # Creates a number of opponent players
    def create_opponents(self, count) -> list[BlackjackComputerPlayer]:
        if count > 4: count = 4
        opps = []

        for i in range(count):
            opps.append(BlackjackComputerPlayer(f"Comp{i + 1}"))

        return opps

    # Actually run the game
    def run_game(self) -> bool:
        print_style("Starting game...", GREEN)
        self.deck = Deck() # Create a fresh shuffled deck

        print_style("Deck shuffled, dealing...", GREEN)

        self.deal_initial_cards()

        print_style("Finished dealing, checking for blackjack...", GREEN)

        for player in self.players[1:]:
            has_blackjack = self.check_for_blackjack(player)
            if has_blackjack: return self.restart()

        print_style("No one has blackjack, taking turns...", GREEN)

        have_winner = self.do_turns()
        if have_winner: return self.restart()

        winners = self.get_winners_from_points()
        print_style(f"{" and ".join(winners)} have won through points! Congrats!", GREEN)

        # Prompt to start again
        return self.restart()

    def restart(self):
        query = input("Wanna go again? Y/N: ").upper()

        if query in ["Y"]:
            for player in self.players:
                player.hand = []
                player.busted = False

            return True

        else: return False

    def deal_initial_cards(self): # Deal each player 2 cards face up and the dealer one card face down and one face up
        cards_dealt = 0

        while cards_dealt < 2:
            # For each player, deal a face up card
            for player in reversed(self.players):
                if player.name == "Dealer": # If its the dealer
                    # If its the first time, deal a face down card to the dealer
                    if cards_dealt == 0:
                        self.deal_card(self, True)
                        print_style("Dealt face down card to dealer", GREEN)
                        time.sleep(.5)
                        continue

                self.deal_card(player)
                print_style(f"Dealt face up card to {player.name}", GREEN)
                time.sleep(.5)
            cards_dealt += 1

    def deal_card(self, target, flipped = False):
        card = self.deck.draw_card()
        if flipped: card.flip()
        target.give_card(card)
        self.render_board()

    def render_board(self):
        os.system("cls" if os.name == "nt" else "clear")
        spacer = "     "
        second_row_players = self.players[1:]

        second_row = join_multiline_strings(
            *(player.get_render() for player in second_row_players),
            spacer = spacer
        )

        # Print the dealer centered
        first_row = self.players[0].get_render()

        board_width = max(
            visible_length(line)
            for line in second_row
        )

        # Every line of the dealer's render is the same width, so shift them all by the same amount
        dealer_width = visible_length(first_row[0])
        left_padding = " " * ((board_width - dealer_width) // 2)

        for line in first_row:
            print(left_padding + line)

        print()

        for line in second_row:
            print(line)

    def check_for_blackjack(self, player: BlackjackPlayer) -> bool:
        if len(player.hand) > 2: return False

        if player.get_score() == 21:
            if any(card.value == "Ace" for card in player.hand):
                print_style(f"{player.name} has blackjack! We have a winner!", GREEN)
                return True

        return False

    def do_turns(self) -> bool:
        # Let each player in order (clockwise) play based on their hand, if a player busts, they are out so remove them from the play order
        for player in reversed(self.players):
            if player.busted: continue # Skip busted players

            print_style(f"{player.name}'s Turn", GREEN)
            time.sleep(0.5)

            if player.name == "Dealer":
                # If all players busted, dealer wins
                if all(player.busted for player in self.players[1:]):
                    print_style(f"Everyone busted, the dealer wins!", GREEN)
                    return True
                
                self.hand[0].flip()
                self.render_board()
                print_style("Dealer flipped card", GREEN)

            # Players keep making decisions until they stand or bust
            while not player.busted:
                hit = player.take_turn()
                time.sleep(0.5)

                if not hit:
                    print_style(f"{player.name} chose to stand", GREEN)
                    time.sleep(0.5)
                    break

                print_style(f"{player.name} chose hit, dealing card...", GREEN)
                self.deal_card(player)
                new_score = player.get_score()

                if new_score > 21:
                    player.busted = True
                    if player.name == "Dealer":
                        print_style(f"{player.name} busted, everyone remaining wins!", GREEN)
                        return True

                    print_style(f"{player.name} busted, they are out of the game", GREEN)

        return False

    def take_turn(self):
        if self.get_score() < 16:
            return True
        else: 
            return False

    def get_winners_from_points(self):
        winners = []
        max_score = max(player.get_score() for player in self.players)

        for player in self.players:
            if player.get_score() == max_score:
                winners.append(player.__str__())

        return winners

from blackjack.manager import BlackjackManager
from solitaire.manager import SolitaireManager



def main():
    human = input("What is your name?: ")
    manager = None

    # Keep asking until we get a game that can actually be played
    while manager is None:
        game = input("What game would you like to play? (Blackjack (1, b) or Solitaire (2, s)): ").lower()

        if game in ["1", "b"]:
            manager = BlackjackManager(human, 2)
        elif game in ["2", "s"]:
            manager = SolitaireManager(human)
        else:
            print("Sorry, try again")

    gaming = True

    while gaming:
        gaming = manager.run_game()

    print("Thanks for playing!")

main()
import sys
import json

import pygame
pygame.init()

import board

def main():

    with open("decks/brightsdeck.json", 'r', encoding='utf-8') as f:
        d = json.load(f)
    
    player1 = board.Player.from_deck_dict(d)
    player2 = board.Player.from_deck_dict(d)

    itf = board.Board((1000, 800), player1, player2)

    player1.hand.extend(player1.draw(4))
    player2.hand.extend(player2.draw(4))

    player1.set_dimensions((1000, 800))
    player2.set_dimensions((1000, 800))

    itf.run_game()

if __name__ == "__main__":
    main()
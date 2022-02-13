import sys
import json

import pygame

import board, pkmn

with open("assets/data/pkmn.json", 'r', encoding='utf-8') as f:
    PKMN = json.load(f)

def main():
    clock = pygame.time.Clock()

    p = pkmn.Pokemon.from_dict(PKMN['fs196sliggoo'])
    p2 = pkmn.Pokemon.from_dict(PKMN['fs117galariancorsola'])
    p3 = pkmn.Pokemon.from_dict(PKMN['fs195goomy'])
    deck = [p.build_unit() for _ in range(15)] + \
           [p3.build_unit() for _ in range(15)] + \
           [pkmn.Energy("psychic") for _ in range(5)] + \
           [pkmn.Energy("water") for _ in range(5)]
    player = board.Player(deck)
    player.shuffle()

    itf = board.Board((1000, 800), player, player)

    player.hand.extend(player.draw(4))
    
    player.front_line[0] = p3.build_unit()
    # player.front_line[1] = p.build_unit()
    player.front_line[3] = p.build_unit()
    player.set_dimensions((1000, 800))

    itf.run_game()

if __name__ == "__main__":
    main()
import sys
import json

import pygame

import board, pkmn

with open("assets/data/pkmn.json", 'r', encoding='utf-8') as f:
    PKMN = json.load(f)

def main():
    clock = pygame.time.Clock()

    p = pkmn.Pokemon.from_dict(PKMN['fs196sliggoo'])
    player = board.Player([p.build_unit() for _ in range(39)])
    itf = board.Board((1000, 800), player, player)

    player.hand.extend(player.draw(4))
    
    player.front_line[0] = p.build_unit()
    player.front_line[1] = p.build_unit()
    player.front_line[2] = p.build_unit()
    player.front_line[3] = p.build_unit()
    player.set_dimensions((1000, 800))

    itf.run_game()

if __name__ == "__main__":
    main()
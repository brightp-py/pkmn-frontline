import sys
import json

import pygame

import board, pkmn

with open("assets/data/pkmn.json", 'r', encoding='utf-8') as f:
    PKMN = json.load(f)

def main():
    clock = pygame.time.Clock()

    itf = board.Board((1600, 1000))
    p = pkmn.Pokemon.from_dict(PKMN['fs196sliggoo'])
    player = board.Player([p.build_unit() for _ in range(39)])
    player.front_line[0] = p.build_unit()
    player.front_line[1] = p.build_unit()
    player.front_line[2] = p.build_unit()
    player.front_line[3] = p.build_unit()
    player.set_dimensions((1600, 1000))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                itf.screen = pygame.display.set_mode(
                    (event.w, event.h),
                    pygame.RESIZABLE
                )
                try:
                    player.set_dimensions((event.w, event.h))
                except Exception as e:
                    print(e)
        
        itf.screen.fill((234, 242, 239))
        player.render(itf.screen, (0, 0))
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
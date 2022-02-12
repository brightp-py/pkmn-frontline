import sys
import json

import pygame

import board, pkmn

with open("assets/data/pkmn.json", 'r', encoding='utf-8') as f:
    PKMN = json.load(f)

def main():
    clock = pygame.time.Clock()

    background = pygame.image.load('assets/img/roman_battlefield.jpg')
    background = pygame.transform.rotate(background, 90)
    bg_w, bg_h = background.get_size()
    bg_x, bg_y = 800-(bg_w // 2), 500-(bg_h // 2)

    itf = board.Board((1600, 1000))
    p = pkmn.Pokemon.from_dict(PKMN['fs196sliggoo'])
    card = p.build_unit()
    cardback = pkmn.Card.cardback()

    D = 89
    H = 240

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        # itf.screen.blit(background, (bg_x, bg_y))
        itf.screen.fill((234, 242, 239))
        card.render(itf.screen, (800-5*D, 640, H, H), True)
        card.render(itf.screen, (800-3*D, 640, H, H), True)
        card.render(itf.screen, (800-D, 640, H, H), True)
        card.render(itf.screen, (800+D, 640, H, H), True)
        card.render(itf.screen, (800+3*D, 640, H, H), True)
        card.render(itf.screen, (800+5*D, 640, H, H), True)

        card.render(itf.screen, (800-5*D, 360, H, H), True)
        card.render(itf.screen, (800-3*D, 360, H, H), True)
        card.render(itf.screen, (800-D, 360, H, H), True)
        card.render(itf.screen, (800+D, 360, H, H), True)
        card.render(itf.screen, (800+3*D, 360, H, H), True)
        card.render(itf.screen, (800+5*D, 360, H, H), True)

        cardback.render(itf.screen, (1460, 620, H, H), True)
        cardback.render(itf.screen, (1460, 870, H, H), True)

        cardback.render(itf.screen, (140, 670, H, H), True)
        cardback.render(itf.screen, (140, 730, H, H), True)
        cardback.render(itf.screen, (140, 790, H, H), True)
        cardback.render(itf.screen, (140, 850, H, H), True)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
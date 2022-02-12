import random

import pygame
from pyrsistent import discard

import pkmn

class Player:

    def __init__(self, deck):
        """Create an instance of a Player.

        Parameters:

            deck - list of Card objects.
        """
        self.deck = deck
        self.prize_cards = self.draw(round(len(deck)/10))
        self.hand = []
        self.discard_pile = []
        self.front_line = [None, None, None, None]

        self._deck_rect = (0, 0, 0, 0)

    
    def shuffle(self):
        """Shuffle the player's deck."""
        random.shuffle(self.deck)

    def draw(self, num):
        """Create a list of Card objects from drawn from the deck.

        Parameters:

            num - int representing number of cards to be drawn.
        """
        toret = self.deck[:num]
        self.deck = self.deck[num:]
        return toret
    
    def set_dimensions(self, size):
        """Fit the player's field to the given size.

        Parameters:

            size - (width, height) of entire screen.
        """
        W, H = size
        if W / H > 1.3:
            W = H * 1.3
        elif H > W:
            H = W
        self._card_h = H * 4 // 18
        self._kern_h = H * 0.4 // 18
        self._card_w = W * 3 // 22
        self._kern_w = W * 0.4 // 22

        self._center = (size[0] // 2, size[1] // 2)
    
    def render(self, screen, mouse_pos):
        """Render this player's field onto the screen.

        Parameters:

            screen    - pygame.Surface to draw onto.

            mouse_pos - (x, y) of mouse position, for interactive elements.
        """
        deck_x = self._center[0] + 2 * self._card_w + int(2.5 * self._kern_w)
        deck_y = self._center[1] + self._kern_h // 2
        discard_y = deck_y + self._card_h + self._kern_h

        fl_x = self._center[0] - int(1.5 * self._kern_w) - 2 * self._card_w
        fl_y = self._center[1] + self._kern_h

        pc_x = self._center[0] - 3 * self._card_w - int(2.5 * self._kern_w)
        pc_y = deck_y

        pkmn.CARDBACK.render(screen,
            (deck_x, deck_y, self._card_w, self._card_h))
        pkmn.CARDBACK.render(screen,
            (deck_x, discard_y, self._card_w, self._card_h))
        
        for card in self.front_line:
            if card:
                card.render(screen,
                    (fl_x, fl_y, self._card_w, self._card_h))
            fl_x += self._card_w + self._kern_w
        
        for card in self.prize_cards:
            pkmn.CARDBACK.render(screen, 
                                 (pc_x, pc_y, self._card_w, self._card_h))
            pc_y += 3 * self._kern_h


class Board:

    def __init__(self, size):
        self._w, self._h = size
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)

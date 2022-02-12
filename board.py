import random

import pygame

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


class Board:

    def __init__(self, size):
        self._w, self._h = size
        self.screen = pygame.display.set_mode(size)

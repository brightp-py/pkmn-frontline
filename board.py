import sys
import random

import pygame

import pkmn

BACKGROUND = (234, 242, 239)

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

        self._deck_card = pkmn.Card.cardback()
    
    def _get_hand_coords(self):
        """Generate coordinates for drawing cards in hand.

        Returns:
            hand_width - Width of the entire hand (including white space).
            hand_start - x-position of left-most card.
            hand_gap   - Horizontal distance between card starts.
            hand_y     - y-position of all cards.
        """
        if len(self.hand) > 4:
            hand_width = 4 * self._card_w + 3 * self._kern_w
            hand_start = self._center[0] - (hand_width // 2)
            hand_gap = (hand_width - self._card_w) / (len(self.hand) - 1)
        else:
            hand_width = len(self.hand) * self._card_w
            hand_start = self._center[0] - (hand_width // 2)
            hand_gap = self._card_w

        hand_y = self._center[1] + int(1.5 * self._card_h)

        return hand_start, hand_gap, hand_y
    
    def _on_hand_loc(self, screen, mouse_pos):
        """Return True if the mouse cursor is on the user's hand."""
        hand_start, _, hand_y = self._get_hand_coords()
        return mouse_pos[0] >= hand_start and \
               mouse_pos[0] <= screen.get_width() - hand_start and \
               mouse_pos[1] > hand_y
    
    def _selected_from_hand(self, hand_start, hand_gap, mouse_pos):
        """Decide which card in the hand is currently selected.
        
        Parameters:

            hand_start - x position of left-most card in hand.

            hand_gap   - Horizontal distance between cards.

            mouse_pos  - (x, y) of mouse cursor.
        """
        selected = int((mouse_pos[0] - hand_start) // hand_gap)
        if selected < 0:
            selected = 0
        elif selected >= len(self.hand):
            selected = len(self.hand) - 1
        return selected
    
    def _selected_from_front_line(self, mouse_pos):
        """Decide which card in the front line is current selected.
        
        Paramters:
            mouse_pos - (x, y) of mouse cursor.
        """
        fl_x = self._center[0] - int(1.5 * self._kern_w) - 2 * self._card_w
        fl_y = self._center[1] + self._kern_h
        fl_gap = self._card_w + self._kern_w

        x, y = mouse_pos
        if y < fl_y or y > fl_y + self._card_h:
            return None

        selected = int((x - fl_x) // fl_gap)
        if 0 <= selected and selected < len(self.front_line):
            return selected
        
        return None
    
    def _card_to_front_line(self, card, position):
        """Place a card on the front line, either playing, evolving, or adding.

        Parameters:

            card - Card object to be put on the front line.

            position - int between 0 and len(front line)-1.
        """
        placement = card.placement()
        if placement == "basic":
            self.front_line[position] = card
        elif placement == "evolved":
            self.front_line[position].evolve_into(card)
            self.front_line[position] = card
        elif placement == "energy":
            self.front_line[position].attach(card)
            self.front_line[position].add_energy(card)
    
    def _place_card(self, screen, check_event, opponent, card):
        """Place the provided card somewhere on the frontline.

        Parameters:

            screen - Pygame Surface to draw on.

            card   - Card object to place.
        
        Returns:
            True if card was successfully place, False otherwise.
        """
        placement = card.placement()
        if placement == "basic":
            valid = [i for i in range(4) if self.front_line[i] is None]
        elif placement == "evolved":
            valid = [i for i in range(4) 
                        if self.front_line[i] and 
                           card.evolves_from(self.front_line[i])]
        elif placement == "energy":
            valid = [i for i in range(4) if self.front_line[i]]
        else:
            return False
        
        if not valid:
            return False
        
        opposing_ss = opponent.get_opposing_snapshot(screen.get_size())
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if check_event(event) == pygame.VIDEORESIZE:
                    opposing_ss = opponent.get_opposing_snapshot(
                        screen.get_size())
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    selected = self._selected_from_front_line(mouse_pos)
                    if selected is not None and selected in valid:
                        self._card_to_front_line(card, selected)
                        return True

                screen.fill(BACKGROUND)
                screen.blit(opposing_ss, (0, 0))
                self.render(screen)
                card.render(screen,
                            (
                                self._center[0],
                                self._center[1] // 2,
                                self._center[1],
                                self._center[1]
                            ),
                            centered=True)
                pygame.display.flip()
                pygame.time.Clock().tick(30)
    
    def choose_action(self, screen, check_event, opponent):
        opposing_ss = opponent.get_opposing_snapshot(screen.get_size())
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if check_event(event) == pygame.VIDEORESIZE:
                    opposing_ss = opponent.get_opposing_snapshot(
                        screen.get_size())
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self._on_hand_loc(screen, mouse_pos):
                        start, gap, _ = self._get_hand_coords()
                        selected = self._selected_from_hand(start, gap,
                                                            mouse_pos)
                        card = self.hand[selected]
                        if self._place_card(screen, check_event, opponent,
                                            card):
                            del self.hand[selected]
                    elif self._deck_card.contains_point(mouse_pos):
                        card = self.draw(1)
                        self.hand.extend(card)

            mouse_pos = pygame.mouse.get_pos()
            screen.fill(BACKGROUND)
            screen.blit(opposing_ss, (0, 0))
            self.render(screen)
            self.render_hand(screen, mouse_pos)
            pygame.display.flip()
            pygame.time.Clock().tick(30)

    
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
    
    def render(self, screen):
        """Render this player's field onto the screen.

        Parameters:

            screen    - pygame.Surface to draw onto.
        """
        deck_x = self._center[0] + 2 * self._card_w + int(2.5 * self._kern_w)
        deck_y = self._center[1] + self._kern_h // 2
        discard_y = deck_y + self._card_h + self._kern_h

        fl_x = self._center[0] - int(1.5 * self._kern_w) - 2 * self._card_w
        fl_y = self._center[1] + self._kern_h

        pc_x = self._center[0] - 3 * self._card_w - int(2.5 * self._kern_w)
        pc_y = deck_y + self._kern_h

        self._deck_card.render(screen,
            (deck_x, deck_y, self._card_w, self._card_h))
        pkmn.CARDBACK.render(screen,
            (deck_x, discard_y, self._card_w, self._card_h))
        
        for card in self.front_line:
            if card:
                card.render_with_energy(screen,
                    (fl_x, fl_y, self._card_w, self._card_h))
            fl_x += self._card_w + self._kern_w
        
        for card in self.prize_cards:
            pkmn.CARDBACK.render(screen, 
                                 (pc_x, pc_y, self._card_w, self._card_h))
            pc_y += 3 * self._kern_h
    
    def get_opposing_snapshot(self, size):
        """Create a pygame.Surface image of this player as the opponent."""
        surface = pygame.Surface(size)
        surface.fill(BACKGROUND)
        self.render(surface)

        hand_start, hand_gap, hand_y = self._get_hand_coords()

        for _ in self.hand:
            pkmn.CARDBACK.render(surface,
                                 (hand_start, hand_y,
                                  self._card_w, self._card_h))
            hand_start += hand_gap
        
        return pygame.transform.rotate(surface, 180)
    
    def render_hand(self, screen, mouse_pos):
        hand_start, hand_gap, hand_y = self._get_hand_coords()

        if self._on_hand_loc(screen, mouse_pos):
            selected = self._selected_from_hand(hand_start, hand_gap,
                                                mouse_pos)
            
            hand_x = hand_start
            for i, card in enumerate(self.hand):
                if i != selected:
                    card.render(screen,
                                (hand_x, hand_y, self._card_w, self._card_h))
                hand_x += hand_gap
            
            self.hand[selected].render(screen,
                (
                    hand_start + hand_gap * selected,
                    hand_y - (self._card_h // 3),
                    self._card_w, self._card_h
                ))

        else:
            hand_x = hand_start
            for card in self.hand:
                card.render(screen,
                            (hand_x, hand_y, self._card_w, self._card_h))
                hand_x += hand_gap


class Board:

    def __init__(self, size, player1, player2):
        self._w, self._h = size
        self._screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        self._p1 = player1
        self._p2 = player2
    
    def _check_event(self, event):
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            self._screen = pygame.display.set_mode((event.w, event.h),
                                                   pygame.RESIZABLE)
            self._p1.set_dimensions((event.w, event.h))
            self._p2.set_dimensions((event.w, event.h))
            return pygame.VIDEORESIZE
    
    def run_game(self):
        while True:
            for event in pygame.event.get():
                self._check_event(event)
            self._p1.choose_action(self._screen, self._check_event, self._p2)
            self._p2.choose_action(self._screen, self._check_event, self._p1)

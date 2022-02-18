import sys
import random

import pygame
pygame.init()

import pkmn
from ui import TextBox, Button

BACKGROUND = (234, 242, 239)

class Player:

    def __init__(self, deck):
        """Create an instance of a Player.

        Parameters:

            deck - list of Card objects.
        """
        self.deck = deck
        self.shuffle()
        self.prize_cards = self.draw(round(len(deck)/10))
        self.hand = []
        self.discard_pile = []
        self.front_line = [None, None, None, None]

        self._deck_card = pkmn.Card.cardback()
    
    @staticmethod
    def from_deck_dict(d):
        """Create an instance of a Player with the given dict as a deck.
        
        Parameters:
            d - dict with attributes "name", "energy", "pokemon"
        """
        deck = []
        for name in d['pokemon']:
            p = pkmn.Pokemon.from_id(name)
            for _ in range(d['pokemon'][name]):
                deck.append(p.build_unit())
        for energy in d['energy']:
            for _ in range(d['energy'][energy]):
                deck.append(pkmn.Energy(energy))
        return Player(deck)
    
    def _focus_on(self, screen, card):
        """Display the given Card as big as possible on the top half."""
        card.render(screen,
                    (
                        self._center[0],
                        self._center[1] // 2,
                        self._center[1],
                        self._center[1]
                    ),
                    centered=True)
    
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
    
    def _discard_front_line(self, i):
        """Discard the card at the given spot of the front line, with attached.
        
        Parameters:
            i - Index of card in front line.
        """
        card = self.front_line[i]
        stowaways = card.detach()
        self.discard_pile.extend(stowaways)
        self.discard_pile.append(card)
        self.front_line[i] = None
    
    def front_line_screen(self, screen, check_event, opponent, valid,
                          card=None, help_text=None, text_on_top=False):
        """Let the user selected one of the front line slots.
        
        Returns the index of the slot selected, or None if bailed out.
        """
        if help_text:
            textbox = TextBox(help_text)
            screen_w, screen_h = screen.get_size()
            if screen_w > screen_h:
                text_l = screen_h
                text_x = (screen_w - text_l) // 2
            else:
                text_l = screen_w
                text_x = 0
            if text_on_top:
                text_y = 0
            else:
                text_y = screen_h - (text_l // 5)

        opposing_ss = opponent.get_opposing_snapshot(screen.get_size())
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if check_event(event) == pygame.VIDEORESIZE:
                    opposing_ss = opponent.get_opposing_snapshot(
                        screen.get_size())
                    if help_text:
                        screen_w, screen_h = screen.get_size()
                        if screen_w > screen_h:
                            text_l = screen_h
                            text_x = (screen_w - text_l) // 2
                        else:
                            text_l = screen_w
                            text_x = 0
                        if text_on_top:
                            text_y = 0
                        else:
                            text_y = screen_h - (text_l // 5)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    selected = self._selected_from_front_line(mouse_pos)
                    if selected is not None and selected in valid:
                        return selected

                screen.fill(BACKGROUND)
                screen.blit(opposing_ss, (0, 0))
                self.render(screen)
                if card:
                    self._focus_on(screen, card)
                if help_text:
                    textbox.render(screen, (text_x, text_y, text_l, text_l//5),
                                   do_title=False)
                pygame.display.flip()
                pygame.time.Clock().tick(30)

    def front_line_opponent(self, screen, check_event, opponent, valid,
                            card=None, help_text=None, text_on_top=False):
        """Let the user selected one of the opponent's front line slots.
        
        Returns the index of the slot selected, or None if bailed out.
        """
        if help_text:
            textbox = TextBox(help_text)
            screen_w, screen_h = screen.get_size()
            if screen_w > screen_h:
                text_l = screen_h
                text_x = (screen_w - text_l) // 2
            else:
                text_l = screen_w
                text_x = 0
            if text_on_top:
                text_y = 0
            else:
                text_y = screen_h - (text_l // 5)
        
        opposing_ss = opponent.get_opposing_snapshot(screen.get_size())
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if check_event(event) == pygame.VIDEORESIZE:
                    opposing_ss = opponent.get_opposing_snapshot(
                        screen.get_size())
                    if help_text:
                        screen_w, screen_h = screen.get_size()
                        if screen_w > screen_h:
                            text_l = screen_h
                            text_x = (screen_w - text_l) // 2
                        else:
                            text_l = screen_w
                            text_x = 0
                        if text_on_top:
                            text_y = 0
                        else:
                            text_y = screen_h - (text_l // 5)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    selected = self._selected_from_front_line(
                        (screen.get_width()-mouse_pos[0],
                        screen.get_height()-mouse_pos[1])
                    )
                    if selected is not None and selected in valid:
                        return selected

                screen.fill(BACKGROUND)
                screen.blit(opposing_ss, (0, 0))
                self.render(screen)
                if card:
                    self._focus_on(screen, card)
                if help_text:
                    textbox.render(screen, (text_x, text_y, text_l, text_l//5),
                                   do_title=False)
                pygame.display.flip()
                pygame.time.Clock().tick(30)
    
    def _place_card(self, screen, check_event, opponent, card):
        """Place the provided card somewhere on the frontline.

        Parameters:

            screen - Pygame Surface to draw on.

            card   - Card object to place.
        
        Returns:
            True if card was successfully placed, False otherwise.
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

        selected = self.front_line_screen(screen, check_event, opponent, valid,
                                          card)
        if selected is None:
            return False
        self._card_to_front_line(card, selected)
        return True
    
    def _pkmn_action(self, screen, check_event, opponent, fl_space):
        """Choose between attack, move, or retreat for the selected Pokemon.

        Parameters:
            fl_space - int of front line slot chose, between 0 and len(fl)-1.
        
        Returns True if successfully executed, False otherwise.
        """
        opposing_ss = opponent.get_opposing_snapshot(screen.get_size())
        card = self.front_line[fl_space]

        if card.affliction() == "asleep":
            options = ["Wake up\n\nAttempt to wake up this Pokemon, removing"
                       " its 'asleep' affliction. Has a 50% chance of success."
                       ]
        else:
            options = [
                "Move\n\nMove this Pokemon to an open space.\n\nThis action"
                " cannot be taken two turns in a row.",
                "Retreat\n\nMove this Pokemon to an open space or switch it"
                " with another active Pokemon."
            ]
            options.extend(card.move_texts())

        current = 0
        textbox = TextBox(options[0])

        def r_click():
            nonlocal current
            current += 1
            current = current % len(options)
            textbox.set_text(options[current])
        
        def l_click():
            nonlocal current
            current -= 1
            current = current % len(options)
            textbox.set_text(options[current])
        
        def ok_click():
            nonlocal current

            if card.affliction() == "asleep":   # WAKE UP
                if random.randint(0, 1):
                    card.afflict(None)
                return True

            elif current == 0:  # MOVE
                valid = [i for i in range(len(self.front_line))
                            if self.front_line[i] is None]
                if not valid:
                    return False
                selected = self.front_line_screen(screen, check_event,
                                                   opponent, valid, card)
                if selected is None:
                    return False
                self.front_line[fl_space], self.front_line[selected] = \
                    self.front_line[selected], self.front_line[fl_space]
                return True
            
            elif current == 1:  # RETREAT
                if not card.sufficient_energy(card.retreat_energy()):
                    return False
                cost = card.retreat_cost()
                valid = [i for i in range(len(self.front_line)) if
                            self.front_line[i] is None or
                            self.front_line[i].retreat_cost() <= cost]
                if not valid:
                    return False
                selected = self.front_line_screen(screen, check_event,
                                                   opponent, card, valid)
                if selected is None:
                    return False
                self.front_line[fl_space], self.front_line[selected] = \
                    self.front_line[selected], self.front_line[fl_space]
                to_hand = card.discard_energy(card.retreat_energy())
                self.hand.extend(to_hand)
                return True
            
            else:               # ATTACK
                move_id = current - 2
                if not card.can_use_move(move_id):
                    return False
                target = opponent.opposite_space(fl_space)
                to_hand = card.attack(move_id, target, self, opponent,
                                      fl_space, screen, check_event)
                self.hand.extend(to_hand)
                opponent.remove_fainted()
                self.remove_fainted()
                return True

        arrow_img = pygame.image.load("assets/img/arrow.png")
        use_img = pygame.image.load("assets/img/use_button.png")

        r_button = Button(arrow_img, r_click)
        l_button = Button(pygame.transform.rotate(arrow_img, 180), l_click)
        ok_button = Button(use_img)

        screen_w, screen_h = screen.get_size()
        if screen_w > screen_h:
            length = screen_h
            x = (screen_w - length) // 2
            y = screen_h // 2
            button_y = screen_h
        else:
            length = screen_w
            x = 0
            y = screen_h // 2
            button_y = y + length // 2
        button_l = length // 15

        while True:
            for event in pygame.event.get():
                if check_event(event) == pygame.VIDEORESIZE:
                    opposing_ss = opponent.get_opposing_snapshot(
                        screen.get_size())
                    screen_w, screen_h = screen.get_size()
                    if screen_w > screen_h:
                        length = screen_h
                        x = (screen_w - length) // 2
                        y = screen_h // 2
                        button_y = screen_h
                    else:
                        length = screen_w
                        x = 0
                        y = screen_h // 2
                        button_y = y + length // 2
                    button_l = length // 10
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    l_button.check_pressed(mouse_pos)
                    r_button.check_pressed(mouse_pos)
                    if ok_button.check_pressed(mouse_pos):
                        if ok_click():
                            return True
                    if not textbox.contains(mouse_pos):
                        return False
            
            screen.fill(BACKGROUND)
            screen.blit(opposing_ss, (0, 0))
            self.render(screen)
            self._focus_on(screen, card)
            textbox.render(screen, (x, y, length, length // 2))
            l_button.render(screen, (x, button_y-button_l, button_l, button_l))
            r_button.render(screen,
                            (
                                x+length-button_l,
                                button_y-button_l,
                                button_l, button_l
                            ))
            ok_button.render(screen,
                             (
                                x+(length-button_l)//2,
                                button_y-button_l,
                                button_l, button_l
                             ))
            pygame.display.flip()
            pygame.time.Clock().tick(30)
    
    def receive_attack(self, screen, check_event, damage, user, _):
        """Roll a d10, and if the result is less than damage, do prize card.

        Parameters:

            damage - Chance that this attack hits.

            user   - Player object dealing the damage.
        """
        if damage == 0:
            return False
        
        choices = [f"{str(i)}0" for i in range(10)]
        defense = "00"

        roll_speed = 40
        roll_count = 0
        roll_peak = 30
        roll_diff = 0.5

        opposing_ss = self.get_opposing_snapshot(screen.get_size())

        textbox = TextBox("\n" + defense)
        width = 100
        height = 80
        x, y = self._center[0] - (width // 2), self._center[1] - (height // 2)

        while True:
            for event in pygame.event.get():
                if check_event(event) == pygame.VIDEORESIZE:
                    opposing_ss = self.get_opposing(screen.get_size())
                    x = self._center[0] - (width // 2)
                    y = self._center[1] - (height // 2)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if roll_speed <= 0:
                        if int(defense) < damage:
                            user.win_prize_card()
                        return
            
            if roll_speed > 0:
                roll_speed -= roll_diff
                roll_count += roll_speed
                if roll_count > roll_peak:
                    roll_count = 0
                    defense = random.choice(choices)
                    textbox.set_text("\n" + defense)
            
            screen.fill(BACKGROUND)
            screen.blit(opposing_ss, (0, 0))
            user.render(screen)
            textbox.render(screen, (x, y, width, height), centered=True)
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

                    # ATTACK, MOVE, or RETREAT
                    fl_space = self._selected_from_front_line(mouse_pos)
                    if fl_space is not None and \
                       self.front_line[fl_space] is not None:
                        if self._pkmn_action(screen, check_event, opponent,
                                          fl_space):
                            return
                        opposing_ss = opponent.get_opposing_snapshot(
                            screen.get_size())

                    # PLAY, EVOLVE, or ATTACH
                    elif self._on_hand_loc(screen, mouse_pos):
                        start, gap, _ = self._get_hand_coords()
                        selected = self._selected_from_hand(start, gap,
                                                            mouse_pos)
                        if selected is None:
                            continue
                        card = self.hand[selected]
                        if self._place_card(screen, check_event, opponent,
                                            card):
                            del self.hand[selected]
                            return
                        opposing_ss = opponent.get_opposing_snapshot(
                            screen.get_size())

                    # DRAW
                    elif self._deck_card.contains_point(mouse_pos):
                        card = self.draw(1)
                        self.hand.extend(card)
                        opposing_ss = opponent.get_opposing_snapshot(
                            screen.get_size())
                        return

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
    
    def win_prize_card(self):
        """Move the top prize card from its place to the hand."""
        self.hand.append(self.prize_cards[0])
        self.prize_cards = self.prize_cards[1:]
    
    def opposite_space(self, i):
        """Return the card that opposes the unit at position i.

        Parameters:
            i - Position of other Player's Pokemon (0-4).
        """
        i = 3 - i
        card = self.front_line[i]
        if card is None:
            return self
        return card

    def remove_fainted(self):
        """Remove any Pokemon on the front line that have fainted."""
        for i, card in enumerate(self.front_line):
            if card and card.is_fainted():
                self._discard_front_line(i)
    
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
            self._p1.choose_action(self._screen, self._check_event, self._p2)
            if not self._p1.prize_cards:
                print("Player 1 wins!")
                break
            self._p2.choose_action(self._screen, self._check_event, self._p1)
            if not self._p2.prize_cards:
                print("Player 2 wins!")
                break

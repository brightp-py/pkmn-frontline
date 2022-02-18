import os
import json
from collections import defaultdict
from functools import lru_cache

import pygame
pygame.init()

from moves import move_by_id

with open("assets/energy/tiles.json", 'r', encoding='utf-8') as f:
    ENERGY_TILE_DATA = json.load(f)
ENERGY_TILES = pygame.image.load("assets/energy/tiles.png")

PKMN = {}
with open("assets/data/pkmn_fs.json", 'r', encoding='utf-8') as f:
    PKMN |= json.load(f)

@lru_cache(128)
def fit_within(outer, inner):
    """Fit the inner rect within the outer, maintaining width/height ratios.

    Parameters:
        outer - (x, y, w, h) representing outer rectangle.
        inner - (w, h) representing inner rectangle's dimensions.
    
    Returns:
        (x, y, w, h) representing inner rectangle's new position and area.
    """
    x1, y1, w1, h1 = outer
    w2, h2 = inner
    if w1 / h1 > w2 / h2:   # white space on left/right edges
        h = h1
        w = (w2 * h1) // h2
        y = y1
        x = x1 + (w1 - w) // 2
    else:                   # white space on top/bottom edges
        w = w1
        h = (h2 * w1) // w2
        x = x1
        y = y1 + (h1 - h) // 2
    return x, y, w, h


@lru_cache(32)
def energy_orb(name, new_length):
    length = ENERGY_TILE_DATA['sidelength']
    surface = pygame.Surface((length, length), pygame.SRCALPHA, 32)
    offset = ENERGY_TILE_DATA[name]
    surface.blit(ENERGY_TILES, (-offset[0], -offset[1]))
    surface = pygame.transform.smoothscale(surface, (new_length, new_length))
    return surface


class Card:

    def __init__(self, image):
        self._orig_image = image
        self._image = image
        self._w, self._h = image.get_size()
        self._x, self._y = 0, 0

    @staticmethod
    def cardback():
        """Create a Card object of the cardback image.
        
        Generally, you should create one of these and re-use it for all
        card backs.
        """
        image = pygame.image.load("assets/card/cardback.png")
        return Card(image)
    
    def set_rect(self, x=None, y=None, w=None, h=None):
        """Set position and dimensions of this card.

        Each parameter is optional.

        Paramters:
            x - Horizontal position.
            y - Vertical position.
            w - Horizontal width.
            h - Vertical height.
        """
        if x is not None:
            self._x = x
        if y is not None:
            self._y = y
        if w is not None:
            self._w = w
        if h is not None:
            self._h = h
    
    def render(self, screen, rect, centered=False):
        """Draw this card's image on the given pygame Surface.
        
        Parameters:

            screen   - pygame.Surface to draw on.

            rect     - (x, y, w, h) the image will fit within.

            centered - If True, x and y represent the center of the image,
                       instead of the top-left corner.
        """
        if centered:
            rect = (rect[0]-rect[2]//2, rect[1]-rect[3]//2, rect[2], rect[3])
        x, y, w, h = fit_within(rect, self._orig_image.get_size())
        self._x, self._y = x, y
        if w != self._w and h != self._h:
            try:
                self._image = pygame.transform.smoothscale(self._orig_image,
                                                          (w, h))
            except ValueError:
                self._image = pygame.transform.scale(self._orig_image, (w, h))
            self._w, self._h = w, h
        screen.blit(self._image, (x, y))

    def contains_point(self, pos):
        """Return True if the given pos lies on this card.
        
        Parameters:
            pos - (x, y) of position.
        
        Ignores rounded corners of Pokemon cards and simply counts the hitbox
        as a rectangle.
        """
        x, y = pos
        return x >= self._x and x <= self._x + self._w and \
               y >= self._y and y <= self._y + self._h


class Energy(Card):
    NAMES = ["dark", "electric", "fairy", "fighting", "fire", "grass",
             "psychic", "steel", "water"]

    def __init__(self, name):
        super().__init__(pygame.image.load(f"assets/energy/{name}.png"))
        self._name = name
        self._placement = "energy"
    
    def name(self):
        """Get name attribute."""
        return self._name
    
    def placement(self):
        """Get placement attribute."""
        return self._placement


class Unit(Card):

    def __init__(self, name, image, hp, element, moves, retreat_cost,
                 weakness, resistance, abilities, pre_evo, attributes):
        super().__init__(image)
        self._name = name
        self._hp = hp
        self._max_hp = hp
        self._element = element
        self._moves = moves
        self._retreat_cost = retreat_cost
        self._weakness = weakness
        self._resistance = resistance
        self._abilities = abilities
        self._pre_evo = pre_evo
        self.attributes = attributes

        self._placement = "evolved" if self._pre_evo else "basic"
        self._attached = []

        self._energy = defaultdict(lambda: 0)
        self._affliction = None
    
    def name(self):
        """Get name attribute."""
        return self._name
    
    def element(self):
        """Get element attribute."""
        return self._element
    
    def moves(self):
        """Get moves attribute as a copy."""
        return self._moves[:]
    
    def energy(self):
        """Get energy attribute as a copy."""
        return self._energy.copy()
    
    def placement(self):
        """Get placement attribute."""
        return self._placement

    def retreat_cost(self):
        """Get retreat_cost attribute."""
        return self._retreat_cost
    
    def affliction(self):
        """Get affliction attribute."""
        return self._affliction
    
    def afflict(self, affliction):
        """Set affliction attributes."""
        if affliction is None:
            self._affliction = affliction
            return
        affliction = affliction.lower()
        if affliction in ("asleep", "burned", "confused", "paralyzed",
                          "poisoned"):
            self._affliction = affliction
    
    def retreat_energy(self):
        """Get a dict of {'colorless': retreat_cost}."""
        if not self._retreat_cost:
            return {}
        return {"colorless": self._retreat_cost}
    
    def move_texts(self):
        """Create a list of strings describing this Pokemon's moves."""
        return [str(move) for move in self._moves]
    
    def is_fainted(self):
        """Return True if this unit's health is 0 or lower."""
        return self._hp <= 0
    
    def attach(self, card):
        """Attach another card to this one.

        Parameters:
            card - Card that gets attached OR list of cards.
        
        Attached cards get discarded with this card.
        """
        if isinstance(card, Card):
            self._attached.append(card)
        elif isinstance(card, list):
            self._attached.extend(card)
    
    def add_energy(self, energy):
        """Attach some number of energies to this Pokemon.
        
        Parameters:
            energy - Card that gets attached OR dict of energies.
        """
        if isinstance(energy, Energy):
            self._energy[energy.name()] += 1
        elif isinstance(energy, dict):
            for name in energy:
                self._energy[name] += energy[name]
    
    def render_with_energy(self, screen, rect):
        """Draw this card on the screen with energy orbs.

        Parameters:

            screen - Pygame Surface to draw onto.

            rect   - (x, y, w, h)
        """
        self.render(screen, rect)
        x, y, w, h = fit_within(rect, (self._w, self._h))

        # energy orbs
        orb_len = w // 5
        orb_x = x
        orb_y = y + h
        a = 0
        for e in self._energy:
            img = energy_orb(e, orb_len)
            for _ in range(self._energy[e]):
                screen.blit(img, (orb_x, orb_y))
                orb_x += orb_len
                a += 1
                if a > 4:
                    a = 0
                    orb_x -= 5 * orb_len
                    orb_y += orb_len
        
        # health bar
        colors = {
            'paralyzed': (245, 245, 0),
            'asleep': (245, 245, 245),
            'poisoned': (125, 0, 140),
            'confused': (0, 245, 245),
            'burned': (245, 125, 0)
        }
        if self._affliction is not None:
            color = colors[self._affliction]
        else:
            color = (0, 245, 0)
        bar_w = (4 * w) // 5
        green_w = (bar_w * self._hp) // self._max_hp
        x, y = x + (w // 10), y + (h // 10)
        bar_h = h // 20
        pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_w, bar_h))
        pygame.draw.rect(screen, color, (x, y, green_w, bar_h))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_w, bar_h), 2)
    
    def sufficient_energy(self, energy):
        """Check if this unit has enough energy for some action.
        
        Parameters:
            energy - defaultdict of energies with elements as keys and amounts
                     as values.
        
        Returns:
            True if sufficient, False otherwise.
        """
        if "colorless" in energy:
            colorless_needed = energy["colorless"]
        else:
            colorless_needed = 0
        for e in Energy.NAMES:
            if e in energy:
                if energy[e] > self._energy[e]:
                    return False
                else:
                    colorless_needed -= self._energy[e] - energy[e]
            elif e in self._energy:
                colorless_needed -= self._energy[e]
        return colorless_needed <= 0
    
    def can_use_move(self, move_index):
        """Return True if this unit has enough energy to use the given move.
        
        Parameters:
            move_index - int of move's index in self._moves.
        """
        move = self._moves[move_index]
        return self.sufficient_energy(move.energy())
    
    def apply_effectiveness(self, damage, element):
        """Modify the damage based on weakness and resistance.
        
        Parameters:
        
            damage  - int of damage before weakness/resistance is applied.

            element - str of the element of the attacking Pokemon.
        """
        if self._weakness and element == self._weakness[0]:
            damage = self._weakness[1](damage)
        elif self._resistance and element == self._resistance[0]:
            damage = self._resistance[1](damage)
        return damage
    
    def attack(self, move_index, target, user, opponent, fl_spot, screen,
               check_event):
        """Deal damage to the target and apply any secondary effects.

        Parameters:
        
            move_index - int of move's index in self._moves.

            target     - Card object being attacked.
        
            user       - Player object using the move.

            opponent   - Player object being attacked.

            screen     - Pygame Surface to draw on for extra effects.
        """
        move = self._moves[move_index]
        damage = move.damage()
        result = move.run(user, self, opponent, target, damage, fl_spot,
                          screen, check_event)
        if result is not None:
            damage = result
        target.receive_attack(screen, check_event, damage, user, self)
        return self.discard_energy(move.energy())
    
    def discard_energy(self, energy):
        """Remove energy cards from this Pokemon to be added to the discard.
        
        Parameters:
            energy - defaultdict of energies with elements as keys and amounts
                     as values.
        
        Returns:
            list of Card objects that were removed.
        """
        discarded = []
        nonenergy = []
        kept = []
        for att in self._attached:
            name = att.name()
            if isinstance(att, Energy) and name in energy and energy[name] > 0:
                discarded.append(att)
                energy[name] -= 1
                self._energy[name] -= 1
            elif isinstance(att, Energy):
                kept.append(att)
            else:
                nonenergy.append(att)
        for i in range(len(kept)-1, -1, -1):
            if "colorless" not in energy or energy["colorless"] < 1:
                break
            if kept[i].name() != self._element:
                energy["colorless"] -= 1
                self._energy[kept[i].name()] -= 1
                discarded.append(kept[i])
                del kept[i]
        for i in range(len(kept)-1, -1, -1):
            if "colorless" not in energy or energy["colorless"] < 1:
                break
            energy["colorless"] -= 1
            self._energy[kept[i].name()] -= 1
            discarded.append(kept[i])
            del kept[i]
        self._attached = nonenergy + kept
        return discarded
    
    def detach(self):
        """Remove all attached cards and return them."""
        self._energy = defaultdict(lambda: 0)
        toret = self._attached
        self._attached = []
        self._hp = self._max_hp
        return toret
    
    def evolves_from(self, other):
        """Return True if this Pokemon evolves from `other`."""
        return self._pre_evo == other.name()
    
    def evolve_into(self, card):
        """Evolve this basic or Stage 1 PKMN into the next stage.
        
        Parameters:
            card - Unit to pass energies onto.
        """
        card.attach(self._attached)
        card.attach(self)
        card.add_energy(self._energy)
        card.take_damage(self._max_hp - self._hp)
        self._hp = self._max_hp
    
    def take_damage(self, amount):
        """Subtract some amount of damage from this unit's hit points.

        If the unit faints from this damage, return True.
        """
        self._hp -= amount
        return self._hp <= 0
    
    def receive_attack(self, _, __, damage, ___, attacker):
        """Receive some damage from an attack.

        This needs to be separate from `take_damage` because certain Pokemon
        have abilities that activate when being attacked, but not when taking
        damage in general.
        """
        damage = self.apply_effectiveness(damage, attacker.element())
        return self.take_damage(damage)


class Pokemon:

    def __init__(self, name, img_id, max_hp, element, moves, retreat_cost,
                 weakness=None, resistance=None, abilities = None,
                 pre_evo=None, attributes=None):
        """Initialize a type of Pokemon card.

        Attributes:
            name         - str of name as it appears in the top-left corner.
            img_id       - Name of image associated with card. (SET###)
            max_hp       - Starting hit points.
            element      - One of the PKMN TCG card elements.
            moves        - List of Move objects.
            retreat_cost - int of energies needed to retreat.
            weakness     - tuple of (element, lambda function to apply).
            resistance   - tuple of (element, lambda function to apply).
            abilities    - List of Ability objects. (To be implemented.)
            pre_evo      - Name of the Pokemon this Pokemon evolves from.
                           NONE for basic Pokemon.
        """
        self._name = name
        self._max_hp = max_hp
        self._element = element
        self._moves = moves
        self._retreat_cost = retreat_cost
        self._weakness = weakness
        self._resistance = resistance
        self._abilities = abilities
        self._pre_evo = pre_evo
        self.attributes = attributes

        self._img_id = img_id
        self._image = self.load_image(img_id)
    
    @staticmethod
    def from_id(name):
        """Create a new Pokemon object from its identification name.
        
        Parameters:
            name - str identifying the Pokemon, as it appears in pkmn.json.
        """
        return Pokemon.from_dict(PKMN[name])
    
    @staticmethod
    def from_dict(d):
        """Create a new Pokemon object from a given json dict.

        Parameters:
            d - dict with attributes "name", "max_hp", etc.
        
        Returns:
            Pokemon object with given properties
        """
        name = d['name']
        img_id = d['img_id']
        max_hp = d['max_hp']
        element = d['element']
        moves = [Move.from_dict(data) for data in d['moves']]
        retreat_cost = d['retreat_cost']
        
        weakness = None
        resistance = None
        abilities = []
        pre_evo = None
        attributes = {}
        
        if 'weakness' in d:
            weakness = (
                d['weakness']['element'],
                Pokemon._effectiveness_str_to_func(d['weakness']['lambda'])
            )
        if 'resistance' in d:
            resistance = (
                d['resistance']['element'],
                Pokemon._effectiveness_str_to_func(d['resistance']['lambda'])
            )
        if 'abilities' in d:
            pass    # TODO
        if 'pre_evo' in d:
            pre_evo = d['pre_evo']
        if 'attributes' in d:
            attributes = d['attributes']
        
        return Pokemon(name, img_id, max_hp, element, moves, retreat_cost,
                       weakness, resistance, abilities, pre_evo, attributes)
    
    @staticmethod
    def _effectiveness_str_to_func(s):
        """Convert a string showing weakness/resistance effect into a function.
        
        Parameters:
            s - str like "*2", "-30"
        """
        i = int(s[1:])
        o = s[0]
        if o in ['*', 'x']:
            return lambda x: x * i
        elif o == '-':
            return lambda x: x - i
        elif o == '/':
            return lambda x: x // i
        elif o == '+':
            return lambda x: x + i
        return lambda x: x

    def load_image(self, img_id):
        """Create a Pygame Surface object of the given file.

        Parameters:
            img_id - str of image name, EXCLUDING EXTENSION.

        Returns:
            Pygame Surface object.
        """
        if os.path.exists(f"assets/card/{img_id}.png"):
            filepath = f"assets/card/{img_id}.png"
        elif os.path.exists(f"assets/card/{img_id}.jpg"):
            filepath = f"assets/card/{img_id}.jpg"
        else:
            filepath = "assets/card/cardback.jpg"

        return pygame.image.load(filepath)

    def build_unit(self):
        """Create a new Unit object with this Pokemon's attributes."""
        return Unit(self._name, self._image, self._max_hp, self._element,
                    self._moves[:], self._retreat_cost, self._weakness,
                    self._resistance, self._abilities[:], self._pre_evo,
                    self.attributes.copy())


class Move:

    def __init__(self, name, energy, damage, effect, text=None, move_id=None):
        self._name = name
        self._energy = energy
        self._damage = damage
        self._effect = effect
        if text:
            self._text = text
        else:
            self._text = ""
        self._move_id = move_id
        self._move_f = move_by_id(move_id)
    
    def __str__(self):
        if self._text:
            return f"{self._name}\n{str(self._damage)} Damage\n\n{self._text}"
        return f"{self._name}\n{str(self._damage)} Damage"
    
    def name(self):
        """Return name attribute."""
        return self._name
    
    def damage(self):
        """Return damage attribute."""
        return self._damage
    
    def energy(self):
        """Return energy attribute."""
        return self._energy.copy()

    @staticmethod
    def from_dict(d):
        """Create a new Move object from data given in a dict.

        Parameters:
            d - dict with attributes "name", "energy", etc.
        
        Returns:
            Move object with given attributes.
        """
        name = d['name']
        energy = d['energy']
        damage = 0
        effect = []
        text = ""
        move_id = None

        if 'damage' in d:
            damage = d['damage']
        if 'effect' in d:
            effect = d['effect']
        if 'text' in d:
            text = d['text']
        if 'move_id' in d:
            move_id = d['move_id']
        
        return Move(name, energy, damage, effect, text, move_id)
    
    def run(self, user, attacker, opponent, target, damage, fl_spot, screen,
            check_event):
        """Run this move's special effects.
        
        Parameters:

            user     - Player object that owns Pokemon being played.

            attacker - Pokemon using this move.

            opponent - Player object receiving the attack.

            target   - Pokemon object being attacked.

            damage   - Starting damage before weakness/resistance.

            fl_spot  - int of which front line slot the attacker is in
        """
        if self._move_f:
            return self._move_f(user, attacker, opponent, target, damage,
                                fl_spot, screen, check_event)


CARDBACK = Card.cardback()

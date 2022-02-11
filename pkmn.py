import os
from collections import defaultdict

import pygame

class Card:

    def __init__(self, image):
        self._image = image


class Unit(Card):

    def __init__(self, name, image, hp, element, moves, retreat_cost,
                 weakness, resistance, abilities, pre_evo):
        super().__init__(image)
        self._name = name
        self._hp = hp
        self._element = element
        self._moves = moves
        self._retreat_cost = retreat_cost
        self._weakness = weakness
        self._resistance = resistance
        self._abilities = abilities
        self._pre_evo = pre_evo

        self._energies = defaultdict(lambda: 0)
        self._affliction = None
    
    def take_damage(self, amount):
        """Subtract some amount of damage from this unit's hit points.

        If the unit faints from this damage, return True.
        """
        self._hp -= amount
        return self._hp <= 0
    
    def receive_attack(self, damage):
        """Receive some damage from an attack.

        This needs to be separate from `take_damage` because certain Pokemon
        have abilities that activate when being attacked, but not when taking
        damage in general.
        """
        return self.take_damage(damage)


class Pokemon:

    def __init__(self, name, img_id, max_hp, element, moves, retreat_cost,
                 weakness=None, resistance=None, abilities = None,
                 pre_evo=None):
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
                         | NONE for basic Pokemon.
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

        self._img_id = img_id
        self._image = self.load_image(img_id)
    
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
        
        if 'weakness' in d:
            weakness = d['weakness']
        if 'resistance' in d:
            resistance = d['resistance']
        if 'abilities' in d:
            pass    # TODO
        if 'pre_evo' in d:
            pre_evo = d['pre_evo']
        
        return Pokemon(name, img_id, max_hp, element, moves, retreat_cost,
                       weakness, resistance, abilities, pre_evo)

    def load_image(self, img_id):
        """Create a Pygame Surface object of the given file.

        Parameters:
            img_id - str of image name, EXCLUDING EXTENSION.

        Returns:
            Pygame Surface object.
        """
        if os.path.exists(f"assets/file/{img_id}.png"):
            filepath = f"assets/file/{img_id}.png"
        elif os.path.exists(f"assets/file/{img_id}.jpg"):
            filepath = f"assets/file/{img_id}.jpg"
        else:
            filepath = "assets/file/cardback.jpg"

        return pygame.image.load(filepath)

    def build_unit(self):
        """Create a new Unit object with this Pokemon's attributes."""
        return Unit(self._name, self._image, self._max_hp, self._element,
                    self._moves[:], self._retreat_cost, self._weakness,
                    self._resistance, self._abilities[:], self._pre_evo)


class Move:

    def __init__(self, name, energy, damage, effect):
        self._name = name
        self._energy = energy
        self._damage = damage
        self._effect = effect

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
        damage = d['damage']
        effect = []

        if 'effect' in d:
            effect = d['effect']
        
        return Move(name, energy, damage, effect)
    
    def sufficient_energy(self, energy):
        """Check if the given energy is enough to use this move.
        
        Parameters:
            energy - defaultdict of energies with elements as keys and amounts
                   | as values.
        
        Returns:
            True if sufficient, False otherwise.
        """
        for e in self._energy:
            if energy[e] < self._energy[e]:
                return False
        return True

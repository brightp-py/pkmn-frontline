import os
from collections import defaultdict

import pygame

class Card:

    def __init__(self, image):
        self._image = image


class Unit(Card):

    def __init__(self, name, image, hp, element, moves, retreat_cost,
                 weakness, resistance, abilities):
        super().__init__(image)
        self._name = name
        self._hp = hp
        self._element = element
        self._moves = moves
        self._retreat_cost = retreat_cost
        self._weakness = weakness
        self._resistance = resistance
        self._abilities = abilities

        self._energies = defaultdict(lambda: 0)
        self._affliction = None
    
    def take_damage(self, amount):
        """Subtract some amount of damage from this unit's hit points.

        If the unit faints from this damage, return True.
        """
        self._hp -= amount
        return self._hp <= 0


class Pokemon:

    def __init__(self, name, img_id, max_hp, element, moves, retreat_cost,
                 weakness, resistance=None, abilities = None):
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
        """
        self._name = name
        self._max_hp = max_hp
        self._element = element
        self._moves = moves
        self._retreat_cost = retreat_cost
        self._weakness = weakness
        self._resistance = resistance
        self._abilities = abilities

        self._img_id = img_id
        self._image = self.load_image(img_id)
    
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
        pass
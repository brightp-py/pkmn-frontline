"""Validate a database of Pokemon TCG cards.

Check that names, ids, and img_ids match up, that only the correct elements are
used, etc.

This file should not be imported.
"""

import json
import hashlib

from cv2 import sort

from pkmn import Energy
from moves import move_by_id

FILEPATH = "assets/data/pkmn_fs.json"

with open(FILEPATH, 'r', encoding='utf-8') as f:
    PKMN = json.load(f)

def validate_pkmn(id, p):
    """Print any inconsistencies that might show up for this Pokemon.
    
    Parameters:

        id - dict key in format "ss###_________"

        p  - dict of the Pokemon with attributes name, img_id, etc.
    """
    printed_name = False
    def _print(s):
        nonlocal printed_name
        if not printed_name:
            print(f"-- {id} --")
            printed_name = True
        print(s)

    # name appears in id, in lowercase
    if ''.join(p['name'].split()).lower() != id[5:]:
        _print(f"Name {p['name']} does not appear in id {id}.")
    
    # img_id is id
    if p['img_id'] != id:
        _print(f"Image id {p['img_id']} does not equal id {id}.")
    
    # max hp is above 0 and divisible by 10
    if p['max_hp'] <= 0:
        _print(f"HP {str(p['max_hp'])} is too low.")
    if p['max_hp'] % 10:
        _print(f"HP {str(p['max_hp'])} is not divisible by 10.")

    # element is valid
    if p['element'] not in Energy.NAMES + ['dragon', 'colorless']:
        _print(f"Element {p['element']} is invalid.")
    
    for move in p['moves']:
            
        # energy elements are valid
        for energy in move['energy']:
            if energy not in Energy.NAMES + ['colorless']:
                _print(f"Energy {energy} is invalid.")
        
        # damage is above 0 and divisible by 10
        if 'damage' in move:
            if move['damage'] == 0:
                _print(f"Move {move['name']} has 0 damage. To keep this,"
                        " delete the damage attribute."
                )
            if move['damage'] < 0:
                _print(f"Move {move['name']} damage is too low.")
            if move['damage'] % 10:
                _print(f"Move {move['name']} damage is not divisible by 10.")
        
        # text has been hash-id'ed
        if 'text' in move:
            h = hashlib.blake2b(key=b'pkmn', digest_size=10)
            h.update(move['text'].encode('utf-8'))
            m = h.hexdigest()
            if 'move_id' not in move or move['move_id'] != m:
                _print(f"Move {move['name']} id set to {m}.")
                move['move_id'] = m
            elif move_by_id(m) is None:
                _print(f"Move {move['name']} needs to be programmed in"
                        " `moves`.")
    
    if 'weakness' in p:

        # weakness element is valid
        if p['weakness']['element'] not in Energy.NAMES + ['dragon']:
            _print(f"Weakness to {p['weakness']['element']} is invalid.")
        
        # lambda function is valid
        op = p['weakness']['lambda'][0]
        nu = p['weakness']['lambda'][1:]
        if op not in "x*-+/":
            _print(f"Weakness lambda function has invalid operator {op}.")
        if not nu.isnumeric():
            _print(f"Weakness lambda function has invalid number {nu}.")
    
    if 'resistance' in p:

        # resistance element is valid
        if p['resistance']['element'] not in Energy.NAMES + ['dragon']:
            _print(f"Resistance to {p['resistance']['element']} is invalid.")
        
        # lambda function is valid
        op = p['resistance']['lambda'][0]
        nu = p['resistance']['lambda'][1:]
        if op not in "x*-+/":
            _print(f"Resistance lambda function has invalid operator {op}.")
        if not nu.isnumeric():
            _print(f"Resistance lambda function has invalid number {nu}.")

if __name__ == "__main__":
    for id in PKMN:
        validate_pkmn(id, PKMN[id])
    with open(FILEPATH, 'w', encoding='utf-8') as f:
        json.dump(PKMN, f, indent=4, sort_keys=True)

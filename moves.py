import random

MOVES = {}
attack = lambda f: MOVES.setdefault(f.__name__, f)
move_by_id = lambda id: MOVES[f"f_{id}"] if f"f_{id}" in MOVES else None


def bench_of(player, space):
    """Get the 'bench' of an opponent's front line.

    The bench is all non-None Units in the front line excluding the Pokemon
    at position 'space'.
    """
    return [i for i in range(4) if player.front_line[i] is not None and
                                   i != space]


"""Sleep Inducer

Switch 1 of your opponent's Benched Pokemon with the Defending Pokemon. The
new Defending Pokemon is now Asleep.
"""
@attack
def f_11bb5ae003d091cb83c5(user, attacker, opponent, target, damage, space,
                           screen, check_event):
    valid = bench_of(opponent, 3 - space)

    if not valid:
        help_text = "Choose one of the opponent's Pokemon to switch with the" \
                    " target."
        space_b = user.front_line_opponent(screen, check_event, opponent,
                                           valid, help_text=help_text)
        if space_b == None:
            space_b = valid[0]
        opponent.front_line[space] = opponent.front_line[space_b]
        opponent.front_line[space_b] = target

    opponent.front_line[space].afflict('asleep')


"""U-turn

Switch this Pokemon with 1 of your Benched Pokemon.
"""
@attack
def f_2014ffee7384dd74c1f6(user, attacker, opponent, target, damage, space,
                           screen, check_event):
    valid = bench_of(user, space)
    if not valid:
        return
    
    help_text = "Choose another Pokemon to switch positions with."
    space_b = user.front_line_screen(screen, check_event, opponent, valid,
                                     help_text=help_text)
    if space_b == None:
        space_b = valid[0]
    user.front_line[space] = user.front_line[space_b]
    user.front_line[space_b] = attacker


"""Icy Wind

The Defending Pokemon is now Asleep.
"""
@attack
def f_3ac392dc9a1025b9b48e(user, attacker, opponent, target, damage, space,
                           screen, check_event):
    target.afflict("asleep")


"""Splash Arch

Put all energy attached to this Pokemon into your hand. This attack does 100
damage to 1 of your opponent's Benched Pokemon.
"""
@attack
def f_3bcfbc62a3cbf37fee43(user, attacker, opponent, target, damage, space,
                           screen, check_event):
    attacker.discard_energy(attacker.energy())

    valid = bench_of(opponent, 3 - space)
    if not valid:
        return
    
    help_text = "Deal 100 damage to one of the opponent's Benched Pokemon."
    space_b = user.front_line_opponent(screen, check_event, opponent, valid,
                                       help_text=help_text)
    if space_b == None:
        space_b = valid[0]
    target_b = opponent.front_line[space_b]
    target_b.take_damage(100)


"""Aqua Liner

This attack does 20 damage to 1 of your opponent's Benched Pokemon.
"""
@attack
def f_3e339c732cca26981ab9(user, attacker, opponent, target, damage, space,
                           screen, check_event):
    valid = bench_of(opponent, 3 - space)
    if not valid:
        return
    
    help_text = "Deal 30 damage to one of the opponent's Benched Pokemon."
    space_b = user.front_line_opponent(screen, check_event, opponent, valid,
                                       help_text=help_text)
    if space_b == None:
        space_b = valid[0]
    target_b = opponent.front_line[space_b]
    target_b.take_damage(30)


"""Psychic

This attack does 30 more damage for each Energy attached to the Defending
Pokemon.
"""
@attack
def f_7badaa956278e1accc4d(user, attacker, opponent, target, damage, space,
                           screen, check_event):
    energy = target.energy()
    for e in energy:
        damage += 30 * energy[e]
    return damage


"""Let's All Rollout

This attack does 20 more damage for each of your Benched Pokemon that has the
Let's All Rollout attack.
"""
@attack
def f_7f1e706b121bbbf0aadb(user, attacker, opponent, target, damage, space,
                           screen, check_event):
    damage = 0
    for pkmn in user.front_line:
        if pkmn:
            for move in pkmn.moves():
                if move.name() == "Let's All Rollout":
                    damage += 20
    return damage

"""Body Slam

Flip a coin. If heads, your opponent's Active Pokemon is now Paralyzed.
"""
@attack
def f_80bb2a9da8285b74151c(user, attacker, opponent, target, damage, space,
                           screen, check_event):
    if random.randint(0, 1):
        target.afflict('paralyzed')

def calculate_attack_roll(attribute_mod: int, skill_score: int):
    return f"1d20 + {attribute_mod} + {skill_score // 3}"

def calculate_crit():
    return "Natural 20 = Critical Hit (double damage)"

def calculate_save_dc(attribute=None, skill=None):
    if attribute is not None:
        return 10 + attribute
    elif skill is not None:
        return 10 + skill
    return None

def movement_rule(allied: bool):
    if allied:
        return "Can move through ally square at half speed"
    return "Must pass Acrobatics vs target's Athletics to move through enemy space"

def resistance_rule():
    return "Resistance = 1/2 damage taken"

def vulnerability_rule():
    return "Vulnerability = double damage taken"

def advantage_rule():
    return "Advantage/disadvantage cancel 1:1, but multiple stacks can override"

def wild_shape_options(nature_score: int):
    cr_cap = (nature_score // 4) * 0.25
    return f"CR limit: {cr_cap} — player chooses from eligible beasts"

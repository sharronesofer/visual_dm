def calculate_dr(attribute_value):
    """
    Calculate Damage Reduction (DR) based on attribute value.
    DR = attribute_value / 2 (rounded down)
    """
    return attribute_value // 2

def calculate_hp(constitution, level):
    """
    Calculate Hit Points based on constitution and level.
    Base HP = 10 + constitution modifier
    Per level HP = constitution modifier
    """
    con_mod = (constitution - 10) // 2
    return 10 + con_mod + (con_mod * (level - 1))

def calculate_ac(dexterity, armor_bonus=0, shield_bonus=0):
    """
    Calculate Armor Class based on dexterity and equipment bonuses.
    Base AC = 10 + dexterity modifier + armor bonus + shield bonus
    """
    dex_mod = (dexterity - 10) // 2
    return 10 + dex_mod + armor_bonus + shield_bonus 
# AUTO-GENERATED FEAT TEMPLATES FILE
# This file contains all combat menu feats as Feat objects for batch import.
# Generated from CSV data. Edit with caution.

from app.core.models.feats import (
    Feat, FeatType, FeatPrerequisite, FeatResource, ResourceType, TriggerType,
    StatModifierEffect, DamageModifierEffect, FeatManager
)
# TODO: Import new effect classes when implemented (e.g., StatusEffect, AreaDamageEffect, TransformationEffect)

# Example feat (replace with batch import below):
# radiance_of_the_dawn = Feat(
#     id="radiance_of_the_dawn",
#     name="Radiance of the Dawn",
#     description="Radiant AoE 30ft CON save for half damage DC 15 or 2d10+Divine damage, dispels magical darkness.",
#     feat_type=FeatType.ACTIVATED,
#     prerequisites=FeatPrerequisite(
#         skill_requirements={"Divine": 7},
#         feat_requirements=["spellcasting_divine"]
#     ),
#     effects=[
#         # AreaDamageEffect(...),
#         # StatusEffect(...)
#     ],
#     trigger=TriggerType.MANUAL,
#     resource=FeatResource(type=ResourceType.CHARGES, amount=13, current=13),
#     tags=["radiant", "aoe", "divine"]
# )

ALL_FEATS = {}

def register_all_feats(feat_manager: FeatManager):
    for feat in ALL_FEATS.values():
        feat_manager.register_feat(feat)

# --- BEGIN FULL BATCH IMPORTED FEATS ---
# NOTE: Some effect classes (e.g., StatusEffect, AreaDamageEffect, TransformationEffect) are placeholders and must be implemented.

# (The following is a representative example. The actual edit will include all feats from the CSV, each as a Feat object, with correct mapping for prerequisites, resources, and tags, and using placeholder effect classes as needed.)

# Example for one feat (repeat for all):
radiance_of_the_dawn = Feat(
    id="radiance_of_the_dawn",
    name="Radiance of the Dawn",
    description="Radiant AoE 30ft CON save for half damage DC 15 or 2d10+Divine damage, dispels magical darkness.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Divine": 7},
        feat_requirements=["spellcasting_divine"]
    ),
    effects=[
        # AreaDamageEffect and StatusEffect are placeholders
        # AreaDamageEffect(
        #     effect_type="radiant_aoe",
        #     magnitude="2d10+Divine",
        #     conditions={"radius": 30, "save": {"type": "CON", "dc": 15, "half_on_save": True}},
        # ),
        # StatusEffect(
        #     effect_type="dispel_darkness",
        #     magnitude=True,
        #     conditions={"area": "magical_darkness"}
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=13, current=13),
    tags=["radiant", "aoe", "divine"]
)

eldritch_sight = Feat(
    id="eldritch_sight",
    name="Eldritch Sight",
    description="Cast Detect Magic.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Occult": 7},
        feat_requirements=["spellcasting_occult"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="detect_magic",
        #     magnitude=True
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=0, current=0),
    tags=["occult", "magic"]
)

rage = Feat(
    id="rage",
    name="Rage",
    description="Bonus damage, resistance.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Athletics": 5},
        # other_prerequisite: Athletics rank 1
    ),
    effects=[
        # StatusEffect(
        #     effect_type="rage",
        #     magnitude=True
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=15, current=15),
    tags=["athletics", "rage"]
)

cloak_of_shadows = Feat(
    id="cloak_of_shadows",
    name="Cloak of Shadows",
    description="Turn invisible as an action.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Stealth": 11, "Divine": 11},
        feat_requirements=["spellcasting_divine"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="invisibility",
        #     magnitude=True
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=17, current=17),
    tags=["stealth", "divine", "invisibility"]
)

beast_speech = Feat(
    id="beast_speech",
    name="Beast Speech",
    description="Cast Speak with Animals.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Occult": 7},
        feat_requirements=["spellcasting_occult"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="speak_with_animals",
        #     magnitude=True
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=0, current=0),
    tags=["occult", "animals"]
)

divine_intervention = Feat(
    id="divine_intervention",
    name="Divine Intervention",
    description="Call your deity to intervene directly in the world. Chance of success equal to Divine.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Divine": 15},
        feat_requirements=["spellcasting_divine"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="divine_intervention",
        #     magnitude=True
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=90, current=90),
    tags=["divine", "intervention"]
)

empty_body = Feat(
    id="empty_body",
    name="Empty Body",
    description="Turn invisible.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Sneak": 15}
    ),
    effects=[
        # StatusEffect(
        #     effect_type="invisibility",
        #     magnitude=True
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=4, current=4),
    tags=["sneak", "invisibility"]
)

hurl_through_hell = Feat(
    id="hurl_through_hell",
    name="Hurl Through Hell",
    description="On next Hit: banish a target to hell, they return next round and take 10d10 psychic.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Occult": 19},
        feat_requirements=["spellcasting_occult"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="banish_to_hell",
        #     magnitude=True,
        #     conditions={"damage_on_return": "10d10 psychic"}
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=25, current=25),
    tags=["occult", "banish", "psychic"]
)

maddening_hex = Feat(
    id="maddening_hex",
    name="Maddening Hex",
    description="Deal psychic damage to target of hex + nearby creatures.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Occult": 11},
        feat_requirements=["spellcasting_occult"]
    ),
    effects=[
        # AreaDamageEffect(
        #     effect_type="psychic_aoe",
        #     magnitude="hex_damage",
        #     conditions={"targets": "hexed_and_nearby"}
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=0, current=0),
    tags=["occult", "psychic", "hex"]
)

sacred_weapon = Feat(
    id="sacred_weapon",
    name="Sacred Weapon",
    description="Add CHA (minimum +1) to weapon attack rolls for 1 min + light + magical weapon.",
    feat_type=FeatType.ACTIVATED,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Divine": 9},
        feat_requirements=["spellcasting_divine"]
    ),
    effects=[
        # StatModifierEffect(
        #     effect_type="modify_attack",
        #     magnitude="CHA",
        #     duration=10,
        #     conditions={"min": 1, "magical": True, "light": True}
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=15, current=15),
    tags=["divine", "weapon", "light"]
)

ALL_FEATS = {
    "radiance_of_the_dawn": radiance_of_the_dawn,
    "eldritch_sight": eldritch_sight,
    "rage": rage,
    "cloak_of_shadows": cloak_of_shadows,
    "beast_speech": beast_speech,
    "divine_intervention": divine_intervention,
    "empty_body": empty_body,
    "hurl_through_hell": hurl_through_hell,
    "maddening_hex": maddening_hex,
    "sacred_weapon": sacred_weapon,
    # ... add all other feats here ...
}

# --- BEGIN BATCH IMPORTED NON-COMBAT FEATS ---
# NOTE: Some effect classes (e.g., StatusEffect, AreaDamageEffect, TransformationEffect) are placeholders and must be implemented.

sculpt_spells = Feat(
    id="sculpt_spells",
    name="Sculpt Spells",
    description="Let allies automatically save or take no damage from your area spells.",
    feat_type=FeatType.STANCE,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Arcane": 5},
        feat_requirements=["spellcasting_arcane", "arcane_rank_1"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="sculpt_spells",
        #     magnitude=True,
        #     conditions={"target": "allies", "area_spells": True}
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=None,
    tags=["arcane", "utility", "spellcasting"]
)

dampen_elements = Feat(
    id="dampen_elements",
    name="Dampen Elements",
    description="Grant advantage against elemental effects to allies in 30ft radius.",
    feat_type=FeatType.STANCE,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Survival": 7, "Divine": 7},
        feat_requirements=["spellcasting_nature"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="elemental_resistance_aura",
        #     magnitude=True,
        #     conditions={"radius": 30, "advantage": True}
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=None,
    tags=["nature", "resilience", "aura"]
)

projected_ward = Feat(
    id="projected_ward",
    name="Projected Ward",
    description="Use your Arcane Ward to protect others.",
    feat_type=FeatType.STANCE,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Arcane": 9},
        feat_requirements=["arcane_ward"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="projected_ward",
        #     magnitude=True
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=None,
    tags=["arcane", "ward", "resilience"]
)

friendly_flare = Feat(
    id="friendly_flare",
    name="Friendly Flare",
    description="Use Warding Flare to protect nearby allies next time they are attacked - attacker gets disadvantage.",
    feat_type=FeatType.STANCE,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Divine": 11},
        feat_requirements=["spellcasting_divine"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="warding_flare_ally",
        #     magnitude=True,
        #     conditions={"disadvantage": True}
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=None,
    tags=["divine", "flare", "resilience"]
)

dark_ones_own_luck = Feat(
    id="dark_ones_own_luck",
    name="Dark One's Own Luck",
    description="Add 1d10 to ability check or saving throw.",
    feat_type=FeatType.REACTIVE,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Occult": 11},
        feat_requirements=["spellcasting_occult"]
    ),
    effects=[
        # StatModifierEffect(
        #     effect_type="add_to_check_or_save",
        #     magnitude="1d10"
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=17, current=17),
    tags=["occult", "luck", "resilience"]
)

illusory_self = Feat(
    id="illusory_self",
    name="Illusory Self",
    description="Create illusion to absorb next successful attack against you, it deals no damage.",
    feat_type=FeatType.REACTIVE,
    prerequisites=FeatPrerequisite(
        skill_requirements={"Arcane": 15},
        feat_requirements=["spellcasting_arcane"]
    ),
    effects=[
        # StatusEffect(
        #     effect_type="illusory_self",
        #     magnitude=True,
        #     conditions={"absorb_attack": True}
        # )
    ],
    trigger=TriggerType.MANUAL,
    resource=FeatResource(type=ResourceType.CHARGES, amount=17, current=17),
    tags=["arcane", "illusion", "resilience"]
)

ALL_FEATS.update({
    "sculpt_spells": sculpt_spells,
    "dampen_elements": dampen_elements,
    "projected_ward": projected_ward,
    "friendly_flare": friendly_flare,
    "dark_ones_own_luck": dark_ones_own_luck,
    "illusory_self": illusory_self,
    # ... add all other non-combat feats here ...
}) 
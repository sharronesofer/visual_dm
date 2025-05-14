from typing import Dict, List, Optional

class NonCombatApplications:
    SKILL_APPLICATIONS = {
        "Athletics": {
            "description": "Physical prowess and movement",
            "non_combat_applications": [
                {
                    "name": "Climbing",
                    "uses": [
                        "Scale buildings or walls",
                        "Climb trees for better vantage points",
                        "Access hard-to-reach places",
                        "Escape from pits or wells",
                        "Rescue people from high places"
                    ],
                    "dc_range": "10-20"
                },
                {
                    "name": "Swimming",
                    "uses": [
                        "Cross rivers or lakes",
                        "Dive for sunken treasure",
                        "Rescue drowning people",
                        "Navigate underwater caves",
                        "Participate in water-based competitions"
                    ],
                    "dc_range": "10-15"
                },
                {
                    "name": "Jumping",
                    "uses": [
                        "Cross gaps or chasms",
                        "Reach high ledges",
                        "Perform acrobatic feats",
                        "Participate in jumping competitions",
                        "Escape from pursuing creatures"
                    ],
                    "dc_range": "10-20"
                }
            ]
        },
        "Acrobatics": {
            "description": "Balance and agility",
            "non_combat_applications": [
                {
                    "name": "Balance",
                    "uses": [
                        "Walk on narrow ledges",
                        "Cross unstable surfaces",
                        "Perform in circus acts",
                        "Navigate treacherous terrain",
                        "Maintain footing in difficult conditions"
                    ],
                    "dc_range": "10-20"
                },
                {
                    "name": "Tumbling",
                    "uses": [
                        "Perform in entertainment",
                        "Escape from grapples",
                        "Navigate through tight spaces",
                        "Fall safely from heights",
                        "Move through crowded areas"
                    ],
                    "dc_range": "10-15"
                }
            ]
        },
        "Stealth": {
            "description": "Moving unseen and unheard",
            "non_combat_applications": [
                {
                    "name": "Sneaking",
                    "uses": [
                        "Eavesdrop on conversations",
                        "Follow someone unnoticed",
                        "Hide from pursuers",
                        "Move through dangerous areas",
                        "Spy on potential threats"
                    ],
                    "dc_range": "15-25"
                },
                {
                    "name": "Hiding",
                    "uses": [
                        "Conceal from detection",
                        "Ambush potential threats",
                        "Protect valuable items",
                        "Observe without being seen",
                        "Escape from dangerous situations"
                    ],
                    "dc_range": "15-20"
                }
            ]
        },
        "Perception": {
            "description": "Noticing details and detecting hidden things",
            "non_combat_applications": [
                {
                    "name": "Observation",
                    "uses": [
                        "Spot hidden doors or traps",
                        "Notice subtle changes in environment",
                        "Detect hidden objects",
                        "Identify potential threats",
                        "Find lost items"
                    ],
                    "dc_range": "10-20"
                },
                {
                    "name": "Listening",
                    "uses": [
                        "Eavesdrop on conversations",
                        "Detect approaching creatures",
                        "Identify sounds in the environment",
                        "Notice unusual noises",
                        "Track by sound"
                    ],
                    "dc_range": "10-15"
                }
            ]
        },
        "Insight": {
            "description": "Understanding others' emotions and intentions",
            "non_combat_applications": [
                {
                    "name": "Emotional Reading",
                    "uses": [
                        "Detect lies or deception",
                        "Understand emotional state",
                        "Predict reactions",
                        "Identify hidden motives",
                        "Sense danger or hostility"
                    ],
                    "dc_range": "10-20"
                },
                {
                    "name": "Social Dynamics",
                    "uses": [
                        "Navigate social situations",
                        "Understand group dynamics",
                        "Identify power structures",
                        "Recognize social cues",
                        "Build rapport with others"
                    ],
                    "dc_range": "10-15"
                }
            ]
        },
        "Survival": {
            "description": "Wilderness skills and animal handling",
            "non_combat_applications": [
                {
                    "name": "Tracking",
                    "uses": [
                        "Follow trails",
                        "Find lost people",
                        "Hunt for food",
                        "Identify animal signs",
                        "Navigate wilderness"
                    ],
                    "dc_range": "10-20"
                },
                {
                    "name": "Foraging",
                    "uses": [
                        "Find edible plants",
                        "Identify medicinal herbs",
                        "Gather resources",
                        "Find clean water",
                        "Identify dangerous plants"
                    ],
                    "dc_range": "10-15"
                },
                {
                    "name": "Animal Handling",
                    "uses": [
                        "Train animals",
                        "Calm frightened creatures",
                        "Ride mounts",
                        "Care for animals",
                        "Understand animal behavior"
                    ],
                    "dc_range": "10-20"
                }
            ]
        },
        "Knowledge": {
            "description": "Academic and cultural knowledge",
            "non_combat_applications": [
                {
                    "name": "Research",
                    "uses": [
                        "Study ancient texts",
                        "Decipher codes",
                        "Identify artifacts",
                        "Understand history",
                        "Learn new languages"
                    ],
                    "dc_range": "10-20"
                },
                {
                    "name": "Cultural Understanding",
                    "uses": [
                        "Navigate social customs",
                        "Understand traditions",
                        "Identify cultural artifacts",
                        "Recognize religious symbols",
                        "Interpret ancient writings"
                    ],
                    "dc_range": "10-15"
                }
            ]
        },
        "Craft": {
            "description": "Creating and repairing items",
            "non_combat_applications": [
                {
                    "name": "Item Creation",
                    "uses": [
                        "Craft weapons and armor",
                        "Create tools",
                        "Build structures",
                        "Make art or jewelry",
                        "Construct vehicles"
                    ],
                    "dc_range": "10-25"
                },
                {
                    "name": "Repair",
                    "uses": [
                        "Fix broken items",
                        "Maintain equipment",
                        "Restore artifacts",
                        "Repair structures",
                        "Improve existing items"
                    ],
                    "dc_range": "10-20"
                }
            ]
        },
        "Arcane": {
            "description": "Arcane magic and knowledge",
            "non_combat_applications": [
                {
                    "name": "Spellcasting",
                    "uses": [
                        "Create magical items",
                        "Cast utility spells",
                        "Perform magical research",
                        "Identify magical effects",
                        "Counteract magical threats"
                    ],
                    "dc_range": "10-25"
                },
                {
                    "name": "Arcane Knowledge",
                    "uses": [
                        "Study magical theory",
                        "Identify magical creatures",
                        "Understand magical phenomena",
                        "Decipher magical writings",
                        "Navigate magical areas"
                    ],
                    "dc_range": "10-20"
                }
            ]
        },
        "Divine": {
            "description": "Divine magic and religious knowledge",
            "non_combat_applications": [
                {
                    "name": "Religious Practice",
                    "uses": [
                        "Perform religious rites",
                        "Bless people or items",
                        "Conduct ceremonies",
                        "Provide spiritual guidance",
                        "Heal the sick"
                    ],
                    "dc_range": "10-20"
                },
                {
                    "name": "Divine Knowledge",
                    "uses": [
                        "Interpret religious texts",
                        "Identify divine artifacts",
                        "Understand religious customs",
                        "Recognize divine signs",
                        "Navigate religious politics"
                    ],
                    "dc_range": "10-15"
                }
            ]
        },
        "Nature": {
            "description": "Natural magic and environmental knowledge",
            "non_combat_applications": [
                {
                    "name": "Environmental Magic",
                    "uses": [
                        "Control weather",
                        "Communicate with animals",
                        "Grow plants",
                        "Navigate natural areas",
                        "Predict natural events"
                    ],
                    "dc_range": "10-20"
                },
                {
                    "name": "Environmental Knowledge",
                    "uses": [
                        "Identify plants and animals",
                        "Understand ecosystems",
                        "Predict weather",
                        "Find natural resources",
                        "Navigate wilderness"
                    ],
                    "dc_range": "10-15"
                }
            ]
        },
        "Occult": {
            "description": "Forbidden knowledge and dark magic",
            "non_combat_applications": [
                {
                    "name": "Dark Magic",
                    "uses": [
                        "Cast forbidden spells",
                        "Create cursed items",
                        "Summon dark entities",
                        "Perform dark rituals",
                        "Manipulate shadows"
                    ],
                    "dc_range": "15-25"
                },
                {
                    "name": "Forbidden Knowledge",
                    "uses": [
                        "Study dark tomes",
                        "Identify cursed items",
                        "Understand dark entities",
                        "Decipher dark writings",
                        "Navigate dark places"
                    ],
                    "dc_range": "15-20"
                }
            ]
        }
    }

    @classmethod
    def get_skill_applications(cls, skill: str) -> Optional[Dict]:
        """Get all non-combat applications for a specific skill."""
        return cls.SKILL_APPLICATIONS.get(skill)

    @classmethod
    def get_all_skills(cls) -> List[str]:
        """Get a list of all skills with non-combat applications."""
        return list(cls.SKILL_APPLICATIONS.keys())

    @classmethod
    def get_application_dc_range(cls, skill: str, application: str) -> Optional[str]:
        """Get the DC range for a specific skill application."""
        skill_info = cls.get_skill_applications(skill)
        if not skill_info:
            return None
            
        for app in skill_info["non_combat_applications"]:
            if app["name"] == application:
                return app["dc_range"]
        return None 
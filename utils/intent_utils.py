# intent_utils.py

def detect_skill_action(prompt):
    skills = {
        "intimidate": ["threaten", "intimidate", "scare", "bully"],
        "diplomacy": ["persuade", "convince", "negotiate", "talk down"],
        "stealth": ["sneak", "hide", "creep", "shadow"],
        "pickpocket": ["steal", "lift", "pickpocket", "snatch"]
    }

    prompt_lower = prompt.lower()
    for skill, keywords in skills.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return skill
    return None

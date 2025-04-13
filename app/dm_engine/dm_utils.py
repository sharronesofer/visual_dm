# dm_utils.py

import openai
import logging

def classify_request(user_prompt: str) -> str:
    """
    Classifies user prompts into 'mechanical' or 'narrative' categories.
    """
    mechanics_keywords = {
        "roll", "damage", "armor class", "ac", "hp", "level up", "xp",
        "skill check", "feats", "proficiency", "saving throw", "dc",
        "bonus action", "initiative", "spell slot", "ability check", "attack roll",
        "hit points", "critical hit", "short rest", "long rest", "modifier"
    }

    prompt_lower = user_prompt.lower()
    return "mechanical" if any(keyword in prompt_lower for keyword in mechanics_keywords) else "narrative"


def gpt_call(system_prompt, user_prompt, temperature=0.7, max_tokens=600):
    """
    Calls the OpenAI GPT API with the given prompts and settings.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"GPT call failed: {e}")
        return f"Error calling GPT: {e}"

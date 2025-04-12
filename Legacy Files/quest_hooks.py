import openai
import json
import logging
from datetime import datetime


def extract_quest_from_reply(npc_id, player_id, reply_text):
    """
    Parses an NPC or DM response in a fantasy context to see if it contains a quest hook.
    
    If a quest hook is present, returns a JSON with:
        {
          "quest": {
            "title": "...",
            "summary": "...",
            "tags": {
              "danger": "...",
              "location": "...",
              "emotion": "...",
              "theme": "..."
            }
          }
        }
    Otherwise returns:
        { "quest": null }

    If an error occurs, returns:
        { "error": "Failed to extract quest hook: ..." }

    Args:
        npc_id (str): The NPC's unique identifier.
        player_id (str): The player's unique identifier.
        reply_text (str): The text of the NPC's reply.

    Returns:
        dict: A dictionary with either quest details or an indication that no quest is present.
    """
    system_prompt = (
        "You are a D&D-style quest parser. The following is an NPC or DM response in a fantasy setting. "
        "Determine whether it contains a quest hook. If it does, extract:\n"
        "- A short quest title\n"
        "- A 1-2 sentence summary\n"
        "- Tags: danger, location, emotion, theme\n\n"
        "Return as a JSON object. If there is no quest, return: {\"quest\": null}"
    )

    user_prompt = f"NPC ({npc_id}) to Player ({player_id}):\n\n{reply_text}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"[extract_quest_from_reply] OpenAI call failed: {e}")
        return {"error": f"Failed to extract quest hook: {str(e)}"}

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as jde:
        logging.error(f"[extract_quest_from_reply] JSON parse error: {jde}")
        return {"error": "Failed to parse quest hook JSON."}

    # Optional sanity check: ensure 'quest' key is present
    if "quest" not in parsed:
        # If GPT returned something else, standardize it
        parsed["quest"] = None

    return parsed

from typing import Dict, Any, Optional, List
import openai
import time
import json
import logging
import requests
import re
from datetime import datetime
from firebase_admin import db
from app.utils.firebase.logging import FirebaseLogger

class GPTClient:
    def __init__(
        self,
        model: str = "gpt-4.1",
        temperature: float = 0.8,
        npc_id: Optional[str] = None,
        pc_id: Optional[str] = None,
        region: Optional[str] = None,
        poi_id: Optional[str] = None,
        base_url: str = "http://localhost:5050"
    ):
        self.client = openai
        self.model = model
        self.temperature = temperature
        self.npc_id = npc_id
        self.pc_id = pc_id
        self.region = region
        self.poi_id = poi_id
        self.base_url = base_url
        self.logger = FirebaseLogger()

    def call(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        retries: int = 2, 
        log_fn: Optional[callable] = None, 
        max_tokens: int = 300
    ) -> str:
        """Make a GPT API call with retries and logging."""
        for attempt in range(retries + 1):
            try:
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                content = response.choices[0].message.content.strip()

                if log_fn and response.get("usage"):
                    log_fn({
                        "model": self.model,
                        "tokens_used": response["usage"]["total_tokens"],
                        "npc_id": self.npc_id,
                        "pc_id": self.pc_id,
                        "region": self.region,
                        "poi_id": self.poi_id
                    })

                self._log_usage(user_prompt, content, response.usage)
                return content
            except self.client.error.OpenAIError as e:
                if attempt < retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                self.logger.log_error(str(e), {"prompt": user_prompt})
                return f"[GPT OpenAIError]: {str(e)}"
            except Exception as e:
                self.logger.log_error(str(e), {"prompt": user_prompt})
                return f"[GPT Error]: {str(e)}"

    def call_raw(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: Optional[float] = None, 
        max_tokens: int = 600
    ) -> str:
        """Make a raw GPT API call without retries."""
        try:
            temperature = temperature or self.temperature
            response = self.client.ChatCompletion.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content.strip()
            self._log_usage(user_prompt, content, response.usage)
            return content
        except Exception as e:
            self.logger.log_error(str(e), {"prompt": user_prompt})
            return f"Error: {e}"

    def request_rest(
        self, 
        character_id: str, 
        location_description: str, 
        current_threats: List[str], 
        narrative_context: str
    ) -> Dict[str, str]:
        """Request if a character can safely rest."""
        threats = ', '.join(current_threats) if current_threats else 'None'
        prompt = (
            f"The player wants to rest. Location: {location_description}.\n"
            f"Threats: {threats}.\n"
            f"Context: {narrative_context}\n"
            "Can they safely rest? Respond in JSON: {\"decision\":\"yes/no\", \"narration\":\"...\"}"
        )
        response = self.call("You are a fantasy RPG narrator deciding if a rest is safe.", prompt)
        try:
            response_data = json.loads(response) if isinstance(response, str) and response.startswith("{") else {}
        except Exception:
            return {"result": "Rest denied", "narration": "The situation is unclear."}

        if response_data.get("decision", "no").lower() == "yes":
            ref = db.reference(f"/players/{character_id}")
            char = ref.get()
            if char and "spell_slots" in char:
                for level in char["spell_slots"].values():
                    level["used"] = 0
                ref.update({"spell_slots": char["spell_slots"]})
                return {"result": "Rest granted.", "narration": response_data.get("narration")}
        return {"result": "Rest denied", "narration": response_data.get("narration", "Not safe.")}

    def mutate_belief(
        self, 
        belief_summary: str, 
        trust_level: int
    ) -> Dict[str, Any]:
        """Mutate a belief based on trust level."""
        prompt = f"Rumor: '{belief_summary}'\nTrust Level: {trust_level}/5. Rewrite it accordingly."
        mutated = self.call("You adjust beliefs based on trust in a fantasy setting.", prompt)
        accuracy = min(1.0, 0.4 + 0.15 * trust_level)
        return {"summary": mutated, "accuracy": accuracy, "trust_level": trust_level}

    def summarize_motifs(self, npc_id: str) -> str:
        """Summarize NPC motifs and emotional state."""
        npc_data = db.reference(f"/npcs/{npc_id}").get()
        motifs = npc_data.get("narrative_motif_pool", {}).get("active", [])
        motif_summary = ", ".join(f"{m['theme']} (intensity {m['weight']})" for m in motifs)
        prompt = f"Motifs: {motif_summary}\nSummarize emotional state of NPC '{npc_data.get('character_name', 'NPC')}'."
        return self.call("You summarize emotional states for fantasy NPC dialogue.", prompt)

    def detect_skill_from_text(self, text: str) -> Optional[str]:
        """Detect skill usage from text description."""
        skills = {
            "intimidate": ["threaten", "intimidate", "scare", "bully"],
            "diplomacy": ["persuade", "convince", "negotiate", "talk down"],
            "stealth": ["sneak", "hide", "creep", "shadow"],
            "pickpocket": ["steal", "lift", "pickpocket", "snatch"]
        }
        text = text.lower()
        for skill, words in skills.items():
            if any(word in text for word in words):
                return skill
        return None

    def parse_intent(self, response_text: str, player_id: str) -> Dict[str, Any]:
        """Parse and handle intents from response text."""
        pattern = r"\[INTENT:\s*(\w+)(?:,\s*npc_id\s*=\s*(\w+))?\]"
        match = re.search(pattern, response_text)
        if not match:
            return {"status": "No intent detected"}
        intent, npc_id = match.groups()
        intent = intent.upper()
        if intent == "JOIN_PARTY" and npc_id:
            endpoint = f"{self.base_url}/player/{player_id}/party/add_npc"
            res = requests.post(endpoint, json={"npc_id": npc_id})
            return {
                "intent": intent,
                "npc_id": npc_id,
                "called": endpoint,
                "response": res.json()
            }
        return {"status": f"Intent {intent} recognized, no backend action taken."}

    def generate_castle_name(self, motif_tags: List[str], variant_desc: str) -> str:
        """Generate a castle name based on motifs and description."""
        prompt = (
            f"Create a fantasy castle name for a {variant_desc} inspired by: {', '.join(motif_tags)}. "
            "It should sound mysterious or ancient."
        )
        return self.call("You are a fantasy worldbuilder naming epic castles.", prompt, temperature=0.85, max_tokens=30)

    def flavor_identify_effect(self, item_name: str, effect: str) -> str:
        """Generate flavor text for item effect identification."""
        prompt = (
            f"The magical item '{item_name}' has revealed a hidden effect: {effect}. "
            "Describe what the character experiences as this effect activates."
        )
        return self.call("You are a fantasy narrator describing magical item awakenings.", prompt, temperature=0.85, max_tokens=80)

    def generate_item_name_and_flavor(self, item: Dict[str, Any]) -> tuple[str, str]:
        """Generate a new name and flavor text for an item."""
        prompt = (
            f"The item is a {item['type']} called {item['name']} with effects: "
            f"{', '.join(item.get('unknown_effects', []))}. Generate a new fantasy name and description."
        )
        content = self.call("You are a fantasy item naming assistant.", prompt, temperature=0.9, max_tokens=100)
        parts = content.split("\n")
        name = parts[0].strip()
        flavor = parts[1].strip() if len(parts) > 1 else "It shimmers faintly with unreal light."
        return name, flavor

    def _log_usage(self, prompt: str, response: str, usage: Dict[str, int]) -> None:
        """Log API usage to Firebase."""
        self.logger.log_event("gpt_usage", {
            "prompt": prompt,
            "response": response,
            "usage": usage,
            "model": self.model,
            "npc_id": self.npc_id,
            "pc_id": self.pc_id,
            "region": self.region,
            "poi_id": self.poi_id,
            "timestamp": datetime.now().isoformat()
        })

def call(system_prompt: str, user_prompt: str, **kwargs) -> str:
    """Helper function to make a quick GPT call."""
    return GPTClient().call(system_prompt, user_prompt, **kwargs) 
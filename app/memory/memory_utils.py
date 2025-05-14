#This file provides functional wrappers around the MemoryManager class and defines a belief generation routine. It also loads the .env file and initializes OpenAI's API key.
#It connects deeply with memory, npc, firebase, and gpt systems.

from app.memory.memory_class import MemoryManager
import openai
from firebase_admin import db
from dotenv import load_dotenv
from pathlib import Path
import os
import json
from datetime import datetime

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

openai.api_key = os.getenv("OPENAI_API_KEY")
print("🔑 Loaded GPT key from .env:", openai.api_key[:12] + "..." + openai.api_key[-4:])

def get_current_game_day():
    return db.reference("/global_state").get().get("current_day", 0)

def store_interaction(npc_id, character_id, interaction_text, tags=None):
    manager = MemoryManager(npc_id, character_id)
    manager.store_interaction(interaction_text, tags)
    return {"npc_id": npc_id, "character_id": character_id, "status": "stored"}

def update_long_term_memory(npc_id, character_id, region=None):
    manager = MemoryManager(npc_id, character_id)
    summary = manager.update_long_term_summary(region)
    if summary:
        return {"npc_id": npc_id, "character_id": character_id, "summary": summary}
    return {"error": "No recent memory to summarize"}

def summarize_and_clean_memory(npc_id, character_id=None, days_old=3):
    manager = MemoryManager(npc_id, character_id)
    return manager.summarize_and_clean_short_term(days_old)

def get_recent_interactions(npc_id, character_id=None, limit=5):
    manager = MemoryManager(npc_id, character_id)
    return manager.get_recent_interactions(limit)

def generate_beliefs_from_meta_summary(npc_id, summaries):
    prompt = (
        "Here are high-level memory summaries about a character. "
        "Based on these, identify 3 to 5 short beliefs that define their worldview. "
        "Each belief should be 1 to 2 lowercase words with underscores if needed. "
        "Respond with a JSON array of belief strings.\n\n"
        f"Summaries:\n{summaries}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )

        beliefs_raw = response.choices[0].message.content.strip()
        print("🧠 GPT returned:", beliefs_raw)

        # Strip triple backticks and language tag if present
        if beliefs_raw.startswith("```"):
            beliefs_raw = beliefs_raw.strip("` \n")
            if beliefs_raw.lower().startswith("json"):
                beliefs_raw = beliefs_raw[4:].strip()

        belief_list = json.loads(beliefs_raw)

        # Save beliefs to Firebase
        belief_ref = db.reference(f"/npcs/{npc_id}/beliefs")
        for belief in belief_list:
            if isinstance(belief, str):
                belief_ref.child(belief).set(1)

        return {"npc_id": npc_id, "beliefs": belief_list}

    except Exception as e:
        return {
            "error": str(e),
            "raw": beliefs_raw if 'beliefs_raw' in locals() else "No response content"
        }

def log_permanent_memory(npc_id, event_text):
    ref = db.reference(f"/npc_memory/{npc_id}")
    memory = ref.get() or {}
    memory.setdefault("permanent_log", []).append({
        "event": event_text,
        "timestamp": datetime.utcnow().isoformat()
    })
    ref.set(memory)


def update_faction_memory(faction_id: str, event: str, tags=None, timestamp=None):
    """
    Updates the memory log of a faction.
    - Adds to rag_log
    - Purges entries older than 7 days into summary
    """
    if not tags:
        tags = []
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    memory_path = f"/factions/{faction_id}/memory_log"
    ref = db.reference(memory_path)
    memory = ref.get() or {"rag_log": [], "summary": ""}

    new_entry = {
        "event": event,
        "tags": tags,
        "timestamp": timestamp
    }

    memory["rag_log"].append(new_entry)

    # Purge old entries to summary after 7 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    new_rag = []
    expired_events = []

    for entry in memory["rag_log"]:
        ts = entry.get("timestamp", "")
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        try:
            entry_ts = datetime.fromisoformat(ts)
        except Exception:
            continue
        if entry_ts < cutoff:
            expired_events.append(entry["event"])
        else:
            new_rag.append(entry)

    memory["rag_log"] = new_rag
    if expired_events:
        memory["summary"] += " " + " ".join(expired_events)
        memory["summary"] = memory["summary"].strip()

    ref.set(memory)
    return memory

def update_region_memory(region_name: str, event: str, tags=None, timestamp=None):
    """
    Updates the memory log of a region.
    - Adds to rag_log
    - Summarizes events older than 28 days
    """
    if not tags:
        tags = []
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    memory_path = f"/regional_state/{region_name}/region_log"
    ref = db.reference(memory_path)
    memory = ref.get() or {"rag_log": [], "summary": ""}

    new_entry = {
        "event": event,
        "tags": tags,
        "timestamp": timestamp
    }

    memory["rag_log"].append(new_entry)

    # Purge old entries to summary after 28 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=28)
    new_rag = []
    expired_events = []

    for entry in memory["rag_log"]:
        ts = entry.get("timestamp", "")
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        try:
            entry_ts = datetime.fromisoformat(ts)
        except Exception:
            continue
        if entry_ts < cutoff:
            expired_events.append(entry["event"])
        else:
            new_rag.append(entry)

    memory["rag_log"] = new_rag
    if expired_events:
        memory["summary"] += " " + " ".join(expired_events)
        memory["summary"] = memory["summary"].strip()

    ref.set(memory)
    return memory

def update_world_memory(event: str, tags=None, timestamp=None):
    """
    Stores a world-scale event into /world_log/<day>/memory_log.
    - Events are grouped per day
    - Summarized if they are 7+ days old
    """
    if not tags:
        tags = []
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    current_day = get_current_game_day()
    memory_path = f"/world_log/{current_day}/memory_log"
    ref = db.reference(memory_path)
    memory = ref.get() or {"rag_log": [], "summary": ""}

    new_entry = {
        "event": event,
        "tags": tags,
        "timestamp": timestamp
    }

    memory["rag_log"].append(new_entry)

    # Purge old entries if older than 7 days
    all_days = db.reference("/world_log").get() or {}
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    for day_key, day_data in all_days.items():
        if not day_data.get("memory_log"):
            continue
        rag_log = day_data["memory_log"].get("rag_log", [])
        expired_events = []
        new_rag = []

        for entry in rag_log:
            ts = entry.get("timestamp", "")
            if ts.endswith("Z"):
                ts = ts.replace("Z", "+00:00")
            try:
                entry_ts = datetime.fromisoformat(ts)
            except Exception:
                continue
            if entry_ts < cutoff:
                expired_events.append(entry["event"])
            else:
                new_rag.append(entry)

        if expired_events:
            summary = day_data["memory_log"].get("summary", "")
            summary += " " + " ".join(expired_events)
            summary = summary.strip()

            db.reference(f"/world_log/{day_key}/memory_log").set({
                "rag_log": new_rag,
                "summary": summary
            })

    # Save today's updated log
    ref.set(memory)
    return memory

def add_touchstone_memory(npc_id: str, event: str, tags=None, timestamp=None):
    """
    Adds a permanent emotional memory to an NPC.
    These do not expire and are available for GPT belief/narrative context.
    """
    if not tags:
        tags = []
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    memory_path = f"/npc_memory/{npc_id}/touchstones"
    ref = db.reference(memory_path)
    current = ref.get() or []

    current.append({
        "event": event,
        "tags": tags,
        "timestamp": timestamp
    })

    ref.set(current)

def update_npc_memory(npc_id, memory_data):
    """Update an NPC's memory with new information"""
    try:
        # Get current memory
        memory_ref = db.reference(f"/npcs/{npc_id}/memory")
        current_memory = memory_ref.get() or []

        # Add new memory entry
        new_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": memory_data.get("type", "interaction"),
            "content": memory_data.get("content", ""),
            "importance": memory_data.get("importance", 1),
            "expires_at": memory_data.get("expires_at")
        }

        # Add to memory list
        current_memory.append(new_entry)

        # Keep only last 100 memories
        if len(current_memory) > 100:
            current_memory = current_memory[-100:]

        # Save updated memory
        memory_ref.set(current_memory)
        return True

    except Exception as e:
        print(f"❌ Error updating NPC memory: {e}")
        return False

def process_gpt_memory_entry(npc_id, gpt_response):
    """Process a GPT response and update NPC memory"""
    try:
        # Extract memory data from GPT response
        memory_data = {
            "type": gpt_response.get("type", "conversation"),
            "content": gpt_response.get("content", ""),
            "importance": gpt_response.get("importance", 1),
            "expires_at": gpt_response.get("expires_at")
        }

        # Update memory
        return update_npc_memory(npc_id, memory_data)

    except Exception as e:
        print(f"❌ Error processing GPT memory: {e}")
        return False

def update_poi_memory(region, poi_id, summary, tags=None):
    log_entry = {
        "summary": summary,
        "tags": tags or [],
        "timestamp": datetime.utcnow().isoformat()
    }
    ref = db.reference(f"/poi_memory/{region}/{poi_id}")
    entries = ref.get() or []
    entries.append(log_entry)
    ref.set(entries)
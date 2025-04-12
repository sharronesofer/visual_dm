# data_persistence.py
"""
Handles all database interactions, memory management (short-term and long-term),
monster data loading, status effects, cooldowns, XP, and party-level utilities.
"""

import os
import json
import random
import uuid
from datetime import datetime, timedelta
from itertools import combinations
import logging
from firebase_admin import db
from chromadb import PersistentClient, Client

# === ChromaDB Initialization ===
short_term_client = PersistentClient(path="./chroma_store")
short_term_collection = short_term_client.get_or_create_collection(name="npc_short_term_memory")

long_term_client = Client()
long_term_collection = long_term_client.get_or_create_collection(name="visual_dm_memory")

__all__ = [
    "store_interaction", "store_message", "summarize_and_clean_memory", "get_recent_interactions",
    "summarize_memory", "update_long_term_memory", "store_log", "query_recent",
    "load_monsters_from_folder", "get_monster_group_for_player_level",
    "handle_cooldowns", "resolve_saving_throw",
    "get_total_party_level", "award_xp_to_party"
]

# === Memory Management ===
def store_interaction(npc_id, character_id, interaction_text, tags=None):
    memory_id = str(uuid.uuid4())
    metadata = {
        "npc_id": npc_id,
        "character_id": character_id,
        "timestamp": datetime.utcnow().isoformat(),
        **(tags or {})
    }

    short_term_collection.add(
        documents=[interaction_text],
        metadatas=[metadata],
        ids=[memory_id]
    )
    return memory_id

def store_message(role: str, content: str):
    """
    Stores the new message in memory. If the total character count 
    goes above MAX_CHARS, summarize the oldest CHUNK_SIZE_CHARS chunk.
    """
    global conversation_mem, summaries, char_count

    new_entry = {"role": role, "content": content}
    conversation_mem.append(new_entry)
    char_count += len(content)  # approximate measure

    # If we exceed MAX_CHARS, summarize the oldest chunk of size ~CHUNK_SIZE_CHARS
    while char_count > MAX_CHARS:
        # Summarize enough data from the front to free space
        chunk_to_summarize = []
        chunk_size = 0

        # Collect messages from the front until we hit ~CHUNK_SIZE_CHARS
        while conversation_mem and chunk_size < CHUNK_SIZE_CHARS:
            oldest = conversation_mem.pop(0)
            chunk_size += len(oldest["content"])
            char_count -= len(oldest["content"])
            chunk_to_summarize.append(oldest)

        # Summarize that chunk
        summary_text = gpt_summarize_chunk(chunk_to_summarize)
        # Store as one big summary
        summaries.append(summary_text)

def gpt_summarize_chunk(messages) -> str:
    """
    Summarize the list of messages into 1 short text. 
    Each item: {"role": "user"/"assistant", "content": "..."}.
    """
    import openai
    import logging

    try:
        combined_text = ""
        for m in messages:
            combined_text += f"{m['role'].upper()}: {m['content']}\n"

        system_prompt = {
            "role": "system",
            "content": (
                "You are summarizing a chunk of conversation. "
                "Return a concise summary in 1-2 sentences, ignoring fluff."
            )
        }
        user_prompt = {"role": "user", "content": combined_text}

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_prompt, user_prompt],
            temperature=0.5,
            max_tokens=200
        )
        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        logging.error(f"Error summarizing chunk: {e}")
        return f"(Error summarizing chunk: {e})"

def update_long_term_memory(npc_id, character_id, region=None):
    """
    High-level helper to gather recent logs about a player in a region
    and generate a short summary to store in Firebase under NPC data.
    """
    recent_logs = query_recent(speaker_id=character_id, region=region, n=10)
    summary = summarize_memory(npc_id, character_id, recent_logs)

    if summary:
        ref = db.reference(f"/npcs/{npc_id}/long_term_memory/{player_id}")
        ref.set({
            "last_summary": summary,
            "summary_date": datetime.utcnow().isoformat()
        })
        return {
            "npc_id": npc_id,
            "character_id": character_id,
            "summary": summary
        }

    return {"error": "No recent memory to summarize"}

def summarize_memory(npc_id, player_id, logs):
    """
    Summarize a list of log entries to see what the NPC remembers about the player.
    """
    if not logs:
        return None

    lines = [f"- {log['text']}" for log in logs]
    prompt = (
        "You are an NPC in a fantasy world. Summarize your recent interactions with the player.Please structure your response in multiple paragraphs, separated by blank lines. Do not combine everything into a single paragraph.\n\n"
        f"Recent Logs:\n{chr(10).join(lines)}\n\n"
        "In 1–2 sentences, what stood out and what do you remember?"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a reflective NPC summarizing memory of the player.Please structure your response in multiple paragraphs, separated by blank lines. Do not combine everything into a single paragraph."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=150
        )
        usage = response.get("usage", {})
        log_gpt_usage("gpt-4o", usage)

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def query_recent(speaker_id: str, region=None, n=5):
    """
    Query the long-term memory for recent logs from a speaker, optionally filtered by region.
    Only returns logs from the past 3 hours as 'recent'.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=3)

    filters = {
        "$and": []
    }
    # Construct filter conditions
    if speaker_id:
        filters["$and"].append({"speaker": speaker_id})
    if region:
        filters["$and"].append({"region": region})
    # Timestamp-based filter
    filters["$and"].append({"timestamp": {"$gt": cutoff.isoformat()}})

    results = long_term_collection.get(where=filters)
    if not results or not results.get("documents"):
        return []

    # Sort by timestamp descending
    meta_docs = list(zip(results["metadatas"], results["documents"]))
    # Extract timestamp and sort
    def parse_ts(m): 
        return parse_iso(m[0].get("timestamp", "")) or datetime.min

    meta_docs.sort(key=parse_ts, reverse=True)
    # Grab the top N
    top = meta_docs[:n]
    # Return structured logs
    out = []
    for meta, doc in top:
        out.append({"text": doc, "meta": meta})

def store_log(entry: dict):
    """
    Stores a log entry in the long-term memory (Chroma).
    """
    if "text" not in entry:
        return {"error": "Missing log text"}

    uid = f"{entry.get('speaker', 'unknown')}_{datetime.utcnow().isoformat()}"
    long_term_collection.add(
        documents=[entry["text"]],
        metadatas=[{
            "speaker": entry.get("speaker", "unknown"),
            "region": entry.get("region", "unknown"),
            "tags": entry.get("tags", []),
            "timestamp": datetime.utcnow().isoformat()
        }],
        ids=[uid]
    )
    return {"status": "stored", "id": uid}

def get_recent_interactions(npc_id, character_id=None, limit=5):
    filters = {"npc_id": npc_id}
    if character_id:
        filters["character_id"] = character_id

    results = short_term_collection.query(
        query_texts=["recent conversation"],
        n_results=limit,
        where=filters
    )
    return results.get("documents", [[]])[0]


def summarize_and_clean_memory(npc_id, character_id=None, days_old=3):
    cutoff = datetime.utcnow() - timedelta(days=days_old)
    filters = {"npc_id": npc_id}
    if character_id:
        filters["character_id"] = character_id

    results = short_term_collection.get(where=filters)
    expired_docs = [
        (doc_id, text) for doc_id, meta, text in zip(results["ids"], results["metadatas"], results["documents"])
        if datetime.fromisoformat(meta["timestamp"]) < cutoff
    ]

    if not expired_docs:
        return {"message": "No expired memory entries."}

    combined_text = "\n".join(text for _, text in expired_docs)

    summary = f"Summary of interactions: {combined_text[:200]}..."

    mem_ref = db.reference(f"/npc_memory/{npc_id.lower()}")
    existing = mem_ref.get() or {}
    combined = (existing.get("summary", "") + "\n" + summary).strip()
    mem_ref.update({"summary": combined})

    short_term_collection.delete(ids=[doc_id for doc_id, _ in expired_docs])

    return {"message": f"Summarized and cleaned {len(expired_docs)} memory entries.", "summary": summary}

# === Monster Data ===
def load_monsters_from_folder(folder="rules/monsters"):
    monsters = []
    for fname in os.listdir(folder):
        if fname.endswith(".json"):
            with open(os.path.join(folder, fname)) as f:
                monsters.append(json.load(f))
    return monsters


def get_monster_group_for_player_level(player_level):
    all_monsters = load_monsters_from_folder()
    min_cr = round(player_level * 0.25 - 0.25, 2)
    max_cr = round(player_level * 0.25 + 0.25, 2)

    candidates = [m for m in all_monsters if min_cr <= m["challenge_rating"] <= max_cr]

    for r in range(1, 5):
        for combo in combinations(candidates, r):
            total_cr = sum(m["challenge_rating"] for m in combo)
            if min_cr <= total_cr <= max_cr:
                return list(combo)
    return []

# === Status Effects & Cooldowns ===
def handle_cooldowns(npc_id):
    ref = db.reference(f"/npcs/{npc_id}")
    npc = ref.get() or {}
    cooldowns = npc.get("cooldowns", {})
    updated_cooldowns = {k: v-1 for k, v in cooldowns.items() if v > 1}

    npc["cooldowns"] = updated_cooldowns
    ref.set(npc)

    return updated_cooldowns


def resolve_saving_throw(stat_mod, dc):
    roll = random.randint(1, 20) + stat_mod
    return {"roll": roll, "modifier": stat_mod, "dc": dc, "success": roll >= dc}

# === XP & Party-level Management ===
def get_total_party_level(party_id, mode="sum"):
    party = db.reference(f"/parties/{party_id}").get() or {"members": []}
    total_level = sum(db.reference(f"/players/{m}").get().get("level", 1) for m in party["members"])

    return total_level if mode == "sum" else total_level // len(party["members"])


def award_xp_to_party(party_id, amount):
    party = db.reference(f"/parties/{party_id}").get() or {"members": []}
    awarded = {}

    for member_id in party["members"]:
        char_ref = db.reference(f"/players/{member_id}")
        char = char_ref.get() or {}
        char["XP"] = char.get("XP", 0) + amount
        char_ref.set(char)
        awarded[member_id] = char["XP"]

    return awarded
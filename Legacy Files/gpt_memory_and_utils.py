import os
import json
import random
import math
import uuid
import logging
from datetime import datetime, timezone, timedelta
from itertools import combinations
from random import randint

import openai
from openai import ChatCompletion
from firebase_admin import db

# === ChromaDB Imports for Memory Management ===
from chromadb import PersistentClient, Client

# -----------------------------------------------------------------------
#   GPT Router, Logging, and Utility Functions
# -----------------------------------------------------------------------

def gpt_router(score=5, flags=None):
    """
    Routes to the appropriate GPT model based on importance score and flags.
    """
    flags = flags or {}

    if flags.get("plot") or flags.get("secret") or flags.get("emotional"):
        return "gpt-4"
    if flags.get("force_gpt4"):
        return "gpt-4"

    if score <= 3:
        return "gpt-4o-mini"
    elif 4 <= score <= 7:
        return "gpt-4o"
    else:
        return "gpt-4"


def log_gpt_usage(model, usage):
    """
    Log GPT API usage data to Firebase for monitoring purposes.
    """
    try:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        log_ref = db.reference(f'/gpt_usage/{model}/{timestamp}')
        log_ref.set(usage)
    except Exception as e:
        logging.error("Error logging GPT usage: %s", str(e))


def call_gpt_model(model, messages, temperature=0.7, max_tokens=150):
    """
    Make a call to the GPT API using the provided model and messages.
    Returns either parsed JSON or raw text if JSON fails to parse.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        usage = response.get("usage", {})
        log_gpt_usage(model, usage)
        message_content = response.choices[0].message.content.strip()

        try:
            return json.loads(message_content)
        except Exception:
            return message_content
    except Exception as e:
        logging.error(f"Error calling GPT model {model}: {str(e)}")
        return None


def get_dm_response(context, prompt, importance_score=5, flags=None, temperature=0.7, max_tokens=150):
    """
    High-level DM prompt function: returns a 'Dungeon Master' style response.
    """
    model = gpt_router(score=importance_score, flags=flags)
    messages = [
        {"role": "system", "content": "You are a Dungeon Master managing a persistent fantasy world."},
        {"role": "user", "content": f"Context: {context}\nPrompt: {prompt}"}
    ]
    return call_gpt_model(model, messages, temperature, max_tokens)


def get_npc_response(npc_context, conversation_history, prompt, importance_score=5, flags=None, temperature=0.7, max_tokens=150):
    """
    High-level NPC prompt function.
    """
    model = gpt_router(score=importance_score, flags=flags)
    messages = [
        {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation."},
        {"role": "user", "content": f"NPC Context: {npc_context}\nConversation History: {conversation_history}\nPrompt: {prompt}"}
    ]
    return call_gpt_model(model, messages, temperature, max_tokens)


def score_interaction(flags: dict) -> int:
    """
    Assigns an importance score (1–10) based on flags for GPT model routing.
    """
    if not flags:
        return 5

    score = 5
    if flags.get("emotionally_charged"):
        score += 2
    if flags.get("conflict_type") in ["loyalty", "morality", "betrayal"]:
        score += 2

    scope = flags.get("scope", "")
    if scope == "regional":
        score += 1
    elif scope == "global":
        score += 2

    if flags.get("force_gpt4"):
        return 10

    return min(score, 10)

# -----------------------------------------------------------------------
#  Short-Term / Long-Term Memory via ChromaDB
# -----------------------------------------------------------------------

# Initialize Short-Term Memory (Chroma Persistent)
short_term_client = PersistentClient(path="./chroma_store")
short_term_collection = short_term_client.get_or_create_collection(name="npc_short_term_memory")

# Initialize Long-Term Memory (Chroma In-Memory or separate DB)
long_term_client = Client()
long_term_collection = long_term_client.get_or_create_collection(name="visual_dm_memory")

def parse_iso(ts):
    """
    Helper to parse an ISO timestamp, handling trailing 'Z'.
    """
    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(ts)
    except:
        return None


# ------------------- Short-Term Memory Functions -------------------

def store_interaction(npc_id, player_id, interaction_text, tags=None):
    """
    Stores an interaction in short-term memory (Chroma).
    """
    memory_id = str(uuid.uuid4())
    meta = {
        "npc_id": npc_id,
        "player_id": player_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    if tags:
        meta.update(tags)

    short_term_collection.add(
        documents=[interaction_text],
        metadatas=[meta],
        ids=[memory_id]
    )
    return memory_id


def get_recent_interactions(npc_id, player_id=None, limit=5):
    """
    Fetch short-term memory for an NPC, optionally filtering by player_id.
    """
    filters = {"npc_id": npc_id}
    if player_id:
        filters["player_id"] = player_id

    results = short_term_collection.query(
        query_texts=["recent conversation"],  # dummy text
        n_results=limit,
        where=filters
    )
    return results["documents"][0] if results.get("documents") else []


def summarize_and_clean_memory(npc_id, player_id=None, days_old=3):
    """
    Summarizes older short-term memory entries and removes them from Chroma.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days_old)

    filters = {"npc_id": npc_id}
    if player_id:
        filters["player_id"] = player_id

    results = short_term_collection.get(where=filters)
    if not results or not results.get("metadatas"):
        return {"message": "No memory to clean."}

    expired_docs = []
    for doc_id, meta, text in zip(results["ids"], results["metadatas"], results["documents"]):
        ts = parse_iso(meta.get("timestamp", ""))
        if ts and ts < cutoff:
            expired_docs.append((doc_id, text))

    if not expired_docs:
        return {"message": "No expired memory entries."}

    combined_text = "\n".join(t for _, t in expired_docs)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are summarizing old NPC dialogue. Recap emotions and key facts."},
                {"role": "user", "content": combined_text}
            ],
            temperature=0.5,
            max_tokens=250
        )
        summary = response.choices[0].message.content.strip()
        usage = response.get("usage", {})
        log_gpt_usage("gpt-3.5-turbo", usage)
    except Exception as e:
        return {"error": f"GPT summarization failed: {str(e)}"}

    mem_ref = db.reference(f"/npc_memory/{npc_id.lower()}")
    existing = mem_ref.get() or {}
    new_summary = existing.get("summary", "") + "\n" + summary
    mem_ref.update({"summary": new_summary.strip()})

    to_delete = [doc_id for doc_id, _ in expired_docs]
    short_term_collection.delete(ids=to_delete)

    return {
        "message": f"Summarized and cleaned {len(to_delete)} memory entries.",
        "summary": summary
    }


# ------------------- Long-Term Memory Functions -------------------

def store_log(entry: dict):
    """
    Stores a log entry in the long-term memory (Chroma).
    """
    if "text" not in entry:
        return {"error": "Missing log text"}

    uid = f"{entry.get('speaker','unknown')}_{datetime.utcnow().isoformat()}"
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


def query_recent(speaker_id: str, region=None, n=5):
    """
    Queries the long-term memory for logs from a speaker in the last 3 hours.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=3)

    filters = {"$and": []}
    if speaker_id:
        filters["$and"].append({"speaker": speaker_id})
    if region:
        filters["$and"].append({"region": region})
    filters["$and"].append({"timestamp": {"$gt": cutoff.isoformat()}})

    results = long_term_collection.get(where=filters)
    if not results or not results.get("documents"):
        return []

    meta_docs = list(zip(results["metadatas"], results["documents"]))
    def parse_ts(m):
        return parse_iso(m[0].get("timestamp", "")) or datetime.min

    meta_docs.sort(key=parse_ts, reverse=True)
    top = meta_docs[:n]

    out = []
    for meta, doc in top:
        out.append({"text": doc, "meta": meta})
    return out


def summarize_memory(npc_id, player_id, logs):
    """
    Summarize a list of log entries to see what the NPC remembers about a player.
    """
    if not logs:
        return None

    lines = [f"- {entry['text']}" for entry in logs]
    prompt = (
        "You are an NPC in a fantasy world. Summarize your recent interactions with this player.\n\n"
        f"Recent Logs:\n{chr(10).join(lines)}\n\n"
        "In 1–2 sentences, what stood out?"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a reflective NPC summarizing memory of the player."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=150
        )
        usage = response.get("usage", {})
        log_gpt_usage("gpt-4", usage)
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def update_long_term_memory(npc_id, player_id, region=None):
    """
    Gather recent logs about a player in a region, generate a summary,
    and store it in Firebase under /npcs/<npc_id>/long_term_memory/<player_id>.
    """
    logs = query_recent(speaker_id=player_id, region=region, n=10)
    summary = summarize_memory(npc_id, player_id, logs)
    if summary:
        ref = db.reference(f"/npcs/{npc_id}/long_term_memory/{player_id}")
        ref.set({"last_summary": summary, "summary_date": datetime.utcnow().isoformat()})
        return {"npc_id": npc_id, "player_id": player_id, "summary": summary}
    return {"error": "No recent memory to summarize"}

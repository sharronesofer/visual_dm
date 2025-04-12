from chromadb import PersistentClient, Client
from datetime import datetime, timedelta
from firebase_admin import db
import openai
import json
import logging
import random
import uuid

# === Clients and Collections ===
short_term_client = PersistentClient(path="./chroma_store")
short_term_collection = short_term_client.get_or_create_collection(name="npc_short_term_memory")

long_term_client = Client()
long_term_collection = long_term_client.get_or_create_collection(name="visual_dm_memory")

# === UTILS ===

def parse_iso(ts):
    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None

# === SHORT-TERM MEMORY ===

def store_interaction(npc_id, player_id, interaction_text, tags=None):
    memory_id = str(uuid.uuid4())
    metadata = {
        "npc_id": npc_id,
        "player_id": player_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if tags:
        metadata.update(tags)

    short_term_collection.add(
        documents=[interaction_text],
        metadatas=[metadata],
        ids=[memory_id]
    )
    return memory_id

def get_recent_interactions(npc_id, player_id=None, limit=5):
    filters = {"npc_id": npc_id}
    if player_id:
        filters["player_id"] = player_id

    results = short_term_collection.query(
        query_texts=["recent conversation"],
        n_results=limit,
        where=filters
    )
    return results["documents"][0] if results.get("documents") else []

def summarize_and_clean_memory(npc_id, player_id=None, days_old=3):
    """
    Summarizes expired short-term memory entries for an NPC (optionally per player),
    stores the summary in Firebase, and deletes the old entries.
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

    combined_text = "\n".join(text for _, text in expired_docs)
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
    except Exception as e:
        return {"error": f"GPT summarization failed: {str(e)}"}

    mem_ref = db.reference(f"/npc_memory/{npc_id.lower()}")
    existing = mem_ref.get() or {}
    combined = (existing.get("summary", "") + "\n" + summary).strip()
    mem_ref.update({"summary": combined})

    ids_to_delete = [doc_id for doc_id, _ in expired_docs]
    short_term_collection.delete(ids=ids_to_delete)

    return {
        "message": f"Summarized and cleaned {len(ids_to_delete)} expired memory entries.",
        "summary": summary
    }

# === LONG-TERM MEMORY ===

def store_log(entry: dict):
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

def query_recent(speaker_id: str, region=None, n=5):
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=3)

    filters = {
        "$and": [
            {"speaker": speaker_id} if speaker_id else {},
            {"region": region} if region else {},
            {"timestamp": {"$gt": cutoff.isoformat()}}
        ]
    }

    results = long_term_collection.get(where=filters)
    memory = sorted(results["metadatas"], key=lambda x: x["timestamp"], reverse=True)
    top = memory[:n]
    return [{"text": doc, "meta": meta} for doc, meta in zip(results["documents"], top)]

def summarize_memory(npc_id, player_id, logs):
    if not logs:
        return None

    lines = [f"- {log['text']}" for log in logs]
    prompt = (
        "You are an NPC in a fantasy world. Summarize your recent interactions with the player.\n\n"
        f"Recent Logs:\n{chr(10).join(lines)}\n\n"
        "In 1–2 sentences, what stood out and what do you remember?"
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
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def update_long_term_memory(npc_id, player_id, region=None):
    recent_logs = query_recent(speaker_id=player_id, region=region, n=10)
    summary = summarize_memory(npc_id, player_id, recent_logs)

    if summary:
        ref = db.reference(f"/npcs/{npc_id}/long_term_memory/{player_id}")
        ref.set({
            "last_summary": summary,
            "summary_date": datetime.utcnow().isoformat()
        })
        return {
            "npc_id": npc_id,
            "player_id": player_id,
            "summary": summary
        }

    return {"error": "No recent memory to summarize"}

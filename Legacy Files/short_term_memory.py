# short_term_memory.py

from chromadb import PersistentClient
from datetime import datetime, timedelta
from firebase_admin import db
import openai
import uuid

# === Setup ===
chroma_client = PersistentClient(path="./chroma_store")
memory_collection = chroma_client.get_or_create_collection(name="npc_short_term_memory")


# === Store Memory ===

def store_interaction(npc_id, player_id, interaction_text, tags=None):
    """
    Stores a single NPC interaction in the ChromaDB short-term memory system.
    """
    memory_id = str(uuid.uuid4())
    metadata = {
        "npc_id": npc_id,
        "player_id": player_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if tags:
        metadata.update(tags)

    memory_collection.add(
        documents=[interaction_text],
        metadatas=[metadata],
        ids=[memory_id]
    )
    return memory_id


# === Retrieve Memory ===

def get_recent_interactions(npc_id, player_id=None, limit=5):
    """
    Retrieves up to `limit` recent interactions for the NPC (and optional player).
    """
    filters = {"npc_id": npc_id}
    if player_id:
        filters["player_id"] = player_id

    results = memory_collection.query(
        query_texts=["recent conversation"],
        n_results=limit,
        where=filters
    )

    return results["documents"][0] if results.get("documents") else []


# === Summarize and Clean Old Memory ===

def parse_iso(ts):
    """
    Converts ISO timestamp to datetime object (handles trailing Z).
    """
    try:
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except Exception:
        return None

def summarize_and_clean_memory(npc_id, player_id=None, days_old=3):
    """
    Summarizes expired short-term memories and stores summary in Firebase.
    Deletes expired entries from ChromaDB.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days_old)

    filters = {"npc_id": npc_id}
    if player_id:
        filters["player_id"] = player_id

    results = memory_collection.get(where=filters)
    if not results or not results.get("metadatas"):
        return {"message": "No memory to clean."}

    expired_docs = []
    kept_docs = []

    for doc_id, meta, text in zip(results["ids"], results["metadatas"], results["documents"]):
        ts = parse_iso(meta.get("timestamp", ""))
        if ts and ts < cutoff:
            expired_docs.append((doc_id, text))
        else:
            kept_docs.append((doc_id, text))

    if not expired_docs:
        return {"message": "No expired memory entries."}

    combined_text = "\n".join(text for _, text in expired_docs)
    system_prompt = (
        "You are summarizing old NPC dialogue logs. Provide a short, in-character recap of key events, emotions, or facts."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": combined_text}
            ],
            temperature=0.5,
            max_tokens=250
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        return {"error": f"GPT summarization failed: {str(e)}"}

    # Update Firebase memory summary
    mem_ref = db.reference(f"/npc_memory/{npc_id.lower()}")
    existing = mem_ref.get() or {}
    current_summary = existing.get("summary", "")
    combined_summary = (current_summary + "\n" + summary).strip()
    mem_ref.update({"summary": combined_summary})

    # Delete expired memory
    ids_to_delete = [doc_id for doc_id, _ in expired_docs]
    memory_collection.delete(ids=ids_to_delete)

    return {
        "npc_id": npc_id,
        "player_id": player_id,
        "deleted_count": len(ids_to_delete),
        "summary": summary,
        "status": "success"
    }

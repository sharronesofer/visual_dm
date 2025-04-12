from flask import Blueprint, request, jsonify
import openai, uuid
from firebase_admin import db
from chromadb import PersistentClient
from datetime import datetime, timedelta

npc_interactions_bp = Blueprint('npc_interactions', __name__)

short_term_client = PersistentClient(path="./chroma_store")
short_term_collection = short_term_client.get_or_create_collection("npc_short_term_memory")

def store_interaction(npc_id, character_id, interaction_text, tags=None):
    memory_id = str(uuid.uuid4())
    metadata = {
        "npc_id": npc_id,
        "character_id": character_id,
        "timestamp": datetime.utcnow().isoformat(),
        **(tags or {})
    }
    short_term_collection.add([interaction_text], [metadata], [memory_id])
    return memory_id

def get_recent_interactions(npc_id, character_id=None, limit=5):
    filters = {"npc_id": npc_id}
    if character_id:
        filters["character_id"] = character_id
    results = short_term_collection.query(["recent conversation"], n_results=limit, where=filters)
    return results.get("documents", [[]])[0]

def summarize_and_clean_memory(npc_id, character_id=None, days_old=3):
    cutoff = datetime.utcnow() - timedelta(days=days_old)
    filters = {"npc_id": npc_id}
    if character_id:
        filters["character_id"] = character_id
    results = short_term_collection.get(where=filters)

    expired = [
        (doc_id, text) for doc_id, meta, text in zip(
            results["ids"], results["metadatas"], results["documents"]
        ) if datetime.fromisoformat(meta["timestamp"]) < cutoff
    ]

    if not expired:
        return {"message": "No expired entries."}

    combined_text = "\n".join(text for _, text in expired)
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize NPC dialogue concisely."},
            {"role": "user", "content": combined_text}
        ]
    )

    summary = response.choices[0].message.content.strip()
    summary_ref = db.reference(f"/npc_memory/{npc_id}/summary")
    existing_summary = summary_ref.get() or ""
    summary_ref.set(existing_summary + "\n" + summary)

    short_term_collection.delete(ids=[doc_id for doc_id, _ in expired])

    return {"message": f"Cleaned {len(expired)} entries.", "summary": summary}

def generate_npc_response_with_arc_context(npc_id, character_id, prompt):
    npc_data = db.reference(f"/npcs/{npc_id}").get()
    player_data = db.reference(f"/players/{character_id}").get()

    npc_arc = npc_data.get("current_arcs", [])
    player_arc = player_data.get("current_arc", "")

    arc_context = f"NPC Arc: {npc_arc[-1]['arc_name']} ({npc_arc[-1]['status']})" if npc_arc else "NPC Arc: None"
    player_context = f"Player Arc: {player_arc}"
    full_prompt = f"{arc_context} {player_context}\n{prompt}"

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an NPC generating context-aware dialogue."},
            {"role": "user", "content": full_prompt}
        ]
    )

    return response.choices[0].message.content.strip()

# memory_cleanup.py

from chromadb import PersistentClient
from datetime import datetime, timedelta
from firebase_admin import db
import openai

# Init Chroma and collection
chroma_client = PersistentClient(path="./chroma_store")
memory_collection = chroma_client.get_or_create_collection(name="npc_short_term_memory")

# Convert ISO string → datetime
def parse_iso(ts):
    try:
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except Exception:
        return None

def summarize_and_clean_memory(npc_id, player_id=None, days_old=3):
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days_old)

    filters = {"npc_id": npc_id}
    if player_id:
        filters["player_id"] = player_id

    # Fetch all matching documents
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

    # Summarize expired memory using GPT
    text_to_summarize = "\n".join(text for _, text in expired_docs)
    system_prompt = (
        "You are summarizing old NPC dialogue. Provide a short recap of the events, feelings, and key info exchanged."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text_to_summarize}
            ],
            temperature=0.5,
            max_tokens=250
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        return {"error": f"GPT summarization failed: {str(e)}"}

    # Push summary into Firebase
    mem_ref = db.reference(f"/npc_memory/{npc_id.lower()}")
    existing = mem_ref.get() or {}
    current_summary = existing.get("summary", "")
    new_summary = current_summary + "\n" + summary
    mem_ref.update({"summary": new_summary.strip()})

    # Delete expired memory from Chroma
    ids_to_delete = [doc_id for doc_id, _ in expired_docs]
    memory_collection.delete(ids=ids_to_delete)

    return {
        "message": f"Summarized and cleaned {len(ids_to_delete)} expired memory entries.",
        "summary": summary
    }

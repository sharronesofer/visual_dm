import chromadb
from datetime import datetime, timedelta
import openai
from firebase_admin import db

client = chromadb.Client()
collection = client.get_or_create_collection(name="visual_dm_memory")

def store_log(entry: dict):
    """
    Stores a log entry in ChromaDB.
    Entry should contain: speaker, text, region, tags, timestamp
    """
    if "text" not in entry:
        return {"error": "Missing log text"}
    
    uid = f"{entry.get('speaker', 'unknown')}_{datetime.utcnow().isoformat()}"
    collection.add(
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
    Returns top N most recent logs related to a speaker or region.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=3)  # short-term only

    results = collection.get(where={
        "$and": [
            {"speaker": speaker_id} if speaker_id else {},
            {"region": region} if region else {},
            {"timestamp": {"$gt": cutoff.isoformat()}}
        ]
    })

    # Sort by recency
    memory = sorted(results["metadatas"], key=lambda x: x["timestamp"], reverse=True)
    top = memory[:n]
    return [{"text": doc, "meta": meta} for doc, meta in zip(results["documents"], top)]

def summarize_memory(npc_id, player_id, logs):
    if not logs:
        return None

    text_lines = [f"- {log['text']}" for log in logs]
    prompt = (
        "You are an NPC in a fantasy roleplaying world. Summarize your recent interactions with the player.\n\n"
        "Recent Logs:\n"
        f"{chr(10).join(text_lines)}\n\n"
        "In 1–2 sentences, summarize what stood out to you and what you remember long-term:"
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
    recent = query_recent(speaker_id=player_id, region=region, n=10)
    summary = summarize_memory(npc_id, player_id, recent)

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
    else:
        return {"error": "No recent memory to summarize"}
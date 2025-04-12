import chromadb
import openai
import uuid
from datetime import datetime, timedelta
from firebase_admin import db

client = chromadb.Client()
collection = client.get_or_create_collection(name="visual_dm_memory")

def store_log(entry: dict):
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
    cutoff = (datetime.utcnow() - timedelta(hours=3)).isoformat()
    conditions = [{"timestamp": {"$gt": cutoff}}]
    if speaker_id:
        conditions.append({"speaker": speaker_id})
    if region:
        conditions.append({"region": region})

    results = collection.get(where={"$and": conditions})
    memory = sorted(results["metadatas"], key=lambda x: x["timestamp"], reverse=True)[:n]
    return [{"text": doc, "meta": meta} for doc, meta in zip(results["documents"], memory)]

def summarize_memory(npc_id, player_id, logs):
    if not logs:
        return None

    text_lines = "\n".join([f"- {log['text']}" for log in logs])
    prompt = f"Summarize recent interactions:\n\n{text_lines}\n\nSummary:"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=150
    )

    return response.choices[0].message.content.strip()

def update_long_term_memory(npc_id, player_id, region=None):
    recent_logs = query_recent(player_id, region, n=10)
    summary = summarize_memory(npc_id, player_id, recent_logs)

    if summary:
        db.reference(f"/npcs/{npc_id}/long_term_memory/{player_id}").set({
            "last_summary": summary,
            "summary_date": datetime.utcnow().isoformat()
        })
        return {"npc_id": npc_id, "summary": summary}
    return {"error": "No recent memory to summarize"}

def create_quest_log_entry(player_id, npc_name, summary, region=None, poi=None):
    note_id = str(uuid.uuid4())
    log_ref = db.reference(f"/quest_log/{player_id}/{note_id}")
    log_data = {
        "note_id": note_id,
        "origin_npc": npc_name,
        "region": region or "unknown",
        "poi": poi or "unknown",
        "first_heard": datetime.utcnow().isoformat(),
        "status": "unresolved",
        "notes": [summary],
        "current_priority": 4
    }
    log_ref.set(log_data)
    return log_data

def append_to_existing_log(player_id, npc_name, summary):
    ref = db.reference(f"/quest_log/{player_id}")
    logs = ref.get() or {}

    for log in logs.values():
        if log["origin_npc"] == npc_name and log["status"] == "unresolved":
            log["notes"].append(summary)
            log["current_priority"] += 1
            ref.child(log["note_id"]).set(log)
            return log

    return create_quest_log_entry(player_id, npc_name, summary)
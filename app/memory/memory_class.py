import uuid
from datetime import datetime, timedelta
from firebase_admin import db
from dateutil.parser import parse as parse_iso
from app.chromadb_client import short_term_collection, long_term_collection
import openai
import logging


class MemoryManager:
    def __init__(self, npc_id, character_id=None):
        self.npc_id = npc_id
        self.character_id = character_id
        self.max_chars = 4000
        self.chunk_size = 1000
        self.conversation_mem = []
        self.summaries = []
        self.char_count = 0

    def store_interaction(self, text, tags=None):
        memory_id = str(uuid.uuid4())
        metadata = {
            "npc_id": self.npc_id,
            "character_id": self.character_id,
            "timestamp": datetime.utcnow().isoformat(),
            **(tags or {})
        }

        short_term_collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[memory_id]
        )
        self._accumulate_for_summarization("user", text)

    def _accumulate_for_summarization(self, role, content):
        self.conversation_mem.append({"role": role, "content": content})
        self.char_count += len(content)
        while self.char_count > self.max_chars:
            chunk, size = [], 0
            while self.conversation_mem and size < self.chunk_size:
                msg = self.conversation_mem.pop(0)
                size += len(msg["content"])
                self.char_count -= len(msg["content"])
                chunk.append(msg)
            summary = self._summarize_chunk(chunk)
            self.summaries.append(summary)

    def _summarize_chunk(self, messages):
        try:
            combined = "".join(f"{m['role'].upper()}: {m['content']}\n" for m in messages)
            res = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Summarize the conversation in 1-2 concise sentences."},
                    {"role": "user", "content": combined}
                ],
                temperature=0.5,
                max_tokens=200
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Summarization error: {e}")
            return "(error summarizing)"

    def update_long_term_summary(self, region=None):
        logs = self.query_recent(region, 10)
        summary = self._summarize_memory(logs)
        if summary:
            ref = db.reference(f"/npcs/{self.npc_id}/long_term_memory/{self.character_id}")
            ref.set({
                "last_summary": summary,
                "summary_date": datetime.utcnow().isoformat()
            })
            return summary
        return None

    def _summarize_memory(self, logs):
        if not logs:
            return None
        lines = [f"- {log['text']}" for log in logs]
        prompt = "\n".join(lines)
        try:
            res = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Summarize recent interactions in 1-2 sentences."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=150
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Summary generation failed: {e}")
            return None

    def query_recent(self, region=None, n=5):
        cutoff = datetime.utcnow() - timedelta(hours=3)
        filters = {"$and": [{"speaker": self.character_id}, {"timestamp": {"$gt": cutoff.isoformat()}}]}
        if region:
            filters["$and"].append({"region": region})
        results = long_term_collection.get(where=filters)
        if not results or not results.get("documents"):
            return []
        meta_docs = sorted(
            zip(results["metadatas"], results["documents"]),
            key=lambda m: parse_iso(m[0].get("timestamp", "")) or datetime.min,
            reverse=True
        )[:n]
        return [{"text": doc, "meta": meta} for meta, doc in meta_docs]

    def summarize_and_clean_short_term(self, days_old=3):
        cutoff = datetime.utcnow() - timedelta(days=days_old)
        filters = {"npc_id": self.npc_id}
        if self.character_id:
            filters["character_id"] = self.character_id
        results = short_term_collection.get(where=filters)
        expired = [
            (doc_id, text) for doc_id, meta, text in zip(results["ids"], results["metadatas"], results["documents"])
            if datetime.fromisoformat(meta["timestamp"]) < cutoff
        ]
        if not expired:
            return {"message": "No expired entries."}
        summary = " ".join(text for _, text in expired)
        mem_ref = db.reference(f"/npc_memory/{self.npc_id.lower()}")
        existing = mem_ref.get() or {}
        combined = (existing.get("summary", "") + "\n" + summary).strip()
        mem_ref.update({"summary": combined})
        short_term_collection.delete(ids=[doc_id for doc_id, _ in expired])
        return {"message": f"Cleaned {len(expired)} entries.", "summary": summary[:200] + "..."}

    def get_recent_interactions(self, limit=5):
        results = short_term_collection.query(
            query_texts=["recent conversation"],
            n_results=limit,
            where={"npc_id": self.npc_id, "character_id": self.character_id}
        )
        return results.get("documents", [[]])[0]

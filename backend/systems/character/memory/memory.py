#This class manages short- and long-term memory for NPCs, integrating with:
#ChromaDB for memory storage and query
#Firebase for persistent summaries
#OpenAI for summarization
#Conversation tracking and cleanup logic
#It is a cornerstone system of memory, npc, firebase, and gpt integrations.

import uuid
from uuid import uuid4
from datetime import datetime, timedelta
from firebase_admin import db
from dateutil.parser import parse as parse_iso
# from app.chromadb_client import short_term_collection, long_term_collection
import openai
import logging


class Memory:
    """
    Represents a single memory instance with decay mechanics and metadata.
    """
    def __init__(self, content, importance, associated_entities, decay_rate, tags, type_):
        """
        Initialize a new Memory instance.
        :param content: Textual content of the memory.
        :param importance: Initial importance of the memory.
        :param associated_entities: List of associated entity IDs.
        :param decay_rate: Decay rate per second for regular memories.
        :param tags: List of tags for categorization and query.
        :param type_: 'core' or 'regular'.
        """
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow()
        self.importance = importance
        self.content = content
        self.associated_entities = associated_entities or []
        self.decay_rate = decay_rate
        self.tags = tags or []
        self.type = type_  # 'core' or 'regular'
        self.current_importance = importance
    def decay(self, delta_seconds):
        """
        Apply decay to the memory's importance over time.
        :param delta_seconds: Time in seconds to decay.
        """
        if self.type == 'core':
            return
        self.current_importance = max(0, self.current_importance - self.decay_rate * delta_seconds)
    def is_expired(self, threshold):
        """
        Determine if the memory is expired based on a threshold.
        :param threshold: Importance threshold for expiration.
        :return: True if expired, False otherwise.
        """
        return self.type == 'regular' and self.current_importance < threshold

class MemoryManager:
    """
    Manages a collection of memories, including decay, event emission, and queries.
    """
    def __init__(self, npc_id, character_id=None):
        """
        Initialize a new MemoryManager for an entity.
        :param npc_id: The NPC/entity ID.
        :param character_id: Optional character ID.
        """
        self.npc_id = npc_id
        self.character_id = character_id
        self.max_chars = 4000
        self.chunk_size = 1000
        self.conversation_mem = []
        self.summaries = []
        self.char_count = 0
        self.memories = []
        self.decay_threshold = 0.1
        self.observers = []

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
                model="gpt-4.1.1-nano",
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
                model="gpt-4.1.1",
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

    def add_observer(self, callback):
        """
        Register an observer callback for memory events.
        :param callback: Function(memory, event_type)
        """
        self.observers.append(callback)

    def _emit_event(self, memory, event_type):
        """
        Emit a memory event to all registered observers.
        :param memory: The Memory instance.
        :param event_type: Event type string (created, decayed, reinforced).
        """
        for cb in self.observers:
            cb(memory, event_type)
        # Optionally integrate with event bus here

    def add_memory(self, memory):
        """
        Add a new memory and emit a creation event.
        :param memory: The Memory instance to add.
        """
        self.memories.append(memory)
        self._emit_event(memory, 'created')

    def decay_memories(self, delta_seconds):
        """
        Apply decay to all memories and emit events for those that cross the threshold.
        :param delta_seconds: Time in seconds to decay.
        """
        for mem in self.memories:
            before = mem.current_importance
            mem.decay(delta_seconds)
            if before >= self.decay_threshold and mem.current_importance < self.decay_threshold:
                self._emit_event(mem, 'decayed')
        self.prune_expired()

    def prune_expired(self):
        """
        Remove expired regular memories from the collection.
        """
        self.memories = [m for m in self.memories if not m.is_expired(self.decay_threshold)]

    def reinforce_memory(self, memory_id, amount):
        """
        Reinforce a regular memory, increasing its importance and emitting an event.
        :param memory_id: The ID of the memory to reinforce.
        :param amount: Amount to increase importance by.
        """
        for mem in self.memories:
            if mem.id == memory_id and mem.type == 'regular':
                mem.current_importance = min(mem.importance, mem.current_importance + amount)
                self._emit_event(mem, 'reinforced')

    def query(self, entity_id=None, start_time=None, end_time=None, min_importance=None, max_importance=None, tags=None, type_=None):
        """
        Query memories by entity, time, importance, tags, and type.
        :param entity_id: Filter by associated entity.
        :param start_time: Filter by start timestamp.
        :param end_time: Filter by end timestamp.
        :param min_importance: Minimum importance.
        :param max_importance: Maximum importance.
        :param tags: List of tags to filter.
        :param type_: 'core' or 'regular'.
        :return: List of matching Memory instances.
        """
        result = self.memories
        if entity_id:
            result = [m for m in result if entity_id in m.associated_entities]
        if start_time:
            result = [m for m in result if m.timestamp >= start_time]
        if end_time:
            result = [m for m in result if m.timestamp <= end_time]
        if min_importance is not None:
            result = [m for m in result if m.current_importance >= min_importance]
        if max_importance is not None:
            result = [m for m in result if m.current_importance <= max_importance]
        if tags:
            result = [m for m in result if any(tag in m.tags for tag in tags)]
        if type_:
            result = [m for m in result if m.type == type_]
        return result

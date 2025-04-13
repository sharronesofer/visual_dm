from app.memory.memory_class import MemoryManager

def store_interaction(npc_id, character_id, interaction_text, tags=None):
    manager = MemoryManager(npc_id, character_id)
    manager.store_interaction(interaction_text, tags)
    return {"npc_id": npc_id, "character_id": character_id, "status": "stored"}

def update_long_term_memory(npc_id, character_id, region=None):
    manager = MemoryManager(npc_id, character_id)
    summary = manager.update_long_term_summary(region)
    if summary:
        return {"npc_id": npc_id, "character_id": character_id, "summary": summary}
    return {"error": "No recent memory to summarize"}

def summarize_and_clean_memory(npc_id, character_id=None, days_old=3):
    manager = MemoryManager(npc_id, character_id)
    return manager.summarize_and_clean_short_term(days_old)

def get_recent_interactions(npc_id, character_id=None, limit=5):
    manager = MemoryManager(npc_id, character_id)
    return manager.get_recent_interactions(limit)

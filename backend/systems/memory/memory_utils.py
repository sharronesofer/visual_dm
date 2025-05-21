#This file provides functional wrappers around the MemoryManager class and defines a belief generation routine. It also loads the .env file and initializes OpenAI's API key.
#It connects deeply with memory, npc, firebase, and gpt systems.

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import json
import openai
from dotenv import load_dotenv
from firebase_admin import db

# Import the robust MemoryManager implementation
from .memory_manager import MemoryManager, MockChromaCollection
from .memory import Memory

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Setup OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
print("🔑 Loaded GPT key from .env:", openai.api_key[:12] + "..." + openai.api_key[-4:])

# Import event dispatcher 
from backend.systems.events.models.event_dispatcher import EventDispatcher

# Create mock vector DB instances for utility functions
short_term_mock = MockChromaCollection()
long_term_mock = MockChromaCollection()
event_dispatcher = EventDispatcher.get_instance()

# Import summarization styles
from .summarization_styles import SummarizationStyle, SummarizationDetail

def get_current_game_day():
    return db.reference("/global_state").get().get("current_day", 0)

async def store_interaction(npc_id, character_id, interaction_text, tags=None):
    """Store an interaction in the memory system"""
    manager = await MemoryManager.get_instance(
        npc_id=npc_id, 
        short_term_db=short_term_mock,
        long_term_db=long_term_mock,
        event_dispatcher=event_dispatcher,
        character_id=character_id
    )
    memory_id = manager.store_interaction(interaction_text, tags)
    return {"npc_id": npc_id, "character_id": character_id, "status": "stored", "memory_id": memory_id}

async def update_long_term_memory(npc_id, character_id, region=None, style=None, detail=None):
    """Update the long-term memory summary for an NPC
    
    Args:
        npc_id: NPC ID
        character_id: Character ID 
        region: Optional region filter
        style: Optional summarization style (concise, detailed, narrative, etc.)
        detail: Optional detail level (low, medium, high)
    
    Returns:
        Summary or error dict
    """
    # Convert style and detail strings to enum values if provided
    style_enum = None
    detail_enum = None
    
    if style:
        try:
            style_enum = SummarizationStyle(style)
        except ValueError:
            return {"error": f"Invalid style '{style}'. Valid styles: {', '.join([s.value for s in SummarizationStyle])}"}
    
    if detail:
        try:
            detail_enum = SummarizationDetail(detail)
        except ValueError:
            return {"error": f"Invalid detail level '{detail}'. Valid levels: {', '.join([d.value for d in SummarizationDetail])}"}
    
    manager = await MemoryManager.get_instance(
        npc_id=npc_id, 
        short_term_db=short_term_mock,
        long_term_db=long_term_mock,
        event_dispatcher=event_dispatcher,
        character_id=character_id
    )
    summary = manager.update_long_term_summary(region, style=style_enum, detail=detail_enum)
    if summary:
        return {
            "npc_id": npc_id, 
            "character_id": character_id, 
            "summary": summary,
            "style": style,
            "detail": detail
        }
    return {"error": "No recent memory to summarize"}

async def summarize_and_clean_memory(npc_id, character_id=None, days_old=3):
    """Summarize and clean older memories"""
    manager = await MemoryManager.get_instance(
        npc_id=npc_id, 
        short_term_db=short_term_mock,
        long_term_db=long_term_mock,
        event_dispatcher=event_dispatcher,
        character_id=character_id
    )
    return manager.summarize_and_clean_short_term(days_old)

async def get_recent_interactions(npc_id, character_id=None, limit=5):
    """Get recent interactions from memory"""
    manager = await MemoryManager.get_instance(
        npc_id=npc_id, 
        short_term_db=short_term_mock,
        long_term_db=long_term_mock,
        event_dispatcher=event_dispatcher,
        character_id=character_id
    )
    return manager.get_recent_interactions(limit)

def generate_beliefs_from_meta_summary(npc_id, summaries):
    """Generate beliefs from memory summaries"""
    prompt = (
        "Here are high-level memory summaries about a character. "
        "Based on these, identify 3 to 5 short beliefs that define their worldview. "
        "Each belief should be 1 to 2 lowercase words with underscores if needed. "
        "Respond with a JSON array of belief strings.\n\n"
        f"Summaries:\n{summaries}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )

        beliefs_raw = response.choices[0].message.content.strip()
        print("🧠 GPT returned:", beliefs_raw)

        # Strip triple backticks and language tag if present
        if beliefs_raw.startswith("```"):
            beliefs_raw = beliefs_raw.strip("` \n")
            if beliefs_raw.lower().startswith("json"):
                beliefs_raw = beliefs_raw[4:].strip()

        belief_list = json.loads(beliefs_raw)

        # Save beliefs to Firebase
        belief_ref = db.reference(f"/npcs/{npc_id}/beliefs")
        for belief in belief_list:
            if isinstance(belief, str):
                belief_ref.child(belief).set(1)

        return {"npc_id": npc_id, "beliefs": belief_list}

    except Exception as e:
        return {
            "error": str(e),
            "raw": beliefs_raw if 'beliefs_raw' in locals() else "No response content"
        }

def log_permanent_memory(npc_id, event_text):
    """Log a permanent memory for an NPC"""
    ref = db.reference(f"/npc_memory/{npc_id}")
    memory = ref.get() or {}
    memory.setdefault("permanent_log", []).append({
        "event": event_text,
        "timestamp": datetime.utcnow().isoformat()
    })
    ref.set(memory)

# The following functions don't need to change since they directly use Firebase

def update_faction_memory(faction_id: str, event: str, tags=None, timestamp=None):
    """
    Updates the memory log of a faction.
    - Adds to rag_log
    - Purges entries older than 7 days into summary
    """
    if not tags:
        tags = []
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    memory_path = f"/factions/{faction_id}/memory_log"
    ref = db.reference(memory_path)
    memory = ref.get() or {"rag_log": [], "summary": ""}

    new_entry = {
        "event": event,
        "tags": tags,
        "timestamp": timestamp
    }

    memory["rag_log"].append(new_entry)

    # Purge old entries to summary after 7 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    new_rag = []
    expired_events = []

    for entry in memory["rag_log"]:
        ts = entry.get("timestamp", "")
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        try:
            entry_ts = datetime.fromisoformat(ts)
        except Exception:
            continue
        if entry_ts < cutoff:
            expired_events.append(entry["event"])
        else:
            new_rag.append(entry)

    memory["rag_log"] = new_rag
    if expired_events:
        memory["summary"] += " " + " ".join(expired_events)
        memory["summary"] = memory["summary"].strip()

    ref.set(memory)
    return memory

def update_region_memory(region_name: str, event: str, tags=None, timestamp=None):
    """
    Updates the memory log of a region.
    - Adds to rag_log
    - Summarizes events older than 28 days
    """
    if not tags:
        tags = []
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    memory_path = f"/regional_state/{region_name}/region_log"
    ref = db.reference(memory_path)
    memory = ref.get() or {"rag_log": [], "summary": ""}

    new_entry = {
        "event": event,
        "tags": tags,
        "timestamp": timestamp
    }

    memory["rag_log"].append(new_entry)

    # Purge old entries to summary after 28 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=28)
    new_rag = []
    expired_events = []

    for entry in memory["rag_log"]:
        ts = entry.get("timestamp", "")
        if ts.endswith("Z"):
            ts = ts.replace("Z", "+00:00")
        try:
            entry_ts = datetime.fromisoformat(ts)
        except Exception:
            continue
        if entry_ts < cutoff:
            expired_events.append(entry["event"])
        else:
            new_rag.append(entry)

    memory["rag_log"] = new_rag
    if expired_events:
        memory["summary"] += " " + " ".join(expired_events)
        memory["summary"] = memory["summary"].strip()

    ref.set(memory)
    return memory

def update_world_memory(event: str, tags=None, timestamp=None):
    """
    Stores a world-scale event into /world_log/<day>/memory_log.
    - Events are grouped per day
    - Summarized if they are 7+ days old
    """
    if not tags:
        tags = []
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    current_day = get_current_game_day()
    memory_path = f"/world_log/{current_day}/memory_log"
    ref = db.reference(memory_path)
    memory = ref.get() or {"rag_log": [], "summary": ""}

    new_entry = {
        "event": event,
        "tags": tags,
        "timestamp": timestamp
    }

    memory["rag_log"].append(new_entry)

    # Purge old entries if older than 7 days
    all_days = db.reference("/world_log").get() or {}
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    for day_key, day_data in all_days.items():
        if not day_data.get("memory_log"):
            continue
        rag_log = day_data["memory_log"].get("rag_log", [])
        expired_events = []
        new_rag = []

        for entry in rag_log:
            ts = entry.get("timestamp", "")
            if ts.endswith("Z"):
                ts = ts.replace("Z", "+00:00")
            try:
                entry_ts = datetime.fromisoformat(ts)
            except Exception:
                continue
            if entry_ts < cutoff:
                expired_events.append(entry["event"])
            else:
                new_rag.append(entry)

        if expired_events:
            summary = day_data["memory_log"].get("summary", "")
            summary += " " + " ".join(expired_events)
            summary = summary.strip()

            db.reference(f"/world_log/{day_key}/memory_log").set({
                "rag_log": new_rag,
                "summary": summary
            })

    # Save today's updated log
    ref.set(memory)
    return memory

def add_touchstone_memory(npc_id: str, event: str, tags=None, timestamp=None):
    """
    Adds a permanent emotional memory to an NPC.
    These do not expire and are available for GPT belief/narrative context.
    """
    if not tags:
        tags = []
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    memory_path = f"/npc_memory/{npc_id}/touchstones"
    ref = db.reference(memory_path)
    current = ref.get() or []

    current.append({
        "event": event,
        "tags": tags,
        "timestamp": timestamp
    })

    ref.set(current)

def process_gpt_memory_entry(npc_id: str, gpt_memory: dict):
    """
    Routes a GPT-generated memory to RAG log or touchstone depending on flags or tags.
    gpt_memory must contain: 'event', and optionally: 'tags', 'touchstone', 'timestamp'
    """
    event = gpt_memory.get("event")
    if not event:
        return {"error": "No event provided."}

    tags = gpt_memory.get("tags", [])
    timestamp = gpt_memory.get("timestamp", datetime.utcnow().isoformat())

    # Define emotion-sensitive tags
    emotional_tags = {"death", "betrayal", "party_change", "recruitment", "loss", "sacrifice", "heroism"}

    # Decision logic
    is_touchstone = (
        gpt_memory.get("touchstone", False)
        or any(tag in emotional_tags for tag in tags)
        or "trauma" in tags
    )

    if is_touchstone:
        add_touchstone_memory(npc_id, event, tags, timestamp)
        return {"status": "touchstone", "event": event}
    else:
        # Changed to update_faction_memory since update_npc_memory doesn't exist
        update_faction_memory(npc_id, event, tags, timestamp)
        return {"status": "rag_log", "event": event}

def update_poi_memory(region, poi_id, summary, tags=None):
    log_entry = {
        "summary": summary,
        "tags": tags or [],
        "timestamp": datetime.utcnow().isoformat()
    }
    ref = db.reference(f"/poi_memory/{region}/{poi_id}")
    entries = ref.get() or []
    entries.append(log_entry)
    ref.set(entries)

async def get_summarization_styles():
    """Get available summarization styles and detail levels
    
    Returns:
        Dictionary with styles and detail level information
    """
    # Initialize a memory manager to access the summarization styles
    manager = await MemoryManager.get_instance(
        npc_id="temp", 
        short_term_db=short_term_mock,
        long_term_db=long_term_mock,
        event_dispatcher=event_dispatcher
    )
    
    return manager.get_available_summarization_styles()

async def retrieve_memories_by_emotion(npc_id, emotion, min_intensity=0.3, limit=10):
    """Retrieve memories for an NPC based on emotional content
    
    Args:
        npc_id: The NPC's ID
        emotion: The emotion to filter by (e.g., 'joy', 'fear')
        min_intensity: Minimum emotional intensity threshold (0.0-1.0)
        limit: Maximum number of memories to return
        
    Returns:
        List of memories with emotional association
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Retrieve memories by emotion
        memories = manager.retrieve_memories_by_emotion(
            emotion=emotion,
            min_intensity=min_intensity,
            limit=limit
        )
        
        return {"memories": memories, "count": len(memories)}
    except Exception as e:
        logging.error(f"Error retrieving memories by emotion: {str(e)}")
        return {"error": str(e)}

async def retrieve_memories_by_cognitive_frame(npc_id, frame, limit=10):
    """Retrieve memories for an NPC based on cognitive frame
    
    Args:
        npc_id: The NPC's ID
        frame: The cognitive frame to filter by
        limit: Maximum number of memories to return
        
    Returns:
        List of memories matching the cognitive frame
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Retrieve memories by cognitive frame
        memories = manager.retrieve_memories_by_cognitive_frame(
            frame=frame,
            limit=limit
        )
        
        return {"memories": memories, "count": len(memories)}
    except Exception as e:
        logging.error(f"Error retrieving memories by cognitive frame: {str(e)}")
        return {"error": str(e)}

async def retrieve_memories_with_complex_query(npc_id, query, limit=10):
    """Retrieve memories using a complex query with multiple filters
    
    Args:
        npc_id: The NPC's ID
        query: Dictionary with filter criteria (emotions, categories, timeframe, etc.)
        limit: Maximum number of memories to return
        
    Returns:
        List of memories matching the query
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Retrieve memories with complex query
        memories = manager.retrieve_memories_with_complex_query(
            query=query,
            limit=limit
        )
        
        return {"memories": memories, "count": len(memories)}
    except Exception as e:
        logging.error(f"Error performing complex memory query: {str(e)}")
        return {"error": str(e)}

async def create_memory_association(npc_id, source_memory_id, target_memory_id, association_type, strength=1.0, bidirectional=True):
    """Create an association between two memories
    
    Args:
        npc_id: NPC ID
        source_memory_id: ID of the source memory
        target_memory_id: ID of the target memory
        association_type: Type of association (e.g., 'cause', 'effect')
        strength: Association strength (0.0-1.0)
        bidirectional: Whether to create inverse association
        
    Returns:
        Association data or error dict
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Create the association
        association = manager.create_memory_association(
            source_memory_id=source_memory_id,
            target_memory_id=target_memory_id,
            association_type=association_type,
            strength=strength,
            bidirectional=bidirectional
        )
        
        # Save associations to database
        await manager.save_associations()
        
        return association
    except Exception as e:
        return {"error": str(e)}

async def get_memory_associations(npc_id, memory_id, association_types=None):
    """Get associations for a memory
    
    Args:
        npc_id: NPC ID
        memory_id: Memory ID
        association_types: Optional list of association types to filter by
        
    Returns:
        List of associations or error dict
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Load associations from database
        await manager.load_associations()
        
        # Get the associations
        associations = manager.get_memory_associations(memory_id, association_types)
        
        return associations
    except Exception as e:
        return {"error": str(e)}

async def detect_memory_associations(npc_id, memory_a_id, memory_b_id):
    """Detect and create associations between two memories
    
    Args:
        npc_id: NPC ID
        memory_a_id: ID of the first memory
        memory_b_id: ID of the second memory
        
    Returns:
        List of created associations or error dict
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Load associations from database
        await manager.load_associations()
        
        # Detect and create associations
        associations = manager.detect_memory_associations(memory_a_id, memory_b_id)
        
        # Save associations to database
        await manager.save_associations()
        
        return associations
    except Exception as e:
        return {"error": str(e)}

async def get_memory_network(npc_id, memory_id, max_depth=2):
    """Get a network of connected memories
    
    Args:
        npc_id: NPC ID
        memory_id: Central memory ID
        max_depth: Maximum traversal depth in the association graph
        
    Returns:
        Memory network data or error dict
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Load associations from database
        await manager.load_associations()
        
        # Get the memory network
        network = manager.get_memory_network(memory_id, max_depth)
        
        return network
    except Exception as e:
        return {"error": str(e)}

async def get_cognitive_frames():
    """Get available cognitive frames
    
    Returns:
        Dictionary with cognitive frames information
    """
    from .cognitive_frames import CognitiveFrame, CognitiveFrameMetadata
    
    frames = []
    for frame in CognitiveFrame:
        metadata = CognitiveFrameMetadata.get_metadata(frame)
        frames.append({
            "id": frame.value,
            "name": metadata["display_name"],
            "description": metadata["description"]
        })
    
    return {
        "frames": frames
    }

async def reinterpret_memory(npc_id, memory_id, frame):
    """Reinterpret a memory through a cognitive frame
    
    Args:
        npc_id: NPC ID
        memory_id: Memory ID
        frame: Cognitive frame to apply (e.g., 'victim', 'hero')
        
    Returns:
        Reinterpreted memory or error dict
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Reinterpret the memory
        reinterpreted = manager.reinterpret_memory(memory_id, frame)
        
        return reinterpreted
    except Exception as e:
        return {"error": str(e)}

async def analyze_memory_emotions(npc_id, memory_id):
    """Analyze the emotional content of a memory
    
    Args:
        npc_id: NPC ID
        memory_id: Memory ID
        
    Returns:
        Emotion analysis data or error dict
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Analyze the memory emotions
        emotions = manager.analyze_memory_emotions(memory_id)
        
        return emotions
    except Exception as e:
        return {"error": str(e)}

async def consolidate_memories(npc_id, memory_ids, consolidation_type="default"):
    """Consolidate multiple memories into a higher-level memory
    
    Args:
        npc_id: NPC ID
        memory_ids: List of memory IDs to consolidate
        consolidation_type: Type of consolidation to perform
        
    Returns:
        Consolidated memory or error dict
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Load associations from database
        await manager.load_associations()
        
        # Consolidate the memories
        consolidated_memory = manager.consolidate_memories(
            memory_ids=memory_ids,
            consolidation_type=consolidation_type
        )
        
        # Save associations to database (created during consolidation)
        await manager.save_associations()
        
        return consolidated_memory
    except Exception as e:
        return {"error": str(e)}

async def calculate_memory_saliency(npc_id, memory_id):
    """Calculate the current saliency score for a memory
    
    Args:
        npc_id: NPC ID
        memory_id: Memory ID
        
    Returns:
        Saliency score or error dict
    """
    try:
        # Import saliency scoring
        from .saliency_scoring import calculate_memory_saliency as calc_saliency
        
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Retrieve the memory
        memory = manager.retrieve_memory_by_id(memory_id)
        if not memory:
            return {"error": f"Memory with ID {memory_id} not found"}
        
        # Calculate saliency
        saliency = calc_saliency(memory)
        
        return {
            "memory_id": memory_id,
            "saliency": saliency,
            "importance": memory.get("importance", 0.5),
            "created_at": memory.get("created_at", ""),
            "memory_type": memory.get("memory_type", "regular"),
            "categories": memory.get("categories", [])
        }
    except Exception as e:
        return {"error": str(e)}

async def rank_memories_by_relevance(npc_id, query_context, consider_saliency=True, limit=10):
    """Rank memories by their relevance to a query context
    
    Args:
        npc_id: NPC ID
        query_context: The query context to match against
        consider_saliency: Whether to consider memory saliency in ranking
        limit: Maximum number of memories to return
        
    Returns:
        List of ranked memories or error dict
    """
    try:
        # Import relevance ranking
        from .saliency_scoring import rank_memories_by_relevance as rank_memories
        
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Get all memories for the NPC
        all_memories = manager.retrieve_all_memories()
        
        # Rank memories by relevance
        ranked_memories = rank_memories(query_context, all_memories, consider_saliency)
        
        # Limit the results
        ranked_memories = ranked_memories[:limit]
        
        # Format the results
        result = []
        for memory, score in ranked_memories:
            result.append({
                "memory": memory,
                "relevance_score": score
            })
        
        return result
    except Exception as e:
        return {"error": str(e)}

async def log_memory_access(npc_id, memory_id, context=""):
    """Log an access to a memory, updating access stats
    
    Args:
        npc_id: NPC ID
        memory_id: Memory ID
        context: Optional context for the access
        
    Returns:
        Success message or error dict
    """
    try:
        # Initialize memory manager
        manager = await MemoryManager.get_instance(
            npc_id=npc_id,
            short_term_db=short_term_mock,
            long_term_db=long_term_mock,
            event_dispatcher=event_dispatcher
        )
        
        # Get the memory
        memory = manager.retrieve_memory_by_id(memory_id)
        if not memory:
            return {"error": f"Memory with ID {memory_id} not found"}
        
        # Create Memory object from dictionary
        from .memory import Memory
        memory_obj = Memory.from_dict(memory, event_dispatcher=event_dispatcher)
        
        # Log the access
        memory_obj.access(context)
        
        # Store updated memory
        manager._store_memory_in_long_term(memory_obj.to_dict())
        
        return {
            "success": True,
            "memory_id": memory_id,
            "access_count": memory_obj.access_count,
            "last_accessed": memory_obj.last_accessed
        }
    except Exception as e:
        return {"error": str(e)}
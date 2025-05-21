#This Flask route module provides access to the NPC memory system, supporting:
#Viewing short-term memory
#Triggering memory summarization
#Adding test interactions
#Evaluating beliefs from monthly summaries
#It ties into the memory, firebase, npc, and beliefs systems.

from flask import Blueprint, jsonify, request
import asyncio
from firebase_admin import db
import logging

# Use local imports rather than app.memory
from .memory_utils import (
    store_interaction, 
    update_long_term_memory, 
    summarize_and_clean_memory, 
    get_recent_interactions, 
    generate_beliefs_from_meta_summary,
    get_summarization_styles,
    retrieve_memories_by_emotion,
    retrieve_memories_by_cognitive_frame,
    retrieve_memories_with_complex_query,
    get_memory_associations,
    create_memory_association,
    detect_memory_associations,
    get_memory_network,
    get_cognitive_frames,
    reinterpret_memory,
    analyze_memory_emotions,
    consolidate_memories,
    calculate_memory_saliency,
    rank_memories_by_relevance,
    log_memory_access
)

memory_bp = Blueprint('memory', __name__)

@memory_bp.route('/memory/<npc_id>', methods=['GET'])
def get_recent_memory(npc_id):
    character_id = request.args.get("character_id")
    entries = db.reference(f"/npc_memory/{npc_id}").get() or {}
    return jsonify({"recent": list(entries.values())})

@memory_bp.route('/memory/<npc_id>/clear', methods=['POST'])
async def clear_npc_memory(npc_id):
    # Handle async function
    result = await summarize_and_clean_memory(npc_id)
    return jsonify(result)

@memory_bp.route('/memory/<npc_id>/store', methods=['POST'])
async def store_npc_interaction(npc_id):
    data = request.get_json()
    character_id = data.get('character_id')
    interaction_text = data.get('text')
    tags = data.get('tags', {})
    
    if not interaction_text:
        return jsonify({"error": "Missing 'text' field"}), 400
        
    result = await store_interaction(npc_id, character_id, interaction_text, tags)
    return jsonify(result)

@memory_bp.route('/memory/<npc_id>/long_term_update', methods=['POST'])
async def update_npc_long_term_memory(npc_id):
    data = request.get_json()
    character_id = data.get('character_id')
    region = data.get('region')
    style = data.get('style')
    detail = data.get('detail')
    
    result = await update_long_term_memory(npc_id, character_id, region, style, detail)
    return jsonify(result)

@memory_bp.route('/memory/<npc_id>/evaluate_beliefs', methods=['POST'])
def evaluate_beliefs(npc_id):
    # Pull last few meta-summaries from Firebase
    summaries_ref = db.reference(f"/npcs/{npc_id}/monthly_meta")
    summaries = summaries_ref.get()

    if not summaries:
        return jsonify({"error": "No meta summaries found."}), 404

    # Merge into one prompt string
    text = "\n".join(summaries.values() if isinstance(summaries, dict) else summaries)
    result = generate_beliefs_from_meta_summary(npc_id, text)
    return jsonify(result)

@memory_bp.route('/memory/summarization-styles', methods=['GET'])
def get_summarization_styles():
    """Get available summarization styles and detail levels"""
    try:
        # Call the async utility function using the event loop
        result = asyncio.run(get_summarization_styles())
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error getting summarization styles: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/npc/<npc_id>/memory/categories', methods=['GET'])
def get_memory_categories(npc_id):
    """Get memory categories for an NPC"""
    from .memory_categories import MemoryCategory
    
    try:
        # Convert enum to dict for JSON response
        categories = {}
        for category in MemoryCategory:
            categories[category.name] = category.value
            
        return jsonify({
            "npc_id": npc_id,
            "categories": categories
        })
    except Exception as e:
        logging.error(f"Error getting memory categories: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/emotions/<emotion>', methods=['GET'])
async def get_memories_by_emotion(npc_id, emotion):
    """Get memories for an NPC filtered by emotion"""
    try:
        min_intensity = float(request.args.get('min_intensity', 0.3))
        limit = int(request.args.get('limit', 10))
        
        # Call the async utility function
        result = await retrieve_memories_by_emotion(
            npc_id=npc_id,
            emotion=emotion,
            min_intensity=min_intensity,
            limit=limit
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error retrieving memories by emotion: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/cognitive-frames/<frame>', methods=['GET'])
async def get_memories_by_cognitive_frame(npc_id, frame):
    """Get memories for an NPC filtered by cognitive frame"""
    try:
        limit = int(request.args.get('limit', 10))
        
        # Call the async utility function
        result = await retrieve_memories_by_cognitive_frame(
            npc_id=npc_id,
            frame=frame,
            limit=limit
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error retrieving memories by cognitive frame: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/complex-query', methods=['POST'])
async def query_memories_complex(npc_id):
    """Query NPC memories with complex filter criteria"""
    try:
        # Get query parameters from request body
        data = request.get_json()
        
        # Extract limit parameter
        limit = data.pop('limit', 10)
        
        # Call the async utility function
        result = await retrieve_memories_with_complex_query(
            npc_id=npc_id,
            query=data,
            limit=limit
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error performing complex memory query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/associations/<memory_id>', methods=['GET'])
async def get_memory_associations_route(npc_id, memory_id):
    """Get associations for a memory"""
    try:
        association_types = request.args.getlist('types')
        association_types = association_types if association_types else None
        
        result = await get_memory_associations(npc_id, memory_id, association_types)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error getting memory associations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/associations/create', methods=['POST'])
async def create_memory_association_route(npc_id):
    """Create an association between two memories"""
    try:
        data = request.get_json()
        source_id = data.get('source_id')
        target_id = data.get('target_id')
        association_type = data.get('association_type')
        strength = float(data.get('strength', 1.0))
        bidirectional = data.get('bidirectional', True)
        
        if not source_id or not target_id or not association_type:
            return jsonify({"error": "Missing required parameters"}), 400
        
        result = await create_memory_association(
            npc_id=npc_id,
            source_memory_id=source_id,
            target_memory_id=target_id,
            association_type=association_type,
            strength=strength,
            bidirectional=bidirectional
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error creating memory association: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/associations/detect', methods=['POST'])
async def detect_memory_associations_route(npc_id):
    """Detect and create associations between two memories"""
    try:
        data = request.get_json()
        memory_a_id = data.get('memory_a_id')
        memory_b_id = data.get('memory_b_id')
        
        if not memory_a_id or not memory_b_id:
            return jsonify({"error": "Missing required parameters"}), 400
        
        result = await detect_memory_associations(npc_id, memory_a_id, memory_b_id)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error detecting memory associations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/network/<memory_id>', methods=['GET'])
async def get_memory_network_route(npc_id, memory_id):
    """Get a network of connected memories"""
    try:
        max_depth = int(request.args.get('max_depth', 2))
        
        result = await get_memory_network(npc_id, memory_id, max_depth)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error getting memory network: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/cognitive-frames', methods=['GET'])
async def get_cognitive_frames_route():
    """Get available cognitive frames"""
    try:
        result = await get_cognitive_frames()
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error getting cognitive frames: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/reinterpret/<memory_id>', methods=['POST'])
async def reinterpret_memory_route(npc_id, memory_id):
    """Reinterpret a memory through a cognitive frame"""
    try:
        data = request.get_json()
        frame = data.get('frame')
        
        if not frame:
            return jsonify({"error": "Missing required 'frame' parameter"}), 400
        
        result = await reinterpret_memory(npc_id, memory_id, frame)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error reinterpreting memory: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/emotions/<memory_id>', methods=['GET'])
async def analyze_memory_emotions_route(npc_id, memory_id):
    """Analyze the emotional content of a memory"""
    try:
        result = await analyze_memory_emotions(npc_id, memory_id)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error analyzing memory emotions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/consolidate', methods=['POST'])
async def consolidate_memories_route(npc_id):
    """Consolidate multiple memories into a higher-level memory"""
    try:
        data = request.get_json()
        memory_ids = data.get('memory_ids', [])
        consolidation_type = data.get('consolidation_type', 'default')
        
        if not memory_ids or len(memory_ids) < 2:
            return jsonify({"error": "At least two memory IDs required"}), 400
        
        result = await consolidate_memories(
            npc_id=npc_id,
            memory_ids=memory_ids,
            consolidation_type=consolidation_type
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error consolidating memories: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/saliency/<memory_id>', methods=['GET'])
async def get_memory_saliency_route(npc_id, memory_id):
    """Get the current saliency score for a memory"""
    try:
        result = await calculate_memory_saliency(npc_id, memory_id)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error calculating memory saliency: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/rank', methods=['POST'])
async def rank_memories_route(npc_id):
    """Rank memories by relevance to a query context"""
    try:
        data = request.get_json()
        query_context = data.get('query_context', '')
        consider_saliency = data.get('consider_saliency', True)
        limit = int(data.get('limit', 10))
        
        if not query_context:
            return jsonify({"error": "Missing required query_context parameter"}), 400
        
        result = await rank_memories_by_relevance(
            npc_id=npc_id,
            query_context=query_context,
            consider_saliency=consider_saliency,
            limit=limit
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error ranking memories by relevance: {str(e)}")
        return jsonify({"error": str(e)}), 500

@memory_bp.route('/memory/<npc_id>/access/<memory_id>', methods=['POST'])
async def log_memory_access_route(npc_id, memory_id):
    """Log an access to a memory"""
    try:
        data = request.get_json() or {}
        context = data.get('context', '')
        
        result = await log_memory_access(npc_id, memory_id, context)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error logging memory access: {str(e)}")
        return jsonify({"error": str(e)}), 500


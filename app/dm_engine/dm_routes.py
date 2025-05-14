#This file handles GPT-powered Dungeon Master narration, including:
#Starting a new campaign with a GPT-generated quest
#Responding to player prompts in immersive or mechanical mode
#Narrating combat outcomes with cinematic prose
#It is deeply tied into gpt, narrative, firebase, quests, and dm_utils systems.

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from firebase_admin import db
import openai
import json
from app.quests.quest_utils import QuestManager
from app.core.utils.gpt.client import GPTClient
from app.dm_engine.dm_utils import classify_request, process_dm_decision, narrate_combat_action
from app.dm_engine.dm_helper_utils import gather_dm_context, generate_dm_response, apply_dm_decision
from app.memory.memory_utils import get_recent_interactions
from app.pois.dungeon_enrichment_utils import enrich_poi_structure
import random
from app.models.character import Character
from app.models.region import Region
from app.models.quest import Quest
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dm_engine.dm_helper_utils import DMHelperUtils
from visual_client.game.narrative import narrate_combat_action

dm_engine_bp = Blueprint("dm_engine", __name__)

router = APIRouter()
logger = logging.getLogger(__name__)
dm_utils = DMHelperUtils()

@dm_engine_bp.route('/dm_response', methods=['POST'])
def dm_response():
    """
    Handles all GPT DM interactions.
    Modes:
    - start_game: Generates a quest based on player info and assigns a social POI start
    - normal: Routes prompt to GPT and classifies it
    """
    try:
        data = request.get_json()
        prompt = data.get("prompt")
        character_id = data.get("character_id")
        mode = data.get("mode", "normal")
        npc_id = data.get("npc_id", None)

        if not prompt or not character_id:
            return jsonify({"error": "Missing prompt or character_id"}), 400

        context = gather_dm_context(character_id, npc_id)

        if mode == "background_prompt":
            gpt_prompt = (
                "Write a fantasy RPG player character background based on the following details. "
                "Limit your response to **no more than 250 words**. Be concise and vivid:\n\n"
                + prompt.strip()
            )
            reply = GPTClient().call(
                system_prompt="You are a fantasy RPG storyteller creating vivid character backgrounds.",
                user_prompt=gpt_prompt,
                temperature=0.7,
                max_tokens=500
            )
            return jsonify({"response": reply})

        elif mode == "start_game":
            # Generate initial quest
            quest_manager = QuestManager()
            quest = quest_manager.generate_quest(character_id)
            
            # Assign starting POI
            poi = quest_manager.assign_starting_poi(quest.id)
            
            return jsonify({
                "response": f"Welcome to your adventure! {quest.description}",
                "quest_id": quest.id,
                "poi_id": poi.id
            })

        else:  # normal mode
            classification = classify_request(prompt, character_id)
            gpt = GPTClient()
            
            if classification == "mechanical":
                response = gpt.handle_mechanical_request(prompt, context)
            elif classification == "npc":
                response = gpt.handle_npc_request(prompt, context)
            else:  # narrative
                response = gpt.handle_narrative_request(prompt, context)
                
            return jsonify({"response": response})

    except Exception as e:
        logging.error(f"Error in dm_response: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@dm_engine_bp.route('/narrate_combat', methods=['POST'])
def generate_combat_narration():
    """Generate narrative for a combat action."""
    try:
        data = request.get_json()
        actor_name = data.get("actor_name")
        action_data = data.get("action_data")
        outcome = data.get("outcome")

        if not all([actor_name, action_data, outcome]):
            return jsonify({"error": "Missing required fields"}), 400

        narration = narrate_combat_action(actor_name, action_data, outcome)
        return jsonify({"narration": narration})

    except Exception as e:
        logging.error(f"Error in generate_combat_narration: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@dm_engine_bp.route('/gpt/enrich_poi', methods=['POST'])
def enrich_poi():
    """Enrich a point of interest with additional details."""
    try:
        data = request.get_json()
        poi_id = data.get("poi_id")
        poi_type = data.get("poi_type")

        if not poi_id or not poi_type:
            return jsonify({"error": "Missing poi_id or poi_type"}), 400

        enriched_poi = enrich_poi_structure(poi_id, poi_type)
        return jsonify(enriched_poi)

    except Exception as e:
        logging.error(f"Error in enrich_poi: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@dm_engine_bp.route('/generate_portrait', methods=['POST'])
def generate_portrait():
    """Generate a character portrait description."""
    try:
        data = request.get_json()
        character_id = data.get("character_id")
        style = data.get("style", "fantasy")

        if not character_id:
            return jsonify({"error": "Missing character_id"}), 400

        gpt = GPTClient()
        portrait = gpt.generate_portrait(character_id, style)
        return jsonify({"portrait": portrait})

    except Exception as e:
        logging.error(f"Error in generate_portrait: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@dm_engine_bp.route('/api/dm/response', methods=['POST'])
def get_dm_response():
    data = request.get_json()
    character_id = data.get('character_id')
    region_id = data.get('region_id')
    quest_id = data.get('quest_id')
    
    if not character_id or not region_id:
        return jsonify({"error": "Missing required fields"}), 400
        
    character = Character.query.get(character_id)
    region = Region.query.get(region_id)
    quest = Quest.query.get(quest_id) if quest_id else None
    
    if not character or not region:
        return jsonify({"error": "Character or region not found"}), 404
        
    response = generate_dm_response(character, region, quest)
    return jsonify(response)

@dm_engine_bp.route('/api/dm/decision', methods=['POST'])
def handle_dm_decision():
    data = request.get_json()
    character_id = data.get('character_id')
    decision = data.get('decision')
    
    if not character_id or not decision:
        return jsonify({"error": "Missing required fields"}), 400
        
    character = Character.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404
        
    result = apply_dm_decision(character, decision)
    return jsonify(result)

@router.post("/encounter/generate")
async def generate_encounter(
    character_ids: List[int],
    region_id: int,
    difficulty: str = "normal",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate an encounter for the given characters in a region.
    
    Args:
        character_ids: List of character IDs to generate encounter for
        region_id: ID of the region where the encounter occurs
        difficulty: The difficulty level of the encounter
        db: Database session
        
    Returns:
        Dict containing encounter details
    """
    try:
        # Get characters and region
        characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
        if not characters:
            raise HTTPException(status_code=404, detail="Characters not found")
            
        region = db.query(Region).filter(Region.id == region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
            
        # Generate encounter
        encounter = dm_utils.generate_encounter(characters, region, difficulty)
        if not encounter:
            raise HTTPException(status_code=500, detail="Failed to generate encounter")
            
        return encounter
        
    except Exception as e:
        logger.error(f"Error generating encounter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quest/assign")
async def assign_quest(
    character_ids: List[int],
    region_id: int,
    quest_type: str = "hunt",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Assign a quest to characters in a region.
    
    Args:
        character_ids: List of character IDs to assign quest to
        region_id: ID of the region where the quest takes place
        quest_type: The type of quest to generate
        db: Database session
        
    Returns:
        Dict containing quest details
    """
    try:
        # Get characters and region
        characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
        if not characters:
            raise HTTPException(status_code=404, detail="Characters not found")
            
        region = db.query(Region).filter(Region.id == region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
            
        # Assign quest
        quest = dm_utils.assign_quest(characters, region, quest_type)
        if not quest:
            raise HTTPException(status_code=500, detail="Failed to assign quest")
            
        # Save quest to database
        db.add(quest)
        db.commit()
        
        return {
            "quest_id": quest.id,
            "name": quest.name,
            "description": quest.description,
            "difficulty": quest.difficulty,
            "reward": quest.reward
        }
        
    except Exception as e:
        logger.error(f"Error assigning quest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/world/tick")
async def process_world_tick(
    region_ids: List[int],
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Process a world tick for the given regions.
    
    Args:
        region_ids: List of region IDs to process
        db: Database session
        
    Returns:
        List of events generated during the tick
    """
    try:
        # Get regions
        regions = db.query(Region).filter(Region.id.in_(region_ids)).all()
        if not regions:
            raise HTTPException(status_code=404, detail="Regions not found")
            
        # Process world tick
        events = dm_utils.process_world_tick(regions)
        
        # Save events to database
        for event in events:
            db.add(event)
        db.commit()
        
        return events
        
    except Exception as e:
        logger.error(f"Error processing world tick: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context/{character_id}")
async def get_dm_context(
    character_id: int,
    npc_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get DM context for a character.
    
    Args:
        character_id: ID of the character
        npc_id: Optional ID of an NPC
        db: Database session
        
    Returns:
        Dict containing DM context
    """
    try:
        # Get character
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
            
        # Get context
        context = gather_dm_context(str(character_id), str(npc_id) if npc_id else None)
        
        return context
        
    except Exception as e:
        logger.error(f"Error getting DM context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/response/generate")
async def generate_dm_response(
    character_id: int,
    region_id: int,
    quest_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a DM response based on character, region, and quest context.
    
    Args:
        character_id: ID of the character
        region_id: ID of the region
        quest_id: Optional ID of the quest
        db: Database session
        
    Returns:
        Dict containing DM response
    """
    try:
        # Get character and region
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
            
        region = db.query(Region).filter(Region.id == region_id).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
            
        # Get quest if specified
        quest = None
        if quest_id:
            quest = db.query(Quest).filter(Quest.id == quest_id).first()
            if not quest:
                raise HTTPException(status_code=404, detail="Quest not found")
                
        # Generate response
        response = generate_dm_response(character, region, quest)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating DM response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decision/apply")
async def apply_dm_decision(
    character_id: int,
    decision: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Apply the consequences of a DM decision.
    
    Args:
        character_id: ID of the character
        decision: The DM decision to apply
        db: Database session
        
    Returns:
        Dict containing decision results
    """
    try:
        # Get character
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
            
        # Apply decision
        result = apply_dm_decision(character, decision)
        
        # Save any changes to database
        db.commit()
        
        return result
        
    except Exception as e:
        logger.error(f"Error applying DM decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

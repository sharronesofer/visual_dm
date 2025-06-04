"""
Language System API Router (Infrastructure Layer)

Provides REST API endpoints for managing language systems:
- Character language proficiency and creation
- Dialogue comprehension processing
- Settlement language profile management
- Language learning recommendations and progression
- Language exposure simulation

This router integrates language business logic with API infrastructure.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from backend.systems.population.models.language_models import (
    language_engine,
    Language,
    LanguageFamily,
    LanguageProficiency
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/languages", tags=["population-languages"])


# Pydantic models for API requests/responses
class CreateCharacterLanguagesRequest(BaseModel):
    """Request model for creating character starting languages"""
    character_id: str = Field(..., description="Unique character identifier")
    intelligence_score: int = Field(..., ge=3, le=20, description="Character's intelligence score (3-20)")
    background_languages: Optional[List[str]] = Field(None, description="Languages from character background")


class ProcessDialogueRequest(BaseModel):
    """Request model for processing dialogue comprehension"""
    character_id: str = Field(..., description="Character attempting to understand")
    dialogue_text: str = Field(..., description="The dialogue text to process")
    speaker_language: str = Field(..., description="Language the speaker is using")
    text_complexity: float = Field(0.5, ge=0.0, le=1.0, description="Complexity of the text (0.0=simple, 1.0=complex)")
    context_clues: bool = Field(True, description="Whether gestures/context clues are available")


class LanguageExposureRequest(BaseModel):
    """Request model for simulating language exposure"""
    character_id: str = Field(..., description="Character being exposed to language")
    exposure_language: str = Field(..., description="Language being learned through exposure")
    hours: int = Field(..., ge=1, le=1000, description="Hours of exposure")
    interaction_quality: float = Field(0.5, ge=0.1, le=1.0, description="Quality of interaction (0.1=poor, 1.0=excellent)")


class CreateSettlementLanguageRequest(BaseModel):
    """Request model for creating settlement language profile"""
    settlement_id: str = Field(..., description="Settlement identifier")
    primary_language: str = Field(..., description="Primary language of the settlement")
    population_size: int = Field(..., ge=1, description="Settlement population size")
    cultural_background: str = Field("mixed", description="Cultural background: isolated, crossroads, mixed")


@router.post("/characters/{character_id}/create")
async def create_character_languages(character_id: str, request: CreateCharacterLanguagesRequest):
    """Create starting languages for a character based on intelligence score"""
    try:
        # Validate background languages if provided
        background_langs = []
        if request.background_languages:
            for lang_str in request.background_languages:
                try:
                    background_langs.append(Language(lang_str))
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid language: {lang_str}. Valid languages: {[lang.value for lang in Language]}"
                    )
        
        # Create character languages
        proficiencies = language_engine.create_character_starting_languages(
            character_id=request.character_id,
            intelligence_score=request.intelligence_score,
            background_languages=background_langs
        )
        
        # Format response
        language_data = []
        for prof in proficiencies:
            language_data.append({
                "language": prof.language.value,
                "comprehension_level": prof.comprehension_level,
                "speaking_level": prof.speaking_level,
                "literacy_level": prof.literacy_level,
                "formal_training": prof.formal_training,
                "acquired_date": prof.acquired_date.isoformat()
            })
        
        return {
            "success": True,
            "character_id": request.character_id,
            "intelligence_score": request.intelligence_score,
            "total_languages": len(proficiencies),
            "languages": language_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating character languages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create character languages: {str(e)}")


@router.get("/characters/{character_id}")
async def get_character_languages(character_id: str):
    """Get all languages known by a character"""
    try:
        if character_id not in language_engine.character_proficiencies:
            raise HTTPException(status_code=404, detail="Character language data not found")
        
        proficiencies = language_engine.character_proficiencies[character_id]
        
        language_data = []
        for prof in proficiencies:
            language_data.append({
                "language": prof.language.value,
                "language_family": language_engine.language_families[prof.language].value,
                "comprehension_level": prof.comprehension_level,
                "speaking_level": prof.speaking_level,
                "literacy_level": prof.literacy_level,
                "exposure_hours": prof.exposure_hours,
                "formal_training": prof.formal_training,
                "acquired_date": prof.acquired_date.isoformat(),
                "fluency_category": _get_fluency_category(prof.comprehension_level)
            })
        
        return {
            "character_id": character_id,
            "total_languages": len(language_data),
            "languages": language_data,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting character languages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get character languages: {str(e)}")


@router.post("/dialogue/process")
async def process_dialogue_comprehension(request: ProcessDialogueRequest):
    """Process dialogue text based on character's language comprehension"""
    try:
        # Validate speaker language
        try:
            speaker_language = Language(request.speaker_language)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid speaker language: {request.speaker_language}"
            )
        
        # Process dialogue
        result = language_engine.process_dialogue_comprehension(
            character_id=request.character_id,
            dialogue_text=request.dialogue_text,
            speaker_language=speaker_language,
            text_complexity=request.text_complexity,
            context_clues=request.context_clues
        )
        
        # Add helpful UI information
        result["ui_hints"] = _generate_ui_hints(result)
        result["processed_at"] = datetime.utcnow().isoformat()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing dialogue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process dialogue: {str(e)}")


@router.post("/characters/{character_id}/exposure")
async def simulate_language_exposure(character_id: str, request: LanguageExposureRequest):
    """Simulate natural language learning through exposure"""
    try:
        # Validate exposure language
        try:
            exposure_language = Language(request.exposure_language)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid exposure language: {request.exposure_language}"
            )
        
        # Simulate exposure
        result = language_engine.simulate_language_exposure(
            character_id=request.character_id,
            exposure_language=exposure_language,
            hours=request.hours,
            interaction_quality=request.interaction_quality
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        result["simulated_at"] = datetime.utcnow().isoformat()
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simulating language exposure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to simulate exposure: {str(e)}")


@router.get("/characters/{character_id}/recommendations")
async def get_language_learning_recommendations(character_id: str):
    """Get recommendations for which languages would be most useful to learn"""
    try:
        recommendations = language_engine.get_language_learning_recommendations(character_id)
        
        if not recommendations:
            return {
                "character_id": character_id,
                "recommendations": [],
                "message": "No language learning recommendations available (character not found or all languages known)",
                "generated_at": datetime.utcnow().isoformat()
            }
        
        return {
            "character_id": character_id,
            "total_recommendations": len(recommendations),
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting language recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/settlements/{settlement_id}/profile")
async def create_settlement_language_profile(settlement_id: str, request: CreateSettlementLanguageRequest):
    """Create a language profile for a settlement"""
    try:
        # Validate primary language
        try:
            primary_language = Language(request.primary_language)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid primary language: {request.primary_language}"
            )
        
        # Create settlement profile
        profile = language_engine.create_settlement_language_profile(
            settlement_id=request.settlement_id,
            primary_language=primary_language,
            population_size=request.population_size,
            cultural_background=request.cultural_background
        )
        
        return {
            "success": True,
            "settlement_id": profile.settlement_id,
            "primary_language": profile.primary_language.value,
            "secondary_languages": [lang.value for lang in profile.secondary_languages],
            "trade_languages": [lang.value for lang in profile.trade_languages],
            "language_diversity": profile.language_diversity,
            "dialect_strength": profile.dialect_strength,
            "literacy_rate": profile.literacy_rate,
            "cultural_background": request.cultural_background,
            "population_size": request.population_size,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating settlement language profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create settlement profile: {str(e)}")


@router.get("/settlements/{settlement_id}/profile")
async def get_settlement_language_profile(settlement_id: str):
    """Get the language profile for a settlement"""
    try:
        if settlement_id not in language_engine.settlement_profiles:
            raise HTTPException(status_code=404, detail="Settlement language profile not found")
        
        profile = language_engine.settlement_profiles[settlement_id]
        
        return {
            "settlement_id": profile.settlement_id,
            "primary_language": profile.primary_language.value,
            "secondary_languages": [lang.value for lang in profile.secondary_languages],
            "trade_languages": [lang.value for lang in profile.trade_languages],
            "language_diversity": profile.language_diversity,
            "dialect_strength": profile.dialect_strength,
            "literacy_rate": profile.literacy_rate,
            "historical_languages": [lang.value for lang in profile.historical_languages],
            "linguistic_description": _generate_linguistic_description(profile),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting settlement language profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get settlement profile: {str(e)}")


@router.get("/comprehension/test")
async def test_language_comprehension(
    character_id: str = Query(..., description="Character ID"),
    target_language: str = Query(..., description="Language to test comprehension for"),
    text_complexity: float = Query(0.5, ge=0.0, le=1.0, description="Text complexity level")
):
    """Test how well a character would understand a specific language"""
    try:
        # Validate target language
        try:
            lang = Language(target_language)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid language: {target_language}"
            )
        
        # Calculate comprehension
        comprehension_level, sources = language_engine.calculate_comprehension(
            character_id=character_id,
            target_language=lang,
            text_complexity=text_complexity
        )
        
        return {
            "character_id": character_id,
            "target_language": target_language,
            "text_complexity": text_complexity,
            "comprehension_level": comprehension_level,
            "comprehension_percentage": round(comprehension_level * 100, 1),
            "comprehension_sources": sources,
            "fluency_category": _get_fluency_category(comprehension_level),
            "can_communicate": comprehension_level >= 0.3,
            "tested_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing language comprehension: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test comprehension: {str(e)}")


@router.get("/system/overview")
async def get_language_system_overview():
    """Get an overview of the entire language system"""
    try:
        # Count language families
        family_counts = {}
        for lang, family in language_engine.language_families.items():
            family_counts[family.value] = family_counts.get(family.value, 0) + 1
        
        # Count relationships
        relationship_types = {}
        for rel in language_engine.language_relationships:
            rel_type = rel.relationship_type
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        return {
            "system_overview": {
                "total_languages": len(Language),
                "language_families": len(LanguageFamily),
                "total_relationships": len(language_engine.language_relationships),
                "active_characters": len(language_engine.character_proficiencies),
                "settlement_profiles": len(language_engine.settlement_profiles)
            },
            "language_families": family_counts,
            "relationship_types": relationship_types,
            "features": [
                "romance_language_relationships",
                "intelligence_based_starting_languages",
                "partial_comprehension_system",
                "natural_language_learning",
                "settlement_linguistic_profiles",
                "context_aware_dialogue_processing"
            ],
            "language_list": [lang.value for lang in Language],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting language system overview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system overview: {str(e)}")


@router.get("/health")
async def language_system_health():
    """Health check for the language system"""
    try:
        return {
            "status": "healthy",
            "system": "population_languages",
            "capabilities": [
                "character_language_creation",
                "dialogue_comprehension_processing",
                "natural_language_learning",
                "settlement_language_profiles",
                "language_learning_recommendations",
                "romance_language_relationships"
            ],
            "language_features": [
                "forgiving_partial_comprehension",
                "intelligence_based_starting_languages",
                "family_based_language_relationships",
                "context_clue_integration",
                "emotional_tone_recognition",
                "natural_learning_simulation"
            ],
            "integration_ready": True,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Language system health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Language system unhealthy: {str(e)}")


# Helper functions
def _get_fluency_category(comprehension_level: float) -> str:
    """Get human-readable fluency category"""
    if comprehension_level >= 0.9:
        return "fluent"
    elif comprehension_level >= 0.7:
        return "proficient"
    elif comprehension_level >= 0.5:
        return "conversational"
    elif comprehension_level >= 0.3:
        return "basic"
    elif comprehension_level >= 0.1:
        return "minimal"
    else:
        return "none"


def _generate_ui_hints(dialogue_result: Dict[str, Any]) -> List[str]:
    """Generate UI hints for dialogue comprehension"""
    hints = []
    
    comprehension = dialogue_result.get("comprehension_level", 0.0)
    
    if comprehension >= 0.9:
        hints.append("You understand clearly")
    elif comprehension >= 0.7:
        hints.append("You understand most of what they're saying")
    elif comprehension >= 0.5:
        hints.append("You can follow the general meaning")
    elif comprehension >= 0.3:
        hints.append("You catch some words and the general tone")
    elif comprehension >= 0.1:
        hints.append("You recognize this as a language but understand very little")
    else:
        hints.append("This sounds completely foreign to you")
    
    if dialogue_result.get("emotional_context"):
        emotional_context = dialogue_result["emotional_context"]
        if emotional_context and emotional_context != ["neutral"]:
            hints.append(f"They seem {', '.join(emotional_context)}")
    
    if dialogue_result.get("learning_opportunity", False):
        hints.append("You might learn something from this conversation")
    
    return hints


def _generate_linguistic_description(profile) -> str:
    """Generate a descriptive text about a settlement's linguistic character"""
    descriptions = []
    
    # Primary language description
    primary = profile.primary_language.value.replace("_", " ").title()
    descriptions.append(f"Primarily speaks {primary}")
    
    # Diversity description
    if profile.language_diversity > 0.7:
        descriptions.append("very linguistically diverse")
    elif profile.language_diversity > 0.4:
        descriptions.append("moderately diverse")
    else:
        descriptions.append("linguistically homogeneous")
    
    # Dialect description
    if profile.dialect_strength > 0.7:
        descriptions.append("strong local dialect")
    elif profile.dialect_strength > 0.4:
        descriptions.append("noticeable regional accent")
    else:
        descriptions.append("standard pronunciation")
    
    # Literacy description
    if profile.literacy_rate > 0.8:
        descriptions.append("highly literate population")
    elif profile.literacy_rate > 0.5:
        descriptions.append("moderately literate")
    else:
        descriptions.append("low literacy rates")
    
    return "; ".join(descriptions) + "." 
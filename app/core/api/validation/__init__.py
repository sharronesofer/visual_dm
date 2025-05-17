"""Validation models for API requests."""

from .base_validators import (
    PaginationValidationMixin,
    SortValidationMixin,
    FilterValidationMixin,
    DateRangeValidationMixin,
    ValidationResult,
    validate_id,
    validate_name,
    validate_description,
    validate_tags,
    validate_metadata
)

from .npc_validators import (
    NPCAlignment,
    NPCCreateRequest,
    NPCUpdateRequest,
    NPCQueryParams
)

from .item_validators import (
    ItemType,
    ItemRarity,
    ItemStatus,
    ItemCreateRequest,
    ItemUpdateRequest,
    ItemQueryParams,
    ItemTransferRequest
)

from .location_validators import (
    LocationType,
    LocationStatus,
    LocationCreateRequest,
    LocationUpdateRequest,
    LocationQueryParams,
    LocationConnectionRequest
)

from .quest_validators import (
    QuestType,
    QuestStatus,
    QuestDifficulty,
    QuestObjectiveType,
    QuestObjective,
    QuestReward,
    QuestCreateRequest,
    QuestUpdateRequest,
    QuestQueryParams,
    QuestObjectiveUpdateRequest
)

from .faction_validators import (
    FactionType,
    FactionStatus,
    FactionAlignment,
    RelationshipType,
    FactionRelationship,
    FactionCreateRequest,
    FactionUpdateRequest,
    FactionQueryParams,
    FactionRelationshipUpdateRequest
)

def validate_request(request):
    return request

def validate_response(response):
    return response

__all__ = [
    # Base validators
    'PaginationValidationMixin',
    'SortValidationMixin',
    'FilterValidationMixin',
    'DateRangeValidationMixin',
    'ValidationResult',
    'validate_id',
    'validate_name',
    'validate_description',
    'validate_tags',
    'validate_metadata',
    
    # NPC validators
    'NPCAlignment',
    'NPCCreateRequest',
    'NPCUpdateRequest',
    'NPCQueryParams',
    
    # Item validators
    'ItemType',
    'ItemRarity',
    'ItemStatus',
    'ItemCreateRequest',
    'ItemUpdateRequest',
    'ItemQueryParams',
    'ItemTransferRequest',
    
    # Location validators
    'LocationType',
    'LocationStatus',
    'LocationCreateRequest',
    'LocationUpdateRequest',
    'LocationQueryParams',
    'LocationConnectionRequest',
    
    # Quest validators
    'QuestType',
    'QuestStatus',
    'QuestDifficulty',
    'QuestObjectiveType',
    'QuestObjective',
    'QuestReward',
    'QuestCreateRequest',
    'QuestUpdateRequest',
    'QuestQueryParams',
    'QuestObjectiveUpdateRequest',
    
    # Faction validators
    'FactionType',
    'FactionStatus',
    'FactionAlignment',
    'RelationshipType',
    'FactionRelationship',
    'FactionCreateRequest',
    'FactionUpdateRequest',
    'FactionQueryParams',
    'FactionRelationshipUpdateRequest'
] 
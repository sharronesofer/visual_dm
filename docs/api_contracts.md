# Visual DM API Contracts Specification

## Overview

This document defines the comprehensive API contracts between the Unity frontend client and the Python FastAPI backend for the Visual DM project. The API follows RESTful principles for CRUD operations and uses WebSocket connections for real-time updates.

**Base URL**: `http://localhost:8000` (development)

## Authentication & Security

### JWT Authentication
All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints
```http
POST /auth/login
POST /auth/register  
POST /auth/logout
GET /auth/me
POST /auth/refresh
```

## Core API Systems

### 1. Combat System (`/combat`)

**Endpoints:**
- `POST /combat/state` - Create new combat instance
- `GET /combat/state/{combat_id}` - Get combat state
- `PUT /combat/state/{combat_id}` - Update combat state
- `DELETE /combat/state/{combat_id}` - End combat instance
- `GET /combat/states` - List all active combats

**DTOs:**
```csharp
public class CombatStateDTO
{
    [JsonPropertyName("combat_id")]
    public string CombatId { get; set; }
    
    [JsonPropertyName("name")]
    public string Name { get; set; }
    
    [JsonPropertyName("description")]
    public string Description { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } // "pending", "active", "completed", "aborted"
    
    [JsonPropertyName("round_number")]
    public int RoundNumber { get; set; }
    
    [JsonPropertyName("current_turn")]
    public int CurrentTurn { get; set; }
    
    [JsonPropertyName("participants")]
    public List<CombatantDTO> Participants { get; set; }
    
    [JsonPropertyName("initiative_order")]
    public List<CombatantDTO> InitiativeOrder { get; set; }
    
    [JsonPropertyName("combat_log")]
    public List<CombatLogEntryDTO> CombatLog { get; set; }
    
    [JsonPropertyName("actions_taken")]
    public List<CombatActionDTO> ActionsTaken { get; set; }
    
    [JsonPropertyName("started_at")]
    public DateTime? StartedAt { get; set; }
    
    [JsonPropertyName("ended_at")]
    public DateTime? EndedAt { get; set; }
    
    [JsonPropertyName("properties")]
    public Dictionary<string, object> Properties { get; set; }
}

public class CombatantDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("character_id")]
    public string CharacterId { get; set; }
    
    [JsonPropertyName("name")]
    public string Name { get; set; }
    
    [JsonPropertyName("team")]
    public string Team { get; set; } // "player", "hostile", "neutral"
    
    [JsonPropertyName("combatant_type")]
    public string CombatantType { get; set; } // "character", "npc", "creature"
    
    [JsonPropertyName("current_hp")]
    public int CurrentHp { get; set; }
    
    [JsonPropertyName("max_hp")]
    public int MaxHp { get; set; }
    
    [JsonPropertyName("armor_class")]
    public int ArmorClass { get; set; }
    
    [JsonPropertyName("initiative")]
    public int Initiative { get; set; }
    
    [JsonPropertyName("dex_modifier")]
    public int DexModifier { get; set; }
    
    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; }
    
    [JsonPropertyName("is_conscious")]
    public bool IsConscious { get; set; }
    
    [JsonPropertyName("position")]
    public Dictionary<string, float> Position { get; set; }
    
    [JsonPropertyName("status_effects")]
    public List<StatusEffectDTO> StatusEffects { get; set; }
    
    [JsonPropertyName("has_used_standard_action")]
    public bool HasUsedStandardAction { get; set; }
    
    [JsonPropertyName("has_used_bonus_action")]
    public bool HasUsedBonusAction { get; set; }
    
    [JsonPropertyName("has_used_reaction")]
    public bool HasUsedReaction { get; set; }
    
    [JsonPropertyName("remaining_movement")]
    public float RemainingMovement { get; set; }
    
    [JsonPropertyName("equipped_weapons")]
    public List<string> EquippedWeapons { get; set; }
    
    [JsonPropertyName("equipped_armor")]
    public string EquippedArmor { get; set; }
    
    [JsonPropertyName("available_spells")]
    public List<string> AvailableSpells { get; set; }
    
    [JsonPropertyName("class_features")]
    public List<string> ClassFeatures { get; set; }
}

public class StatusEffectDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("name")]
    public string Name { get; set; }
    
    [JsonPropertyName("description")]
    public string Description { get; set; }
    
    [JsonPropertyName("duration")]
    public int Duration { get; set; }
    
    [JsonPropertyName("category")]
    public string Category { get; set; } // "buff", "debuff", "condition"
    
    [JsonPropertyName("effects")]
    public List<StatusEffectItemDTO> Effects { get; set; }
    
    [JsonPropertyName("stackable")]
    public bool Stackable { get; set; }
    
    [JsonPropertyName("dispellable")]
    public bool Dispellable { get; set; }
    
    [JsonPropertyName("source_id")]
    public string SourceId { get; set; }
    
    [JsonPropertyName("combatant_id")]
    public string CombatantId { get; set; }
}

public class CombatActionDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("action_id")]
    public string ActionId { get; set; }
    
    [JsonPropertyName("action_name")]
    public string ActionName { get; set; }
    
    [JsonPropertyName("actor_id")]
    public string ActorId { get; set; }
    
    [JsonPropertyName("actor_name")]
    public string ActorName { get; set; }
    
    [JsonPropertyName("target_ids")]
    public List<string> TargetIds { get; set; }
    
    [JsonPropertyName("target_name")]
    public string TargetName { get; set; }
    
    [JsonPropertyName("success")]
    public bool Success { get; set; }
    
    [JsonPropertyName("encounter_id")]
    public string EncounterId { get; set; }
    
    [JsonPropertyName("round_number")]
    public int RoundNumber { get; set; }
    
    [JsonPropertyName("turn_number")]
    public int TurnNumber { get; set; }
    
    [JsonPropertyName("damage_dealt")]
    public int DamageDealt { get; set; }
    
    [JsonPropertyName("healing_applied")]
    public int HealingApplied { get; set; }
    
    [JsonPropertyName("status_effects_applied")]
    public List<string> StatusEffectsApplied { get; set; }
    
    [JsonPropertyName("executed_at")]
    public DateTime ExecutedAt { get; set; }
}

public class CombatLogEntryDTO
{
    [JsonPropertyName("round")]
    public int Round { get; set; }
    
    [JsonPropertyName("turn")]
    public int Turn { get; set; }
    
    [JsonPropertyName("timestamp")]
    public string Timestamp { get; set; }
    
    [JsonPropertyName("message")]
    public string Message { get; set; }
    
    [JsonPropertyName("data")]
    public Dictionary<string, object> Data { get; set; }
}

**WebSocket Events:**
- `combat_update` - Real-time combat state changes
- `turn_advance` - Turn progression notifications  
- `action_executed` - Combat action resolution results

### 2. Faction System (`/factions`)

**Endpoints:**
- `POST /factions` - Create new faction with optional hidden attributes
- `GET /factions` - List factions with pagination and filtering
- `GET /factions/{id}` - Get faction details including hidden attributes
- `PUT /factions/{id}` - Update faction properties and attributes
- `DELETE /factions/{id}` - Soft delete faction
- `GET /factions/{id}/hidden-attributes` - Get faction's hidden attributes
- `GET /factions/{id}/behavior-modifiers` - Get calculated behavior modifiers
- `GET /factions/{id}/diplomatic-status` - Get diplomatic relationships and status
- `GET /factions/{id}/stability-assessment` - Get faction stability analysis
- `GET /factions/{id}/power-score` - Get faction power calculations
- `GET /factions/{id}/betrayal-risk/{ally_id}` - Calculate betrayal risk for alliance
- `POST /factions/generate-hidden-attributes` - Generate random hidden attributes
- `POST /factions/{id}/evaluate-alliance/{target_id}` - Evaluate alliance proposal
- `POST /factions/{id}/propose-alliance/{target_id}` - Create alliance proposal
- `GET /factions/stats` - System statistics and health check

**DTOs:**
```csharp
public class FactionDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("name")]
    public string Name { get; set; }
    
    [JsonPropertyName("description")]
    public string Description { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } // "active", "inactive", "disbanded"
    
    [JsonPropertyName("properties")]
    public Dictionary<string, object> Properties { get; set; }
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
    
    [JsonPropertyName("updated_at")]
    public DateTime? UpdatedAt { get; set; }
    
    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; }
    
    // Hidden Attributes (1-10 range)
    [JsonPropertyName("hidden_ambition")]
    public int HiddenAmbition { get; set; }
    
    [JsonPropertyName("hidden_integrity")]
    public int HiddenIntegrity { get; set; }
    
    [JsonPropertyName("hidden_discipline")]
    public int HiddenDiscipline { get; set; }
    
    [JsonPropertyName("hidden_impulsivity")]
    public int HiddenImpulsivity { get; set; }
    
    [JsonPropertyName("hidden_pragmatism")]
    public int HiddenPragmatism { get; set; }
    
    [JsonPropertyName("hidden_resilience")]
    public int HiddenResilience { get; set; }
}

public class CreateFactionDTO
{
    [JsonPropertyName("name")]
    [Required]
    [StringLength(255, MinimumLength = 1)]
    public string Name { get; set; }
    
    [JsonPropertyName("description")]
    [StringLength(1000)]
    public string Description { get; set; }
    
    [JsonPropertyName("properties")]
    public Dictionary<string, object> Properties { get; set; }
    
    // Optional hidden attributes (will be randomly generated if not provided)
    [JsonPropertyName("hidden_ambition")]
    [Range(1, 10)]
    public int? HiddenAmbition { get; set; }
    
    [JsonPropertyName("hidden_integrity")]
    [Range(1, 10)]
    public int? HiddenIntegrity { get; set; }
    
    [JsonPropertyName("hidden_discipline")]
    [Range(1, 10)]
    public int? HiddenDiscipline { get; set; }
    
    [JsonPropertyName("hidden_impulsivity")]
    [Range(1, 10)]
    public int? HiddenImpulsivity { get; set; }
    
    [JsonPropertyName("hidden_pragmatism")]
    [Range(1, 10)]
    public int? HiddenPragmatism { get; set; }
    
    [JsonPropertyName("hidden_resilience")]
    [Range(1, 10)]
    public int? HiddenResilience { get; set; }
}

public class UpdateFactionDTO
{
    [JsonPropertyName("name")]
    [StringLength(255, MinimumLength = 1)]
    public string Name { get; set; }
    
    [JsonPropertyName("description")]
    [StringLength(1000)]
    public string Description { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; }
    
    [JsonPropertyName("properties")]
    public Dictionary<string, object> Properties { get; set; }
    
    // Optional hidden attributes updates
    [JsonPropertyName("hidden_ambition")]
    [Range(1, 10)]
    public int? HiddenAmbition { get; set; }
    
    [JsonPropertyName("hidden_integrity")]
    [Range(1, 10)]
    public int? HiddenIntegrity { get; set; }
    
    [JsonPropertyName("hidden_discipline")]
    [Range(1, 10)]
    public int? HiddenDiscipline { get; set; }
    
    [JsonPropertyName("hidden_impulsivity")]
    [Range(1, 10)]
    public int? HiddenImpulsivity { get; set; }
    
    [JsonPropertyName("hidden_pragmatism")]
    [Range(1, 10)]
    public int? HiddenPragmatism { get; set; }
    
    [JsonPropertyName("hidden_resilience")]
    [Range(1, 10)]
    public int? HiddenResilience { get; set; }
}

public class FactionListDTO
{
    [JsonPropertyName("items")]
    public List<FactionDTO> Items { get; set; }
    
    [JsonPropertyName("total")]
    public int Total { get; set; }
    
    [JsonPropertyName("page")]
    public int Page { get; set; }
    
    [JsonPropertyName("size")]
    public int Size { get; set; }
    
    [JsonPropertyName("has_next")]
    public bool HasNext { get; set; }
    
    [JsonPropertyName("has_prev")]
    public bool HasPrev { get; set; }
}

public class FactionBehaviorModifiersDTO
{
    [JsonPropertyName("expansion_tendency")]
    public float ExpansionTendency { get; set; }
    
    [JsonPropertyName("alliance_reliability")]
    public float AllianceReliability { get; set; }
    
    [JsonPropertyName("betrayal_likelihood")]
    public float BetrayalLikelihood { get; set; }
    
    [JsonPropertyName("diplomatic_flexibility")]
    public float DiplomaticFlexibility { get; set; }
    
    [JsonPropertyName("crisis_management")]
    public float CrisisManagement { get; set; }
    
    [JsonPropertyName("military_aggression")]
    public float MilitaryAggression { get; set; }
    
    [JsonPropertyName("economic_cooperation")]
    public float EconomicCooperation { get; set; }
    
    [JsonPropertyName("succession_stability")]
    public float SuccessionStability { get; set; }
}

public class FactionDiplomaticStatusDTO
{
    [JsonPropertyName("faction_id")]
    public string FactionId { get; set; }
    
    [JsonPropertyName("faction_name")]
    public string FactionName { get; set; }
    
    [JsonPropertyName("diplomatic_stance")]
    public string DiplomaticStance { get; set; }
    
    [JsonPropertyName("active_treaties")]
    public List<TreatyDTO> ActiveTreaties { get; set; }
    
    [JsonPropertyName("current_negotiations")]
    public List<NegotiationDTO> CurrentNegotiations { get; set; }
    
    [JsonPropertyName("relationship_summary")]
    public Dictionary<string, int> RelationshipSummary { get; set; }
    
    [JsonPropertyName("trust_levels")]
    public Dictionary<string, float> TrustLevels { get; set; }
    
    [JsonPropertyName("betrayal_risks")]
    public Dictionary<string, float> BetrayalRisks { get; set; }
    
    [JsonPropertyName("recent_events")]
    public List<DiplomaticEventDTO> RecentEvents { get; set; }
    
    [JsonPropertyName("diplomatic_priorities")]
    public List<string> DiplomaticPriorities { get; set; }
}

public class FactionStabilityAssessmentDTO
{
    [JsonPropertyName("stability_score")]
    public float StabilityScore { get; set; }
    
    [JsonPropertyName("category")]
    public string Category { get; set; } // "highly_stable", "stable", "unstable", "volatile", "chaotic"
    
    [JsonPropertyName("organizational_stability")]
    public float OrganizationalStability { get; set; }
    
    [JsonPropertyName("leadership_stability")]
    public float LeadershipStability { get; set; }
    
    [JsonPropertyName("adaptability")]
    public float Adaptability { get; set; }
    
    [JsonPropertyName("risk_factors")]
    public List<string> RiskFactors { get; set; }
    
    [JsonPropertyName("predicted_issues")]
    public List<string> PredictedIssues { get; set; }
}

public class FactionPowerScoreDTO
{
    [JsonPropertyName("power_score")]
    public float PowerScore { get; set; }
    
    [JsonPropertyName("power_category")]
    public string PowerCategory { get; set; } // "dominant", "major", "moderate", "minor", "negligible"
    
    [JsonPropertyName("breakdown")]
    public Dictionary<string, float> Breakdown { get; set; }
    
    [JsonPropertyName("comparison_data")]
    public Dictionary<string, object> ComparisonData { get; set; }
}

public class AllianceEvaluationDTO
{
    [JsonPropertyName("evaluating_faction_id")]
    public string EvaluatingFactionId { get; set; }
    
    [JsonPropertyName("target_faction_id")]
    public string TargetFactionId { get; set; }
    
    [JsonPropertyName("alliance_type")]
    public string AllianceType { get; set; }
    
    [JsonPropertyName("compatibility_score")]
    public float CompatibilityScore { get; set; }
    
    [JsonPropertyName("success_probability")]
    public float SuccessProbability { get; set; }
    
    [JsonPropertyName("recommendation")]
    public string Recommendation { get; set; } // "accept", "reject", "negotiate"
    
    [JsonPropertyName("evaluation_factors")]
    public Dictionary<string, float> EvaluationFactors { get; set; }
    
    [JsonPropertyName("potential_benefits")]
    public List<string> PotentialBenefits { get; set; }
    
    [JsonPropertyName("potential_risks")]
    public List<string> PotentialRisks { get; set; }
}

public class BetrayalRiskDTO
{
    [JsonPropertyName("faction_id")]
    public string FactionId { get; set; }
    
    [JsonPropertyName("ally_id")]
    public string AllyId { get; set; }
    
    [JsonPropertyName("scenario")]
    public string Scenario { get; set; }
    
    [JsonPropertyName("betrayal_risk_score")]
    public float BetrayalRiskScore { get; set; }
    
    [JsonPropertyName("risk_level")]
    public string RiskLevel { get; set; } // "low", "medium", "high"
    
    [JsonPropertyName("risk_factors")]
    public Dictionary<string, float> RiskFactors { get; set; }
    
    [JsonPropertyName("mitigation_suggestions")]
    public List<string> MitigationSuggestions { get; set; }
}

public class TreatyDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("name")]
    public string Name { get; set; }
    
    [JsonPropertyName("type")]
    public string Type { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; }
    
    [JsonPropertyName("partner_factions")]
    public List<string> PartnerFactions { get; set; }
}

public class NegotiationDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("type")]
    public string Type { get; set; }
    
    [JsonPropertyName("partner")]
    public string Partner { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; }
    
    [JsonPropertyName("progress")]
    public float Progress { get; set; }
}

public class DiplomaticEventDTO
{
    [JsonPropertyName("event")]
    public string Event { get; set; }
    
    [JsonPropertyName("partner")]
    public string Partner { get; set; }
    
    [JsonPropertyName("date")]
    public string Date { get; set; }
    
    [JsonPropertyName("impact")]
    public string Impact { get; set; }
}

### 3. Character System (`/characters`)

**Endpoints:**
- `POST /characters` - Create character
- `GET /characters/{character_id}` - Get character by ID
- `GET /characters/by-game-id/{character_id}` - Get by game ID
- `PUT /characters/{character_id}` - Update character
- `DELETE /characters/{character_id}` - Soft delete character
- `GET /characters` - Search/list characters with filters
- `POST /characters/{character_id}/experience` - Grant XP
- `POST /characters/{character_id}/skills` - Increase skill
- `POST /characters/{character_id}/abilities` - Add ability
- `GET /characters/{character_id}/progression` - Get progression history

**DTOs:**
```csharp
public class CharacterDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("character_id")]
    [Required]
    public string CharacterId { get; set; }
    
    [JsonPropertyName("character_name")]
    [Required]
    public string CharacterName { get; set; }
    
    [JsonPropertyName("race")]
    [Required]
    public string Race { get; set; }
    
    [JsonPropertyName("level")]
    public int Level { get; set; } = 1;
    
    [JsonPropertyName("experience_points")]
    public int ExperiencePoints { get; set; } = 0;
    
    [JsonPropertyName("attributes")]
    public CharacterAttributesDTO Attributes { get; set; }
    
    [JsonPropertyName("skills")]
    public Dictionary<string, int> Skills { get; set; }
    
    [JsonPropertyName("abilities")]
    public List<string> Abilities { get; set; }
    
    [JsonPropertyName("background")]
    public string Background { get; set; }
    
    [JsonPropertyName("personality")]
    public string Personality { get; set; }
    
    [JsonPropertyName("alignment")]
    public string Alignment { get; set; }
    
    [JsonPropertyName("hit_points")]
    public int HitPoints { get; set; }
    
    [JsonPropertyName("max_hit_points")]
    public int MaxHitPoints { get; set; }
    
    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; } = true;
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
    
    [JsonPropertyName("updated_at")]
    public DateTime UpdatedAt { get; set; }
}

public class CharacterAttributesDTO
{
    [JsonPropertyName("strength")]
    [Range(-3, 5)]
    public int Strength { get; set; }
    
    [JsonPropertyName("dexterity")]
    [Range(-3, 5)]
    public int Dexterity { get; set; }
    
    [JsonPropertyName("constitution")]
    [Range(-3, 5)]
    public int Constitution { get; set; }
    
    [JsonPropertyName("intelligence")]
    [Range(-3, 5)]
    public int Intelligence { get; set; }
    
    [JsonPropertyName("wisdom")]
    [Range(-3, 5)]
    public int Wisdom { get; set; }
    
    [JsonPropertyName("charisma")]
    [Range(-3, 5)]
    public int Charisma { get; set; }
}
```

### 4. Quest System (`/quests`)

**Endpoints:**
- `POST /quests` - Create quest
- `GET /quests/{quest_id}` - Get quest details
- `PUT /quests/{quest_id}` - Update quest
- `DELETE /quests/{quest_id}` - Delete quest
- `GET /quests` - List quests with filters
- `POST /quests/{quest_id}/progress` - Update quest progress
- `POST /quests/{quest_id}/complete` - Complete quest

**DTOs:**
```csharp
public class QuestDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("title")]
    [Required]
    public string Title { get; set; }
    
    [JsonPropertyName("description")]
    [Required]
    public string Description { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } // "available", "active", "completed", "failed"
    
    [JsonPropertyName("objectives")]
    public List<QuestObjectiveDTO> Objectives { get; set; }
    
    [JsonPropertyName("rewards")]
    public QuestRewardsDTO Rewards { get; set; }
    
    [JsonPropertyName("prerequisites")]
    public List<string> Prerequisites { get; set; }
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}
```

### 5. Time System (`/time`)

**Endpoints:**
- `GET /time/current` - Get current game time
- `POST /time/advance` - Advance time
- `GET /time/calendar` - Get calendar information
- `POST /time/pause` - Pause time advancement
- `POST /time/resume` - Resume time advancement

**DTOs:**
```csharp
public class GameTimeDTO
{
    [JsonPropertyName("year")]
    public int Year { get; set; }
    
    [JsonPropertyName("month")]
    public int Month { get; set; }
    
    [JsonPropertyName("day")]
    public int Day { get; set; }
    
    [JsonPropertyName("hour")]
    public int Hour { get; set; }
    
    [JsonPropertyName("minute")]
    public int Minute { get; set; }
    
    [JsonPropertyName("is_paused")]
    public bool IsPaused { get; set; }
    
    [JsonPropertyName("time_scale")]
    public float TimeScale { get; set; }
}
```

### 6. Region System (`/regions`)

**Endpoints:**
- `GET /regions` - List all regions
- `GET /regions/{region_id}` - Get region details
- `POST /regions` - Create region
- `PUT /regions/{region_id}` - Update region
- `GET /regions/{region_id}/population` - Get region population
- `GET /regions/{region_id}/economy` - Get economic data

**DTOs:**
```csharp
public class RegionDTO
{
    [JsonPropertyName("id")]
    public string Id { get; set; }
    
    [JsonPropertyName("name")]
    [Required]
    public string Name { get; set; }
    
    [JsonPropertyName("type")]
    public string Type { get; set; } // "urban", "rural", "wilderness"
    
    [JsonPropertyName("population")]
    public int Population { get; set; }
    
    [JsonPropertyName("coordinates")]
    public CoordinatesDTO Coordinates { get; set; }
    
    [JsonPropertyName("biome")]
    public string Biome { get; set; }
    
    [JsonPropertyName("resources")]
    public Dictionary<string, float> Resources { get; set; }
    
    [JsonPropertyName("settlements")]
    public List<SettlementDTO> Settlements { get; set; }
}
```

### 7. World Generation System (`/world-generation`)

**Endpoints:**
- `POST /world-generation/generate` - Generate world
- `GET /world-generation/parameters` - Get generation parameters
- `POST /world-generation/parameters` - Set generation parameters
- `GET /world-generation/progress` - Get generation progress
- `POST /world-generation/preview` - Generate preview

**DTOs:**
```csharp
public class WorldGenerationParametersDTO
{
    [JsonPropertyName("seed")]
    public int Seed { get; set; }
    
    [JsonPropertyName("world_size")]
    public Vector2IntDTO WorldSize { get; set; }
    
    [JsonPropertyName("biome_settings")]
    public BiomeSettingsDTO BiomeSettings { get; set; }
    
    [JsonPropertyName("region_count")]
    [Range(1, 1000)]
    public int RegionCount { get; set; }
    
    [JsonPropertyName("settlement_density")]
    [Range(0.0f, 1.0f)]
    public float SettlementDensity { get; set; }
}
```

### 8. Population System (`/population`)

**Endpoints:**
- `GET /population/demographics` - Get demographic data
- `GET /population/migration` - Get migration patterns
- `POST /population/update` - Update population data
- `GET /population/growth` - Get growth statistics

### 9. Arc System (`/arcs`)

**Endpoints:**
- `GET /arcs` - List narrative arcs
- `POST /arcs` - Create arc
- `GET /arcs/{arc_id}` - Get arc details
- `PUT /arcs/{arc_id}` - Update arc
- `POST /arcs/{arc_id}/progress` - Progress arc

### 10. Motif System (`/motifs`)

**Endpoints:**
- `GET /motifs` - List motifs
- `POST /motifs` - Create motif
- `GET /motifs/{motif_id}` - Get motif details
- `PUT /motifs/{motif_id}` - Update motif

### 11. Relationship System (`/relationships`)

**Endpoints:**
- `GET /relationships` - List relationships
- `POST /relationships` - Create relationship
- `GET /relationships/{relationship_id}` - Get relationship
- `PUT /relationships/{relationship_id}` - Update relationship
- `DELETE /relationships/{relationship_id}` - Delete relationship

### 12. Economy System (`/economy`)

**Endpoints:**
- `GET /economy/markets` - Get market data
- `GET /economy/trade-routes` - Get trade routes
- `POST /economy/transactions` - Record transaction
- `GET /economy/prices` - Get item prices

### 13. Inventory System (`/inventory`)

**Endpoints:**
- `GET /inventory/{character_id}` - Get character inventory
- `POST /inventory/{character_id}/items` - Add item to inventory
- `PUT /inventory/{character_id}/items/{item_id}` - Update item
- `DELETE /inventory/{character_id}/items/{item_id}` - Remove item

## WebSocket Real-Time API (`/ws`)

The WebSocket endpoint provides real-time updates for:

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### Message Format
All WebSocket messages use this format:
```json
{
  "type": "message_type",
  "data": { /* message-specific data */ },
  "timestamp": "2025-01-29T12:00:00Z",
  "id": "unique_message_id"
}
```

### Message Types

#### Time Updates
```json
{
  "type": "time_update",
  "data": {
    "current_time": {
      "year": 1024,
      "month": 3,
      "day": 15,
      "hour": 14,
      "minute": 30
    },
    "time_scale": 1.0,
    "is_paused": false
  }
}
```

#### Combat Updates
```json
{
  "type": "combat_update", 
  "data": {
    "combat_id": "combat_123",
    "event": "turn_change",
    "current_participant": "character_456",
    "updated_state": { /* CombatStateDTO */ }
  }
}
```

#### Character Updates
```json
{
  "type": "character_update",
  "data": {
    "character_id": "char_123",
    "changes": {
      "hit_points": 25,
      "experience_points": 1500,
      "level": 3
    }
  }
}
```

#### Quest Updates
```json
{
  "type": "quest_update",
  "data": {
    "quest_id": "quest_789",
    "status": "completed",
    "objectives_completed": ["objective_1", "objective_2"]
  }
}
```

#### Region Events
```json
{
  "type": "region_event",
  "data": {
    "region_id": "region_101",
    "event_type": "population_change",
    "details": {
      "new_population": 5420,
      "change": 50,
      "reason": "migration"
    }
  }
}
```

## Unity Client Integration Patterns

### HTTP Client Usage
```csharp
// Example service implementation
public class CharacterServiceClient : BaseHTTPClient
{
    protected override string GetClientName() => "CharacterService";
    
    public void CreateCharacter(CharacterCreateDTO character, Action<CharacterDTO> onSuccess, Action<string> onError)
    {
        StartCoroutine(PostRequestCoroutine("/characters", character, (success, response) =>
        {
            if (success)
            {
                var characterDto = SafeDeserialize<CharacterDTO>(response);
                onSuccess?.Invoke(characterDto);
            }
            else
            {
                onError?.Invoke(response);
            }
        }));
    }
}
```

### WebSocket Integration
```csharp
public class WebSocketManager : MonoBehaviour
{
    private WebSocket webSocket;
    
    // Event system for message routing
    public event Action<TimeUpdateDTO> OnTimeUpdate;
    public event Action<CombatUpdateDTO> OnCombatUpdate;
    public event Action<CharacterUpdateDTO> OnCharacterUpdate;
    
    private void HandleMessage(string message)
    {
        var webSocketMessage = JsonUtility.FromJson<WebSocketMessage>(message);
        
        switch (webSocketMessage.type)
        {
            case "time_update":
                var timeUpdate = JsonUtility.FromJson<TimeUpdateDTO>(webSocketMessage.data);
                OnTimeUpdate?.Invoke(timeUpdate);
                break;
                
            case "combat_update":
                var combatUpdate = JsonUtility.FromJson<CombatUpdateDTO>(webSocketMessage.data);
                OnCombatUpdate?.Invoke(combatUpdate);
                break;
                
            case "character_update":
                var characterUpdate = JsonUtility.FromJson<CharacterUpdateDTO>(webSocketMessage.data);
                OnCharacterUpdate?.Invoke(characterUpdate);
                break;
        }
    }
}
```

## Data Transfer Object Standards

### Serialization Attributes
All DTOs use consistent JSON serialization:
```csharp
[JsonPropertyName("snake_case_property")]
public string CamelCaseProperty { get; set; }
```

### Validation Attributes
```csharp
[Required]
[StringLength(100, MinimumLength = 1)]
[Range(-3, 5)]
[EmailAddress]
[Url]
```

### Common Base Types
```csharp
public class Vector2DTO
{
    [JsonPropertyName("x")]
    public float X { get; set; }
    
    [JsonPropertyName("y")]
    public float Y { get; set; }
}

public class Vector2IntDTO
{
    [JsonPropertyName("x")]
    public int X { get; set; }
    
    [JsonPropertyName("y")]
    public int Y { get; set; }
}

public class CoordinatesDTO
{
    [JsonPropertyName("latitude")]
    public double Latitude { get; set; }
    
    [JsonPropertyName("longitude")]
    public double Longitude { get; set; }
}
```

## Error Handling

### HTTP Error Responses
```json
{
  "detail": "Error message",
  "error_code": "CHARACTER_NOT_FOUND",
  "timestamp": "2025-01-29T12:00:00Z"
}
```

### HTTP Status Codes
- `200 OK` - Successful GET/PUT
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation errors
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Unity Error Handling
```csharp
protected void HandleErrorResponse(string response, Action<string> onError)
{
    try
    {
        var errorDto = JsonUtility.FromJson<ErrorResponseDTO>(response);
        onError?.Invoke(errorDto.Detail);
    }
    catch
    {
        onError?.Invoke("Unknown error occurred");
    }
}
```

## Performance Considerations

### Pagination
List endpoints support pagination:
```http
GET /characters?page=1&per_page=10
```

Response includes metadata:
```json
{
  "items": [ /* list of items */ ],
  "total": 150,
  "page": 1,
  "per_page": 10,
  "pages": 15
}
```

### Caching Headers
Responses include appropriate cache headers:
```http
Cache-Control: max-age=300
ETag: "abc123"
Last-Modified: Wed, 29 Jan 2025 12:00:00 GMT
```

### Rate Limiting
API includes rate limiting:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643472000
```

## Development & Testing

### Mock Server
Unity includes mock server implementation for development and testing.

### API Documentation
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

### Health Checks
- Backend health: `GET /health`
- Service-specific health: `GET /{service}/health`

---

This API contract serves as the definitive specification for Unity-Backend communication in the Visual DM project. All client implementations should conform to these contracts to ensure proper integration and data consistency. 
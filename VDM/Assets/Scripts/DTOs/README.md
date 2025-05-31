# Data Transfer Objects (DTOs) for Visual DM Unity Client

This directory contains C# Data Transfer Objects that match the backend API specification schemas from `api_contracts.yaml`. These DTOs provide type-safe data exchange between the Unity frontend and the Python backend.

## Organization Structure

DTOs are organized by backend system/domain to maintain clean separation of concerns:

```
DTOs/
├── Core/           # Foundation layer DTOs
│   ├── Auth/       # Authentication and user management
│   ├── Events/     # Event system DTOs
│   └── Shared/     # Shared/common DTOs
├── Game/           # Core game layer DTOs
│   ├── Character/  # Character system DTOs
│   ├── Combat/     # Combat system DTOs
│   ├── Magic/      # Magic system DTOs
│   └── Time/       # Time system DTOs
├── World/          # World simulation DTOs
│   ├── Region/     # Region system DTOs
│   ├── POI/        # Point of Interest DTOs
│   ├── Population/ # Population system DTOs
│   └── WorldGen/   # World generation DTOs
├── Social/         # Social layer DTOs
│   ├── NPC/        # NPC system DTOs
│   ├── Faction/    # Faction system DTOs
│   ├── Diplomacy/  # Diplomacy system DTOs
│   └── Memory/     # Memory system DTOs
├── Economic/       # Economic layer DTOs
│   ├── Economy/    # Economy system DTOs
│   ├── Inventory/  # Inventory system DTOs
│   ├── Equipment/  # Equipment system DTOs
│   ├── Crafting/   # Crafting system DTOs
│   └── Loot/       # Loot system DTOs
├── Content/        # Content layer DTOs
│   ├── Quest/      # Quest system DTOs
│   ├── Arc/        # Narrative arc DTOs
│   ├── Motif/      # Motif system DTOs
│   ├── Rumor/      # Rumor system DTOs
│   └── Religion/   # Religion system DTOs
└── Interaction/    # Interaction layer DTOs
    ├── Dialogue/   # Dialogue system DTOs
    └── TensionWar/ # Tension/War system DTOs
```

## DTO Standards

### Naming Conventions
- Class names use PascalCase and end with `DTO` suffix
- Properties use PascalCase to match C# conventions
- Enums use PascalCase for both name and values

### Serialization
- All DTOs use `System.Text.Json` attributes for serialization
- Properties use `[JsonPropertyName("property_name")]` to match backend snake_case
- Optional properties are marked as nullable types (`Type?`)

### Validation
- Required properties are non-nullable
- String properties include length constraints where applicable
- Numeric properties include range constraints where applicable
- Custom validation attributes for complex validation rules

### Example DTO Structure

```csharp
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

[Serializable]
public class CharacterDTO
{
    [JsonPropertyName("id")]
    [Required]
    public string Id { get; set; }
    
    [JsonPropertyName("name")]
    [Required]
    [StringLength(100, MinimumLength = 1)]
    public string Name { get; set; }
    
    [JsonPropertyName("level")]
    [Range(1, 100)]
    public int Level { get; set; }
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
    
    [JsonPropertyName("properties")]
    public Dictionary<string, object>? Properties { get; set; }
}
```

## Integration with MockClient

These DTOs are designed to work seamlessly with the Unity `MockClient` for API communication. The MockClient handles serialization/deserialization automatically using these DTO definitions.

## Maintenance

When backend API contracts change:
1. Update the corresponding DTO classes
2. Ensure proper validation attributes
3. Update any dependent Unity code
4. Test with MockClient integration

## Dependencies

- System.Text.Json (Unity 2021.3+)
- System.ComponentModel.DataAnnotations
- Unity.Collections (for some specialized types) 
# Frontend Development Protocol (Unity)

## Overview
This document establishes the comprehensive protocol for all Unity frontend development work, ensuring consistency, quality, and alignment with the backend architecture standards.

## Assessment and Architecture Alignment

### System Analysis Requirements
- **Target Systems**: Run comprehensive analysis on all systems under `/VDM/Assets/Scripts/Systems/` and `/VDM/Assets/Scripts/Tests/`
- **Backend Alignment**: Ensure frontend systems mirror `/backend/systems/` structure exactly
- **Architecture Reference**: Reference `/VDM/docs/frontend_systems_inventory.md` for implementation status
- **Documentation Compliance**: Follow `Development_Bible.md` frontend architecture section

### Analysis Tools
- Use Unity's built-in compilation to identify missing dependencies and errors
- Perform exhaustive searches using grep/ripgrep for existing implementations
- Review Unity console for compilation errors and namespace issues
- Test WebSocket and API communication with backend services

## Structure and Organization Enforcement

### Unity Directory Organization
- **Canonical Location**: All frontend code MUST reside under `/VDM/Assets/Scripts/`
- **System Alignment**: Each system MUST mirror backend structure with four layers
- **Assembly Definitions**: Proper assembly definitions for each major component

### Directory Structure Standards
```
/VDM/Assets/Scripts/
├── Core/                    # Foundation classes
├── Infrastructure/          # Cross-cutting infrastructure
├── DTOs/                   # Data transfer objects
├── Systems/                # Game domain logic (mirrors backend)
│   └── {system_name}/
│       ├── Models/         # Data models and DTOs
│       ├── Services/       # API communication services
│       ├── UI/             # User interface components
│       ├── Integration/    # Unity-specific integration
│       └── README.md       # System documentation
├── UI/                     # UI framework
├── Services/               # Global services
├── Integration/            # Unity integrations
├── Runtime/                # Runtime logic
├── Tests/                  # Test suites
└── Examples/               # Sample implementations
```

## Unity-Specific Standards

### C# Coding Standards
- **Namespace Convention**: Follow `VDM.{Layer}.{System}` pattern
- **Assembly References**: Use proper assembly definitions and dependencies
- **Async/Await**: Use async/await for all API communication
- **Event Handling**: Use Unity Events and C# events appropriately

### Namespace Examples
```csharp
// ✅ CORRECT - Canonical namespaces
namespace VDM.Systems.Character.Services
namespace VDM.Infrastructure.Services.Http
namespace VDM.UI.Components.Common
namespace VDM.DTOs.Character

// ❌ INCORRECT - Non-standard namespaces
namespace Character.Services
namespace VDM.Services
namespace UIComponents
```

## DTO and API Communication Standards

### Data Transfer Objects
- **Backend Alignment**: DTOs MUST mirror backend schemas exactly
- **Serialization**: Use proper JSON serialization attributes
- **Validation**: Include client-side validation matching backend rules
- **Location Standard**: All DTOs in `/VDM/Assets/Scripts/DTOs/{System}/`

### DTO Implementation Pattern
```csharp
using System;
using System.ComponentModel.DataAnnotations;
using Newtonsoft.Json;

namespace VDM.DTOs.Character
{
    [Serializable]
    public class CharacterResponseDTO
    {
        [JsonProperty("id")]
        public int Id { get; set; }

        [JsonProperty("name")]
        [Required]
        public string Name { get; set; }

        [JsonProperty("description")]
        public string Description { get; set; }

        // Mirror backend DTO structure exactly
    }
}
```

## Service Layer Standards

### API Communication Services
- **HTTP Services**: Inherit from BaseHttpService for consistency
- **WebSocket Services**: Use standardized WebSocket handlers
- **Error Handling**: Comprehensive error handling and logging
- **Async Patterns**: All API calls must be async

### Service Implementation Pattern
```csharp
using System.Threading.Tasks;
using UnityEngine;
using VDM.Infrastructure.Core.Services;
using VDM.DTOs.Character;

namespace VDM.Systems.Character.Services
{
    public class CharacterService : BaseHttpService
    {
        private const string CHARACTERS_ENDPOINT = "/characters";

        public async Task<CharacterResponseDTO> GetCharacterAsync(int characterId)
        {
            try
            {
                return await GetAsync<CharacterResponseDTO>($"{CHARACTERS_ENDPOINT}/{characterId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get character {characterId}: {ex.Message}");
                throw;
            }
        }
    }
}
```

## UI Framework Standards

### Component Architecture
- **Base Components**: All UI components inherit from base classes
- **Event-Driven**: Use Unity Events for UI communication
- **Responsive Design**: Support multiple screen sizes and resolutions
- **Theme Support**: Consistent theming across all components

### UI Component Pattern
```csharp
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;
using VDM.UI.Core;
using VDM.DTOs.Character;

namespace VDM.Systems.Character.UI
{
    public class CharacterPanel : BaseUIPanel
    {
        [Header("UI Components")]
        [SerializeField] private Text characterNameText;
        [SerializeField] private Button editButton;

        [Header("Events")]
        public UnityEvent<CharacterResponseDTO> OnCharacterSelected;

        public void DisplayCharacter(CharacterResponseDTO character)
        {
            characterNameText.text = character.Name;
            OnCharacterSelected?.Invoke(character);
        }
    }
}
```

## Integration Layer Standards

### Unity-Specific Integration
- **Scene Management**: Proper scene loading and management
- **Prefab Management**: Standardized prefab creation and instantiation
- **Performance Optimization**: Efficient rendering and memory management
- **Platform Adaptation**: Platform-specific implementations when needed

### Integration Pattern
```csharp
using UnityEngine;
using VDM.Systems.Character.Services;
using VDM.Systems.Character.UI;

namespace VDM.Systems.Character.Integration
{
    public class CharacterSystemManager : MonoBehaviour
    {
        [SerializeField] private CharacterPanel characterPanel;
        private CharacterService characterService;

        private void Start()
        {
            characterService = ServiceLocator.GetService<CharacterService>();
            InitializeCharacterSystem();
        }

        private async void InitializeCharacterSystem()
        {
            // Integration logic between services and UI
        }
    }
}
```

## Testing Standards

### Test Organization
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test system integration and API communication
- **UI Tests**: Test user interface components and interactions
- **Performance Tests**: Test performance and memory usage

### Test Implementation Pattern
```csharp
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using VDM.Systems.Character.Services;

namespace VDM.Tests.Character
{
    public class CharacterServiceTests
    {
        private CharacterService characterService;

        [SetUp]
        public void Setup()
        {
            characterService = new CharacterService();
        }

        [Test]
        public async Task GetCharacter_ValidId_ReturnsCharacter()
        {
            // Test implementation
            var result = await characterService.GetCharacterAsync(1);
            Assert.IsNotNull(result);
            Assert.AreEqual(1, result.Id);
        }
    }
}
```

## Quality and Integration Standards

### Compilation Requirements
- **Zero Errors**: All code must compile without errors
- **Warning Management**: Address compilation warnings appropriately
- **Assembly Dependencies**: Proper assembly reference management
- **Namespace Resolution**: All namespaces must resolve correctly

### Performance Standards
- **Memory Management**: Efficient memory usage and garbage collection
- **Rendering Performance**: Smooth frame rates and efficient rendering
- **API Efficiency**: Minimize API calls and optimize data transfer
- **Caching Strategy**: Implement appropriate caching for performance

## WebSocket and Real-Time Communication

### WebSocket Standards
- **Event-Driven Updates**: Use WebSocket for real-time updates
- **Reconnection Logic**: Handle connection failures gracefully
- **Message Serialization**: Proper JSON message handling
- **Performance Optimization**: Efficient message processing

### WebSocket Implementation Pattern
```csharp
using System;
using UnityEngine;
using VDM.Infrastructure.Services;
using VDM.DTOs.Character;

namespace VDM.Systems.Character.Services
{
    public class CharacterWebSocketHandler : BaseWebSocketHandler
    {
        public event Action<CharacterResponseDTO> OnCharacterUpdated;

        protected override void OnMessageReceived(string message)
        {
            try
            {
                var character = JsonUtility.FromJson<CharacterResponseDTO>(message);
                OnCharacterUpdated?.Invoke(character);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to process character update: {ex.Message}");
            }
        }
    }
}
```

## Implementation Workflow

### Development Process
1. **Analysis Phase**: Identify requirements and backend dependencies
2. **DTO Implementation**: Create DTOs mirroring backend schemas
3. **Service Layer**: Implement API communication services
4. **UI Components**: Create user interface components
5. **Integration**: Bridge Unity-specific requirements
6. **Testing**: Comprehensive testing at all levels
7. **Documentation**: Update system documentation

### Quality Assurance Checklist
- [ ] System mirrors backend structure exactly
- [ ] All compilation errors resolved
- [ ] DTOs match backend schemas
- [ ] API communication tested and working
- [ ] UI components functional and responsive
- [ ] WebSocket integration operational
- [ ] Tests implemented and passing
- [ ] Documentation updated

## Reference Documents

### Primary Standards
- **Development Bible**: `/docs/Development_Bible.md` - Primary architectural standard
- **Frontend Systems Inventory**: `/VDM/docs/frontend_systems_inventory.md` - Implementation status reference
- **Backend Systems Inventory**: `backend/docs/backend_systems_inventory.md` - Backend alignment reference
- **API Contracts**: `api_contracts.yaml` - API specification (when available)

### Unity-Specific References
- **Unity Best Practices**: Follow Unity's official coding standards
- **Performance Guidelines**: Unity's performance optimization guidelines
- **UI Toolkit Documentation**: Modern Unity UI framework reference

---

**Note**: This protocol ensures frontend development maintains consistency with backend architecture while leveraging Unity's capabilities effectively. 
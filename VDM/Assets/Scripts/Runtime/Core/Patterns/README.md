# Standard Frontend System Patterns

This document defines the standard patterns and templates for implementing frontend systems in the VDM Unity project. These patterns ensure consistent architecture, maintainability, and seamless integration with the backend systems.

## Architecture Overview

Each frontend system mirrors the backend/systems/ structure exactly with Unity-specific additions:

```
SystemName/
├── Models/         # DTOs and data models matching backend exactly
├── Services/       # HTTP/WebSocket communication services  
├── UI/            # User interface components and controllers
└── Integration/   # Unity-specific integration logic
```

## Core Patterns

### 1. System Models (ISystemModel)

All system models must implement `ISystemModel` interface for consistency:

```csharp
[System.Serializable]
public class MySystemModel : ISystemModel
{
    [JsonProperty("id")]
    public string Id { get; set; }
    
    [JsonProperty("created_at")]
    public DateTime CreatedAt { get; set; }
    
    [JsonProperty("updated_at")]
    public DateTime UpdatedAt { get; set; }
    
    // System-specific properties with JsonProperty attributes
}
```

**Requirements:**
- Use `[System.Serializable]` for Unity inspector support
- Use `[JsonProperty]` attributes for API compatibility
- Match backend DTO structure exactly
- Include standard timestamp fields

### 2. HTTP Services (HttpService<T>)

For CRUD operations with backend APIs:

```csharp
public class MySystemHttpService : HttpService<MySystemModel>
{
    public MySystemHttpService() : base("api/mysystem") { }
    
    // Implement all abstract methods
    public override async Task<MySystemModel> CreateAsync(MySystemModel model) { }
    public override async Task<MySystemModel> GetByIdAsync(string id) { }
    public override async Task<List<MySystemModel>> GetAllAsync() { }
    public override async Task<MySystemModel> UpdateAsync(string id, MySystemModel model) { }
    public override async Task<bool> DeleteAsync(string id) { }
}
```

**Features:**
- Automatic header management
- Consistent error handling
- Async/await pattern
- Type-safe operations

### 3. WebSocket Handlers (WebSocketHandler)

For real-time features and live updates:

```csharp
public class MySystemWebSocketHandler : WebSocketHandler
{
    public event Action<MySystemModel> OnDataUpdated;
    
    protected override void RegisterMessageHandlers()
    {
        _messageHandlers["my_system_update"] = HandleDataUpdate;
    }
    
    private void HandleDataUpdate(string data)
    {
        var model = JsonConvert.DeserializeObject<MySystemModel>(data);
        OnDataUpdated?.Invoke(model);
    }
}
```

**Features:**
- Event-driven architecture
- Automatic message routing
- Connection state management
- Type-safe event handlers

### 4. UI Controllers (UIController)

For managing system UI components:

```csharp
public class MySystemUIController : UIController
{
    [Header("My System Components")]
    [SerializeField] private MySystemDataBinder _dataBinder;
    
    private MySystemHttpService _httpService;
    private MySystemWebSocketHandler _webSocketHandler;
    
    protected override void InitializeController()
    {
        // Get services from ServiceLocator
        _httpService = ServiceLocator.Instance.GetService<MySystemHttpService>();
        _webSocketHandler = ServiceLocator.Instance.GetService<MySystemWebSocketHandler>();
        
        // Subscribe to real-time updates
        if (_webSocketHandler != null)
            _webSocketHandler.OnDataUpdated += OnDataUpdated;
    }
}
```

**Features:**
- Canvas-based visibility management
- Service dependency injection
- Event subscription management
- Unity lifecycle integration

### 5. Data Binders (DataBinder<T>)

For model-view data binding:

```csharp
public class MySystemDataBinder : DataBinder<List<MySystemModel>>
{
    [SerializeField] private Transform _listContainer;
    [SerializeField] private GameObject _itemPrefab;
    
    protected override void OnDataChanged()
    {
        // Clear existing items
        // Create new items from bound data
        // Update UI display
    }
}
```

**Features:**
- Automatic UI updates on data changes
- Flexible data binding
- Performance-optimized updates
- Reusable across systems

### 6. System Managers (SystemManager)

For Unity lifecycle integration:

```csharp
public class MySystemManager : SystemManager
{
    [Header("My System Configuration")]
    [SerializeField] private string _backendUrl = "localhost:8000";
    
    protected override async Task InitializeSystem()
    {
        // Initialize services
        var httpService = new MySystemHttpService();
        var webSocketHandler = new MySystemWebSocketHandler();
        
        // Register with ServiceLocator
        ServiceLocator.Instance.RegisterService(httpService);
        ServiceLocator.Instance.RegisterService(webSocketHandler);
        
        // Connect WebSocket
        await webSocketHandler.ConnectAsync($"ws://{_backendUrl}/ws/mysystem");
    }
    
    protected override void ShutdownSystem()
    {
        // Cleanup and unregister services
    }
}
```

**Features:**
- Automatic dependency management
- Service registration/cleanup
- Async initialization
- Unity lifecycle integration

## Implementation Checklist

When creating a new system, follow this checklist:

### Models Layer ✅
- [ ] Create models implementing `ISystemModel`
- [ ] Add `[JsonProperty]` attributes matching backend
- [ ] Include all backend DTO fields
- [ ] Add Unity `[System.Serializable]` attribute

### Services Layer ✅
- [ ] Create HTTP service extending `HttpService<T>`
- [ ] Implement all CRUD operations
- [ ] Create WebSocket handler extending `WebSocketHandler`
- [ ] Register message handlers for real-time events
- [ ] Add appropriate event callbacks

### UI Layer ✅
- [ ] Create UI controller extending `UIController`
- [ ] Create data binders extending `DataBinder<T>`
- [ ] Design UI components with proper bindings
- [ ] Implement responsive layout if needed
- [ ] Add item-specific UI components

### Integration Layer ✅
- [ ] Create system manager extending `SystemManager`
- [ ] Create cache manager extending `CacheManager`
- [ ] Create configuration ScriptableObject
- [ ] Register services with ServiceLocator
- [ ] Set up WebSocket connections

### File Organization ✅
- [ ] Place files in correct directories
- [ ] Follow naming conventions
- [ ] Add appropriate Unity meta files
- [ ] Update assembly definitions if needed

## Naming Conventions

### Files and Classes
- **Models**: `{System}Model.cs` (e.g., `CharacterModel.cs`)
- **HTTP Services**: `{System}HttpService.cs` (e.g., `CharacterHttpService.cs`)
- **WebSocket Handlers**: `{System}WebSocketHandler.cs` (e.g., `CharacterWebSocketHandler.cs`)
- **UI Controllers**: `{System}UIController.cs` (e.g., `CharacterUIController.cs`)
- **Data Binders**: `{System}DataBinder.cs` (e.g., `CharacterDataBinder.cs`)
- **System Managers**: `{System}SystemManager.cs` (e.g., `CharacterSystemManager.cs`)
- **Cache Managers**: `{System}CacheManager.cs` (e.g., `CharacterCacheManager.cs`)
- **Configurations**: `{System}Configuration.cs` (e.g., `CharacterConfiguration.cs`)

### Namespaces
- **Models**: `VDM.Runtime.{System}.Models`
- **Services**: `VDM.Runtime.{System}.Services`
- **UI**: `VDM.Runtime.{System}.UI`
- **Integration**: `VDM.Runtime.{System}.Integration`

### Events and Methods
- Use PascalCase for all public members
- Prefix events with "On" (e.g., `OnDataUpdated`)
- Use async suffix for async methods (e.g., `LoadDataAsync`)

## Service Integration

### ServiceLocator Usage

Register services in SystemManager:
```csharp
ServiceLocator.Instance.RegisterService<IMyService>(myService);
```

Access services in UI components:
```csharp
var service = ServiceLocator.Instance.GetService<IMyService>();
```

### Event Broadcasting

Use EventBroadcaster for cross-system communication:
```csharp
// Subscribe
EventBroadcaster.Instance.Subscribe<MyEvent>(OnMyEvent);

// Broadcast
EventBroadcaster.Instance.Broadcast(new MyEvent { Data = "test" });
```

## Performance Considerations

### Caching Strategy
- Cache frequently accessed data
- Set appropriate expiry times
- Clear expired cache regularly
- Use system-specific cache keys

### UI Optimization
- Use object pooling for dynamic UI elements
- Implement lazy loading for large datasets
- Batch UI updates when possible
- Use efficient data binding patterns

### Network Optimization
- Implement request debouncing
- Use compression for large payloads
- Handle network failures gracefully
- Implement offline mode where appropriate

## Testing Patterns

### Unit Testing
- Test models serialization/deserialization
- Test service operations independently
- Mock external dependencies
- Verify event handling

### Integration Testing
- Test full system workflows
- Verify backend communication
- Test real-time features
- Validate UI updates

### Example Test Structure
```csharp
[Test]
public async Task MySystemHttpService_CreateAsync_ShouldReturnValidModel()
{
    // Arrange
    var service = new MySystemHttpService();
    var model = new MySystemModel { Name = "Test" };
    
    // Act
    var result = await service.CreateAsync(model);
    
    // Assert
    Assert.IsNotNull(result);
    Assert.IsNotEmpty(result.Id);
}
```

## Common Patterns

### Error Handling
```csharp
try
{
    var result = await _httpService.GetAllAsync();
    UpdateUI(result);
}
catch (Exception ex)
{
    Debug.LogError($"Failed to load data: {ex.Message}");
    // Show user-friendly error message
}
```

### Loading States
```csharp
public async Task LoadData()
{
    SetLoadingState(true);
    try
    {
        var data = await _httpService.GetAllAsync();
        UpdateUI(data);
    }
    finally
    {
        SetLoadingState(false);
    }
}
```

### Resource Cleanup
```csharp
protected override void OnDestroy()
{
    if (_webSocketHandler != null)
    {
        _webSocketHandler.OnDataUpdated -= OnDataUpdated;
    }
    base.OnDestroy();
}
```

## Migration Guidelines

When migrating existing systems to follow these patterns:

1. **Audit Existing Code**: Identify current structure and dependencies
2. **Create New Structure**: Set up directories following the standard pattern
3. **Migrate Models**: Convert existing data classes to implement ISystemModel
4. **Extract Services**: Separate API communication into HttpService and WebSocketHandler
5. **Refactor UI**: Convert MonoBehaviour UI to use UIController and DataBinder patterns
6. **Add Integration**: Create SystemManager for lifecycle management
7. **Update References**: Update all references to use new structure
8. **Test Migration**: Verify functionality works after migration

## Best Practices

### Code Organization
- Keep related functionality together
- Use clear, descriptive names
- Follow Single Responsibility Principle
- Minimize dependencies between systems

### Performance
- Use async/await for all network operations
- Implement proper caching strategies
- Optimize UI updates and rendering
- Profile and monitor performance regularly

### Maintainability
- Document complex logic
- Use consistent patterns across systems
- Keep configurations externalized
- Write comprehensive tests

### Unity Integration
- Follow Unity best practices
- Use Unity events where appropriate
- Implement proper MonoBehaviour lifecycle
- Handle Unity-specific concerns in Integration layer

This pattern system ensures consistent, maintainable, and scalable frontend architecture that seamlessly integrates with the backend systems while providing excellent Unity integration and user experience. 
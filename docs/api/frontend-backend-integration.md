# Frontend-Backend Integration API Documentation

## Overview

This document describes the API integration patterns between the Unity frontend and FastAPI backend, including HTTP requests, WebSocket communication, data synchronization, and error handling.

## Authentication & Security

### JWT Token-Based Authentication

#### Authentication Flow
```csharp
// AuthService.cs - Unity Frontend
public class AuthService : MonoBehaviour
{
    private const string TokenKey = "auth_token";
    private string _currentToken;
    
    public async Task<bool> LoginAsync(string username, string password)
    {
        var loginData = new LoginRequest
        {
            Username = username,
            Password = password
        };
        
        try
        {
            var response = await HttpClient.PostAsync("/auth/token", loginData);
            if (response.IsSuccessStatusCode)
            {
                var tokenResponse = await response.Content.ReadAsAsync<TokenResponse>();
                _currentToken = tokenResponse.AccessToken;
                
                // Store token securely
                PlayerPrefs.SetString(TokenKey, _currentToken);
                
                // Set up automatic refresh
                StartCoroutine(RefreshTokenPeriodically());
                
                return true;
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"Login failed: {ex.Message}");
        }
        
        return false;
    }
    
    public void SetAuthorizationHeader(HttpClient client)
    {
        if (!string.IsNullOrEmpty(_currentToken))
        {
            client.DefaultRequestHeaders.Authorization = 
                new AuthenticationHeaderValue("Bearer", _currentToken);
        }
    }
}
```

#### Backend Token Validation
```python
# auth.py - FastAPI Backend
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        user = await get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
            
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## HTTP Service Layer Pattern

### Base HTTP Service
```csharp
// BaseHttpService.cs
public abstract class BaseHttpService<T> where T : class
{
    protected readonly HttpClient _httpClient;
    protected readonly ICacheService _cache;
    protected readonly ILogger _logger;
    
    protected BaseHttpService(HttpClient httpClient, ICacheService cache, ILogger logger)
    {
        _httpClient = httpClient;
        _cache = cache;
        _logger = logger;
    }
    
    protected async Task<TResult> GetAsync<TResult>(string endpoint, bool useCache = true)
    {
        string cacheKey = $"{typeof(T).Name}_{endpoint}";
        
        // Check cache first
        if (useCache)
        {
            var cached = _cache.Get<TResult>(cacheKey);
            if (cached != null)
            {
                _logger.LogDebug($"Cache hit for {cacheKey}");
                return cached;
            }
        }
        
        try
        {
            _logger.LogDebug($"HTTP GET: {endpoint}");
            var response = await _httpClient.GetAsync(endpoint);
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                var result = JsonConvert.DeserializeObject<TResult>(content);
                
                // Cache successful responses
                if (useCache && result != null)
                {
                    _cache.Set(cacheKey, result, TimeSpan.FromMinutes(5));
                }
                
                return result;
            }
            else
            {
                await HandleErrorResponse(response);
                return default(TResult);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError($"HTTP GET failed for {endpoint}: {ex.Message}");
            throw new ApiException($"Request failed: {ex.Message}", ex);
        }
    }
    
    protected async Task<TResult> PostAsync<TData, TResult>(string endpoint, TData data)
    {
        try
        {
            var json = JsonConvert.SerializeObject(data);
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            
            _logger.LogDebug($"HTTP POST: {endpoint}");
            var response = await _httpClient.PostAsync(endpoint, content);
            
            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<TResult>(responseContent);
            }
            else
            {
                await HandleErrorResponse(response);
                return default(TResult);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError($"HTTP POST failed for {endpoint}: {ex.Message}");
            throw new ApiException($"Request failed: {ex.Message}", ex);
        }
    }
    
    private async Task HandleErrorResponse(HttpResponseMessage response)
    {
        var content = await response.Content.ReadAsStringAsync();
        var error = JsonConvert.DeserializeObject<ErrorResponse>(content);
        
        _logger.LogError($"API Error {response.StatusCode}: {error?.Detail ?? "Unknown error"}");
        
        switch (response.StatusCode)
        {
            case HttpStatusCode.Unauthorized:
                // Trigger re-authentication
                EventBus.Publish(new AuthenticationRequiredEvent());
                break;
            case HttpStatusCode.NotFound:
                throw new NotFoundException(error?.Detail ?? "Resource not found");
            case HttpStatusCode.BadRequest:
                throw new ValidationException(error?.Detail ?? "Invalid request");
            default:
                throw new ApiException($"API Error: {error?.Detail ?? "Unknown error"}");
        }
    }
}
```

### System-Specific Service Implementation
```csharp
// CharacterService.cs
public class CharacterService : BaseHttpService<CharacterDto>
{
    public CharacterService(HttpClient httpClient, ICacheService cache, ILogger logger)
        : base(httpClient, cache, logger) { }
    
    public async Task<CharacterDto> GetCharacterAsync(int id)
    {
        return await GetAsync<CharacterDto>($"/api/characters/{id}");
    }
    
    public async Task<List<CharacterDto>> GetCharactersAsync(CharacterFilter filter = null)
    {
        var queryString = BuildQueryString(filter);
        return await GetAsync<List<CharacterDto>>($"/api/characters{queryString}");
    }
    
    public async Task<CharacterDto> CreateCharacterAsync(CreateCharacterRequest request)
    {
        var character = await PostAsync<CreateCharacterRequest, CharacterDto>("/api/characters", request);
        
        // Invalidate relevant caches
        _cache.RemoveByPattern("characters_*");
        
        // Publish event for UI updates
        EventBus.Publish(new CharacterCreatedEvent(character));
        
        return character;
    }
    
    public async Task<CharacterDto> UpdateCharacterAsync(int id, UpdateCharacterRequest request)
    {
        var character = await PutAsync<UpdateCharacterRequest, CharacterDto>($"/api/characters/{id}", request);
        
        // Invalidate specific character cache
        _cache.Remove($"CharacterDto_/api/characters/{id}");
        
        // Publish event for UI updates
        EventBus.Publish(new CharacterUpdatedEvent(character));
        
        return character;
    }
    
    private string BuildQueryString(CharacterFilter filter)
    {
        if (filter == null) return "";
        
        var queryParams = new List<string>();
        
        if (!string.IsNullOrEmpty(filter.Name))
            queryParams.Add($"name={Uri.EscapeDataString(filter.Name)}");
        
        if (filter.MinLevel.HasValue)
            queryParams.Add($"min_level={filter.MinLevel}");
        
        if (filter.MaxLevel.HasValue)
            queryParams.Add($"max_level={filter.MaxLevel}");
        
        return queryParams.Count > 0 ? "?" + string.Join("&", queryParams) : "";
    }
}
```

## WebSocket Real-Time Communication

### WebSocket Manager
```csharp
// WebSocketManager.cs
public class WebSocketManager : MonoBehaviour
{
    private ClientWebSocket _webSocket;
    private CancellationTokenSource _cancellationToken;
    private readonly Dictionary<string, List<Action<object>>> _subscriptions = new();
    
    public bool IsConnected => _webSocket?.State == WebSocketState.Open;
    
    public async Task ConnectAsync(string url)
    {
        try
        {
            _webSocket = new ClientWebSocket();
            _cancellationToken = new CancellationTokenSource();
            
            // Add authentication header
            var authService = ServiceLocator.Get<AuthService>();
            if (authService.HasValidToken)
            {
                _webSocket.Options.SetRequestHeader("Authorization", $"Bearer {authService.Token}");
            }
            
            await _webSocket.ConnectAsync(new Uri(url), _cancellationToken.Token);
            
            // Start listening for messages
            _ = StartListening();
            
            Debug.Log("WebSocket connected successfully");
        }
        catch (Exception ex)
        {
            Debug.LogError($"WebSocket connection failed: {ex.Message}");
            throw;
        }
    }
    
    public void Subscribe<T>(Action<T> handler) where T : class
    {
        var messageType = typeof(T).Name;
        
        if (!_subscriptions.ContainsKey(messageType))
        {
            _subscriptions[messageType] = new List<Action<object>>();
        }
        
        _subscriptions[messageType].Add(obj => handler(obj as T));
    }
    
    public async Task SendAsync<T>(T message)
    {
        if (!IsConnected)
        {
            throw new InvalidOperationException("WebSocket is not connected");
        }
        
        var json = JsonConvert.SerializeObject(message);
        var bytes = Encoding.UTF8.GetBytes(json);
        var buffer = new ArraySegment<byte>(bytes);
        
        await _webSocket.SendAsync(buffer, WebSocketMessageType.Text, true, _cancellationToken.Token);
    }
    
    private async Task StartListening()
    {
        var buffer = new byte[4096];
        
        try
        {
            while (_webSocket.State == WebSocketState.Open && !_cancellationToken.Token.IsCancellationRequested)
            {
                var result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), _cancellationToken.Token);
                
                if (result.MessageType == WebSocketMessageType.Text)
                {
                    var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    await ProcessMessage(message);
                }
                else if (result.MessageType == WebSocketMessageType.Close)
                {
                    Debug.Log("WebSocket connection closed by server");
                    break;
                }
            }
        }
        catch (OperationCanceledException)
        {
            Debug.Log("WebSocket listening cancelled");
        }
        catch (Exception ex)
        {
            Debug.LogError($"WebSocket listening error: {ex.Message}");
            
            // Attempt reconnection
            _ = ReconnectAsync();
        }
    }
    
    private async Task ProcessMessage(string message)
    {
        try
        {
            var webSocketMessage = JsonConvert.DeserializeObject<WebSocketMessage>(message);
            
            if (_subscriptions.TryGetValue(webSocketMessage.Type, out var handlers))
            {
                var data = JsonConvert.DeserializeObject(webSocketMessage.Data.ToString(), 
                    Type.GetType(webSocketMessage.Type));
                
                foreach (var handler in handlers)
                {
                    try
                    {
                        handler(data);
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"Error in WebSocket message handler: {ex.Message}");
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to process WebSocket message: {ex.Message}");
        }
    }
    
    private async Task ReconnectAsync()
    {
        const int maxRetries = 5;
        const int baseDelayMs = 1000;
        
        for (int i = 0; i < maxRetries; i++)
        {
            try
            {
                await Task.Delay(baseDelayMs * (int)Math.Pow(2, i)); // Exponential backoff
                await ConnectAsync(_webSocket.Options.RequestHeaders["Host"]);
                return;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"Reconnection attempt {i + 1} failed: {ex.Message}");
            }
        }
        
        Debug.LogError("Failed to reconnect WebSocket after all retry attempts");
        EventBus.Publish(new WebSocketConnectionLostEvent());
    }
}
```

### WebSocket Message Handling
```csharp
// System-specific WebSocket handlers
public class CharacterWebSocketHandler : MonoBehaviour
{
    private WebSocketManager _webSocketManager;
    private CharacterService _characterService;
    
    void Start()
    {
        _webSocketManager = ServiceLocator.Get<WebSocketManager>();
        _characterService = ServiceLocator.Get<CharacterService>();
        
        // Subscribe to character-related WebSocket events
        _webSocketManager.Subscribe<CharacterUpdatedEvent>(OnCharacterUpdated);
        _webSocketManager.Subscribe<CharacterLevelUpEvent>(OnCharacterLevelUp);
        _webSocketManager.Subscribe<CharacterHealthChangedEvent>(OnCharacterHealthChanged);
    }
    
    private void OnCharacterUpdated(CharacterUpdatedEvent evt)
    {
        // Invalidate cache for this character
        var cacheService = ServiceLocator.Get<ICacheService>();
        cacheService.Remove($"CharacterDto_/api/characters/{evt.CharacterId}");
        
        // Publish Unity event for UI updates
        EventBus.Publish(evt);
        
        Debug.Log($"Character {evt.CharacterId} updated via WebSocket");
    }
    
    private void OnCharacterLevelUp(CharacterLevelUpEvent evt)
    {
        // Show level up notification
        var notificationService = ServiceLocator.Get<INotificationService>();
        notificationService.ShowSuccess($"{evt.CharacterName} leveled up to {evt.NewLevel}!");
        
        // Play level up sound effect
        var audioService = ServiceLocator.Get<IAudioService>();
        audioService.PlaySFX("levelup");
        
        // Update quest system for level-based unlocks
        EventBus.Publish(evt);
    }
    
    private void OnCharacterHealthChanged(CharacterHealthChangedEvent evt)
    {
        // Update health bar immediately without API call
        EventBus.Publish(evt);
        
        // Check for critical health warnings
        if (evt.NewHealth < evt.MaxHealth * 0.2f)
        {
            var notificationService = ServiceLocator.Get<INotificationService>();
            notificationService.ShowWarning($"{evt.CharacterName} health is critically low!");
        }
    }
}
```

## Data Transfer Objects (DTOs)

### Matching Backend Models
```csharp
// CharacterDto.cs - Must match backend Character model exactly
[System.Serializable]
public class CharacterDto
{
    [JsonProperty("id")]
    public int Id { get; set; }
    
    [JsonProperty("name")]
    public string Name { get; set; }
    
    [JsonProperty("level")]
    public int Level { get; set; }
    
    [JsonProperty("experience")]
    public int Experience { get; set; }
    
    [JsonProperty("health")]
    public int Health { get; set; }
    
    [JsonProperty("max_health")]
    public int MaxHealth { get; set; }
    
    [JsonProperty("attributes")]
    public CharacterAttributesDto Attributes { get; set; }
    
    [JsonProperty("skills")]
    public List<CharacterSkillDto> Skills { get; set; }
    
    [JsonProperty("equipment")]
    public List<EquipmentDto> Equipment { get; set; }
    
    [JsonProperty("faction_id")]
    public int? FactionId { get; set; }
    
    [JsonProperty("created_at")]
    public DateTime CreatedAt { get; set; }
    
    [JsonProperty("updated_at")]
    public DateTime UpdatedAt { get; set; }
}

[System.Serializable]
public class CharacterAttributesDto
{
    [JsonProperty("strength")]
    public int Strength { get; set; }
    
    [JsonProperty("dexterity")]
    public int Dexterity { get; set; }
    
    [JsonProperty("constitution")]
    public int Constitution { get; set; }
    
    [JsonProperty("intelligence")]
    public int Intelligence { get; set; }
    
    [JsonProperty("wisdom")]
    public int Wisdom { get; set; }
    
    [JsonProperty("charisma")]
    public int Charisma { get; set; }
}

// Request DTOs for API calls
[System.Serializable]
public class CreateCharacterRequest
{
    [JsonProperty("name")]
    public string Name { get; set; }
    
    [JsonProperty("race")]
    public string Race { get; set; }
    
    [JsonProperty("character_class")]
    public string CharacterClass { get; set; }
    
    [JsonProperty("attributes")]
    public CharacterAttributesDto Attributes { get; set; }
    
    [JsonProperty("background")]
    public string Background { get; set; }
}
```

### Backend Model (Reference)
```python
# models.py - Backend Character model
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class Character(BaseModel):
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    health = Column(Integer, nullable=False)
    max_health = Column(Integer, nullable=False)
    
    # Relationships
    attributes = relationship("CharacterAttributes", back_populates="character", uselist=False)
    skills = relationship("CharacterSkill", back_populates="character")
    equipment = relationship("Equipment", back_populates="character")
    
    faction_id = Column(Integer, ForeignKey("factions.id"), nullable=True)
    faction = relationship("Faction", back_populates="members")
```

## Error Handling and Retry Logic

### Unified Error Handling
```csharp
// ApiException.cs
public class ApiException : Exception
{
    public int StatusCode { get; }
    public string ErrorCode { get; }
    
    public ApiException(string message, int statusCode = 500, string errorCode = null) 
        : base(message)
    {
        StatusCode = statusCode;
        ErrorCode = errorCode;
    }
    
    public ApiException(string message, Exception innerException) 
        : base(message, innerException) { }
}

public class ValidationException : ApiException
{
    public Dictionary<string, string[]> ValidationErrors { get; }
    
    public ValidationException(string message, Dictionary<string, string[]> errors = null) 
        : base(message, 400, "validation_error")
    {
        ValidationErrors = errors ?? new Dictionary<string, string[]>();
    }
}

public class NotFoundException : ApiException
{
    public NotFoundException(string message) : base(message, 404, "not_found") { }
}
```

### Retry Logic Implementation
```csharp
// RetryService.cs
public static class RetryService
{
    public static async Task<T> ExecuteWithRetry<T>(
        Func<Task<T>> operation,
        int maxRetries = 3,
        TimeSpan? delay = null,
        Func<Exception, bool> retryCondition = null)
    {
        delay ??= TimeSpan.FromSeconds(1);
        retryCondition ??= (ex) => !(ex is ValidationException || ex is NotFoundException);
        
        for (int attempt = 0; attempt <= maxRetries; attempt++)
        {
            try
            {
                return await operation();
            }
            catch (Exception ex) when (attempt < maxRetries && retryCondition(ex))
            {
                Debug.LogWarning($"Operation failed (attempt {attempt + 1}/{maxRetries + 1}): {ex.Message}");
                
                // Exponential backoff
                var currentDelay = TimeSpan.FromMilliseconds(delay.Value.TotalMilliseconds * Math.Pow(2, attempt));
                await Task.Delay(currentDelay);
            }
        }
        
        // This should never be reached due to the when clause, but compiler requires it
        throw new InvalidOperationException("Retry logic error");
    }
}

// Usage in service
public async Task<CharacterDto> GetCharacterWithRetry(int id)
{
    return await RetryService.ExecuteWithRetry(
        async () => await GetCharacterAsync(id),
        maxRetries: 3,
        delay: TimeSpan.FromSeconds(1),
        retryCondition: ex => ex is not NotFoundException
    );
}
```

## Caching Strategy

### Cache Service Implementation
```csharp
// ICacheService.cs
public interface ICacheService
{
    T Get<T>(string key) where T : class;
    void Set<T>(string key, T value, TimeSpan expiration) where T : class;
    void Remove(string key);
    void RemoveByPattern(string pattern);
    void Clear();
}

// MemoryCacheService.cs
public class MemoryCacheService : ICacheService
{
    private readonly MemoryCache _cache;
    private readonly HashSet<string> _keys;
    
    public MemoryCacheService()
    {
        _cache = new MemoryCache(new MemoryCacheOptions
        {
            SizeLimit = 1000 // Limit cache entries
        });
        _keys = new HashSet<string>();
    }
    
    public T Get<T>(string key) where T : class
    {
        return _cache.TryGetValue(key, out var value) ? value as T : null;
    }
    
    public void Set<T>(string key, T value, TimeSpan expiration) where T : class
    {
        var options = new MemoryCacheEntryOptions
        {
            AbsoluteExpirationRelativeToNow = expiration,
            Size = 1,
            PostEvictionCallbacks = { new PostEvictionCallbackRegistration
            {
                EvictionCallback = (k, v, r, s) => _keys.Remove(k.ToString())
            }}
        };
        
        _cache.Set(key, value, options);
        _keys.Add(key);
    }
    
    public void Remove(string key)
    {
        _cache.Remove(key);
        _keys.Remove(key);
    }
    
    public void RemoveByPattern(string pattern)
    {
        var regex = new Regex(pattern.Replace("*", ".*"));
        var keysToRemove = _keys.Where(key => regex.IsMatch(key)).ToList();
        
        foreach (var key in keysToRemove)
        {
            Remove(key);
        }
    }
    
    public void Clear()
    {
        _cache.Dispose();
        _keys.Clear();
    }
}
```

## Performance Optimization

### Request Batching
```csharp
// BatchRequestService.cs
public class BatchRequestService
{
    private readonly Dictionary<string, List<BatchRequest>> _pendingRequests = new();
    private readonly float _batchDelay = 0.1f; // 100ms batch window
    
    public async Task<T> BatchRequest<T>(string batchKey, string endpoint, object data = null)
    {
        var request = new BatchRequest<T>
        {
            Endpoint = endpoint,
            Data = data,
            TaskCompletionSource = new TaskCompletionSource<T>()
        };
        
        if (!_pendingRequests.ContainsKey(batchKey))
        {
            _pendingRequests[batchKey] = new List<BatchRequest>();
            
            // Schedule batch execution
            _ = ScheduleBatchExecution(batchKey);
        }
        
        _pendingRequests[batchKey].Add(request);
        
        return await request.TaskCompletionSource.Task;
    }
    
    private async Task ScheduleBatchExecution(string batchKey)
    {
        await Task.Delay(TimeSpan.FromSeconds(_batchDelay));
        
        if (_pendingRequests.TryGetValue(batchKey, out var requests) && requests.Count > 0)
        {
            await ExecuteBatch(batchKey, requests);
            _pendingRequests.Remove(batchKey);
        }
    }
    
    private async Task ExecuteBatch(string batchKey, List<BatchRequest> requests)
    {
        try
        {
            // Create batch request payload
            var batchPayload = new
            {
                Requests = requests.Select(r => new { r.Endpoint, r.Data }).ToList()
            };
            
            // Send batch request
            var response = await HttpClient.PostAsync("/api/batch", batchPayload);
            var results = await response.Content.ReadAsAsync<List<object>>();
            
            // Distribute results to individual task completion sources
            for (int i = 0; i < requests.Count && i < results.Count; i++)
            {
                requests[i].SetResult(results[i]);
            }
        }
        catch (Exception ex)
        {
            // Set exception for all pending requests
            foreach (var request in requests)
            {
                request.SetException(ex);
            }
        }
    }
}
```

### Connection Pooling
```csharp
// HttpClientFactory.cs
public class HttpClientFactory
{
    private static readonly Lazy<HttpClient> _lazyClient = new Lazy<HttpClient>(CreateHttpClient);
    
    public static HttpClient Instance => _lazyClient.Value;
    
    private static HttpClient CreateHttpClient()
    {
        var handler = new HttpClientHandler()
        {
            MaxConnectionsPerServer = 10, // Connection pooling
            UseCookies = false
        };
        
        var client = new HttpClient(handler)
        {
            BaseAddress = new Uri(ConfigService.GetBackendUrl()),
            Timeout = TimeSpan.FromSeconds(30)
        };
        
        // Set default headers
        client.DefaultRequestHeaders.Accept.Clear();
        client.DefaultRequestHeaders.Accept.Add(
            new MediaTypeWithQualityHeaderValue("application/json"));
        
        client.DefaultRequestHeaders.Add("User-Agent", "VisualDM-Unity-Client/1.0");
        
        return client;
    }
}
```

This comprehensive API documentation provides the foundation for robust frontend-backend integration in Visual DM, ensuring reliable communication, proper error handling, and optimal performance across all systems. 
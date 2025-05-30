using Newtonsoft.Json;
using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Core.Patterns;


namespace VDM.Runtime.Core.Templates
{
    /// <summary>
    /// Template system demonstrating standard implementation patterns
    /// Copy this template when creating new systems, replacing "Template" with your system name
    /// </summary>
    public static class TemplateSystemExample
    {
        // ===== MODELS LAYER =====
        
        /// <summary>
        /// DTO model matching backend exactly
        /// Should be placed in: SystemName/Models/SystemNameModel.cs
        /// </summary>
        [System.Serializable]
        public class TemplateModel : ISystemModel
        {
            [JsonProperty("id")]
            public string Id { get; set; }
            
            [JsonProperty("name")]
            public string Name { get; set; }
            
            [JsonProperty("description")]
            public string Description { get; set; }
            
            [JsonProperty("created_at")]
            public DateTime CreatedAt { get; set; }
            
            [JsonProperty("updated_at")]
            public DateTime UpdatedAt { get; set; }
            
            // System-specific properties
            [JsonProperty("template_data")]
            public Dictionary<string, object> TemplateData { get; set; }
            
            public TemplateModel()
            {
                TemplateData = new Dictionary<string, object>();
            }
        }

        // ===== SERVICES LAYER =====
        
        /// <summary>
        /// HTTP service for CRUD operations
        /// Should be placed in: SystemName/Services/SystemNameHttpService.cs
        /// </summary>
        public class TemplateHttpService : HttpService<TemplateModel>
        {
            public TemplateHttpService() : base("api/template") { }

            public override async Task<TemplateModel> CreateAsync(TemplateModel model)
            {
                // Implementation would use actual HTTP client
                // For now, return mock data
                model.Id = Guid.NewGuid().ToString();
                model.CreatedAt = DateTime.UtcNow;
                model.UpdatedAt = DateTime.UtcNow;
                return model;
            }

            public override async Task<TemplateModel> GetByIdAsync(string id)
            {
                // Implementation would call actual API
                await Task.Delay(100); // Simulate network delay
                
                return new TemplateModel
                {
                    Id = id,
                    Name = $"Template {id}",
                    CreatedAt = DateTime.UtcNow.AddDays(-1),
                    UpdatedAt = DateTime.UtcNow
                };
            }

            public override async Task<List<TemplateModel>> GetAllAsync()
            {
                await Task.Delay(100);
                
                return new List<TemplateModel>
                {
                    new TemplateModel { Id = "1", Name = "Template 1" },
                    new TemplateModel { Id = "2", Name = "Template 2" }
                };
            }

            public override async Task<TemplateModel> UpdateAsync(string id, TemplateModel model)
            {
                await Task.Delay(100);
                
                model.Id = id;
                model.UpdatedAt = DateTime.UtcNow;
                return model;
            }

            public override async Task<bool> DeleteAsync(string id)
            {
                await Task.Delay(100);
                return true; // Success
            }
        }

        /// <summary>
        /// WebSocket handler for real-time updates
        /// Should be placed in: SystemName/Services/SystemNameWebSocketHandler.cs
        /// </summary>
        public class TemplateWebSocketHandler : WebSocketHandler
        {
            public event Action<TemplateModel> OnTemplateCreated;
            public event Action<TemplateModel> OnTemplateUpdated;
            public event Action<string> OnTemplateDeleted;

            public override async Task ConnectAsync(string url)
            {
                // Implementation would connect to actual WebSocket
                _isConnected = true;
                _connectionId = Guid.NewGuid().ToString();
                await Task.Delay(100);
            }

            public override async Task DisconnectAsync()
            {
                _isConnected = false;
                _connectionId = null;
                await Task.Delay(100);
            }

            public override async Task SendMessageAsync(string messageType, object data)
            {
                if (!_isConnected) return;
                
                var message = JsonConvert.SerializeObject(new
                {
                    type = messageType,
                    data = data,
                    connectionId = _connectionId
                });
                
                // Send message via actual WebSocket
                await Task.Delay(50);
            }

            protected override void RegisterMessageHandlers()
            {
                _messageHandlers["template_created"] = HandleTemplateCreated;
                _messageHandlers["template_updated"] = HandleTemplateUpdated;
                _messageHandlers["template_deleted"] = HandleTemplateDeleted;
            }

            private void HandleTemplateCreated(string data)
            {
                var template = JsonConvert.DeserializeObject<TemplateModel>(data);
                OnTemplateCreated?.Invoke(template);
            }

            private void HandleTemplateUpdated(string data)
            {
                var template = JsonConvert.DeserializeObject<TemplateModel>(data);
                OnTemplateUpdated?.Invoke(template);
            }

            private void HandleTemplateDeleted(string data)
            {
                var deleteData = JsonConvert.DeserializeObject<Dictionary<string, string>>(data);
                OnTemplateDeleted?.Invoke(deleteData["id"]);
            }
        }

        // ===== UI LAYER =====
        
        /// <summary>
        /// UI Controller for system interface
        /// Should be placed in: SystemName/UI/SystemNameController.cs
        /// </summary>
        public class TemplateUIController : UIController
        {
            [Header("Template UI Components")]
            [SerializeField] private GameObject _templateListParent;
            [SerializeField] private GameObject _templateItemPrefab;
            [SerializeField] private TemplateDataBinder _dataBinder;

            private TemplateHttpService _httpService;
            private TemplateWebSocketHandler _webSocketHandler;
            private List<TemplateModel> _templateData;

            protected override void InitializeController()
            {
                _httpService = ServiceLocator.Instance.GetService<TemplateHttpService>();
                _webSocketHandler = ServiceLocator.Instance.GetService<TemplateWebSocketHandler>();
                _templateData = new List<TemplateModel>();

                if (_webSocketHandler != null)
                {
                    _webSocketHandler.OnTemplateCreated += OnTemplateCreated;
                    _webSocketHandler.OnTemplateUpdated += OnTemplateUpdated;
                    _webSocketHandler.OnTemplateDeleted += OnTemplateDeleted;
                }
            }

            private async void Start()
            {
                await LoadTemplateData();
            }

            public async Task LoadTemplateData()
            {
                if (_httpService == null) return;

                try
                {
                    _templateData = await _httpService.GetAllAsync();
                    UpdateUI();
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Failed to load template data: {ex.Message}");
                }
            }

            private void UpdateUI()
            {
                if (_dataBinder != null)
                {
                    _dataBinder.BoundData = _templateData;
                }
            }

            private void OnTemplateCreated(TemplateModel template)
            {
                _templateData.Add(template);
                UpdateUI();
            }

            private void OnTemplateUpdated(TemplateModel template)
            {
                var index = _templateData.FindIndex(t => t.Id == template.Id);
                if (index >= 0)
                {
                    _templateData[index] = template;
                    UpdateUI();
                }
            }

            private void OnTemplateDeleted(string templateId)
            {
                _templateData.RemoveAll(t => t.Id == templateId);
                UpdateUI();
            }

            protected override void OnDestroy()
            {
                if (_webSocketHandler != null)
                {
                    _webSocketHandler.OnTemplateCreated -= OnTemplateCreated;
                    _webSocketHandler.OnTemplateUpdated -= OnTemplateUpdated;
                    _webSocketHandler.OnTemplateDeleted -= OnTemplateDeleted;
                }
                base.OnDestroy();
            }
        }

        /// <summary>
        /// Data binder for UI data binding
        /// Should be placed in: SystemName/UI/SystemNameDataBinder.cs
        /// </summary>
        public class TemplateDataBinder : DataBinder<List<TemplateModel>>
        {
            [Header("Template Display Components")]
            [SerializeField] private Transform _listContainer;
            [SerializeField] private GameObject _itemPrefab;

            private readonly List<GameObject> _instantiatedItems = new List<GameObject>();

            protected override void OnDataChanged()
            {
                ClearExistingItems();
                
                if (_boundData == null) return;

                foreach (var template in _boundData)
                {
                    CreateTemplateItem(template);
                }
            }

            private void ClearExistingItems()
            {
                foreach (var item in _instantiatedItems)
                {
                    if (item != null)
                        DestroyImmediate(item);
                }
                _instantiatedItems.Clear();
            }

            private void CreateTemplateItem(TemplateModel template)
            {
                if (_itemPrefab == null || _listContainer == null) return;

                var item = Instantiate(_itemPrefab, _listContainer);
                var itemBinder = item.GetComponent<TemplateItemBinder>();
                
                if (itemBinder != null)
                {
                    itemBinder.BoundData = template;
                }

                _instantiatedItems.Add(item);
            }
        }

        /// <summary>
        /// Individual item data binder
        /// Should be placed in: SystemName/UI/SystemNameItemBinder.cs
        /// </summary>
        public class TemplateItemBinder : DataBinder<TemplateModel>
        {
            [Header("Item Components")]
            [SerializeField] private UnityEngine.UI.Text _nameText;
            [SerializeField] private UnityEngine.UI.Text _descriptionText;
            [SerializeField] private UnityEngine.UI.Button _actionButton;

            protected override void OnDataChanged()
            {
                if (_boundData == null) return;

                if (_nameText != null)
                    _nameText.text = _boundData.Name;

                if (_descriptionText != null)
                    _descriptionText.text = _boundData.Description;

                if (_actionButton != null)
                {
                    _actionButton.onClick.RemoveAllListeners();
                    _actionButton.onClick.AddListener(() => OnItemAction(_boundData));
                }
            }

            private void OnItemAction(TemplateModel template)
            {
                Debug.Log($"Action triggered for template: {template.Name}");
                // Implement item-specific actions here
            }
        }

        // ===== INTEGRATION LAYER =====
        
        /// <summary>
        /// System manager for Unity lifecycle integration
        /// Should be placed in: SystemName/Integration/SystemNameManager.cs
        /// </summary>
        public class TemplateSystemManager : SystemManager
        {
            [Header("Template System Configuration")]
            [SerializeField] private string _backendUrl = "localhost:8000";
            [SerializeField] private bool _enableWebSocket = true;

            private TemplateHttpService _httpService;
            private TemplateWebSocketHandler _webSocketHandler;
            private TemplateCacheManager _cacheManager;

            protected override async Task InitializeSystem()
            {
                // Initialize services
                _httpService = new TemplateHttpService();
                _cacheManager = new TemplateCacheManager();

                if (_enableWebSocket)
                {
                    _webSocketHandler = new TemplateWebSocketHandler();
                    await _webSocketHandler.ConnectAsync($"ws://{_backendUrl}/ws/template");
                }

                // Register services
                ServiceLocator.Instance.RegisterService(_httpService);
                ServiceLocator.Instance.RegisterService(_webSocketHandler);
                ServiceLocator.Instance.RegisterService(_cacheManager);

                LogMessage("Template system initialized");
            }

            protected override void ShutdownSystem()
            {
                _webSocketHandler?.DisconnectAsync();
                
                ServiceLocator.Instance.UnregisterService<TemplateHttpService>();
                ServiceLocator.Instance.UnregisterService<TemplateWebSocketHandler>();
                ServiceLocator.Instance.UnregisterService<TemplateCacheManager>();

                LogMessage("Template system shut down");
            }
        }

        /// <summary>
        /// Cache manager for system-specific caching
        /// Should be placed in: SystemName/Integration/SystemNameCacheManager.cs
        /// </summary>
        public class TemplateCacheManager : CacheManager
        {
            public void CacheTemplate(TemplateModel template)
            {
                Set($"template_{template.Id}", template, TimeSpan.FromMinutes(10));
            }

            public TemplateModel GetCachedTemplate(string id)
            {
                return Get<TemplateModel>($"template_{id}");
            }

            public void CacheTemplateList(List<TemplateModel> templates)
            {
                Set("template_list", templates, TimeSpan.FromMinutes(5));
            }

            public List<TemplateModel> GetCachedTemplateList()
            {
                return Get<List<TemplateModel>>("template_list");
            }
        }

        /// <summary>
        /// Configuration for system settings
        /// Should be placed in: SystemName/Integration/SystemNameConfig.cs
        /// </summary>
        [CreateAssetMenu(fileName = "TemplateConfig", menuName = "VDM/Template/Configuration")]
        public class TemplateConfiguration : ConfigurationManager
        {
            [Header("Template Settings")]
            [SerializeField] private string _apiEndpoint = "api/template";
            [SerializeField] private int _maxCacheItems = 100;
            [SerializeField] private bool _enableAutoRefresh = true;
            [SerializeField] private float _refreshIntervalSeconds = 30f;

            public string ApiEndpoint => _apiEndpoint;
            public int MaxCacheItems => _maxCacheItems;
            public bool EnableAutoRefresh => _enableAutoRefresh;
            public float RefreshIntervalSeconds => _refreshIntervalSeconds;

            public override void LoadConfiguration()
            {
                // Load configuration from file or PlayerPrefs
                LogMessage("Template configuration loaded");
            }

            public override void SaveConfiguration()
            {
                // Save configuration to file or PlayerPrefs
                LogMessage("Template configuration saved");
            }

            public override void ResetToDefaults()
            {
                _apiEndpoint = "api/template";
                _maxCacheItems = 100;
                _enableAutoRefresh = true;
                _refreshIntervalSeconds = 30f;
                LogMessage("Template configuration reset to defaults");
            }

            protected override void ValidateConfiguration()
            {
                if (string.IsNullOrEmpty(_apiEndpoint))
                    _apiEndpoint = "api/template";
                
                if (_maxCacheItems <= 0)
                    _maxCacheItems = 100;
                
                if (_refreshIntervalSeconds <= 0)
                    _refreshIntervalSeconds = 30f;
            }

            private void LogMessage(string message)
            {
                if (EnableDebugMode)
                    Debug.Log($"[TemplateConfig] {message}");
            }
        }
    }
} 
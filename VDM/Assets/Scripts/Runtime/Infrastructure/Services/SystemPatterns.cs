using NativeWebSocket;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;


namespace VDM.Infrastructure.Core.Core.Patterns
{
    /// <summary>
    /// Base interface for all frontend system models that communicate with backend
    /// </summary>
    public interface ISystemModel
    {
        string Id { get; set; }
        DateTime CreatedAt { get; set; }
        DateTime UpdatedAt { get; set; }
    }

    /// <summary>
    /// Base class for HTTP service operations following CRUD patterns
    /// </summary>
    /// <typeparam name="T">The model type this service handles</typeparam>
    public abstract class HttpService<T> where T : class, ISystemModel
    {
        protected readonly string _baseUrl;
        protected readonly Dictionary<string, string> _defaultHeaders;

        protected HttpService(string baseUrl)
        {
            _baseUrl = baseUrl;
            _defaultHeaders = new Dictionary<string, string>
            {
                {"Content-Type", "application/json"},
                {"Accept", "application/json"}
            };
        }

        public abstract Task<T> CreateAsync(T model);
        public abstract Task<T> GetByIdAsync(string id);
        public abstract Task<List<T>> GetAllAsync();
        public abstract Task<T> UpdateAsync(string id, T model);
        public abstract Task<bool> DeleteAsync(string id);

        protected virtual Dictionary<string, string> GetHeaders()
        {
            return new Dictionary<string, string>(_defaultHeaders);
        }
    }

    /// <summary>
    /// Base class for WebSocket handlers for real-time features
    /// </summary>
    public abstract class WebSocketHandler
    {
        protected string _connectionId;
        protected bool _isConnected;
        protected readonly Dictionary<string, Action<string>> _messageHandlers;

        protected WebSocketHandler()
        {
            _messageHandlers = new Dictionary<string, Action<string>>();
            RegisterMessageHandlers();
        }

        public abstract Task ConnectAsync(string url);
        public abstract Task DisconnectAsync();
        public abstract Task SendMessageAsync(string messageType, object data);

        protected abstract void RegisterMessageHandlers();
        protected virtual void OnMessageReceived(string messageType, string data)
        {
            if (_messageHandlers.TryGetValue(messageType, out var handler))
            {
                handler(data);
            }
        }

        public bool IsConnected => _isConnected;
    }

    /// <summary>
    /// Base class for UI controllers that manage UI logic
    /// </summary>
    public abstract class UIController : MonoBehaviour
    {
        [SerializeField] protected Canvas _canvas;
        [SerializeField] protected bool _startActive = false;

        protected virtual void Awake()
        {
            if (_canvas == null)
                _canvas = GetComponent<Canvas>();
                
            InitializeController();
        }

        protected virtual void Start()
        {
            if (!_startActive)
                Hide();
        }

        protected abstract void InitializeController();

        public virtual void Show()
        {
            if (_canvas != null)
                _canvas.enabled = true;
            gameObject.SetActive(true);
        }

        public virtual void Hide()
        {
            if (_canvas != null)
                _canvas.enabled = false;
        }

        public virtual void Toggle()
        {
            if (IsVisible())
                Hide();
            else
                Show();
        }

        public virtual bool IsVisible()
        {
            return _canvas != null ? _canvas.enabled : gameObject.activeInHierarchy;
        }
    }

    /// <summary>
    /// Data binder for model-view binding
    /// </summary>
    /// <typeparam name="T">The model type to bind</typeparam>
    public abstract class DataBinder<T> : MonoBehaviour where T : class
    {
        [SerializeField] protected T _boundData;
        
        public T BoundData 
        { 
            get => _boundData; 
            set => SetData(value); 
        }

        protected virtual void SetData(T data)
        {
            _boundData = data;
            OnDataChanged();
        }

        protected abstract void OnDataChanged();

        public virtual void RefreshDisplay()
        {
            OnDataChanged();
        }
    }

    /// <summary>
    /// Factory pattern for dynamic UI creation
    /// </summary>
    /// <typeparam name="T">The UI component type to create</typeparam>
    public abstract class UIFactory<T> where T : Component
    {
        protected readonly Transform _parent;
        protected readonly List<T> _activeInstances;

        protected UIFactory(Transform parent)
        {
            _parent = parent;
            _activeInstances = new List<T>();
        }

        public abstract T Create();
        public abstract void Destroy(T instance);

        public virtual void DestroyAll()
        {
            foreach (var instance in _activeInstances.ToArray())
            {
                Destroy(instance);
            }
            _activeInstances.Clear();
        }

        protected virtual void RegisterInstance(T instance)
        {
            _activeInstances.Add(instance);
        }

        protected virtual void UnregisterInstance(T instance)
        {
            _activeInstances.Remove(instance);
        }
    }

    /// <summary>
    /// Responsive layout management for different screen sizes
    /// </summary>
    public abstract class ResponsiveLayout : MonoBehaviour
    {
        [SerializeField] protected Vector2 _referenceResolution = new Vector2(1920, 1080);
        [SerializeField] protected float _matchWidthOrHeight = 0.5f;

        protected virtual void Start()
        {
            ApplyLayout();
        }

        protected virtual void OnRectTransformDimensionsChange()
        {
            ApplyLayout();
        }

        protected abstract void ApplyLayout();

        protected virtual float GetScaleFactor()
        {
            var currentResolution = new Vector2(Screen.width, Screen.height);
            var widthScale = currentResolution.x / _referenceResolution.x;
            var heightScale = currentResolution.y / _referenceResolution.y;
            return Mathf.Lerp(widthScale, heightScale, _matchWidthOrHeight);
        }
    }
} 
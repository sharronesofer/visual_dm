using System;
using UnityEngine;
using UnityEngine.InputSystem;
using VisualDM.Core;

namespace VisualDM.Core
{
    /// <summary>
    /// Manages input using the new Unity Input System
    /// </summary>
    public class InputManager : MonoBehaviour
    {
        [SerializeField] private bool _initializeOnAwake = true;
        
        private static InputManager _instance;
        private PlayerInput _playerInput;
        private bool _isInitialized;
        
        // Input Actions
        private InputAction _moveAction;
        private InputAction _lookAction;
        private InputAction _interactAction;
        private InputAction _pauseAction;
        
        // Input values
        private Vector2 _moveInput;
        private Vector2 _lookInput;
        
        public static InputManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<InputManager>();
                    if (_instance == null)
                    {
                        GameObject gameObject = new GameObject("InputManager");
                        _instance = gameObject.AddComponent<InputManager>();
                        DontDestroyOnLoad(gameObject);
                    }
                }
                return _instance;
            }
        }
        
        public bool IsInitialized => _isInitialized;
        public Vector2 MoveInput => _moveInput;
        public Vector2 LookInput => _lookInput;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            if (_initializeOnAwake)
            {
                Initialize();
            }
        }

        private void OnEnable()
        {
            if (_isInitialized)
            {
                EnableInput();
            }
        }

        private void OnDisable()
        {
            if (_isInitialized)
            {
                DisableInput();
            }
        }

        /// <summary>
        /// Initialize the input manager
        /// </summary>
        public void Initialize()
        {
            if (_isInitialized)
            {
                return;
            }
            
            try
            {
                // Create PlayerInput component if it doesn't exist
                if (_playerInput == null)
                {
                    _playerInput = gameObject.AddComponent<PlayerInput>();
                    _playerInput.notificationBehavior = PlayerNotifications.InvokeCSharpEvents;
                }
                
                // Get references to input actions
                _moveAction = _playerInput.actions["Gameplay/Move"];
                _lookAction = _playerInput.actions["Gameplay/Look"];
                _interactAction = _playerInput.actions["Gameplay/Interact"];
                _pauseAction = _playerInput.actions["System/Pause"];
                
                // Setup input action callbacks
                _moveAction.performed += OnMovePerformed;
                _moveAction.canceled += OnMoveCanceled;
                
                _lookAction.performed += OnLookPerformed;
                _lookAction.canceled += OnLookCanceled;
                
                _interactAction.performed += OnInteractPerformed;
                
                _pauseAction.performed += OnPausePerformed;
                
                // Initially enable input
                EnableInput();
                
                _isInitialized = true;
                Debug.Log("Input Manager initialized");
                
                EventSystem.Publish(new InputInitializedEvent());
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to initialize Input Manager: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Enable all input actions
        /// </summary>
        public void EnableInput()
        {
            if (!_isInitialized) return;
            
            _moveAction?.Enable();
            _lookAction?.Enable();
            _interactAction?.Enable();
            _pauseAction?.Enable();
        }
        
        /// <summary>
        /// Disable all input actions
        /// </summary>
        public void DisableInput()
        {
            if (!_isInitialized) return;
            
            _moveAction?.Disable();
            _lookAction?.Disable();
            _interactAction?.Disable();
            _pauseAction?.Disable();
        }
        
        /// <summary>
        /// Switch to a specific action map
        /// </summary>
        public void SwitchActionMap(string actionMapName)
        {
            if (!_isInitialized || _playerInput == null) return;
            
            _playerInput.SwitchCurrentActionMap(actionMapName);
            Debug.Log($"Switched to action map: {actionMapName}");
            
            EventSystem.Publish(new InputActionMapChangedEvent { ActionMapName = actionMapName });
        }
        
        #region Input Event Handlers
        
        private void OnMovePerformed(InputAction.CallbackContext context)
        {
            _moveInput = context.ReadValue<Vector2>();
            EventSystem.Publish(new MoveInputEvent { Value = _moveInput });
        }
        
        private void OnMoveCanceled(InputAction.CallbackContext context)
        {
            _moveInput = Vector2.zero;
            EventSystem.Publish(new MoveInputEvent { Value = _moveInput });
        }
        
        private void OnLookPerformed(InputAction.CallbackContext context)
        {
            _lookInput = context.ReadValue<Vector2>();
            EventSystem.Publish(new LookInputEvent { Value = _lookInput });
        }
        
        private void OnLookCanceled(InputAction.CallbackContext context)
        {
            _lookInput = Vector2.zero;
            EventSystem.Publish(new LookInputEvent { Value = _lookInput });
        }
        
        private void OnInteractPerformed(InputAction.CallbackContext context)
        {
            EventSystem.Publish(new InteractInputEvent());
        }
        
        private void OnPausePerformed(InputAction.CallbackContext context)
        {
            EventSystem.Publish(new PauseInputEvent());
        }
        
        #endregion
    }
    
    #region Input Events
    
    public class InputInitializedEvent
    {
    }
    
    public class InputActionMapChangedEvent
    {
        public string ActionMapName { get; set; }
    }
    
    public class MoveInputEvent
    {
        public Vector2 Value { get; set; }
    }
    
    public class LookInputEvent
    {
        public Vector2 Value { get; set; }
    }
    
    public class InteractInputEvent
    {
    }
    
    public class PauseInputEvent
    {
    }
    
    #endregion
} 
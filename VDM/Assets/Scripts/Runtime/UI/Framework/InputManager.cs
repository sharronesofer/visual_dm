using System.Collections.Generic;
using System;
using UnityEngine.EventSystems;
using UnityEngine;


namespace VDM.Runtime.UI.Framework
{
    /// <summary>
    /// Input types supported by the input manager
    /// </summary>
    public enum InputType
    {
        KeyDown,
        KeyUp,
        KeyHeld,
        MouseDown,
        MouseUp,
        MouseHeld,
        MouseScroll,
        TouchTap,
        TouchHold,
        TouchSwipe,
        Gesture
    }
    
    /// <summary>
    /// Input action data
    /// </summary>
    [Serializable]
    public class InputAction
    {
        public string actionName;
        public InputType inputType;
        public KeyCode keyCode;
        public int mouseButton;
        public bool requiresShift;
        public bool requiresCtrl;
        public bool requiresAlt;
        public float holdDuration = 0.5f;
        public bool enabled = true;
        
        public InputAction(string name, InputType type, KeyCode key)
        {
            actionName = name;
            inputType = type;
            keyCode = key;
            mouseButton = -1;
        }
        
        public InputAction(string name, InputType type, int mouseBtn)
        {
            actionName = name;
            inputType = type;
            mouseButton = mouseBtn;
            keyCode = KeyCode.None;
        }
    }
    
    /// <summary>
    /// Touch input data
    /// </summary>
    public struct TouchData
    {
        public int fingerId;
        public Vector2 position;
        public Vector2 deltaPosition;
        public float pressure;
        public TouchPhase phase;
        public float startTime;
    }
    
    /// <summary>
    /// Swipe gesture data
    /// </summary>
    public struct SwipeData
    {
        public Vector2 startPosition;
        public Vector2 endPosition;
        public Vector2 direction;
        public float distance;
        public float duration;
    }
    
    /// <summary>
    /// Comprehensive input manager for UI and game controls
    /// </summary>
    public class InputManager : MonoBehaviour
    {
        [Header("Input Settings")]
        [SerializeField] private bool enableKeyboardInput = true;
        [SerializeField] private bool enableMouseInput = true;
        [SerializeField] private bool enableTouchInput = true;
        [SerializeField] private bool enableGestures = true;
        [SerializeField] private bool enableAccessibility = true;
        
        [Header("Mouse Settings")]
        [SerializeField] private float mouseSensitivity = 1f;
        [SerializeField] private bool invertMouseY = false;
        [SerializeField] private float scrollSensitivity = 1f;
        [SerializeField] private float doubleClickTime = 0.3f;
        
        [Header("Touch Settings")]
        [SerializeField] private float swipeThreshold = 50f;
        [SerializeField] private float tapThreshold = 0.2f;
        [SerializeField] private float holdThreshold = 0.5f;
        [SerializeField] private int maxTouchCount = 10;
        
        [Header("Accessibility")]
        [SerializeField] private bool enableVoiceCommands = false;
        [SerializeField] private bool enableGazeControl = false;
        [SerializeField] private float gazeClickTime = 2f;
        [SerializeField] private bool enableHighContrast = false;
        
        // Input action registry
        private Dictionary<string, InputAction> inputActions = new Dictionary<string, InputAction>();
        private Dictionary<string, float> keyHoldStartTimes = new Dictionary<string, float>();
        private Dictionary<string, bool> keyHoldStates = new Dictionary<string, bool>();
        
        // Mouse state
        private Vector2 lastMousePosition;
        private float lastClickTime = 0f;
        private int clickCount = 0;
        
        // Touch state
        private Dictionary<int, TouchData> activeTouches = new Dictionary<int, TouchData>();
        private Dictionary<int, Vector2> touchStartPositions = new Dictionary<int, Vector2>();
        private Dictionary<int, float> touchStartTimes = new Dictionary<int, float>();
        
        // Events
        public event Action<string> OnInputAction;
        public event Action<string, float> OnInputHold;
        public event Action<Vector2> OnMouseMove;
        public event Action<float> OnMouseScroll;
        public event Action<Vector2> OnMouseClick;
        public event Action<Vector2> OnMouseDoubleClick;
        public event Action<TouchData> OnTouchStart;
        public event Action<TouchData> OnTouchMove;
        public event Action<TouchData> OnTouchEnd;
        public event Action<SwipeData> OnSwipe;
        public event Action<Vector2, float> OnPinch;
        
        // Properties
        public bool IsInputEnabled { get; private set; } = true;
        public Vector2 MousePosition => Input.mousePosition;
        public Vector2 MouseDelta => (Vector2)Input.mousePosition - lastMousePosition;
        public bool IsMouseOverUI => EventSystem.current && EventSystem.current.IsPointerOverGameObject();
        public int ActiveTouchCount => activeTouches.Count;
        
        // Singleton instance
        private static InputManager instance;
        public static InputManager Instance
        {
            get
            {
                if (!instance)
                {
                    instance = FindObjectOfType<InputManager>();
                    if (!instance)
                    {
                        var go = new GameObject("InputManager");
                        instance = go.AddComponent<InputManager>();
                        DontDestroyOnLoad(go);
                    }
                }
                return instance;
            }
        }
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            if (instance && instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            instance = this;
            DontDestroyOnLoad(gameObject);
            
            InitializeDefaultActions();
        }
        
        private void Update()
        {
            if (!IsInputEnabled) return;
            
            if (enableKeyboardInput)
                HandleKeyboardInput();
            
            if (enableMouseInput)
                HandleMouseInput();
            
            if (enableTouchInput && Input.touchSupported)
                HandleTouchInput();
            
            if (enableAccessibility)
                HandleAccessibilityInput();
            
            UpdateInputStates();
        }
        
        #endregion
        
        #region Initialization
        
        /// <summary>
        /// Initialize default input actions
        /// </summary>
        private void InitializeDefaultActions()
        {
            // UI Navigation
            RegisterAction("Navigate_Up", InputType.KeyDown, KeyCode.UpArrow);
            RegisterAction("Navigate_Down", InputType.KeyDown, KeyCode.DownArrow);
            RegisterAction("Navigate_Left", InputType.KeyDown, KeyCode.LeftArrow);
            RegisterAction("Navigate_Right", InputType.KeyDown, KeyCode.RightArrow);
            RegisterAction("Select", InputType.KeyDown, KeyCode.Return);
            RegisterAction("Cancel", InputType.KeyDown, KeyCode.Escape);
            RegisterAction("Menu", InputType.KeyDown, KeyCode.Tab);
            
            // Game Controls
            RegisterAction("Inventory", InputType.KeyDown, KeyCode.I);
            RegisterAction("Character", InputType.KeyDown, KeyCode.C);
            RegisterAction("QuestLog", InputType.KeyDown, KeyCode.J);
            RegisterAction("Map", InputType.KeyDown, KeyCode.M);
            RegisterAction("Settings", InputType.KeyDown, KeyCode.O);
            
            // Movement (WASD)
            RegisterAction("Move_Forward", InputType.KeyHeld, KeyCode.W);
            RegisterAction("Move_Backward", InputType.KeyHeld, KeyCode.S);
            RegisterAction("Move_Left", InputType.KeyHeld, KeyCode.A);
            RegisterAction("Move_Right", InputType.KeyHeld, KeyCode.D);
            RegisterAction("Run", InputType.KeyHeld, KeyCode.LeftShift);
            RegisterAction("Jump", InputType.KeyDown, KeyCode.Space);
            
            // Mouse Actions
            RegisterAction("Primary_Action", InputType.MouseDown, 0);
            RegisterAction("Secondary_Action", InputType.MouseDown, 1);
            RegisterAction("Middle_Action", InputType.MouseDown, 2);
            
            // Hotbar
            for (int i = 1; i <= 10; i++)
            {
                RegisterAction($"Hotbar_{i}", InputType.KeyDown, KeyCode.Alpha0 + i);
            }
        }
        
        #endregion
        
        #region Input Action Management
        
        /// <summary>
        /// Register a new input action
        /// </summary>
        public void RegisterAction(string actionName, InputType inputType, KeyCode keyCode)
        {
            var action = new InputAction(actionName, inputType, keyCode);
            inputActions[actionName] = action;
        }
        
        /// <summary>
        /// Register a mouse input action
        /// </summary>
        public void RegisterAction(string actionName, InputType inputType, int mouseButton)
        {
            var action = new InputAction(actionName, inputType, mouseButton);
            inputActions[actionName] = action;
        }
        
        /// <summary>
        /// Unregister an input action
        /// </summary>
        public void UnregisterAction(string actionName)
        {
            inputActions.Remove(actionName);
            keyHoldStartTimes.Remove(actionName);
            keyHoldStates.Remove(actionName);
        }
        
        /// <summary>
        /// Enable or disable an input action
        /// </summary>
        public void SetActionEnabled(string actionName, bool enabled)
        {
            if (inputActions.TryGetValue(actionName, out var action))
            {
                action.enabled = enabled;
            }
        }
        
        /// <summary>
        /// Remap an input action to a new key
        /// </summary>
        public void RemapAction(string actionName, KeyCode newKey)
        {
            if (inputActions.TryGetValue(actionName, out var action))
            {
                action.keyCode = newKey;
                action.mouseButton = -1;
            }
        }
        
        /// <summary>
        /// Remap an input action to a new mouse button
        /// </summary>
        public void RemapAction(string actionName, int newMouseButton)
        {
            if (inputActions.TryGetValue(actionName, out var action))
            {
                action.mouseButton = newMouseButton;
                action.keyCode = KeyCode.None;
            }
        }
        
        /// <summary>
        /// Get all registered actions
        /// </summary>
        public Dictionary<string, InputAction> GetAllActions()
        {
            return new Dictionary<string, InputAction>(inputActions);
        }
        
        #endregion
        
        #region Keyboard Input
        
        /// <summary>
        /// Handle keyboard input
        /// </summary>
        private void HandleKeyboardInput()
        {
            foreach (var kvp in inputActions)
            {
                var actionName = kvp.Key;
                var action = kvp.Value;
                
                if (!action.enabled || action.keyCode == KeyCode.None) continue;
                
                // Check modifier keys
                if (action.requiresShift && !Input.GetKey(KeyCode.LeftShift) && !Input.GetKey(KeyCode.RightShift)) continue;
                if (action.requiresCtrl && !Input.GetKey(KeyCode.LeftControl) && !Input.GetKey(KeyCode.RightControl)) continue;
                if (action.requiresAlt && !Input.GetKey(KeyCode.LeftAlt) && !Input.GetKey(KeyCode.RightAlt)) continue;
                
                switch (action.inputType)
                {
                    case InputType.KeyDown:
                        if (Input.GetKeyDown(action.keyCode))
                        {
                            OnInputAction?.Invoke(actionName);
                        }
                        break;
                        
                    case InputType.KeyUp:
                        if (Input.GetKeyUp(action.keyCode))
                        {
                            OnInputAction?.Invoke(actionName);
                        }
                        break;
                        
                    case InputType.KeyHeld:
                        HandleKeyHold(actionName, action);
                        break;
                }
            }
        }
        
        /// <summary>
        /// Handle key hold input
        /// </summary>
        private void HandleKeyHold(string actionName, InputAction action)
        {
            bool isPressed = Input.GetKey(action.keyCode);
            bool wasHeld = keyHoldStates.GetValueOrDefault(actionName, false);
            
            if (isPressed)
            {
                if (!keyHoldStartTimes.ContainsKey(actionName))
                {
                    keyHoldStartTimes[actionName] = Time.time;
                }
                
                float holdTime = Time.time - keyHoldStartTimes[actionName];
                
                if (holdTime >= action.holdDuration && !wasHeld)
                {
                    keyHoldStates[actionName] = true;
                    OnInputAction?.Invoke(actionName);
                }
                
                if (wasHeld)
                {
                    OnInputHold?.Invoke(actionName, holdTime);
                }
            }
            else
            {
                keyHoldStartTimes.Remove(actionName);
                keyHoldStates.Remove(actionName);
            }
        }
        
        #endregion
        
        #region Mouse Input
        
        /// <summary>
        /// Handle mouse input
        /// </summary>
        private void HandleMouseInput()
        {
            // Handle mouse movement
            Vector2 currentMousePos = Input.mousePosition;
            if (currentMousePos != lastMousePosition)
            {
                OnMouseMove?.Invoke(currentMousePos);
                lastMousePosition = currentMousePos;
            }
            
            // Handle mouse scroll
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.01f)
            {
                OnMouseScroll?.Invoke(scroll * scrollSensitivity);
            }
            
            // Handle mouse clicks
            HandleMouseClicks();
            
            // Handle mouse actions
            foreach (var kvp in inputActions)
            {
                var actionName = kvp.Key;
                var action = kvp.Value;
                
                if (!action.enabled || action.mouseButton == -1) continue;
                
                switch (action.inputType)
                {
                    case InputType.MouseDown:
                        if (Input.GetMouseButtonDown(action.mouseButton))
                        {
                            OnInputAction?.Invoke(actionName);
                        }
                        break;
                        
                    case InputType.MouseUp:
                        if (Input.GetMouseButtonUp(action.mouseButton))
                        {
                            OnInputAction?.Invoke(actionName);
                        }
                        break;
                        
                    case InputType.MouseHeld:
                        if (Input.GetMouseButton(action.mouseButton))
                        {
                            HandleMouseHold(actionName, action);
                        }
                        break;
                }
            }
        }
        
        /// <summary>
        /// Handle mouse clicks and double clicks
        /// </summary>
        private void HandleMouseClicks()
        {
            if (Input.GetMouseButtonDown(0))
            {
                Vector2 clickPos = Input.mousePosition;
                float currentTime = Time.time;
                
                if (currentTime - lastClickTime < doubleClickTime)
                {
                    clickCount++;
                }
                else
                {
                    clickCount = 1;
                }
                
                lastClickTime = currentTime;
                
                if (clickCount == 1)
                {
                    OnMouseClick?.Invoke(clickPos);
                }
                else if (clickCount == 2)
                {
                    OnMouseDoubleClick?.Invoke(clickPos);
                    clickCount = 0;
                }
            }
        }
        
        /// <summary>
        /// Handle mouse hold input
        /// </summary>
        private void HandleMouseHold(string actionName, InputAction action)
        {
            if (!keyHoldStartTimes.ContainsKey(actionName))
            {
                keyHoldStartTimes[actionName] = Time.time;
            }
            
            float holdTime = Time.time - keyHoldStartTimes[actionName];
            
            if (holdTime >= action.holdDuration)
            {
                OnInputHold?.Invoke(actionName, holdTime);
            }
        }
        
        #endregion
        
        #region Touch Input
        
        /// <summary>
        /// Handle touch input
        /// </summary>
        private void HandleTouchInput()
        {
            // Update active touches
            foreach (Touch touch in Input.touches)
            {
                if (touch.fingerId >= maxTouchCount) continue;
                
                var touchData = new TouchData
                {
                    fingerId = touch.fingerId,
                    position = touch.position,
                    deltaPosition = touch.deltaPosition,
                    pressure = touch.pressure,
                    phase = touch.phase,
                    startTime = touchStartTimes.GetValueOrDefault(touch.fingerId, Time.time)
                };
                
                switch (touch.phase)
                {
                    case TouchPhase.Began:
                        HandleTouchStart(touchData);
                        break;
                        
                    case TouchPhase.Moved:
                        HandleTouchMove(touchData);
                        break;
                        
                    case TouchPhase.Ended:
                    case TouchPhase.Canceled:
                        HandleTouchEnd(touchData);
                        break;
                }
                
                activeTouches[touch.fingerId] = touchData;
            }
            
            // Handle gestures
            if (enableGestures)
            {
                HandleGestures();
            }
        }
        
        /// <summary>
        /// Handle touch start
        /// </summary>
        private void HandleTouchStart(TouchData touchData)
        {
            touchStartPositions[touchData.fingerId] = touchData.position;
            touchStartTimes[touchData.fingerId] = Time.time;
            
            OnTouchStart?.Invoke(touchData);
        }
        
        /// <summary>
        /// Handle touch move
        /// </summary>
        private void HandleTouchMove(TouchData touchData)
        {
            OnTouchMove?.Invoke(touchData);
        }
        
        /// <summary>
        /// Handle touch end
        /// </summary>
        private void HandleTouchEnd(TouchData touchData)
        {
            if (touchStartPositions.TryGetValue(touchData.fingerId, out var startPos))
            {
                float distance = Vector2.Distance(startPos, touchData.position);
                float duration = Time.time - touchStartTimes[touchData.fingerId];
                
                // Check for tap
                if (distance < swipeThreshold && duration < tapThreshold)
                {
                    // Handle tap
                    OnInputAction?.Invoke("Touch_Tap");
                }
                // Check for swipe
                else if (distance >= swipeThreshold)
                {
                    var swipeData = new SwipeData
                    {
                        startPosition = startPos,
                        endPosition = touchData.position,
                        direction = (touchData.position - startPos).normalized,
                        distance = distance,
                        duration = duration
                    };
                    
                    OnSwipe?.Invoke(swipeData);
                }
                
                touchStartPositions.Remove(touchData.fingerId);
                touchStartTimes.Remove(touchData.fingerId);
            }
            
            activeTouches.Remove(touchData.fingerId);
            OnTouchEnd?.Invoke(touchData);
        }
        
        /// <summary>
        /// Handle multi-touch gestures
        /// </summary>
        private void HandleGestures()
        {
            if (activeTouches.Count == 2)
            {
                var touches = new TouchData[2];
                int index = 0;
                foreach (var touch in activeTouches.Values)
                {
                    touches[index++] = touch;
                    if (index >= 2) break;
                }
                
                // Calculate pinch
                float currentDistance = Vector2.Distance(touches[0].position, touches[1].position);
                Vector2 center = (touches[0].position + touches[1].position) * 0.5f;
                
                // This would require storing previous distance for pinch delta
                // For now, just trigger pinch event
                OnPinch?.Invoke(center, currentDistance);
            }
        }
        
        #endregion
        
        #region Accessibility Input
        
        /// <summary>
        /// Handle accessibility input features
        /// </summary>
        private void HandleAccessibilityInput()
        {
            if (enableVoiceCommands)
            {
                // Voice command integration would go here
                // This would integrate with platform speech recognition
            }
            
            if (enableGazeControl)
            {
                // Gaze control integration would go here
                // This would integrate with eye tracking hardware
            }
        }
        
        #endregion
        
        #region Input State Management
        
        /// <summary>
        /// Update input states
        /// </summary>
        private void UpdateInputStates()
        {
            // Clean up old hold states
            var keysToRemove = new List<string>();
            foreach (var kvp in keyHoldStartTimes)
            {
                var actionName = kvp.Key;
                if (inputActions.TryGetValue(actionName, out var action))
                {
                    bool isStillPressed = false;
                    
                    if (action.keyCode != KeyCode.None)
                    {
                        isStillPressed = Input.GetKey(action.keyCode);
                    }
                    else if (action.mouseButton != -1)
                    {
                        isStillPressed = Input.GetMouseButton(action.mouseButton);
                    }
                    
                    if (!isStillPressed)
                    {
                        keysToRemove.Add(actionName);
                    }
                }
            }
            
            foreach (var key in keysToRemove)
            {
                keyHoldStartTimes.Remove(key);
                keyHoldStates.Remove(key);
            }
        }
        
        /// <summary>
        /// Enable or disable all input
        /// </summary>
        public void SetInputEnabled(bool enabled)
        {
            IsInputEnabled = enabled;
            
            if (!enabled)
            {
                // Clear all held states
                keyHoldStartTimes.Clear();
                keyHoldStates.Clear();
                activeTouches.Clear();
                touchStartPositions.Clear();
                touchStartTimes.Clear();
            }
        }
        
        /// <summary>
        /// Check if a specific action is currently pressed
        /// </summary>
        public bool IsActionPressed(string actionName)
        {
            if (!inputActions.TryGetValue(actionName, out var action) || !action.enabled)
                return false;
            
            if (action.keyCode != KeyCode.None)
            {
                return Input.GetKey(action.keyCode);
            }
            else if (action.mouseButton != -1)
            {
                return Input.GetMouseButton(action.mouseButton);
            }
            
            return false;
        }
        
        /// <summary>
        /// Check if a specific action was just pressed
        /// </summary>
        public bool IsActionDown(string actionName)
        {
            if (!inputActions.TryGetValue(actionName, out var action) || !action.enabled)
                return false;
            
            if (action.keyCode != KeyCode.None)
            {
                return Input.GetKeyDown(action.keyCode);
            }
            else if (action.mouseButton != -1)
            {
                return Input.GetMouseButtonDown(action.mouseButton);
            }
            
            return false;
        }
        
        /// <summary>
        /// Check if a specific action was just released
        /// </summary>
        public bool IsActionUp(string actionName)
        {
            if (!inputActions.TryGetValue(actionName, out var action) || !action.enabled)
                return false;
            
            if (action.keyCode != KeyCode.None)
            {
                return Input.GetKeyUp(action.keyCode);
            }
            else if (action.mouseButton != -1)
            {
                return Input.GetMouseButtonUp(action.mouseButton);
            }
            
            return false;
        }
        
        #endregion
        
        #region Settings
        
        /// <summary>
        /// Apply input settings
        /// </summary>
        public void ApplyInputSettings(Dictionary<string, object> settings)
        {
            if (settings.TryGetValue("MouseSensitivity", out var mouseSens))
            {
                mouseSensitivity = Convert.ToSingle(mouseSens);
            }
            
            if (settings.TryGetValue("InvertMouseY", out var invertY))
            {
                invertMouseY = Convert.ToBoolean(invertY);
            }
            
            if (settings.TryGetValue("ScrollSensitivity", out var scrollSens))
            {
                scrollSensitivity = Convert.ToSingle(scrollSens);
            }
            
            if (settings.TryGetValue("DoubleClickTime", out var doubleClick))
            {
                doubleClickTime = Convert.ToSingle(doubleClick);
            }
            
            if (settings.TryGetValue("SwipeThreshold", out var swipeThresh))
            {
                swipeThreshold = Convert.ToSingle(swipeThresh);
            }
        }
        
        /// <summary>
        /// Get current input settings
        /// </summary>
        public Dictionary<string, object> GetInputSettings()
        {
            return new Dictionary<string, object>
            {
                ["MouseSensitivity"] = mouseSensitivity,
                ["InvertMouseY"] = invertMouseY,
                ["ScrollSensitivity"] = scrollSensitivity,
                ["DoubleClickTime"] = doubleClickTime,
                ["SwipeThreshold"] = swipeThreshold,
                ["EnableKeyboard"] = enableKeyboardInput,
                ["EnableMouse"] = enableMouseInput,
                ["EnableTouch"] = enableTouchInput,
                ["EnableGestures"] = enableGestures,
                ["EnableAccessibility"] = enableAccessibility
            };
        }
        
        #endregion
    }
} 
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System;
using UnityEngine.UI;
using UnityEngine;
using VDM.UI.Core;


namespace VDM.Infrastructure.Debug
{
    /// <summary>
    /// In-game developer console for debugging and command execution
    /// Implements Task 22: Developer Console with command system
    /// </summary>
    public class DebugConsole : MonoBehaviour
    {
        [Header("Console UI")]
        [SerializeField] private GameObject consolePanel;
        [SerializeField] private ScrollRect scrollRect;
        [SerializeField] private Text outputText;
        [SerializeField] private InputField inputField;
        [SerializeField] private Button submitButton;
        [SerializeField] private Button clearButton;
        [SerializeField] private Button toggleButton;
        
        [Header("Console Settings")]
        [SerializeField] private KeyCode toggleKey = KeyCode.BackQuote; // Tilde key
        [SerializeField] private int maxOutputLines = 500;
        [SerializeField] private bool showTimestamps = true;
        [SerializeField] private bool logToUnityConsole = true;
        
        // Singleton instance
        public static DebugConsole Instance { get; private set; }
        
        // Console state
        private bool _isConsoleOpen = false;
        private List<string> _outputLines = new List<string>();
        private List<string> _commandHistory = new List<string>();
        private int _historyIndex = -1;
        
        // Command system
        private Dictionary<string, DebugCommand> _commands = new Dictionary<string, DebugCommand>();
        private Dictionary<string, string> _aliases = new Dictionary<string, string>();
        
        // Events
        public event Action<bool> OnConsoleToggled;
        public event Action<string> OnCommandExecuted;
        
        private void Awake()
        {
            if (Instance == null)
            {
                Instance = this;
                DontDestroyOnLoad(gameObject);
                Initialize();
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        private void Initialize()
        {
            SetupUI();
            RegisterDefaultCommands();
            RegisterSystemCommands();
            
            AddOutput("Debug Console initialized. Type 'help' for available commands.");
        }
        
        private void SetupUI()
        {
            // Create console UI if not assigned
            if (consolePanel == null)
            {
                CreateConsoleUI();
            }
            
            // Setup input handling
            if (inputField != null)
            {
                inputField.onEndEdit.AddListener(OnInputSubmit);
                inputField.text = "";
            }
            
            if (submitButton != null)
            {
                submitButton.onClick.AddListener(() => OnInputSubmit(inputField.text));
            }
            
            if (clearButton != null)
            {
                clearButton.onClick.AddListener(ClearOutput);
            }
            
            if (toggleButton != null)
            {
                toggleButton.onClick.AddListener(() => ToggleConsole());
            }
            
            // Initially hide console
            SetConsoleVisible(false);
        }
        
        private void CreateConsoleUI()
        {
            // Create console panel under UI overlay
            var canvas = UIManager.Instance?.transform ?? FindObjectOfType<Canvas>()?.transform;
            if (canvas == null)
            {
                Debug.LogError("[DebugConsole] No Canvas found for console UI");
                return;
            }
            
            consolePanel = new GameObject("DebugConsole");
            consolePanel.transform.SetParent(canvas, false);
            
            var rectTransform = consolePanel.AddComponent<RectTransform>();
            rectTransform.anchorMin = new Vector2(0, 0.5f);
            rectTransform.anchorMax = new Vector2(1, 1);
            rectTransform.sizeDelta = Vector2.zero;
            rectTransform.anchoredPosition = Vector2.zero;
            
            // Background
            var image = consolePanel.AddComponent<Image>();
            image.color = new Color(0, 0, 0, 0.8f);
            
            // Create scrollable text area
            CreateScrollableOutput();
            
            // Create input field
            CreateInputField();
        }
        
        private void CreateScrollableOutput()
        {
            var scrollRectGO = new GameObject("ScrollRect");
            scrollRectGO.transform.SetParent(consolePanel.transform, false);
            
            var scrollRectTransform = scrollRectGO.AddComponent<RectTransform>();
            scrollRectTransform.anchorMin = new Vector2(0, 0.1f);
            scrollRectTransform.anchorMax = new Vector2(1, 1);
            scrollRectTransform.sizeDelta = Vector2.zero;
            scrollRectTransform.anchoredPosition = Vector2.zero;
            
            scrollRect = scrollRectGO.AddComponent<ScrollRect>();
            scrollRect.vertical = true;
            scrollRect.horizontal = false;
            
            // Content area
            var contentGO = new GameObject("Content");
            contentGO.transform.SetParent(scrollRectGO.transform, false);
            
            var contentTransform = contentGO.AddComponent<RectTransform>();
            contentTransform.anchorMin = new Vector2(0, 0);
            contentTransform.anchorMax = new Vector2(1, 1);
            contentTransform.sizeDelta = Vector2.zero;
            contentTransform.anchoredPosition = Vector2.zero;
            
            scrollRect.content = contentTransform;
            
            // Output text
            var textGO = new GameObject("OutputText");
            textGO.transform.SetParent(contentGO.transform, false);
            
            var textTransform = textGO.AddComponent<RectTransform>();
            textTransform.anchorMin = Vector2.zero;
            textTransform.anchorMax = Vector2.one;
            textTransform.sizeDelta = Vector2.zero;
            textTransform.anchoredPosition = Vector2.zero;
            
            outputText = textGO.AddComponent<Text>();
            outputText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            outputText.fontSize = 12;
            outputText.color = Color.white;
            outputText.alignment = TextAnchor.LowerLeft;
            outputText.verticalOverflow = VerticalWrapMode.Overflow;
            outputText.horizontalOverflow = HorizontalWrapMode.Wrap;
        }
        
        private void CreateInputField()
        {
            var inputGO = new GameObject("InputField");
            inputGO.transform.SetParent(consolePanel.transform, false);
            
            var inputTransform = inputGO.AddComponent<RectTransform>();
            inputTransform.anchorMin = new Vector2(0, 0);
            inputTransform.anchorMax = new Vector2(1, 0.1f);
            inputTransform.sizeDelta = Vector2.zero;
            inputTransform.anchoredPosition = Vector2.zero;
            
            inputField = inputGO.AddComponent<InputField>();
            
            // Input field background
            var inputImage = inputGO.AddComponent<Image>();
            inputImage.color = new Color(0.2f, 0.2f, 0.2f, 0.8f);
            
            // Input field text
            var textGO = new GameObject("Text");
            textGO.transform.SetParent(inputGO.transform, false);
            
            var textTransform = textGO.AddComponent<RectTransform>();
            textTransform.anchorMin = Vector2.zero;
            textTransform.anchorMax = Vector2.one;
            textTransform.sizeDelta = Vector2.zero;
            textTransform.anchoredPosition = Vector2.zero;
            
            var text = textGO.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            text.fontSize = 14;
            text.color = Color.white;
            text.supportRichText = false;
            
            inputField.textComponent = text;
            inputField.text = "";
        }
        
        private void Update()
        {
            HandleInput();
        }
        
        private void HandleInput()
        {
            // Toggle console
            if (Input.GetKeyDown(toggleKey))
            {
                ToggleConsole();
            }
            
            // Command history navigation
            if (_isConsoleOpen && inputField != null && inputField.isFocused)
            {
                if (Input.GetKeyDown(KeyCode.UpArrow))
                {
                    NavigateHistory(-1);
                }
                else if (Input.GetKeyDown(KeyCode.DownArrow))
                {
                    NavigateHistory(1);
                }
            }
        }
        
        private void NavigateHistory(int direction)
        {
            if (_commandHistory.Count == 0) return;
            
            _historyIndex += direction;
            _historyIndex = Mathf.Clamp(_historyIndex, -1, _commandHistory.Count - 1);
            
            if (_historyIndex >= 0)
            {
                inputField.text = _commandHistory[_historyIndex];
                inputField.caretPosition = inputField.text.Length;
            }
            else
            {
                inputField.text = "";
            }
        }
        
        public void ToggleConsole()
        {
            SetConsoleVisible(!_isConsoleOpen);
        }
        
        public void SetConsoleVisible(bool visible)
        {
            _isConsoleOpen = visible;
            
            if (consolePanel != null)
            {
                consolePanel.SetActive(visible);
            }
            
            if (visible && inputField != null)
            {
                inputField.Select();
                inputField.ActivateInputField();
            }
            
            OnConsoleToggled?.Invoke(visible);
        }
        
        private void OnInputSubmit(string input)
        {
            if (string.IsNullOrWhiteSpace(input)) return;
            
            // Add to history
            if (_commandHistory.Count == 0 || _commandHistory[_commandHistory.Count - 1] != input)
            {
                _commandHistory.Add(input);
                if (_commandHistory.Count > 50) // Limit history
                {
                    _commandHistory.RemoveAt(0);
                }
            }
            _historyIndex = -1;
            
            // Echo command
            AddOutput($"> {input}");
            
            // Execute command
            ExecuteCommand(input);
            
            // Clear input
            inputField.text = "";
            inputField.Select();
            inputField.ActivateInputField();
        }
        
        public void ExecuteCommand(string commandLine)
        {
            try
            {
                var parts = ParseCommand(commandLine);
                if (parts.Length == 0) return;
                
                var commandName = parts[0].ToLower();
                var args = parts.Skip(1).ToArray();
                
                // Check for alias
                if (_aliases.ContainsKey(commandName))
                {
                    commandName = _aliases[commandName];
                }
                
                // Execute command
                if (_commands.ContainsKey(commandName))
                {
                    _commands[commandName].Execute(args);
                    OnCommandExecuted?.Invoke(commandLine);
                }
                else
                {
                    AddOutput($"Unknown command: {commandName}. Type 'help' for available commands.");
                }
            }
            catch (Exception ex)
            {
                AddOutput($"Error executing command: {ex.Message}");
                if (logToUnityConsole)
                {
                    Debug.LogError($"[DebugConsole] Command execution error: {ex}");
                }
            }
        }
        
        private string[] ParseCommand(string commandLine)
        {
            var parts = new List<string>();
            var current = "";
            var inQuotes = false;
            
            for (int i = 0; i < commandLine.Length; i++)
            {
                var c = commandLine[i];
                
                if (c == '"' && (i == 0 || commandLine[i - 1] != '\\'))
                {
                    inQuotes = !inQuotes;
                }
                else if (c == ' ' && !inQuotes)
                {
                    if (!string.IsNullOrEmpty(current))
                    {
                        parts.Add(current);
                        current = "";
                    }
                }
                else
                {
                    current += c;
                }
            }
            
            if (!string.IsNullOrEmpty(current))
            {
                parts.Add(current);
            }
            
            return parts.ToArray();
        }
        
        public void AddOutput(string text)
        {
            var timestamp = showTimestamps ? $"[{DateTime.Now:HH:mm:ss}] " : "";
            var line = timestamp + text;
            
            _outputLines.Add(line);
            
            // Limit output lines
            while (_outputLines.Count > maxOutputLines)
            {
                _outputLines.RemoveAt(0);
            }
            
            // Update UI
            if (outputText != null)
            {
                outputText.text = string.Join("\n", _outputLines);
                
                // Scroll to bottom
                if (scrollRect != null)
                {
                    Canvas.ForceUpdateCanvases();
                    scrollRect.verticalNormalizedPosition = 0f;
                }
            }
            
            // Log to Unity console if enabled
            if (logToUnityConsole)
            {
                Debug.Log($"[DebugConsole] {text}");
            }
        }
        
        public void ClearOutput()
        {
            _outputLines.Clear();
            if (outputText != null)
            {
                outputText.text = "";
            }
        }
        
        public void RegisterCommand(DebugCommand command)
        {
            if (command == null || string.IsNullOrEmpty(command.Name)) return;
            
            var name = command.Name.ToLower();
            _commands[name] = command;
            
            // Register aliases
            if (command.Aliases != null)
            {
                foreach (var alias in command.Aliases)
                {
                    if (!string.IsNullOrEmpty(alias))
                    {
                        _aliases[alias.ToLower()] = name;
                    }
                }
            }
        }
        
        public void UnregisterCommand(string name)
        {
            if (string.IsNullOrEmpty(name)) return;
            
            name = name.ToLower();
            _commands.Remove(name);
            
            // Remove aliases
            var aliasesToRemove = _aliases.Where(kvp => kvp.Value == name).Select(kvp => kvp.Key).ToList();
            foreach (var alias in aliasesToRemove)
            {
                _aliases.Remove(alias);
            }
        }
        
        public IEnumerable<DebugCommand> GetCommands()
        {
            return _commands.Values;
        }
        
        private void RegisterDefaultCommands()
        {
            // Help command
            RegisterCommand(new DebugCommand("help", "Show available commands", new[] { "?" }, args =>
            {
                if (args.Length > 0)
                {
                    // Show help for specific command
                    var commandName = args[0].ToLower();
                    if (_commands.ContainsKey(commandName))
                    {
                        var cmd = _commands[commandName];
                        AddOutput($"{cmd.Name}: {cmd.Description}");
                        if (!string.IsNullOrEmpty(cmd.Usage))
                        {
                            AddOutput($"Usage: {cmd.Usage}");
                        }
                    }
                    else
                    {
                        AddOutput($"Unknown command: {commandName}");
                    }
                }
                else
                {
                    // Show all commands
                    AddOutput("Available commands:");
                    foreach (var cmd in _commands.Values.OrderBy(c => c.Name))
                    {
                        var aliases = cmd.Aliases != null && cmd.Aliases.Length > 0 
                            ? $" ({string.Join(", ", cmd.Aliases)})" 
                            : "";
                        AddOutput($"  {cmd.Name}{aliases} - {cmd.Description}");
                    }
                }
            }));
            
            // Clear command
            RegisterCommand(new DebugCommand("clear", "Clear console output", new[] { "cls" }, args =>
            {
                ClearOutput();
            }));
            
            // Echo command
            RegisterCommand(new DebugCommand("echo", "Echo text to console", null, args =>
            {
                AddOutput(string.Join(" ", args));
            }));
            
            // Quit command
            RegisterCommand(new DebugCommand("quit", "Close console", new[] { "exit" }, args =>
            {
                SetConsoleVisible(false);
            }));
        }
        
        private void RegisterSystemCommands()
        {
            // Find and register commands from other systems
            var assemblies = AppDomain.CurrentDomain.GetAssemblies();
            
            foreach (var assembly in assemblies)
            {
                try
                {
                    var types = assembly.GetTypes()
                        .Where(t => t.IsClass && !t.IsAbstract);
                    
                    foreach (var type in types)
                    {
                        var methods = type.GetMethods(BindingFlags.Static | BindingFlags.Public)
                            .Where(m => m.GetCustomAttribute<ConsoleCommandAttribute>() != null);
                        
                        foreach (var method in methods)
                        {
                            var attr = method.GetCustomAttribute<ConsoleCommandAttribute>();
                            RegisterMethodAsCommand(method, attr);
                        }
                    }
                }
                catch (Exception ex)
                {
                    Debug.LogWarning($"[DebugConsole] Error scanning assembly {assembly.FullName}: {ex.Message}");
                }
            }
        }
        
        private void RegisterMethodAsCommand(MethodInfo method, ConsoleCommandAttribute attr)
        {
            var command = new DebugCommand(attr.Name, attr.Description, attr.Aliases, args =>
            {
                try
                {
                    var parameters = method.GetParameters();
                    var convertedArgs = new object[parameters.Length];
                    
                    for (int i = 0; i < parameters.Length; i++)
                    {
                        if (i < args.Length)
                        {
                            convertedArgs[i] = Convert.ChangeType(args[i], parameters[i].ParameterType);
                        }
                        else if (parameters[i].HasDefaultValue)
                        {
                            convertedArgs[i] = parameters[i].DefaultValue;
                        }
                        else
                        {
                            AddOutput($"Missing required parameter: {parameters[i].Name}");
                            return;
                        }
                    }
                    
                    var result = method.Invoke(null, convertedArgs);
                    if (result != null)
                    {
                        AddOutput(result.ToString());
                    }
                }
                catch (Exception ex)
                {
                    AddOutput($"Error executing command {attr.Name}: {ex.Message}");
                }
            });
            
            command.Usage = attr.Usage;
            RegisterCommand(command);
        }
        
        public bool IsConsoleOpen => _isConsoleOpen;
    }
    
    /// <summary>
    /// Debug command data structure
    /// </summary>
    public class DebugCommand
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public string[] Aliases { get; set; }
        public string Usage { get; set; }
        public Action<string[]> Execute { get; set; }
        
        public DebugCommand(string name, string description, string[] aliases, Action<string[]> execute)
        {
            Name = name;
            Description = description;
            Aliases = aliases;
            Execute = execute;
        }
    }
    
    /// <summary>
    /// Attribute for marking static methods as console commands
    /// </summary>
    [AttributeUsage(AttributeTargets.Method)]
    public class ConsoleCommandAttribute : Attribute
    {
        public string Name { get; }
        public string Description { get; }
        public string[] Aliases { get; set; }
        public string Usage { get; set; }
        
        public ConsoleCommandAttribute(string name, string description)
        {
            Name = name;
            Description = description;
        }
    }
} 
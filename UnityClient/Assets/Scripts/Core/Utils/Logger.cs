using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using UnityEngine;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

namespace Core.Utils
{
    /// <summary>
    /// Log levels enum
    /// </summary>
    public enum LogLevel
    {
        DEBUG,
        INFO,
        WARNING,
        ERROR,
        CRITICAL
    }

    /// <summary>
    /// Log entry class
    /// </summary>
    public class LogEntry
    {
        public LogLevel Level { get; set; }
        public string Message { get; set; }
        public string Timestamp { get; set; }
        public Dictionary<string, object> Context { get; set; }
        public Exception Error { get; set; }
    }

    /// <summary>
    /// Logger configuration
    /// </summary>
    [Serializable]
    public class LoggerConfig
    {
        public LogLevel MinLevel = LogLevel.INFO;
        public bool EnableConsole = true;
        public bool EnableTimestamp = true;
        public bool EnableFileOutput = false;
        public string LogFilePath = "Logs/app.log";
        public bool StripDebugInBuild = true;
        public int MaxLogFileSize = 5242880; // 5MB
        public int MaxLogFiles = 5;
    }

    /// <summary>
    /// Log handler interface
    /// </summary>
    public interface ILogHandler
    {
        void Handle(LogEntry entry);
    }

    /// <summary>
    /// Unity Debug Console log handler
    /// </summary>
    public class UnityConsoleLogHandler : ILogHandler
    {
        public void Handle(LogEntry entry)
        {
            var timestamp = entry.Timestamp != null ? $"[{entry.Timestamp}] " : "";
            var context = entry.Context != null ? $" {JsonUtility.ToJson(new Dictionary<string, object>(entry.Context))}" : "";
            var message = $"{timestamp}[{entry.Level}] {entry.Message}{context}";

            switch (entry.Level)
            {
                case LogLevel.DEBUG:
                    UnityEngine.Debug.Log(message);
                    break;
                case LogLevel.INFO:
                    UnityEngine.Debug.Log(message);
                    break;
                case LogLevel.WARNING:
                    UnityEngine.Debug.LogWarning(message);
                    break;
                case LogLevel.ERROR:
                case LogLevel.CRITICAL:
                    if (entry.Error != null)
                    {
                        UnityEngine.Debug.LogException(entry.Error);
                    }
                    else
                    {
                        UnityEngine.Debug.LogError(message);
                    }
                    break;
            }
        }
    }

    /// <summary>
    /// File log handler
    /// </summary>
    public class FileLogHandler : ILogHandler
    {
        private string _filePath;
        private int _maxFileSize;
        private int _maxLogFiles;
        private object _fileLock = new object();

        public FileLogHandler(string filePath, int maxFileSize = 5242880, int maxLogFiles = 5)
        {
            _filePath = filePath;
            _maxFileSize = maxFileSize;
            _maxLogFiles = maxLogFiles;

            // Create directory if it doesn't exist
            var directory = Path.GetDirectoryName(filePath);
            if (!Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            // Create file if it doesn't exist
            if (!File.Exists(_filePath))
            {
                File.WriteAllText(_filePath, "");
            }
        }

        public void Handle(LogEntry entry)
        {
            var timestamp = entry.Timestamp != null ? $"[{entry.Timestamp}] " : "";
            var level = entry.Level.ToString();
            var context = entry.Context != null ? $" {JsonUtility.ToJson(new Dictionary<string, object>(entry.Context))}" : "";
            var message = $"{timestamp}[{level}] {entry.Message}{context}";

            if (entry.Error != null)
            {
                message += $"\n{entry.Error}\n{entry.Error.StackTrace}";
            }

            lock (_fileLock)
            {
                // Check file size and rotate if necessary
                var fileInfo = new FileInfo(_filePath);
                if (fileInfo.Exists && fileInfo.Length > _maxFileSize)
                {
                    RotateLogFiles();
                }

                // Append to file
                File.AppendAllText(_filePath, message + "\n");
            }
        }

        private void RotateLogFiles()
        {
            // Delete oldest log file if max reached
            var oldestLog = _filePath + "." + _maxLogFiles;
            if (File.Exists(oldestLog))
            {
                File.Delete(oldestLog);
            }

            // Shift log files
            for (int i = _maxLogFiles - 1; i > 0; i--)
            {
                var source = _filePath + "." + i;
                var target = _filePath + "." + (i + 1);
                if (File.Exists(source))
                {
                    File.Move(source, target);
                }
            }

            // Move current to .1
            if (File.Exists(_filePath))
            {
                File.Move(_filePath, _filePath + ".1");
            }

            // Create new log file
            File.WriteAllText(_filePath, "");
        }
    }

    /// <summary>
    /// Logger class
    /// </summary>
    public class Logger
    {
        private static Logger _instance;
        private LoggerConfig _config;
        private List<ILogHandler> _handlers;
        private string _prefix;
        private Dictionary<string, object> _metadata;
        private Queue<LogEntry> _backgroundQueue;
        private bool _processingQueue;

        /// <summary>
        /// Get logger instance (singleton)
        /// </summary>
        public static Logger Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = new Logger();
                }
                return _instance;
            }
        }

        private Logger()
        {
            _config = new LoggerConfig();
            _handlers = new List<ILogHandler>();
            _prefix = "";
            _metadata = new Dictionary<string, object>();
            _backgroundQueue = new Queue<LogEntry>();

            if (_config.EnableConsole)
            {
                _handlers.Add(new UnityConsoleLogHandler());
            }

            if (_config.EnableFileOutput)
            {
                _handlers.Add(new FileLogHandler(_config.LogFilePath, _config.MaxLogFileSize, _config.MaxLogFiles));
            }
        }

        /// <summary>
        /// Configure the logger
        /// </summary>
        public void Configure(LoggerConfig config)
        {
            _config = config;
            _handlers.Clear();

            if (_config.EnableConsole)
            {
                _handlers.Add(new UnityConsoleLogHandler());
            }

            if (_config.EnableFileOutput)
            {
                _handlers.Add(new FileLogHandler(_config.LogFilePath, _config.MaxLogFileSize, _config.MaxLogFiles));
            }
        }

        /// <summary>
        /// Add a log handler
        /// </summary>
        public void AddHandler(ILogHandler handler)
        {
            _handlers.Add(handler);
        }

        /// <summary>
        /// Remove a log handler
        /// </summary>
        public void RemoveHandler(ILogHandler handler)
        {
            _handlers.Remove(handler);
        }

        /// <summary>
        /// Create a child logger with a prefix
        /// </summary>
        public Logger CreateChild(string prefix, Dictionary<string, object> metadata = null)
        {
            var childLogger = new Logger();
            childLogger._prefix = _prefix != "" ? $"{_prefix}:{prefix}" : prefix;
            childLogger._metadata = new Dictionary<string, object>(_metadata);
            
            if (metadata != null)
            {
                foreach (var kvp in metadata)
                {
                    childLogger._metadata[kvp.Key] = kvp.Value;
                }
            }
            
            childLogger._config = _config;
            childLogger._handlers = _handlers;
            
            return childLogger;
        }

        /// <summary>
        /// Create a log entry
        /// </summary>
        private LogEntry CreateEntry(LogLevel level, string message, Dictionary<string, object> context = null, Exception error = null)
        {
            return new LogEntry
            {
                Level = level,
                Message = message,
                Timestamp = _config.EnableTimestamp ? DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ") : null,
                Context = context,
                Error = error
            };
        }

        /// <summary>
        /// Log a message
        /// </summary>
        private void Log(LogLevel level, string message, Dictionary<string, object> context = null, Exception error = null)
        {
            // Skip logging if level is below minimum
            if (level < _config.MinLevel)
            {
                return;
            }

            // Skip debug logs in build if configured
            if (_config.StripDebugInBuild && level == LogLevel.DEBUG && !UnityEngine.Debug.isDebugBuild)
            {
                return;
            }

            // Add prefix to message if set
            var prefixedMessage = _prefix != "" ? $"[{_prefix}] {message}" : message;
            
            // Merge context with metadata
            Dictionary<string, object> mergedContext = null;
            if (_metadata.Count > 0 || context != null)
            {
                mergedContext = new Dictionary<string, object>();
                
                if (_metadata.Count > 0)
                {
                    foreach (var kvp in _metadata)
                    {
                        mergedContext[kvp.Key] = kvp.Value;
                    }
                }
                
                if (context != null)
                {
                    foreach (var kvp in context)
                    {
                        mergedContext[kvp.Key] = kvp.Value;
                    }
                }
            }

            var entry = CreateEntry(level, prefixedMessage, mergedContext, error);
            
            // Process log handlers
            foreach (var handler in _handlers)
            {
                try
                {
                    handler.Handle(entry);
                }
                catch (Exception e)
                {
                    UnityEngine.Debug.LogException(e);
                }
            }
        }

        /// <summary>
        /// Log a message asynchronously
        /// </summary>
        private void LogAsync(LogLevel level, string message, Dictionary<string, object> context = null, Exception error = null)
        {
            // Skip logging if level is below minimum
            if (level < _config.MinLevel)
            {
                return;
            }

            // Skip debug logs in build if configured
            if (_config.StripDebugInBuild && level == LogLevel.DEBUG && !UnityEngine.Debug.isDebugBuild)
            {
                return;
            }

            // Add prefix to message if set
            var prefixedMessage = _prefix != "" ? $"[{_prefix}] {message}" : message;
            
            // Merge context with metadata
            Dictionary<string, object> mergedContext = null;
            if (_metadata.Count > 0 || context != null)
            {
                mergedContext = new Dictionary<string, object>();
                
                if (_metadata.Count > 0)
                {
                    foreach (var kvp in _metadata)
                    {
                        mergedContext[kvp.Key] = kvp.Value;
                    }
                }
                
                if (context != null)
                {
                    foreach (var kvp in context)
                    {
                        mergedContext[kvp.Key] = kvp.Value;
                    }
                }
            }

            var entry = CreateEntry(level, prefixedMessage, mergedContext, error);
            
            // Queue the log entry for background processing
            lock (_backgroundQueue)
            {
                _backgroundQueue.Enqueue(entry);
            }
            
            // Start processing queue if not already running
            if (!_processingQueue)
            {
                _processingQueue = true;
                Task.Run(ProcessLogQueue);
            }
        }

        /// <summary>
        /// Process log queue in background
        /// </summary>
        private async Task ProcessLogQueue()
        {
            while (true)
            {
                LogEntry entry = null;
                
                lock (_backgroundQueue)
                {
                    if (_backgroundQueue.Count > 0)
                    {
                        entry = _backgroundQueue.Dequeue();
                    }
                    else
                    {
                        _processingQueue = false;
                        break;
                    }
                }
                
                if (entry != null)
                {
                    // Process log handlers
                    foreach (var handler in _handlers)
                    {
                        try
                        {
                            handler.Handle(entry);
                        }
                        catch (Exception e)
                        {
                            UnityEngine.Debug.LogException(e);
                        }
                    }
                }
                
                // Small delay to prevent overwhelming the CPU
                await Task.Delay(1);
            }
        }

        /// <summary>
        /// Log a debug message
        /// </summary>
        [Conditional("UNITY_EDITOR")]
        public void Debug(string message, Dictionary<string, object> context = null)
        {
            Log(LogLevel.DEBUG, message, context);
        }

        /// <summary>
        /// Log a debug message (with caller info)
        /// </summary>
        [Conditional("UNITY_EDITOR")]
        public void Debug(string message, 
            [CallerMemberName] string memberName = "", 
            [CallerFilePath] string sourceFilePath = "", 
            [CallerLineNumber] int sourceLineNumber = 0)
        {
            var context = new Dictionary<string, object>
            {
                { "memberName", memberName },
                { "filePath", Path.GetFileName(sourceFilePath) },
                { "lineNumber", sourceLineNumber }
            };
            
            Log(LogLevel.DEBUG, message, context);
        }

        /// <summary>
        /// Log an info message
        /// </summary>
        public void Info(string message, Dictionary<string, object> context = null)
        {
            Log(LogLevel.INFO, message, context);
        }

        /// <summary>
        /// Log a warning message
        /// </summary>
        public void Warn(string message, Dictionary<string, object> context = null)
        {
            Log(LogLevel.WARNING, message, context);
        }

        /// <summary>
        /// Log an error message
        /// </summary>
        public void Error(string message, Exception error = null, Dictionary<string, object> context = null)
        {
            Log(LogLevel.ERROR, message, context, error);
        }

        /// <summary>
        /// Log a critical message
        /// </summary>
        public void Critical(string message, Exception error = null, Dictionary<string, object> context = null)
        {
            Log(LogLevel.CRITICAL, message, context, error);
        }

        /// <summary>
        /// Log a debug message asynchronously
        /// </summary>
        [Conditional("UNITY_EDITOR")]
        public void DebugAsync(string message, Dictionary<string, object> context = null)
        {
            LogAsync(LogLevel.DEBUG, message, context);
        }

        /// <summary>
        /// Log an info message asynchronously
        /// </summary>
        public void InfoAsync(string message, Dictionary<string, object> context = null)
        {
            LogAsync(LogLevel.INFO, message, context);
        }

        /// <summary>
        /// Log a warning message asynchronously
        /// </summary>
        public void WarnAsync(string message, Dictionary<string, object> context = null)
        {
            LogAsync(LogLevel.WARNING, message, context);
        }

        /// <summary>
        /// Log an error message asynchronously
        /// </summary>
        public void ErrorAsync(string message, Exception error = null, Dictionary<string, object> context = null)
        {
            LogAsync(LogLevel.ERROR, message, context, error);
        }

        /// <summary>
        /// Log a critical message asynchronously
        /// </summary>
        public void CriticalAsync(string message, Exception error = null, Dictionary<string, object> context = null)
        {
            LogAsync(LogLevel.CRITICAL, message, context, error);
        }
    }
} 
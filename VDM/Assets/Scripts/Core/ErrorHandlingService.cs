using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Core
{
    /// <summary>
    /// Centralized error handling and logging service for UI and quest scripts.
    /// </summary>
    public class ErrorHandlingService : MonoBehaviour
    {
        private static ErrorHandlingService _instance;
        public static ErrorHandlingService Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("ErrorHandlingService");
                    _instance = go.AddComponent<ErrorHandlingService>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        public event Action<ErrorContext> OnErrorLogged;
        private readonly List<ErrorContext> errorLog = new List<ErrorContext>();

        /// <summary>
        /// Log an exception with context and user-friendly message.
        /// </summary>
        public void LogException(Exception ex, string userMessage = null, string context = null, string systemState = null)
        {
            var error = new ErrorContext
            {
                ExceptionType = ex.GetType().Name,
                ExceptionMessage = ex.Message,
                StackTrace = ex.StackTrace,
                UserMessage = userMessage ?? "An unexpected error occurred.",
                Context = context,
                SystemState = systemState,
                Timestamp = DateTime.UtcNow,
                SessionId = SystemInfo.deviceUniqueIdentifier
            };
            errorLog.Add(error);
            Debug.LogError($"[ErrorHandlingService] {error}");
            OnErrorLogged?.Invoke(error);
        }

        /// <summary>
        /// Log a user-facing error without an exception.
        /// </summary>
        public void LogUserError(string userMessage, string context = null, string systemState = null)
        {
            var error = new ErrorContext
            {
                ExceptionType = null,
                ExceptionMessage = null,
                StackTrace = null,
                UserMessage = userMessage,
                Context = context,
                SystemState = systemState,
                Timestamp = DateTime.UtcNow,
                SessionId = SystemInfo.deviceUniqueIdentifier
            };
            errorLog.Add(error);
            Debug.LogWarning($"[ErrorHandlingService] {error}");
            OnErrorLogged?.Invoke(error);
        }

        /// <summary>
        /// Get the error log for diagnostics.
        /// </summary>
        public IReadOnlyList<ErrorContext> GetErrorLog() => errorLog.AsReadOnly();
    }

    /// <summary>
    /// Contextual information for an error or exception.
    /// </summary>
    public class ErrorContext
    {
        public string ExceptionType;
        public string ExceptionMessage;
        public string StackTrace;
        public string UserMessage;
        public string Context;
        public string SystemState;
        public DateTime Timestamp;
        public string SessionId;

        public override string ToString()
        {
            return $"[{Timestamp:u}] Session: {SessionId} | Context: {Context} | UserMsg: {UserMessage} | Ex: {ExceptionType}: {ExceptionMessage}\n{StackTrace}";
        }
    }
} 
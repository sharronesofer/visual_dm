using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Dialogue
{
    /// <summary>
    /// Manages conversation context for dynamic GPT-driven dialogue.
    /// </summary>
    public class DialogueContextManager : MonoBehaviour
    {
        private static DialogueContextManager _instance;
        public static DialogueContextManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("DialogueContextManager");
                    _instance = go.AddComponent<DialogueContextManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        // Key: conversationId (e.g., NPC name or unique ID), Value: list of lines
        private readonly Dictionary<string, List<string>> _contexts = new();
        private const int MaxContextLines = 10; // Sliding window size

        public void AddLine(string conversationId, string line)
        {
            if (!_contexts.ContainsKey(conversationId))
                _contexts[conversationId] = new List<string>();
            _contexts[conversationId].Add(line);
            // Keep only the last N lines
            if (_contexts[conversationId].Count > MaxContextLines)
                _contexts[conversationId].RemoveAt(0);
        }

        public List<string> GetContext(string conversationId)
        {
            if (_contexts.TryGetValue(conversationId, out var context))
                return new List<string>(context);
            return new List<string>();
        }

        public void ClearContext(string conversationId)
        {
            if (_contexts.ContainsKey(conversationId))
                _contexts[conversationId].Clear();
        }
    }
} 
using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Core;

namespace VisualDM.Input
{
    public enum InputType
    {
        Press,
        Hold,
        Combination
    }

    public struct InputEvent
    {
        public KeyCode Key;
        public InputType Type;
        public float Timestamp;

        public InputEvent(KeyCode key, InputType type, float timestamp)
        {
            Key = key;
            Type = type;
            Timestamp = timestamp;
        }
    }

    public class InputBuffer
    {
        private InputEvent[] buffer;
        private int head;
        private int tail;
        private int capacity;
        private float bufferWindowMs;
        private readonly float minWindow = 15f;
        private readonly float maxWindow = 500f;
        private Dictionary<KeyCode, float> lastInputTimestamps = new Dictionary<KeyCode, float>();
        private float debounceWindowMs = 50f;

        public float BufferWindowMs
        {
            get => bufferWindowMs;
            set => bufferWindowMs = Mathf.Clamp(value, minWindow, maxWindow);
        }

        public int Count { get; private set; }

        public InputBuffer(int maxEvents = 32, float bufferWindowMs = 150f)
        {
            capacity = Mathf.Max(4, maxEvents);
            buffer = new InputEvent[capacity];
            head = 0;
            tail = 0;
            Count = 0;
            BufferWindowMs = bufferWindowMs;
        }

        public void AddInput(KeyCode key, InputType type)
        {
            float now = Time.unscaledTime * 1000f;
            var inputEvent = new InputEvent(key, type, now);
            buffer[tail] = inputEvent;
            tail = (tail + 1) % capacity;
            if (Count < capacity)
                Count++;
            else
                head = (head + 1) % capacity; // Overwrite oldest
            PruneOldEvents(now);
        }

        public List<InputEvent> GetBufferedInputs()
        {
            float now = Time.unscaledTime * 1000f;
            PruneOldEvents(now);
            var result = new List<InputEvent>();
            for (int i = 0, idx = head; i < Count; i++, idx = (idx + 1) % capacity)
            {
                if (now - buffer[idx].Timestamp <= bufferWindowMs)
                    result.Add(buffer[idx]);
            }
            return result;
        }

        public void ClearBuffer()
        {
            head = 0;
            tail = 0;
            Count = 0;
        }

        private void PruneOldEvents(float now)
        {
            while (Count > 0 && now - buffer[head].Timestamp > bufferWindowMs)
            {
                head = (head + 1) % capacity;
                Count--;
            }
        }

        public static InputType ClassifyInput(KeyCode key, bool isHeld, bool isCombo)
        {
            if (isCombo) return InputType.Combination;
            if (isHeld) return InputType.Hold;
            return InputType.Press;
        }

        public bool ValidateInput(InputEvent input, GameState currentState, HashSet<KeyCode> conflictingKeys = null)
        {
            // Debounce: filter rapid repeats
            if (!DebounceInput(input.Key, input.Timestamp))
                return false;

            // Conflicting input check
            if (conflictingKeys != null && conflictingKeys.Contains(input.Key))
                return false;

            // Contextual validation
            if (currentState == GameState.Cutscene || currentState == GameState.SceneTransition || currentState == GameState.Menu)
                return false;

            // Add more context checks as needed
            return true;
        }

        private bool DebounceInput(KeyCode key, float timestamp)
        {
            if (lastInputTimestamps.TryGetValue(key, out float lastTime))
            {
                if (timestamp - lastTime < debounceWindowMs)
                    return false;
            }
            lastInputTimestamps[key] = timestamp;
            return true;
        }

        public void ClearBufferOnState(GameState state)
        {
            if (state == GameState.Cutscene || state == GameState.SceneTransition || state == GameState.Menu)
                ClearBuffer();
        }
    }
} 
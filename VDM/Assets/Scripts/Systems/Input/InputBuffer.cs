using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.Input
{
    /// <summary>
    /// Types of input events (press, hold, combination).
    /// </summary>
    public enum InputType
    {
        Press,
        Hold,
        Combination
    }

    /// <summary>
    /// Represents a buffered input event.
    /// </summary>
    public struct InputEvent
    {
        /// <summary>
        /// The key code of the input.
        /// </summary>
        public KeyCode Key;
        /// <summary>
        /// The type of input (press, hold, combination).
        /// </summary>
        public InputType Type;
        /// <summary>
        /// The timestamp when the input was received.
        /// </summary>
        public float Timestamp;

        public InputEvent(KeyCode key, InputType type, float timestamp)
        {
            Key = key;
            Type = type;
            Timestamp = timestamp;
        }
    }

    /// <summary>
    /// Circular buffer for input events, with configurable window and validation.
    /// </summary>
    public class InputBuffer : MonoBehaviour
    {
        /// <summary>
        /// Buffer window duration in milliseconds (15-500ms).
        /// </summary>
        [Tooltip("Buffer window duration in milliseconds (15-500ms)")]
        [Range(15, 500)]
        public int BufferWindowDuration = 150;

        private InputEvent[] buffer;
        private int capacity;
        private int head;
        private int tail;
        private int count;

        /// <summary>
        /// Gets the buffer capacity.
        /// </summary>
        public int Capacity => capacity;
        /// <summary>
        /// Gets the current number of buffered inputs.
        /// </summary>
        public int Count => count;

        public InputBuffer(int bufferCapacity = 32)
        {
            capacity = bufferCapacity;
            buffer = new InputEvent[capacity];
            head = 0;
            tail = 0;
            count = 0;
        }

        /// <summary>
        /// Adds an input event to the buffer.
        /// </summary>
        public void AddInput(InputEvent input)
        {
            float now = Time.time;
            PruneExpired(now);
            buffer[tail] = input;
            tail = (tail + 1) % capacity;
            if (count == capacity)
            {
                head = (head + 1) % capacity; // Overwrite oldest
            }
            else
            {
                count++;
            }
        }

        /// <summary>
        /// Returns all valid buffered inputs within the current time window.
        /// </summary>
        public List<InputEvent> GetBufferedInputs()
        {
            float now = Time.time;
            PruneExpired(now);
            List<InputEvent> validInputs = new List<InputEvent>();
            for (int i = 0, idx = head; i < count; i++, idx = (idx + 1) % capacity)
            {
                validInputs.Add(buffer[idx]);
            }
            return validInputs;
        }

        /// <summary>
        /// Clears the input buffer.
        /// </summary>
        public void ClearBuffer()
        {
            head = 0;
            tail = 0;
            count = 0;
        }

        private void PruneExpired(float now)
        {
            float window = BufferWindowDuration / 1000f;
            while (count > 0)
            {
                float age = now - buffer[head].Timestamp;
                if (age > window)
                {
                    head = (head + 1) % capacity;
                    count--;
                }
                else
                {
                    break;
                }
            }
        }

        /// <summary>
        /// Classifies an input as press, hold, or combination.
        /// </summary>
        public static InputType ClassifyInput(KeyCode key, bool isHeld, bool isCombo)
        {
            if (isCombo) return InputType.Combination;
            if (isHeld) return InputType.Hold;
            return InputType.Press;
        }

        // Minimal stubs for integration
        public enum GameState
        {
            Normal,
            SceneTransition,
            Cutscene,
            Paused
        }

        public class GameContext
        {
            public GameState State { get; set; } = GameState.Normal;
            // Extend as needed for contextual validation
        }

        private Dictionary<KeyCode, float> lastInputTimestamps = new Dictionary<KeyCode, float>();
        private const float DebounceWindow = 0.05f; // 50ms debounce

        /// <summary>
        /// Validates an input event against debounce, conflict, and context rules.
        /// </summary>
        public bool ValidateInput(InputEvent input, GameContext context)
        {
            // Debounce: prevent rapid repeats
            if (DebounceInput(input)) return false;

            // Example: conflicting inputs (e.g., left/right)
            if (IsConflictingInput(input)) return false;

            // Contextual validation
            if (!IsInputAllowedInState(input, context.State)) return false;

            return true;
        }

        private bool DebounceInput(InputEvent input)
        {
            float now = Time.time;
            if (lastInputTimestamps.TryGetValue(input.Key, out float lastTime))
            {
                if (now - lastTime < DebounceWindow)
                {
                    return true; // Debounced
                }
            }
            lastInputTimestamps[input.Key] = now;
            return false;
        }

        private bool IsConflictingInput(InputEvent input)
        {
            // Example: left/right, up/down (expand as needed)
            if (input.Key == KeyCode.LeftArrow && lastInputTimestamps.ContainsKey(KeyCode.RightArrow))
                return true;
            if (input.Key == KeyCode.RightArrow && lastInputTimestamps.ContainsKey(KeyCode.LeftArrow))
                return true;
            if (input.Key == KeyCode.UpArrow && lastInputTimestamps.ContainsKey(KeyCode.DownArrow))
                return true;
            if (input.Key == KeyCode.DownArrow && lastInputTimestamps.ContainsKey(KeyCode.UpArrow))
                return true;
            return false;
        }

        private bool IsInputAllowedInState(InputEvent input, GameState state)
        {
            switch (state)
            {
                case GameState.SceneTransition:
                case GameState.Cutscene:
                case GameState.Paused:
                    return false;
                default:
                    return true;
            }
        }

        /// <summary>
        /// Clears the buffer on specific game state changes.
        /// </summary>
        public void ClearBufferOnState(GameState state)
        {
            if (state == GameState.SceneTransition || state == GameState.Cutscene || state == GameState.Paused)
            {
                ClearBuffer();
            }
        }
    }
} 
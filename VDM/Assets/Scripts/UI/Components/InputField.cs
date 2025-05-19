using UnityEngine;
using TMPro;
using VisualDM.UI.DesignTokens;
using System;

namespace VisualDM.UI
{
    /// <summary>
    /// Runtime-generated, accessible input field component for Unity 2D UI.
    /// Supports states, placeholder, and keyboard input. No scene references.
    /// </summary>
    public class CoreField : MonoBehaviour
    {
        public enum State { Default, Focused, Error, Disabled }

        public State FieldState = State.Default;
        public string Placeholder = "Enter text...";
        public string Value = "";
        public bool IsFocused = false;
        public bool IsPassword = false;
        public Action<string> OnValueChanged;
        public Action OnSubmit;
        /// <summary>
        /// Optional validator function for input. If set, input is validated on change.
        /// </summary>
        public Func<string, bool> Validator;
        /// <summary>
        /// Returns true if the current Value passes validation.
        /// </summary>
        public bool IsValid { get; private set; } = true;

        private SpriteRenderer _background;
        private TextMeshPro _text;
        private TextMeshPro _placeholder;
        private float _width = 240f;
        private float _height = 40f;

        void Awake()
        {
            // Background
            _background = gameObject.AddComponent<SpriteRenderer>();
            _background.drawMode = SpriteDrawMode.Sliced;
            _background.size = new Vector2(_width, _height);
            // Text
            var textObj = new GameObject("Text");
            textObj.transform.SetParent(transform);
            _text = textObj.AddComponent<TextMeshPro>();
            _text.fontSize = Typography.Body;
            _text.font = Typography.SansFont;
            _text.alignment = TextAlignmentOptions.Left;
            _text.rectTransform.sizeDelta = new Vector2(_width - Spacing.Medium, _height);
            _text.rectTransform.localPosition = new Vector3(Spacing.Small, 0, 0);
            _text.enableWordWrapping = false;
            _text.text = Value;
            // Placeholder
            var placeholderObj = new GameObject("Placeholder");
            placeholderObj.transform.SetParent(transform);
            _placeholder = placeholderObj.AddComponent<TextMeshPro>();
            _placeholder.fontSize = Typography.Body;
            _placeholder.font = Typography.SansFont;
            _placeholder.alignment = TextAlignmentOptions.Left;
            _placeholder.rectTransform.sizeDelta = new Vector2(_width - Spacing.Medium, _height);
            _placeholder.rectTransform.localPosition = new Vector3(Spacing.Small, 0, 0);
            _placeholder.enableWordWrapping = false;
            _placeholder.text = Placeholder;
            _placeholder.color = Colors.Neutral400;
            // Collider for focus
            var collider = gameObject.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(_width, _height);
            collider.isTrigger = true;
            // Initial style
            ApplyStyle();
        }

        void OnMouseDown() { if (FieldState != State.Disabled) Focus(); }

        void Update()
        {
            if (IsFocused && FieldState != State.Disabled)
            {
                foreach (char c in Core.inputString)
                {
                    if (c == '\b') // Backspace
                    {
                        if (Value.Length > 0) Value = Value.Substring(0, Value.Length - 1);
                    }
                    else if (c == '\n' || c == '\r') // Enter
                    {
                        OnSubmit?.Invoke();
                        IsFocused = false;
                        SetState(State.Default);
                    }
                    else if (!char.IsControl(c))
                    {
                        Value += c;
                    }
                }
                // Validate input if validator is set
                if (Validator != null)
                {
                    IsValid = Validator(Value);
                    SetState(IsValid ? (IsFocused ? State.Focused : State.Default) : State.Error);
                }
                else
                {
                    IsValid = true;
                }
                if (IsValid)
                {
                    HandleCore(Value);
                }
                _text.text = IsPassword ? new string('*', Value.Length) : Value;
                _placeholder.gameObject.SetActive(string.IsNullOrEmpty(Value));
            }
        }

        public void Focus()
        {
            IsFocused = true;
            SetState(State.Focused);
        }

        public void Blur()
        {
            IsFocused = false;
            SetState(State.Default);
        }

        public void SetState(State state)
        {
            FieldState = state;
            ApplyStyle();
        }

        public void SetValue(string value)
        {
            Value = value;
            _text.text = IsPassword ? new string('*', value.Length) : value;
            _placeholder.gameObject.SetActive(string.IsNullOrEmpty(value));
        }

        public void SetPlaceholder(string text)
        {
            Placeholder = text;
            _placeholder.text = text;
        }

        private void ApplyStyle()
        {
            Color bg, border, text;
            switch (FieldState)
            {
                case State.Default:
                    bg = Colors.Neutral100;
                    border = Borders.Default;
                    text = Colors.Neutral900;
                    break;
                case State.Focused:
                    bg = Colors.Neutral100;
                    border = Borders.Focus;
                    text = Colors.Neutral900;
                    break;
                case State.Error:
                    bg = Colors.Neutral100;
                    border = Borders.Error;
                    text = Borders.Error;
                    break;
                case State.Disabled:
                    bg = Colors.Neutral200;
                    border = Colors.Neutral300;
                    text = Colors.Neutral400;
                    break;
                default:
                    bg = Colors.Neutral100;
                    border = Borders.Default;
                    text = Colors.Neutral900;
                    break;
            }
            _background.color = bg;
            _text.color = text;
            // TODO: Draw border using additional SpriteRenderer or outline
            // TODO: Add focus ring if IsFocused
        }

        private void HandleCore(string value)
        {
            try
            {
                OnValueChanged?.Invoke(value);
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Core field value change failed.", "CoreField.HandleCore");
            }
        }
    }
} 
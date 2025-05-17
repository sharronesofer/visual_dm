using UnityEngine;
using TMPro;
using VisualDM.UI.DesignTokens;
using System;

namespace VisualDM.UI.Components
{
    /// <summary>
    /// Runtime-generated, accessible button component for Unity 2D UI.
    /// Supports variants, states, and keyboard navigation. No scene references.
    /// </summary>
    public class Button : MonoBehaviour
    {
        public enum Variant { Primary, Secondary, Danger }
        public enum State { Default, Hover, Active, Disabled, Loading }

        public Variant ButtonVariant = Variant.Primary;
        public State ButtonState = State.Default;
        public string Label = "Button";
        public Action OnClick;
        public bool IsFocused = false;

        private SpriteRenderer _background;
        private TextMeshPro _label;
        private float _width = 160f;
        private float _height = 40f;

        void Awake()
        {
            // Background
            _background = gameObject.AddComponent<SpriteRenderer>();
            _background.drawMode = SpriteDrawMode.Sliced;
            _background.size = new Vector2(_width, _height);
            // Label
            var labelObj = new GameObject("Label");
            labelObj.transform.SetParent(transform);
            _label = labelObj.AddComponent<TextMeshPro>();
            _label.text = Label;
            _label.fontSize = Typography.Body;
            _label.font = Typography.SansFont;
            _label.alignment = TextAlignmentOptions.Center;
            _label.rectTransform.sizeDelta = new Vector2(_width, _height);
            _label.rectTransform.localPosition = Vector3.zero;
            _label.enableWordWrapping = false;
            _label.color = Colors.Neutral100;
            // Accessibility: Add collider for mouse/keyboard
            var collider = gameObject.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(_width, _height);
            collider.isTrigger = true;
            // Initial style
            ApplyStyle();
        }

        void OnMouseEnter() { if (ButtonState != State.Disabled) SetState(State.Hover); }
        void OnMouseExit() { if (ButtonState != State.Disabled) SetState(State.Default); }
        void OnMouseDown() { if (ButtonState != State.Disabled) SetState(State.Active); }
        void OnMouseUp() { if (ButtonState != State.Disabled) { SetState(State.Hover); TriggerClick(); } }

        void Update()
        {
            // Keyboard navigation (Enter/Space triggers click if focused)
            if (IsFocused && ButtonState != State.Disabled && (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space)))
            {
                SetState(State.Active);
                TriggerClick();
            }
            // Visual focus indicator
            if (IsFocused && ButtonState != State.Disabled)
                _background.color = Colors.Focus;
            else
                ApplyStyle();
        }

        public void SetState(State state)
        {
            ButtonState = state;
            ApplyStyle();
        }

        public void SetVariant(Variant variant)
        {
            ButtonVariant = variant;
            ApplyStyle();
        }

        public void SetLabel(string text)
        {
            Label = text;
            if (_label != null) _label.text = text;
        }

        public void TriggerClick()
        {
            try
            {
                OnClick?.Invoke();
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Button click failed.", "Button.TriggerClick");
            }
        }

        private void ApplyStyle()
        {
            // Color by variant/state
            Color bg, border, text;
            switch (ButtonVariant)
            {
                case Variant.Primary:
                    bg = ButtonState switch
                    {
                        State.Default => Colors.PrimaryDefault,
                        State.Hover => Colors.PrimaryHover,
                        State.Active => Colors.PrimaryActive,
                        State.Disabled => Colors.Neutral300,
                        State.Loading => Colors.PrimaryDefault,
                        _ => Colors.PrimaryDefault
                    };
                    border = Colors.PrimaryActive;
                    text = Colors.Neutral100;
                    break;
                case Variant.Secondary:
                    bg = ButtonState switch
                    {
                        State.Default => Colors.SecondaryDefault,
                        State.Hover => Colors.SecondaryHover,
                        State.Active => Colors.SecondaryActive,
                        State.Disabled => Colors.Neutral300,
                        State.Loading => Colors.SecondaryDefault,
                        _ => Colors.SecondaryDefault
                    };
                    border = Colors.SecondaryActive;
                    text = Colors.Neutral900;
                    break;
                case Variant.Danger:
                    bg = ButtonState switch
                    {
                        State.Default => Borders.Error,
                        State.Hover => new Color(0.9f, 0.3f, 0.3f, 1f),
                        State.Active => new Color(0.7f, 0.1f, 0.1f, 1f),
                        State.Disabled => Colors.Neutral300,
                        State.Loading => Borders.Error,
                        _ => Borders.Error
                    };
                    border = Borders.Error;
                    text = Colors.Neutral100;
                    break;
                default:
                    bg = Colors.PrimaryDefault;
                    border = Colors.PrimaryActive;
                    text = Colors.Neutral100;
                    break;
            }
            _background.color = bg;
            _label.color = text;
            // TODO: Draw border using additional SpriteRenderer or outline
            // TODO: Add loading spinner overlay if State.Loading
            // TODO: Add focus ring if IsFocused
        }
    }
} 
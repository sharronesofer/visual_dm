using UnityEngine;
using VisualDM.UI.DesignTokens;
using System;

namespace VisualDM.UI.Components
{
    /// <summary>
    /// Runtime-generated, accessible checkbox component for Unity 2D UI.
    /// Supports checked/unchecked states, keyboard/mouse input, and focus. No scene references.
    /// </summary>
    public class Checkbox : MonoBehaviour
    {
        public bool IsChecked = false;
        public bool IsFocused = false;
        public Action<bool> OnValueChanged;

        private SpriteRenderer _box;
        private Icon _checkmark;
        private float _size = 24f;

        void Awake()
        {
            // Box
            _box = gameObject.AddComponent<SpriteRenderer>();
            _box.size = new Vector2(_size, _size);
            // Checkmark
            var checkObj = new GameObject("Checkmark");
            checkObj.transform.SetParent(transform);
            _checkmark = checkObj.AddComponent<Icon>();
            _checkmark.SetIcon("checkmark"); // Assumes a checkmark sprite in Resources
            _checkmark.SetSize(_size * 0.7f);
            _checkmark.SetTint(Colors.PrimaryDefault);
            _checkmark.gameObject.SetActive(IsChecked);
            // Collider
            var collider = gameObject.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(_size, _size);
            collider.isTrigger = true;
            // Initial style
            ApplyStyle();
        }

        void OnMouseDown() { if (enabled) Toggle(); }

        void Update()
        {
            // Keyboard toggle (Space/Enter)
            if (IsFocused && (Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.Return)))
                Toggle();
            // Focus ring
            if (IsFocused)
                _box.color = Colors.Focus;
            else
                ApplyStyle();
        }

        public void Toggle()
        {
            IsChecked = !IsChecked;
            _checkmark.gameObject.SetActive(IsChecked);
            OnValueChanged?.Invoke(IsChecked);
            ApplyStyle();
        }

        public void SetChecked(bool value)
        {
            IsChecked = value;
            _checkmark.gameObject.SetActive(value);
            ApplyStyle();
        }

        private void ApplyStyle()
        {
            _box.color = IsChecked ? Colors.PrimaryDefault : Colors.Neutral300;
            _checkmark.SetTint(IsChecked ? Colors.Neutral100 : Colors.Neutral300);
        }
    }
} 
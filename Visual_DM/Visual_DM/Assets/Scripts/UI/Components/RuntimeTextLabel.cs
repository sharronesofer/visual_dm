using UnityEngine;
using TMPro;
using VisualDM.UI.DesignTokens;

namespace VisualDM.UI.Components
{
    /// <summary>
    /// Runtime-generated text label for Unity 2D UI, using TextMeshPro.
    /// Supports design tokens for typography and color.
    /// </summary>
    [RequireComponent(typeof(TextMeshPro))]
    public class RuntimeTextLabel : MonoBehaviour
    {
        public enum TextType { HeadingLarge, HeadingMedium, HeadingSmall, Body, Caption, Code }

        public string Text
        {
            get => _textMesh.text;
            set => _textMesh.text = value;
        }
        public TextType Type = TextType.Body;
        public Color? OverrideColor = null;
        public TextAlignmentOptions Alignment = TextAlignmentOptions.Left;

        private TextMeshPro _textMesh;

        void Awake()
        {
            _textMesh = GetComponent<TextMeshPro>();
            ApplyStyle();
        }

        void OnValidate()
        {
            if (_textMesh == null) _textMesh = GetComponent<TextMeshPro>();
            ApplyStyle();
        }

        public void SetText(string text) { Text = text; }
        public void SetType(TextType type) { Type = type; ApplyStyle(); }
        public void SetColor(Color color) { OverrideColor = color; ApplyStyle(); }
        public void SetAlignment(TextAlignmentOptions alignment) { Alignment = alignment; ApplyStyle(); }

        private void ApplyStyle()
        {
            if (_textMesh == null) return;
            switch (Type)
            {
                case TextType.HeadingLarge:
                    _textMesh.fontSize = Typography.HeadingLarge;
                    _textMesh.font = Typography.SansFont;
                    _textMesh.fontWeight = Typography.HeadingWeight;
                    break;
                case TextType.HeadingMedium:
                    _textMesh.fontSize = Typography.HeadingMedium;
                    _textMesh.font = Typography.SansFont;
                    _textMesh.fontWeight = Typography.HeadingWeight;
                    break;
                case TextType.HeadingSmall:
                    _textMesh.fontSize = Typography.HeadingSmall;
                    _textMesh.font = Typography.SansFont;
                    _textMesh.fontWeight = Typography.HeadingWeight;
                    break;
                case TextType.Body:
                    _textMesh.fontSize = Typography.Body;
                    _textMesh.font = Typography.SansFont;
                    _textMesh.fontWeight = Typography.BodyWeight;
                    break;
                case TextType.Caption:
                    _textMesh.fontSize = Typography.Caption;
                    _textMesh.font = Typography.SansFont;
                    _textMesh.fontWeight = Typography.BodyWeight;
                    break;
                case TextType.Code:
                    _textMesh.fontSize = Typography.Code;
                    _textMesh.font = Typography.MonoFont;
                    _textMesh.fontWeight = Typography.CodeWeight;
                    break;
            }
            _textMesh.alignment = Alignment;
            _textMesh.color = OverrideColor ?? Colors.Neutral900;
        }
    }
} 
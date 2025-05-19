using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace VisualDM.Timeline.Visualization
{
    public class TooltipPanel : MonoBehaviour
    {
        public CanvasGroup CanvasGroup { get; private set; }
        public RectTransform RectTransform { get; private set; }
        public TextMeshProUGUI Text { get; private set; }

        private void Awake()
        {
            CanvasGroup = gameObject.AddComponent<CanvasGroup>();
            RectTransform = gameObject.AddComponent<RectTransform>();
            var bg = new GameObject("BG").AddComponent<Image>();
            bg.transform.SetParent(transform, false);
            bg.color = new Color(0, 0, 0, 0.85f);
            bg.rectTransform.anchorMin = Vector2.zero;
            bg.rectTransform.anchorMax = Vector2.one;
            bg.rectTransform.offsetMin = Vector2.zero;
            bg.rectTransform.offsetMax = Vector2.zero;
            Text = new GameObject("Text").AddComponent<TextMeshProUGUI>();
            Text.transform.SetParent(transform, false);
            Text.fontSize = 18;
            Text.color = Color.white;
            Text.alignment = TextAlignmentOptions.TopLeft;
            Text.rectTransform.anchorMin = new Vector2(0, 0);
            Text.rectTransform.anchorMax = new Vector2(1, 1);
            Text.rectTransform.offsetMin = new Vector2(8, 8);
            Text.rectTransform.offsetMax = new Vector2(-8, -8);
            CanvasGroup.alpha = 0f;
        }

        public void SetText(string content)
        {
            Text.text = content;
            CanvasGroup.alpha = 1f;
        }

        public void SetPosition(Vector2 screenPos)
        {
            RectTransform.anchoredPosition = screenPos;
        }

        private void OnDisable()
        {
            CanvasGroup.alpha = 0f;
        }
    }
} 
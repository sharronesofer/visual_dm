using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace VisualDM.Systems.Input
{
    public class QueueVisualizer : MonoBehaviour
    {
        public ActionQueue ActionQueue;
        public bool ShowDebugPanel = true;
        public bool ShowPlayerIndicators = true;
        public Canvas UICanvas;
        private Text debugText;
        private List<GameObject> playerIndicators = new List<GameObject>();

        void Start()
        {
            if (ShowDebugPanel)
            {
                GameObject debugObj = new GameObject("QueueDebugText");
                debugObj.transform.SetParent(UICanvas.transform);
                debugText = debugObj.AddComponent<Text>();
                debugText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
                debugText.fontSize = 14;
                debugText.color = Color.yellow;
                debugText.alignment = TextAnchor.UpperLeft;
                debugText.rectTransform.anchorMin = new Vector2(0, 1);
                debugText.rectTransform.anchorMax = new Vector2(0, 1);
                debugText.rectTransform.pivot = new Vector2(0, 1);
                debugText.rectTransform.anchoredPosition = new Vector2(10, -10);
            }
        }

        void Update()
        {
            if (ShowDebugPanel && debugText != null && ActionQueue != null)
            {
                var snapshot = ActionQueue.GetQueueSnapshot();
                debugText.text = "Action Queue:\n";
                foreach (var action in snapshot)
                {
                    debugText.text += $"{action.Input.Key} [{action.Priority}] ({action.Input.Type})\n";
                }
            }
            if (ShowPlayerIndicators && ActionQueue != null)
            {
                UpdatePlayerIndicators(ActionQueue.GetQueueSnapshot());
            }
        }

        private void UpdatePlayerIndicators(List<QueuedAction> actions)
        {
            // Remove old indicators
            foreach (var go in playerIndicators)
            {
                Destroy(go);
            }
            playerIndicators.Clear();
            // Create new indicators (simple icons, runtime only)
            float startX = 50f;
            float y = 50f;
            float spacing = 40f;
            foreach (var action in actions)
            {
                GameObject icon = new GameObject($"ActionIcon_{action.Input.Key}");
                icon.transform.SetParent(UICanvas.transform);
                Image img = icon.AddComponent<Image>();
                img.color = GetColorForPriority(action.Priority);
                // Use a simple built-in sprite (circle)
                img.sprite = Resources.GetBuiltinResource<Sprite>("UI/Skin/Knob.psd");
                RectTransform rt = icon.GetComponent<RectTransform>();
                rt.sizeDelta = new Vector2(24, 24);
                rt.anchoredPosition = new Vector2(startX, y);
                startX += spacing;
                playerIndicators.Add(icon);
            }
        }

        private Color GetColorForPriority(ActionPriority priority)
        {
            switch (priority)
            {
                case ActionPriority.Critical: return Color.red;
                case ActionPriority.High: return Color.magenta;
                case ActionPriority.Normal: return Color.green;
                case ActionPriority.Low: return Color.gray;
                default: return Color.white;
            }
        }
    }
} 
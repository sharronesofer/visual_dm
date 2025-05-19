using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using VisualDM.AI;

namespace VisualDM.UI
{
    /// <summary>
    /// Displays all rumors known to the player, including content, believability, source, spread, and mutation history.
    /// </summary>
    public class RumorJournalUI : MonoBehaviour
    {
        private GameObject panel;
        private RectTransform panelRect;
        private VerticalLayoutGroup layoutGroup;
        private List<GameObject> rumorEntries = new();
        private const float PanelWidth = 600f;
        private const float PanelHeight = 800f;

        public void Initialize()
        {
            panel = new GameObject("RumorJournalPanel");
            panelRect = panel.AddComponent<RectTransform>();
            panelRect.sizeDelta = new Vector2(PanelWidth, PanelHeight);
            panel.transform.SetParent(UIManager.Instance.transform, false);
            panel.AddComponent<Image>().color = new Color(0.1f, 0.1f, 0.2f, 0.95f);
            layoutGroup = panel.AddComponent<VerticalLayoutGroup>();
            layoutGroup.childControlHeight = true;
            layoutGroup.childControlWidth = true;
            layoutGroup.childForceExpandHeight = false;
            layoutGroup.childForceExpandWidth = true;
            panel.SetActive(false);
        }

        public void Show()
        {
            if (panel == null) Initialize();
            panel.SetActive(true);
            Refresh();
        }

        public void Hide()
        {
            if (panel != null) panel.SetActive(false);
        }

        public void Refresh()
        {
            foreach (var entry in rumorEntries)
                Destroy(entry);
            rumorEntries.Clear();
            var rumors = RumorManager.Instance.GetAllRumors();
            foreach (var kvp in rumors)
            {
                var rumor = kvp.Value;
                var entry = CreateRumorEntry(rumor);
                entry.transform.SetParent(panel.transform, false);
                rumorEntries.Add(entry);
            }
        }

        private GameObject CreateRumorEntry(Rumor rumor)
        {
            var entry = new GameObject("RumorEntry");
            var rect = entry.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(PanelWidth - 40f, 100f);
            var bg = entry.AddComponent<Image>();
            bg.color = new Color(0.2f, 0.2f, 0.3f, 0.85f);
            var textObj = new GameObject("RumorText");
            var text = textObj.AddComponent<Text>();
            textObj.transform.SetParent(entry.transform, false);
            text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            text.color = Color.white;
            text.alignment = TextAnchor.UpperLeft;
            text.rectTransform.anchorMin = Vector2.zero;
            text.rectTransform.anchorMax = Vector2.one;
            text.rectTransform.offsetMin = new Vector2(10, 10);
            text.rectTransform.offsetMax = new Vector2(-10, -10);
            // Compose rumor details
            string details = $"Rumor: {rumor.CoreContent}\n" +
                             $"Source: {rumor.Origin?.OriginNpcId ?? "Unknown"}\n" +
                             $"Believability: {rumor.TruthValue:P0}\n" +
                             $"Importance: {rumor.Importance:F2}\n";
            if (rumor.TransformationHistory != null && rumor.TransformationHistory.Count > 0)
            {
                details += "Mutations:";
                foreach (var t in rumor.TransformationHistory)
                {
                    details += $"\n- {t.Timestamp.ToShortDateString()} by {t.NpcId}: {t.TransformationType} (Distortion: {t.DistortionLevel:F2})";
                }
            }
            text.text = details;
            return entry;
        }
    }
} 
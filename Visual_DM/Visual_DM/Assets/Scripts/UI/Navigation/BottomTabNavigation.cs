using UnityEngine;
using TMPro;
using System.Collections.Generic;

namespace VisualDM.UI.Navigation
{
    /// <summary>
    /// Bottom tab navigation for mobile, supports notification badges and runtime tab creation.
    /// </summary>
    public class BottomTabNavigation : MonoBehaviour
    {
        [System.Serializable]
        public class TabData
        {
            public string Label;
            public int BadgeCount;
        }

        public List<TabData> Tabs = new List<TabData> {
            new TabData { Label = "Home", BadgeCount = 0 },
            new TabData { Label = "Quests", BadgeCount = 2 },
            new TabData { Label = "Inventory", BadgeCount = 0 },
            new TabData { Label = "Profile", BadgeCount = 1 }
        };

        private List<GameObject> tabButtons = new List<GameObject>();
        private float tabWidth = 120f;
        private float tabHeight = 64f;
        private float startY = -320f;

        void Start()
        {
            CreateTabs();
        }

        private void CreateTabs()
        {
            float totalWidth = Tabs.Count * tabWidth;
            float startX = -totalWidth / 2 + tabWidth / 2;
            for (int i = 0; i < Tabs.Count; i++)
            {
                var tab = Tabs[i];
                var go = new GameObject($"Tab_{tab.Label}");
                go.transform.SetParent(transform);
                go.transform.localPosition = new Vector3(startX + i * tabWidth, startY, 0);
                var label = go.AddComponent<TextMeshPro>();
                label.text = tab.Label;
                label.fontSize = UI.DesignTokens.Typography.Body;
                label.font = UI.DesignTokens.Typography.SansFont;
                label.color = UI.DesignTokens.Colors.Neutral900;
                label.alignment = TextAlignmentOptions.Center;
                // Badge
                if (tab.BadgeCount > 0)
                {
                    var badge = new GameObject("Badge");
                    badge.transform.SetParent(go.transform);
                    badge.transform.localPosition = new Vector3(40, 20, 0);
                    var badgeLabel = badge.AddComponent<TextMeshPro>();
                    badgeLabel.text = tab.BadgeCount.ToString();
                    badgeLabel.fontSize = 18;
                    badgeLabel.color = UI.DesignTokens.Colors.Error500;
                    badgeLabel.alignment = TextAlignmentOptions.Center;
                }
                // Click handler
                var btn = go.AddComponent<BottomTabButton>();
                btn.TabIndex = i;
                btn.OnTabSelected = OnTabSelected;
                tabButtons.Add(go);
            }
        }

        private void OnTabSelected(int index)
        {
            var tab = Tabs[index];
            NavigationService.Instance.NavigateTo(tab.Label);
            // Visual feedback for selected tab
            for (int i = 0; i < tabButtons.Count; i++)
            {
                var label = tabButtons[i].GetComponent<TextMeshPro>();
                label.color = (i == index) ? UI.DesignTokens.Colors.Primary500 : UI.DesignTokens.Colors.Neutral900;
            }
        }
    }

    public class BottomTabButton : MonoBehaviour
    {
        public int TabIndex;
        public System.Action<int> OnTabSelected;
        private void OnMouseDown() { OnTabSelected?.Invoke(TabIndex); }
        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Tab) && TabIndex == 0)
                OnTabSelected?.Invoke(TabIndex);
        }
    }
} 
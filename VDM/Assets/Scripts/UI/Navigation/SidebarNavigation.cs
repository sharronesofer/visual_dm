using UnityEngine;
using TMPro;
using System.Collections.Generic;

namespace VisualDM.UI
{
    /// <summary>
    /// Sidebar navigation for desktop, collapsible, expandable, keyboard shortcuts, responsive.
    /// </summary>
    public class SidebarNavigation : MonoBehaviour
    {
        [System.Serializable]
        public class SectionData
        {
            public string Label;
            public List<string> Items;
        }

        public List<SectionData> Sections = new List<SectionData> {
            new SectionData { Label = "Main", Items = new List<string> { "Home", "Quests", "Inventory" } },
            new SectionData { Label = "Profile", Items = new List<string> { "User", "Settings" } }
        };

        private List<GameObject> sectionObjects = new List<GameObject>();
        private float sectionWidth = 220f;
        private float sectionHeight = 48f;
        private bool isCollapsed = false;

        void Start()
        {
            CreateSections();
        }

        private void CreateSections()
        {
            float y = 200f;
            foreach (var section in Sections)
            {
                var sectionObj = new GameObject($"Section_{section.Label}");
                sectionObj.transform.SetParent(transform);
                sectionObj.transform.localPosition = new Vector3(0, y, 0);
                var label = sectionObj.AddComponent<TextMeshPro>();
                label.text = section.Label;
                label.fontSize = UI.DesignTokens.Typography.Body;
                label.font = UI.DesignTokens.Typography.SansFont;
                label.color = UI.DesignTokens.Colors.Neutral700;
                label.alignment = TextAlignmentOptions.Left;
                y -= sectionHeight;
                foreach (var item in section.Items)
                {
                    var itemObj = new GameObject($"Item_{item}");
                    itemObj.transform.SetParent(sectionObj.transform);
                    itemObj.transform.localPosition = new Vector3(24, y, 0);
                    var itemLabel = itemObj.AddComponent<TextMeshPro>();
                    itemLabel.text = item;
                    itemLabel.fontSize = UI.DesignTokens.Typography.Body;
                    itemLabel.font = UI.DesignTokens.Typography.SansFont;
                    itemLabel.color = UI.DesignTokens.Colors.Neutral900;
                    itemLabel.alignment = TextAlignmentOptions.Left;
                    var btn = itemObj.AddComponent<SidebarNavButton>();
                    btn.Section = section.Label;
                    btn.Item = item;
                    btn.OnNavSelected = OnNavSelected;
                    y -= sectionHeight;
                }
                sectionObjects.Add(sectionObj);
            }
        }

        private void OnNavSelected(string section, string item)
        {
            NavigationService.Instance.NavigateTo(item);
        }

        void Update()
        {
            // Keyboard shortcut: collapse/expand sidebar
            if (Core.GetKeyDown(KeyCode.LeftArrow))
                SetCollapsed(true);
            if (Core.GetKeyDown(KeyCode.RightArrow))
                SetCollapsed(false);
        }

        private void SetCollapsed(bool collapsed)
        {
            isCollapsed = collapsed;
            foreach (var sectionObj in sectionObjects)
            {
                sectionObj.SetActive(!collapsed);
            }
        }
    }

    public class SidebarNavButton : MonoBehaviour
    {
        public string Section;
        public string Item;
        public System.Action<string, string> OnNavSelected;
        private void OnMouseDown() { OnNavSelected?.Invoke(Section, Item); }
        private void Update()
        {
            if (Core.GetKeyDown(KeyCode.Return))
                OnNavSelected?.Invoke(Section, Item);
        }
    }
} 
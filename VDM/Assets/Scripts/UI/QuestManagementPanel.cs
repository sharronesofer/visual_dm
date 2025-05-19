using UnityEngine;
using System;

namespace VisualDM.UI
{
    public class QuestManagementPanel : PanelBase
    {
        private GameObject titleObj;
        private GameObject listPlaceholder;
        private GameObject addButton;
        private float width = 600f;
        private float height = 400f;
        private Color bgColor = new Color(0.18f, 0.18f, 0.22f, 0.98f);

        public override void Initialize(params object[] args)
        {
            try
            {
                // Background
                var sr = gameObject.AddComponent<SpriteRenderer>();
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
                sr.sortingOrder = 110;

                // Title
                titleObj = new GameObject("Title");
                titleObj.transform.SetParent(transform);
                titleObj.transform.localPosition = new Vector3(0, height/2 - 30, 0);
                var titleLabel = titleObj.AddComponent<TMPro.TextMeshPro>();
                titleLabel.text = "Quest Management";
                titleLabel.fontSize = UI.DesignTokens.Typography.HeadingMedium;
                titleLabel.font = UI.DesignTokens.Typography.SansFont;
                titleLabel.color = UI.DesignTokens.Colors.Neutral900;
                titleLabel.alignment = TMPro.TextAlignmentOptions.Center;

                // Quest list rendering
                listPlaceholder = new GameObject("QuestList");
                listPlaceholder.transform.SetParent(transform);
                listPlaceholder.transform.localPosition = new Vector3(0, 0, 0);
                var listLabel = listPlaceholder.AddComponent<TMPro.TextMeshPro>();
                listLabel.text = GenerateQuestListText();
                listLabel.fontSize = UI.DesignTokens.Typography.Body;
                listLabel.font = UI.DesignTokens.Typography.SansFont;
                listLabel.color = UI.DesignTokens.Colors.Neutral400;
                listLabel.alignment = TMPro.TextAlignmentOptions.TopLeft;

                // Add button
                addButton = new GameObject("AddQuestButton");
                addButton.transform.SetParent(transform);
                addButton.transform.localPosition = new Vector3(width/2 - 60, -height/2 + 30, 0);
                var btn = addButton.AddComponent<UI.Components.Button>();
                btn.Label = "Add Quest";
                btn.OnClick = () => {
                    try
                    {
                        // TODO: Implement add quest logic
                    }
                    catch (Exception ex)
                    {
                        VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to add quest.", "QuestManagementPanel.AddQuestButton.OnClick");
                    }
                };

                // Map indicator placeholder for cross-region objectives
                var mapIndicator = new GameObject("MapIndicatorPlaceholder");
                mapIndicator.transform.SetParent(transform);
                mapIndicator.transform.localPosition = new Vector3(0, -height/2 + 60, 0);
                var mapLabel = mapIndicator.AddComponent<TMPro.TextMeshPro>();
                mapLabel.text = "[Map indicators for cross-region quest objectives will appear here]";
                mapLabel.fontSize = UI.DesignTokens.Typography.Caption;
                mapLabel.font = UI.DesignTokens.Typography.SansFont;
                mapLabel.color = UI.DesignTokens.Colors.Neutral300;
                mapLabel.alignment = TMPro.TextAlignmentOptions.Center;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to initialize Quest Management Panel.", "QuestManagementPanel.Initialize");
                // Optionally show a user-friendly error UI here
            }
        }

        private string GenerateQuestListText()
        {
            // Example: fetch quests from a manager and distinguish global/regional
            var globalArcs = GlobalArcManager.Instance.GetAllGlobalArcs();
            var text = "<b>Global Quests:</b>\n";
            foreach (var arc in globalArcs)
            {
                text += $"- {arc.Title} (Stage {arc.CurrentStageIndex + 1}/{arc.Stages.Count})\n";
                var regionals = GlobalArcManager.Instance.GetRegionalArcsForGlobal(arc.Id);
                foreach (var reg in regionals)
                {
                    text += $"    • Regional: {reg.RegionName} - {reg.Title} (Stage {reg.CurrentStageIndex + 1}/{reg.Stages.Count})\n";
                }
            }
            return text + "\n<b>Regional Quests:</b>\n[Other regional quests not linked to global arcs would be listed here]";
        }

        public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint)
        {
            switch (breakpoint)
            {
                case UIManager.Breakpoint.Mobile:
                    width = 320f; height = 220f;
                    break;
                case UIManager.Breakpoint.Tablet:
                    width = 420f; height = 300f;
                    break;
                case UIManager.Breakpoint.Desktop:
                    width = 600f; height = 400f;
                    break;
                case UIManager.Breakpoint.LargeDesktop:
                    width = 800f; height = 520f;
                    break;
            }
            var sr = GetComponent<SpriteRenderer>();
            if (sr != null)
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            if (titleObj != null) titleObj.transform.localPosition = new Vector3(0, height/2 - 30, 0);
            if (addButton != null) addButton.transform.localPosition = new Vector3(width/2 - 60, -height/2 + 30, 0);
        }
    }
} 
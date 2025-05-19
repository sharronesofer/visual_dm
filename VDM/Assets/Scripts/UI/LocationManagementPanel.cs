using UnityEngine;
using System;

namespace VisualDM.UI
{
    public class LocationManagementPanel : PanelBase
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
                titleLabel.text = "Location Management";
                titleLabel.fontSize = UI.DesignTokens.Typography.HeadingMedium;
                titleLabel.font = UI.DesignTokens.Typography.SansFont;
                titleLabel.color = UI.DesignTokens.Colors.Neutral900;
                titleLabel.alignment = TMPro.TextAlignmentOptions.Center;

                // Location list placeholder (to be replaced with actual list rendering)
                listPlaceholder = new GameObject("LocationListPlaceholder");
                listPlaceholder.transform.SetParent(transform);
                listPlaceholder.transform.localPosition = new Vector3(0, 0, 0);
                var listLabel = listPlaceholder.AddComponent<TMPro.TextMeshPro>();
                listLabel.text = "[Location List Here]";
                listLabel.fontSize = UI.DesignTokens.Typography.Body;
                listLabel.font = UI.DesignTokens.Typography.SansFont;
                listLabel.color = UI.DesignTokens.Colors.Neutral400;
                listLabel.alignment = TMPro.TextAlignmentOptions.Center;

                // Add button
                addButton = new GameObject("AddLocationButton");
                addButton.transform.SetParent(transform);
                addButton.transform.localPosition = new Vector3(width/2 - 60, -height/2 + 30, 0);
                var btn = addButton.AddComponent<UI.Components.Button>();
                btn.Label = "Add Location";
                btn.OnClick = () => { /* TODO: Implement add location logic */ };
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to initialize Location Management Panel.", "LocationManagementPanel.Initialize");
                // Optionally show a user-friendly error UI here
            }
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
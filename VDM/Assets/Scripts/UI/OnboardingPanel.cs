using UnityEngine;
using System;

namespace VisualDM.UI
{
    public class OnboardingPanel : PanelBase
    {
        private GameObject[] stepPanels;
        private GameObject progressIndicator;
        private GameObject skipButton;
        private GameObject continueButton;
        private int currentStep = 0;
        private int totalSteps = 3; // Example: 3 steps
        private float width = 500f;
        private float height = 320f;
        private Color bgColor = new Color(0.16f, 0.16f, 0.22f, 0.98f);

        public override void Initialize(params object[] args)
        {
            try
            {
                // Background
                var sr = gameObject.AddComponent<SpriteRenderer>();
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
                sr.sortingOrder = 120;

                // Progress indicator
                progressIndicator = new GameObject("ProgressIndicator");
                progressIndicator.transform.SetParent(transform);
                progressIndicator.transform.localPosition = new Vector3(0, 120, 0);
                var progressLabel = progressIndicator.AddComponent<TMPro.TextMeshPro>();
                progressLabel.text = $"Step {currentStep + 1} of {totalSteps}";
                progressLabel.fontSize = UI.DesignTokens.Typography.Body;
                progressLabel.font = UI.DesignTokens.Typography.SansFont;
                progressLabel.color = UI.DesignTokens.Colors.Neutral900;
                progressLabel.alignment = TMPro.TextAlignmentOptions.Center;

                // Step panels
                stepPanels = new GameObject[totalSteps];
                for (int i = 0; i < totalSteps; i++)
                {
                    var stepPanel = new GameObject($"StepPanel_{i}");
                    stepPanel.transform.SetParent(transform);
                    stepPanel.transform.localPosition = new Vector3(0, 30, 0);
                    var stepLabel = stepPanel.AddComponent<TMPro.TextMeshPro>();
                    stepLabel.text = $"Onboarding Step {i + 1}";
                    stepLabel.fontSize = UI.DesignTokens.Typography.Body;
                    stepLabel.font = UI.DesignTokens.Typography.SansFont;
                    stepLabel.color = UI.DesignTokens.Colors.Neutral700;
                    stepLabel.alignment = TMPro.TextAlignmentOptions.Center;
                    stepPanel.SetActive(i == 0);
                    stepPanels[i] = stepPanel;
                }

                // Skip button
                skipButton = new GameObject("SkipButton");
                skipButton.transform.SetParent(transform);
                skipButton.transform.localPosition = new Vector3(-100, -100, 0);
                var skipBtn = skipButton.AddComponent<UI.Components.Button>();
                skipBtn.Label = "Skip";
                skipBtn.OnClick = () => { /* TODO: Implement skip logic */ };

                // Continue button
                continueButton = new GameObject("ContinueButton");
                continueButton.transform.SetParent(transform);
                continueButton.transform.localPosition = new Vector3(100, -100, 0);
                var continueBtn = continueButton.AddComponent<UI.Components.Button>();
                continueBtn.Label = "Continue";
                continueBtn.OnClick = () => { NextStep(); };
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to initialize Onboarding Panel.", "OnboardingPanel.Initialize");
            }
        }

        private void NextStep()
        {
            if (currentStep < totalSteps - 1)
            {
                stepPanels[currentStep].SetActive(false);
                currentStep++;
                stepPanels[currentStep].SetActive(true);
                var progressLabel = progressIndicator.GetComponent<TMPro.TextMeshPro>();
                progressLabel.text = $"Step {currentStep + 1} of {totalSteps}";
            }
            else
            {
                // TODO: Complete onboarding
            }
        }

        public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint)
        {
            switch (breakpoint)
            {
                case UIManager.Breakpoint.Mobile:
                    width = 320f; height = 180f;
                    break;
                case UIManager.Breakpoint.Tablet:
                    width = 400f; height = 240f;
                    break;
                case UIManager.Breakpoint.Desktop:
                    width = 500f; height = 320f;
                    break;
                case UIManager.Breakpoint.LargeDesktop:
                    width = 640f; height = 400f;
                    break;
            }
            var sr = GetComponent<SpriteRenderer>();
            if (sr != null)
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            if (progressIndicator != null) progressIndicator.transform.localPosition = new Vector3(0, height/3, 0);
            if (skipButton != null) skipButton.transform.localPosition = new Vector3(-width/4, -height/3, 0);
            if (continueButton != null) continueButton.transform.localPosition = new Vector3(width/4, -height/3, 0);
        }
    }
} 
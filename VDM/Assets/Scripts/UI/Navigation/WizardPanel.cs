using UnityEngine;
using TMPro;
using System.Collections.Generic;

namespace VisualDM.UI
{
    /// <summary>
    /// Manages multi-step wizard flows, progress, validation, and data persistence.
    /// </summary>
    public class WizardPanel : MonoBehaviour
    {
        private int currentStep = 0;
        private int totalSteps = 4;
        private List<GameObject> stepPanels = new List<GameObject>();
        private GameObject progressIndicator;
        private GameObject nextButton;
        private GameObject backButton;
        private GameObject summaryPanel;
        private Dictionary<int, Dictionary<string, string>> stepData = new Dictionary<int, Dictionary<string, string>>();
        private float width = 500f;
        private float height = 340f;
        private Color bgColor = new Color(0.16f, 0.16f, 0.22f, 0.98f);

        void Start()
        {
            Initialize();
        }

        public void Initialize()
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
            var progressLabel = progressIndicator.AddComponent<TextMeshPro>();
            progressLabel.text = $"Step {currentStep + 1} of {totalSteps}";
            progressLabel.fontSize = UI.DesignTokens.Typography.Body;
            progressLabel.font = UI.DesignTokens.Typography.SansFont;
            progressLabel.color = UI.DesignTokens.Colors.Neutral900;
            progressLabel.alignment = TextAlignmentOptions.Center;

            // Step panels
            for (int i = 0; i < totalSteps; i++)
            {
                var stepPanel = new GameObject($"StepPanel_{i}");
                stepPanel.transform.SetParent(transform);
                stepPanel.transform.localPosition = new Vector3(0, 30, 0);
                var stepLabel = stepPanel.AddComponent<TextMeshPro>();
                stepLabel.text = $"Form Step {i + 1}";
                stepLabel.fontSize = UI.DesignTokens.Typography.Body;
                stepLabel.font = UI.DesignTokens.Typography.SansFont;
                stepLabel.color = UI.DesignTokens.Colors.Neutral700;
                stepLabel.alignment = TextAlignmentOptions.Center;
                stepPanel.SetActive(i == 0);
                stepPanels.Add(stepPanel);
                stepData[i] = new Dictionary<string, string>();
            }

            // Navigation buttons
            backButton = new GameObject("BackButton");
            backButton.transform.SetParent(transform);
            backButton.transform.localPosition = new Vector3(-100, -120, 0);
            var backBtn = backButton.AddComponent<UI.Components.Button>();
            backBtn.Label = "Back";
            backBtn.OnClick = () => { PrevStep(); };
            backButton.SetActive(false);

            nextButton = new GameObject("NextButton");
            nextButton.transform.SetParent(transform);
            nextButton.transform.localPosition = new Vector3(100, -120, 0);
            var nextBtn = nextButton.AddComponent<UI.Components.Button>();
            nextBtn.Label = "Next";
            nextBtn.OnClick = () => { NextStep(); };

            // Summary panel (hidden until last step)
            summaryPanel = new GameObject("SummaryPanel");
            summaryPanel.transform.SetParent(transform);
            summaryPanel.transform.localPosition = new Vector3(0, 0, 0);
            var summaryLabel = summaryPanel.AddComponent<TextMeshPro>();
            summaryLabel.text = "Summary/Review";
            summaryLabel.fontSize = UI.DesignTokens.Typography.Body;
            summaryLabel.font = UI.DesignTokens.Typography.SansFont;
            summaryLabel.color = UI.DesignTokens.Colors.Neutral900;
            summaryLabel.alignment = TextAlignmentOptions.Center;
            summaryPanel.SetActive(false);
        }

        private void NextStep()
        {
            if (!ValidateStep(currentStep))
                return;
            stepPanels[currentStep].SetActive(false);
            currentStep++;
            if (currentStep < totalSteps)
            {
                stepPanels[currentStep].SetActive(true);
                backButton.SetActive(true);
                if (currentStep == totalSteps - 1)
                    nextButton.GetComponent<UI.Components.Button>().Label = "Review";
                progressIndicator.GetComponent<TextMeshPro>().text = $"Step {currentStep + 1} of {totalSteps}";
            }
            else
            {
                ShowSummary();
            }
        }

        private void PrevStep()
        {
            if (currentStep > 0)
            {
                stepPanels[currentStep].SetActive(false);
                currentStep--;
                stepPanels[currentStep].SetActive(true);
                nextButton.GetComponent<UI.Components.Button>().Label = "Next";
                progressIndicator.GetComponent<TextMeshPro>().text = $"Step {currentStep + 1} of {totalSteps}";
                if (currentStep == 0)
                    backButton.SetActive(false);
            }
        }

        private bool ValidateStep(int step)
        {
            // TODO: Implement real validation logic
            return true;
        }

        private void ShowSummary()
        {
            foreach (var panel in stepPanels)
                panel.SetActive(false);
            nextButton.SetActive(false);
            backButton.SetActive(false);
            summaryPanel.SetActive(true);
            // TODO: Populate summary with stepData
            // TODO: Analytics tracking stub
        }
    }
} 
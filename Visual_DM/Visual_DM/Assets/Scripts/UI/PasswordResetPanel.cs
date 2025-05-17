using UnityEngine;
using System;

namespace VisualDM.UI
{
    public class PasswordResetPanel : PanelBase
    {
        private GameObject emailField;
        private GameObject submitButton;
        private GameObject errorMsg;
        private float width = 400f;
        private float height = 220f;
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

                // Email label and field
                var emailLabelObj = new GameObject("EmailLabel");
                emailLabelObj.transform.SetParent(transform);
                emailLabelObj.transform.localPosition = new Vector3(0, 60, 0);
                var emailLabel = emailLabelObj.AddComponent<TMPro.TextMeshPro>();
                emailLabel.text = "Email";
                emailLabel.fontSize = UI.DesignTokens.Typography.Body;
                emailLabel.font = UI.DesignTokens.Typography.SansFont;
                emailLabel.color = UI.DesignTokens.Colors.Neutral900;
                emailLabel.alignment = TMPro.TextAlignmentOptions.Center;

                emailField = new GameObject("EmailField");
                emailField.transform.SetParent(transform);
                emailField.transform.localPosition = new Vector3(0, 30, 0);
                var emailInput = emailField.AddComponent<UI.Components.InputField>();
                emailInput.Placeholder = "Enter your email";
                emailInput.OnValueChanged = (val) => { };

                // Submit button
                submitButton = new GameObject("SubmitButton");
                submitButton.transform.SetParent(transform);
                submitButton.transform.localPosition = new Vector3(0, -30, 0);
                var btn = submitButton.AddComponent<UI.Components.Button>();
                btn.Label = "Reset Password";
                btn.OnClick = () => { /* TODO: Implement password reset logic */ };

                // Error message
                errorMsg = new GameObject("ErrorMsg");
                errorMsg.transform.SetParent(transform);
                errorMsg.transform.localPosition = new Vector3(0, -80, 0);
                var errorLabel = errorMsg.AddComponent<TMPro.TextMeshPro>();
                errorLabel.text = "";
                errorLabel.fontSize = UI.DesignTokens.Typography.Caption;
                errorLabel.font = UI.DesignTokens.Typography.SansFont;
                errorLabel.color = UI.DesignTokens.Colors.Neutral400;
                errorLabel.alignment = TMPro.TextAlignmentOptions.Center;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to initialize Password Reset Panel.", "PasswordResetPanel.Initialize");
            }
        }

        public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint)
        {
            switch (breakpoint)
            {
                case UIManager.Breakpoint.Mobile:
                    width = 260f; height = 140f;
                    break;
                case UIManager.Breakpoint.Tablet:
                    width = 320f; height = 180f;
                    break;
                case UIManager.Breakpoint.Desktop:
                    width = 400f; height = 220f;
                    break;
                case UIManager.Breakpoint.LargeDesktop:
                    width = 520f; height = 300f;
                    break;
            }
            var sr = GetComponent<SpriteRenderer>();
            if (sr != null)
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            if (emailField != null) emailField.transform.localPosition = new Vector3(0, height/4, 0);
            if (submitButton != null) submitButton.transform.localPosition = new Vector3(0, -height/8, 0);
            if (errorMsg != null) errorMsg.transform.localPosition = new Vector3(0, -height/3, 0);
        }
    }
} 
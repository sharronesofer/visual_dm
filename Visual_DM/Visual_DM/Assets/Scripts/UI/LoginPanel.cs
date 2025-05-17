using UnityEngine;
using System;

namespace VisualDM.UI
{
    public class LoginPanel : PanelBase
    {
        private GameObject usernameField;
        private GameObject passwordField;
        private GameObject loginButton;
        private GameObject errorMsg;
        private float width = 400f;
        private float height = 300f;
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

                // Username label and field
                var usernameLabelObj = new GameObject("UsernameLabel");
                usernameLabelObj.transform.SetParent(transform);
                usernameLabelObj.transform.localPosition = new Vector3(0, 90, 0);
                var usernameLabel = usernameLabelObj.AddComponent<TMPro.TextMeshPro>();
                usernameLabel.text = "Username";
                usernameLabel.fontSize = UI.DesignTokens.Typography.Body;
                usernameLabel.font = UI.DesignTokens.Typography.SansFont;
                usernameLabel.color = UI.DesignTokens.Colors.Neutral900;
                usernameLabel.alignment = TMPro.TextAlignmentOptions.Center;

                usernameField = new GameObject("UsernameField");
                usernameField.transform.SetParent(transform);
                usernameField.transform.localPosition = new Vector3(0, 60, 0);
                var usernameInput = usernameField.AddComponent<UI.Components.InputField>();
                usernameInput.Placeholder = "Enter username";
                usernameInput.OnValueChanged = (val) => { };

                // Password label and field
                var passwordLabelObj = new GameObject("PasswordLabel");
                passwordLabelObj.transform.SetParent(transform);
                passwordLabelObj.transform.localPosition = new Vector3(0, 40, 0);
                var passwordLabel = passwordLabelObj.AddComponent<TMPro.TextMeshPro>();
                passwordLabel.text = "Password";
                passwordLabel.fontSize = UI.DesignTokens.Typography.Body;
                passwordLabel.font = UI.DesignTokens.Typography.SansFont;
                passwordLabel.color = UI.DesignTokens.Colors.Neutral900;
                passwordLabel.alignment = TMPro.TextAlignmentOptions.Center;

                passwordField = new GameObject("PasswordField");
                passwordField.transform.SetParent(transform);
                passwordField.transform.localPosition = new Vector3(0, 10, 0);
                var passwordInput = passwordField.AddComponent<UI.Components.InputField>();
                passwordInput.Placeholder = "Enter password";
                passwordInput.IsPassword = true;
                passwordInput.OnValueChanged = (val) => { };

                // Login button
                loginButton = new GameObject("LoginButton");
                loginButton.transform.SetParent(transform);
                loginButton.transform.localPosition = new Vector3(0, -50, 0);
                var btn = loginButton.AddComponent<UI.Components.Button>();
                btn.Label = "Login";
                btn.OnClick = () => { /* TODO: Implement login logic */ };

                // Error message
                errorMsg = new GameObject("ErrorMsg");
                errorMsg.transform.SetParent(transform);
                errorMsg.transform.localPosition = new Vector3(0, -100, 0);
                var errorLabel = errorMsg.AddComponent<TMPro.TextMeshPro>();
                errorLabel.text = "";
                errorLabel.fontSize = UI.DesignTokens.Typography.Caption;
                errorLabel.font = UI.DesignTokens.Typography.SansFont;
                errorLabel.color = UI.DesignTokens.Colors.Neutral400;
                errorLabel.alignment = TMPro.TextAlignmentOptions.Center;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to initialize Login Panel.", "LoginPanel.Initialize");
                // Optionally show a user-friendly error UI here
            }
        }

        public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint)
        {
            switch (breakpoint)
            {
                case UIManager.Breakpoint.Mobile:
                    width = 260f; height = 180f;
                    break;
                case UIManager.Breakpoint.Tablet:
                    width = 320f; height = 220f;
                    break;
                case UIManager.Breakpoint.Desktop:
                    width = 400f; height = 300f;
                    break;
                case UIManager.Breakpoint.LargeDesktop:
                    width = 520f; height = 380f;
                    break;
            }
            var sr = GetComponent<SpriteRenderer>();
            if (sr != null)
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            if (usernameField != null) usernameField.transform.localPosition = new Vector3(0, height/5, 0);
            if (passwordField != null) passwordField.transform.localPosition = new Vector3(0, height/15, 0);
            if (loginButton != null) loginButton.transform.localPosition = new Vector3(0, -height/6, 0);
            if (errorMsg != null) errorMsg.transform.localPosition = new Vector3(0, -height/3, 0);
        }
    }
} 
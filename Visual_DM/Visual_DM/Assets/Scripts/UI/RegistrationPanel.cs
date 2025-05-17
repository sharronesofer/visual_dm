using UnityEngine;
using System;

namespace VisualDM.UI
{
    public class RegistrationPanel : PanelBase
    {
        private GameObject usernameField;
        private GameObject passwordField;
        private GameObject confirmPasswordField;
        private GameObject registerButton;
        private GameObject errorMsg;
        private float width = 400f;
        private float height = 360f;
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
                usernameLabelObj.transform.localPosition = new Vector3(0, 130, 0);
                var usernameLabel = usernameLabelObj.AddComponent<TMPro.TextMeshPro>();
                usernameLabel.text = "Username";
                usernameLabel.fontSize = UI.DesignTokens.Typography.Body;
                usernameLabel.font = UI.DesignTokens.Typography.SansFont;
                usernameLabel.color = UI.DesignTokens.Colors.Neutral900;
                usernameLabel.alignment = TMPro.TextAlignmentOptions.Center;

                usernameField = new GameObject("UsernameField");
                usernameField.transform.SetParent(transform);
                usernameField.transform.localPosition = new Vector3(0, 100, 0);
                var usernameInput = usernameField.AddComponent<UI.Components.InputField>();
                usernameInput.Placeholder = "Enter username";
                usernameInput.OnValueChanged = (val) => { };

                // Password label and field
                var passwordLabelObj = new GameObject("PasswordLabel");
                passwordLabelObj.transform.SetParent(transform);
                passwordLabelObj.transform.localPosition = new Vector3(0, 80, 0);
                var passwordLabel = passwordLabelObj.AddComponent<TMPro.TextMeshPro>();
                passwordLabel.text = "Password";
                passwordLabel.fontSize = UI.DesignTokens.Typography.Body;
                passwordLabel.font = UI.DesignTokens.Typography.SansFont;
                passwordLabel.color = UI.DesignTokens.Colors.Neutral900;
                passwordLabel.alignment = TMPro.TextAlignmentOptions.Center;

                passwordField = new GameObject("PasswordField");
                passwordField.transform.SetParent(transform);
                passwordField.transform.localPosition = new Vector3(0, 50, 0);
                var passwordInput = passwordField.AddComponent<UI.Components.InputField>();
                passwordInput.Placeholder = "Enter password";
                passwordInput.IsPassword = true;
                passwordInput.OnValueChanged = (val) => { };

                // Confirm password label and field
                var confirmLabelObj = new GameObject("ConfirmPasswordLabel");
                confirmLabelObj.transform.SetParent(transform);
                confirmLabelObj.transform.localPosition = new Vector3(0, 30, 0);
                var confirmLabel = confirmLabelObj.AddComponent<TMPro.TextMeshPro>();
                confirmLabel.text = "Confirm Password";
                confirmLabel.fontSize = UI.DesignTokens.Typography.Body;
                confirmLabel.font = UI.DesignTokens.Typography.SansFont;
                confirmLabel.color = UI.DesignTokens.Colors.Neutral900;
                confirmLabel.alignment = TMPro.TextAlignmentOptions.Center;

                confirmPasswordField = new GameObject("ConfirmPasswordField");
                confirmPasswordField.transform.SetParent(transform);
                confirmPasswordField.transform.localPosition = new Vector3(0, 0, 0);
                var confirmInput = confirmPasswordField.AddComponent<UI.Components.InputField>();
                confirmInput.Placeholder = "Re-enter password";
                confirmInput.IsPassword = true;
                confirmInput.OnValueChanged = (val) => { };

                // Register button
                registerButton = new GameObject("RegisterButton");
                registerButton.transform.SetParent(transform);
            // Background
            var sr = gameObject.AddComponent<SpriteRenderer>();
            sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            sr.sortingOrder = 120;

            // Username label and field
            var usernameLabelObj = new GameObject("UsernameLabel");
            usernameLabelObj.transform.SetParent(transform);
            usernameLabelObj.transform.localPosition = new Vector3(0, 130, 0);
            var usernameLabel = usernameLabelObj.AddComponent<TMPro.TextMeshPro>();
            usernameLabel.text = "Username";
            usernameLabel.fontSize = UI.DesignTokens.Typography.Body;
            usernameLabel.font = UI.DesignTokens.Typography.SansFont;
            usernameLabel.color = UI.DesignTokens.Colors.Neutral900;
            usernameLabel.alignment = TMPro.TextAlignmentOptions.Center;

            usernameField = new GameObject("UsernameField");
            usernameField.transform.SetParent(transform);
            usernameField.transform.localPosition = new Vector3(0, 100, 0);
            var usernameInput = usernameField.AddComponent<UI.Components.InputField>();
            usernameInput.Placeholder = "Enter username";
            usernameInput.OnValueChanged = (val) => { };

            // Password label and field
            var passwordLabelObj = new GameObject("PasswordLabel");
            passwordLabelObj.transform.SetParent(transform);
            passwordLabelObj.transform.localPosition = new Vector3(0, 80, 0);
            var passwordLabel = passwordLabelObj.AddComponent<TMPro.TextMeshPro>();
            passwordLabel.text = "Password";
            passwordLabel.fontSize = UI.DesignTokens.Typography.Body;
            passwordLabel.font = UI.DesignTokens.Typography.SansFont;
            passwordLabel.color = UI.DesignTokens.Colors.Neutral900;
            passwordLabel.alignment = TMPro.TextAlignmentOptions.Center;

            passwordField = new GameObject("PasswordField");
            passwordField.transform.SetParent(transform);
            passwordField.transform.localPosition = new Vector3(0, 50, 0);
            var passwordInput = passwordField.AddComponent<UI.Components.InputField>();
            passwordInput.Placeholder = "Enter password";
            passwordInput.IsPassword = true;
            passwordInput.OnValueChanged = (val) => { };

            // Confirm password label and field
            var confirmLabelObj = new GameObject("ConfirmPasswordLabel");
            confirmLabelObj.transform.SetParent(transform);
            confirmLabelObj.transform.localPosition = new Vector3(0, 30, 0);
            var confirmLabel = confirmLabelObj.AddComponent<TMPro.TextMeshPro>();
            confirmLabel.text = "Confirm Password";
            confirmLabel.fontSize = UI.DesignTokens.Typography.Body;
            confirmLabel.font = UI.DesignTokens.Typography.SansFont;
            confirmLabel.color = UI.DesignTokens.Colors.Neutral900;
            confirmLabel.alignment = TMPro.TextAlignmentOptions.Center;

            confirmPasswordField = new GameObject("ConfirmPasswordField");
            confirmPasswordField.transform.SetParent(transform);
            confirmPasswordField.transform.localPosition = new Vector3(0, 0, 0);
            var confirmInput = confirmPasswordField.AddComponent<UI.Components.InputField>();
            confirmInput.Placeholder = "Re-enter password";
            confirmInput.IsPassword = true;
            confirmInput.OnValueChanged = (val) => { };

            // Register button
            registerButton = new GameObject("RegisterButton");
            registerButton.transform.SetParent(transform);
            registerButton.transform.localPosition = new Vector3(0, -60, 0);
            var btn = registerButton.AddComponent<UI.Components.Button>();
            btn.Label = "Register";
            btn.OnClick = () => { /* TODO: Implement registration logic */ };

            // Error message
            errorMsg = new GameObject("ErrorMsg");
            errorMsg.transform.SetParent(transform);
            errorMsg.transform.localPosition = new Vector3(0, -120, 0);
            var errorLabel = errorMsg.AddComponent<TMPro.TextMeshPro>();
            errorLabel.text = "";
            errorLabel.fontSize = UI.DesignTokens.Typography.Caption;
            errorLabel.font = UI.DesignTokens.Typography.SansFont;
            errorLabel.color = UI.DesignTokens.Colors.Neutral400;
            errorLabel.alignment = TMPro.TextAlignmentOptions.Center;
        }

        public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint)
        {
            switch (breakpoint)
            {
                case UIManager.Breakpoint.Mobile:
                    width = 260f; height = 220f;
                    break;
                case UIManager.Breakpoint.Tablet:
                    width = 320f; height = 260f;
                    break;
                case UIManager.Breakpoint.Desktop:
                    width = 400f; height = 360f;
                    break;
                case UIManager.Breakpoint.LargeDesktop:
                    width = 520f; height = 420f;
                    break;
            }
            var sr = GetComponent<SpriteRenderer>();
            if (sr != null)
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            if (usernameField != null) usernameField.transform.localPosition = new Vector3(0, height/4, 0);
            if (passwordField != null) passwordField.transform.localPosition = new Vector3(0, height/8, 0);
            if (confirmPasswordField != null) confirmPasswordField.transform.localPosition = new Vector3(0, 0, 0);
            if (registerButton != null) registerButton.transform.localPosition = new Vector3(0, -height/6, 0);
            if (errorMsg != null) errorMsg.transform.localPosition = new Vector3(0, -height/3, 0);
        }
    }
} 
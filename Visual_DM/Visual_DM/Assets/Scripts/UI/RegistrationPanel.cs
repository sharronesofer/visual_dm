using UnityEngine;

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
            // Background
            var sr = gameObject.AddComponent<SpriteRenderer>();
            sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            sr.sortingOrder = 120;

            // TODO: Add username field rendering
            usernameField = new GameObject("UsernameField");
            usernameField.transform.SetParent(transform);
            usernameField.transform.localPosition = new Vector3(0, 100, 0);
            // TODO: Add input logic

            // TODO: Add password field rendering
            passwordField = new GameObject("PasswordField");
            passwordField.transform.SetParent(transform);
            passwordField.transform.localPosition = new Vector3(0, 50, 0);
            // TODO: Add input logic

            // TODO: Add confirm password field rendering
            confirmPasswordField = new GameObject("ConfirmPasswordField");
            confirmPasswordField.transform.SetParent(transform);
            confirmPasswordField.transform.localPosition = new Vector3(0, 0, 0);
            // TODO: Add input logic

            // Register button
            registerButton = new GameObject("RegisterButton");
            registerButton.transform.SetParent(transform);
            registerButton.transform.localPosition = new Vector3(0, -60, 0);
            var btnSr = registerButton.AddComponent<SpriteRenderer>();
            btnSr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { 140, 40, new Color(0.25f, 0.4f, 0.25f, 1f) }) as Sprite;
            btnSr.sortingOrder = 121;
            // TODO: Add click logic and validation

            // Error message placeholder
            errorMsg = new GameObject("ErrorMsg");
            errorMsg.transform.SetParent(transform);
            errorMsg.transform.localPosition = new Vector3(0, -120, 0);
            // TODO: Add text rendering for error messages
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
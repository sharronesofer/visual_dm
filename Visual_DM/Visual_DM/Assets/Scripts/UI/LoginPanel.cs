using UnityEngine;

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
            // Background
            var sr = gameObject.AddComponent<SpriteRenderer>();
            sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            sr.sortingOrder = 120;

            // TODO: Add username field rendering
            usernameField = new GameObject("UsernameField");
            usernameField.transform.SetParent(transform);
            usernameField.transform.localPosition = new Vector3(0, 60, 0);
            // TODO: Add input logic

            // TODO: Add password field rendering
            passwordField = new GameObject("PasswordField");
            passwordField.transform.SetParent(transform);
            passwordField.transform.localPosition = new Vector3(0, 10, 0);
            // TODO: Add input logic

            // Login button
            loginButton = new GameObject("LoginButton");
            loginButton.transform.SetParent(transform);
            loginButton.transform.localPosition = new Vector3(0, -50, 0);
            var btnSr = loginButton.AddComponent<SpriteRenderer>();
            btnSr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { 120, 40, new Color(0.25f, 0.4f, 0.25f, 1f) }) as Sprite;
            btnSr.sortingOrder = 121;
            // TODO: Add click logic and validation

            // Error message placeholder
            errorMsg = new GameObject("ErrorMsg");
            errorMsg.transform.SetParent(transform);
            errorMsg.transform.localPosition = new Vector3(0, -100, 0);
            // TODO: Add text rendering for error messages
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
using UnityEngine;

namespace VisualDM.UI
{
    public class UserProfilePanel : PanelBase
    {
        private GameObject usernameField;
        private GameObject emailField;
        private GameObject editButton;
        private GameObject logoutButton;
        private float width = 400f;
        private float height = 260f;
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
            // TODO: Add text rendering

            // TODO: Add email field rendering
            emailField = new GameObject("EmailField");
            emailField.transform.SetParent(transform);
            emailField.transform.localPosition = new Vector3(0, 20, 0);
            // TODO: Add text rendering

            // Edit button
            editButton = new GameObject("EditButton");
            editButton.transform.SetParent(transform);
            editButton.transform.localPosition = new Vector3(-60, -40, 0);
            var editSr = editButton.AddComponent<SpriteRenderer>();
            editSr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { 100, 36, new Color(0.25f, 0.4f, 0.25f, 1f) }) as Sprite;
            editSr.sortingOrder = 121;
            // TODO: Add click logic

            // Logout button
            logoutButton = new GameObject("LogoutButton");
            logoutButton.transform.SetParent(transform);
            logoutButton.transform.localPosition = new Vector3(60, -40, 0);
            var logoutSr = logoutButton.AddComponent<SpriteRenderer>();
            logoutSr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { 100, 36, new Color(0.4f, 0.25f, 0.25f, 1f) }) as Sprite;
            logoutSr.sortingOrder = 121;
            // TODO: Add click logic
        }

        public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint)
        {
            switch (breakpoint)
            {
                case UIManager.Breakpoint.Mobile:
                    width = 220f; height = 140f;
                    break;
                case UIManager.Breakpoint.Tablet:
                    width = 300f; height = 180f;
                    break;
                case UIManager.Breakpoint.Desktop:
                    width = 400f; height = 260f;
                    break;
                case UIManager.Breakpoint.LargeDesktop:
                    width = 520f; height = 320f;
                    break;
            }
            var sr = GetComponent<SpriteRenderer>();
            if (sr != null)
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            if (usernameField != null) usernameField.transform.localPosition = new Vector3(0, height/5, 0);
            if (emailField != null) emailField.transform.localPosition = new Vector3(0, height/13, 0);
            if (editButton != null) editButton.transform.localPosition = new Vector3(-width/6, -height/6, 0);
            if (logoutButton != null) logoutButton.transform.localPosition = new Vector3(width/6, -height/6, 0);
        }
    }
} 
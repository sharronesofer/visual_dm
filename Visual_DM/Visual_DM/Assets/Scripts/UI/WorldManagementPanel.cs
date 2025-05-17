using UnityEngine;

namespace VisualDM.UI
{
    public class WorldManagementPanel : PanelBase
    {
        private GameObject titleObj;
        private GameObject listPlaceholder;
        private GameObject addButton;
        private float width = 600f;
        private float height = 400f;
        private Color bgColor = new Color(0.18f, 0.18f, 0.22f, 0.98f);

        public override void Initialize(params object[] args)
        {
            // Background
            var sr = gameObject.AddComponent<SpriteRenderer>();
            sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            sr.sortingOrder = 110;

            // TODO: Add title text rendering
            titleObj = new GameObject("Title");
            titleObj.transform.SetParent(transform);
            titleObj.transform.localPosition = new Vector3(0, height/2 - 30, 0);
            // TODO: Add text rendering for title

            // Placeholder for world list
            listPlaceholder = new GameObject("WorldListPlaceholder");
            listPlaceholder.transform.SetParent(transform);
            listPlaceholder.transform.localPosition = new Vector3(0, 0, 0);
            // TODO: Add list rendering

            // Add button
            addButton = new GameObject("AddWorldButton");
            addButton.transform.SetParent(transform);
            addButton.transform.localPosition = new Vector3(width/2 - 60, -height/2 + 30, 0);
            var btnSr = addButton.AddComponent<SpriteRenderer>();
            btnSr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { 100, 40, new Color(0.25f, 0.4f, 0.25f, 1f) }) as Sprite;
            btnSr.sortingOrder = 111;
            // TODO: Add click logic
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
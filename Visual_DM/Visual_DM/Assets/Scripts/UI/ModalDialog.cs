using UnityEngine;
using System;

namespace VisualDM.UI
{
    /// <summary>
    /// Runtime-generated modal dialog with message and buttons. Inherits from PanelBase.
    /// </summary>
    public class ModalDialog : PanelBase
    {
        private GameObject okButton;
        private GameObject cancelButton;
        private Action onOk;
        private Action onCancel;
        private float width = 400f;
        private float height = 200f;
        private Color bgColor = new Color(0.2f, 0.2f, 0.3f, 0.98f);
        private Color buttonColor = new Color(0.3f, 0.3f, 0.4f, 1f);

        public override void Initialize(params object[] args)
        {
            string message = args.Length > 0 && args[0] is string msg ? msg : "Are you sure?";
            onOk = args.Length > 1 && args[1] is Action ok ? ok : null;
            onCancel = args.Length > 2 && args[2] is Action cancel ? cancel : null;

            // Background
            var sr = gameObject.AddComponent<SpriteRenderer>();
            sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            sr.sortingOrder = 201;

            // TODO: Add message text rendering (requires custom text rendering or TextMeshPro integration)

            // OK Button
            okButton = new GameObject("OKButton");
            okButton.transform.SetParent(transform);
            okButton.transform.localPosition = new Vector3(-80, -60, 0);
            var okSr = okButton.AddComponent<SpriteRenderer>();
            okSr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { 100, 40, buttonColor }) as Sprite;
            okSr.sortingOrder = 202;
            // Add click logic here if needed

            // Cancel Button
            cancelButton = new GameObject("CancelButton");
            cancelButton.transform.SetParent(transform);
            cancelButton.transform.localPosition = new Vector3(80, -60, 0);
            var cancelSr = cancelButton.AddComponent<SpriteRenderer>();
            cancelSr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { 100, 40, buttonColor }) as Sprite;
            cancelSr.sortingOrder = 202;
            // Add click logic here if needed
        }

        public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint)
        {
            switch (breakpoint)
            {
                case UIManager.Breakpoint.Mobile:
                    width = 260f; height = 120f;
                    break;
                case UIManager.Breakpoint.Tablet:
                    width = 320f; height = 160f;
                    break;
                case UIManager.Breakpoint.Desktop:
                    width = 400f; height = 200f;
                    break;
                case UIManager.Breakpoint.LargeDesktop:
                    width = 520f; height = 260f;
                    break;
            }
            // Update background size
            var sr = GetComponent<SpriteRenderer>();
            if (sr != null)
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            // Update button positions
            if (okButton != null) okButton.transform.localPosition = new Vector3(-width/5, -height/3, 0);
            if (cancelButton != null) cancelButton.transform.localPosition = new Vector3(width/5, -height/3, 0);
        }
    }
} 
using UnityEngine;
using System;
using System.Collections.Generic;

namespace VisualDM.UI
{
    /// <summary>
    /// Runtime-generated navigation bar with buttons. Inherits from PanelBase.
    /// </summary>
    public class NavigationBar : PanelBase
    {
        private List<GameObject> buttons = new List<GameObject>();
        private float buttonWidth = 120f;
        private float buttonHeight = 40f;
        private float spacing = 10f;
        private Color bgColor = new Color(0.15f, 0.15f, 0.2f, 0.95f);
        private Color buttonColor = new Color(0.25f, 0.25f, 0.35f, 1f);
        private string[] labels;
        private Action<int>[] actions;

        public override void Initialize(params object[] args)
        {
            labels = args.Length > 0 && args[0] is string[] arr ? arr : new string[] { "Home", "Worlds", "NPCs", "Quests", "Combat", "Items" };
            actions = args.Length > 1 && args[1] is Action<int>[] acts ? acts : null;
            CreateLayout(UIManager.Instance.CurrentBreakpoint);
        }

        public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint)
        {
            CreateLayout(breakpoint);
        }

        private void CreateLayout(UIManager.Breakpoint breakpoint)
        {
            // Remove old buttons
            foreach (var btn in buttons)
                if (btn != null) GameObject.Destroy(btn);
            buttons.Clear();

            // Adjust size/spacing based on breakpoint
            switch (breakpoint)
            {
                case UIManager.Breakpoint.Mobile:
                    buttonWidth = 80f; buttonHeight = 32f; spacing = 4f;
                    break;
                case UIManager.Breakpoint.Tablet:
                    buttonWidth = 100f; buttonHeight = 36f; spacing = 8f;
                    break;
                case UIManager.Breakpoint.Desktop:
                    buttonWidth = 120f; buttonHeight = 40f; spacing = 10f;
                    break;
                case UIManager.Breakpoint.LargeDesktop:
                    buttonWidth = 140f; buttonHeight = 48f; spacing = 14f;
                    break;
            }

            // Background
            var sr = GetComponent<SpriteRenderer>();
            if (sr == null) sr = gameObject.AddComponent<SpriteRenderer>();
            sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { (int)(labels.Length * (buttonWidth + spacing)), (int)buttonHeight, bgColor }) as Sprite;
            sr.sortingOrder = 101;

            // Create buttons
            for (int i = 0; i < labels.Length; i++)
            {
                GameObject btn = new GameObject($"NavButton_{labels[i]}");
                btn.transform.SetParent(transform);
                btn.transform.localPosition = new Vector3(i * (buttonWidth + spacing), 0, 0);
                var btnSr = btn.AddComponent<SpriteRenderer>();
                btnSr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)buttonWidth, (int)buttonHeight, buttonColor }) as Sprite;
                btnSr.sortingOrder = 102;
                // Add button logic (click detection) here if needed
                buttons.Add(btn);
            }
        }
    }
} 
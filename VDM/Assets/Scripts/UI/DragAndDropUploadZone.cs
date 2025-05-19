using UnityEngine;
using System;
using System.Collections.Generic;

namespace VisualDM.UI
{
    /// <summary>
    /// Runtime-generated drag-and-drop upload zone. Handles file drag-and-drop with visual feedback and file capture.
    /// </summary>
    public class DragAndDropUploadZone : PanelBase
    {
        public Action<List<string>> OnFilesDropped; // List of file paths
        private SpriteRenderer _background;
        private Color _normalColor = new Color(0.18f, 0.18f, 0.22f, 0.95f);
        private Color _hoverColor = new Color(0.28f, 0.28f, 0.38f, 0.98f);
        private float _width = 480f;
        private float _height = 180f;
        private bool _isHovering = false;

        public override void Initialize(params object[] args)
        {
            // Optionally accept width, height, and callback
            if (args.Length > 0 && args[0] is float w) _width = w;
            if (args.Length > 1 && args[1] is float h) _height = h;
            if (args.Length > 2 && args[2] is Action<List<string>> cb) OnFilesDropped = cb;

            // Background
            _background = gameObject.AddComponent<SpriteRenderer>();
            _background.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { (int)_width, (int)_height, _normalColor }) as Sprite;
            _background.sortingOrder = 110;
        }

        void Update()
        {
#if UNITY_STANDALONE || UNITY_EDITOR
            // Only works in standalone builds or editor
            if (IsPointerOverZone())
            {
                if (!_isHovering)
                {
                    _isHovering = true;
                    _background.color = _hoverColor;
                }
                if (Core.GetMouseButtonUp(0))
                {
                    // On mouse up, check for dropped files
                    var droppedFiles = GetDroppedFiles();
                    if (droppedFiles != null && droppedFiles.Count > 0)
                    {
                        OnFilesDropped?.Invoke(droppedFiles);
                    }
                }
            }
            else if (_isHovering)
            {
                _isHovering = false;
                _background.color = _normalColor;
            }
#endif
        }

        // Checks if the mouse is over the zone (simple AABB test)
        private bool IsPointerOverZone()
        {
            Vector3 mouseWorld = Camera.main.ScreenToWorldPoint(Core.mousePosition);
            Vector3 pos = transform.position;
            float halfW = _width / 200f; // SpriteRenderer units
            float halfH = _height / 200f;
            return mouseWorld.x > pos.x - halfW && mouseWorld.x < pos.x + halfW &&
                   mouseWorld.y > pos.y - halfH && mouseWorld.y < pos.y + halfH;
        }

        // Platform-specific: get dropped files (Editor/Standalone only)
        private List<string> GetDroppedFiles()
        {
#if UNITY_EDITOR
            // In Editor, use DragAndDrop (not available at runtime)
            return null;
#elif UNITY_STANDALONE_WIN || UNITY_STANDALONE_OSX || UNITY_STANDALONE_LINUX
            // At runtime, Unity does not natively support OS drag-and-drop. This is a placeholder for native plugin integration.
            return null;
#else
            return null;
#endif
        }
    }
} 
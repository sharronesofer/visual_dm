using UnityEngine;
using System;

namespace VisualDM.UI
{
    /// <summary>
    /// Runtime-generated upload progress bar. Displays percent, speed, and ETA.
    /// </summary>
    public class UploadProgressBar : MonoBehaviour
    {
        private SpriteRenderer _background;
        private SpriteRenderer _bar;
        private float _width = 400f;
        private float _height = 32f;
        private Color _bgColor = new Color(0.15f, 0.15f, 0.18f, 0.95f);
        private Color _barColor = new Color(0.3f, 0.7f, 0.3f, 1f);
        private float _progress = 0f;
        private float _speed = 0f;
        private TimeSpan? _eta = null;
        private string _label = "";

        public void Initialize(float width, float height)
        {
            _width = width;
            _height = height;
            // Background
            _background = gameObject.AddComponent<SpriteRenderer>();
            _background.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { (int)_width, (int)_height, _bgColor }) as Sprite;
            _background.sortingOrder = 120;
            // Bar
            GameObject barObj = new GameObject("Bar");
            barObj.transform.SetParent(transform);
            barObj.transform.localPosition = new Vector3(-_width / 2f, 0, 0);
            _bar = barObj.AddComponent<SpriteRenderer>();
            _bar.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { 1, (int)_height, _barColor }) as Sprite;
            _bar.sortingOrder = 121;
        }

        public void SetProgress(float progress, float speedBytesPerSec = 0f, TimeSpan? eta = null, string label = "")
        {
            _progress = Mathf.Clamp01(progress);
            _speed = speedBytesPerSec;
            _eta = eta;
            _label = label;
            UpdateBar();
        }

        private void UpdateBar()
        {
            if (_bar == null) return;
            float barWidth = _width * _progress;
            _bar.size = new Vector2(barWidth, _height);
            // Optionally update label (requires text rendering solution)
        }
    }
} 
using UnityEngine;
using TMPro;
using System;

namespace VisualDM.UI.Navigation
{
    /// <summary>
    /// Represents a single breadcrumb segment, supports focus, click, and accessibility.
    /// </summary>
    public class BreadcrumbItem : MonoBehaviour
    {
        public bool IsEllipsis = false;
        public bool IsActive = false;
        public int Index = 0;
        public Action<int> OnBreadcrumbSelected;

        private TextMeshPro label;
        private void Awake()
        {
            label = GetComponent<TextMeshPro>();
        }

        private void OnMouseDown()
        {
            OnBreadcrumbSelected?.Invoke(Index);
        }

        private void OnMouseEnter()
        {
            // Microanimation: scale up on hover
            transform.localScale = Vector3.one * 1.1f;
        }

        private void OnMouseExit()
        {
            // Microanimation: scale back
            transform.localScale = Vector3.one;
        }

        private void Update()
        {
            // Keyboard navigation: Tab/Enter
            if (IsActive && Input.GetKeyDown(KeyCode.Return))
            {
                OnBreadcrumbSelected?.Invoke(Index);
            }
        }
    }
} 
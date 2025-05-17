using UnityEngine;
using System.Collections.Generic;
using TMPro;

namespace VisualDM.UI.Navigation
{
    /// <summary>
    /// Manages breadcrumb navigation, supports dynamic updates, truncation, and accessibility.
    /// </summary>
    public class BreadcrumbNavigation : MonoBehaviour
    {
        public List<string> PathSegments { get; private set; } = new List<string>();
        public int MaxVisibleSegments = 4;
        private List<GameObject> breadcrumbItems = new List<GameObject>();
        private float spacing = 32f;
        private float startX = -120f;

        public void SetPath(List<string> segments)
        {
            PathSegments = new List<string>(segments);
            UpdateBreadcrumbs();
        }

        public void AddSegment(string segment)
        {
            PathSegments.Add(segment);
            UpdateBreadcrumbs();
        }

        public void RemoveLastSegment()
        {
            if (PathSegments.Count > 0)
                PathSegments.RemoveAt(PathSegments.Count - 1);
            UpdateBreadcrumbs();
        }

        private void UpdateBreadcrumbs()
        {
            // Clear old items
            foreach (var go in breadcrumbItems)
                Destroy(go);
            breadcrumbItems.Clear();

            int count = PathSegments.Count;
            int startIdx = Mathf.Max(0, count - MaxVisibleSegments);
            bool truncated = count > MaxVisibleSegments;

            float x = startX;
            if (truncated)
            {
                var ellipsis = CreateBreadcrumbItem("...", x, true);
                breadcrumbItems.Add(ellipsis);
                x += spacing;
            }

            for (int i = startIdx; i < count; i++)
            {
                var item = CreateBreadcrumbItem(PathSegments[i], x, false, i == count - 1);
                breadcrumbItems.Add(item);
                x += spacing;
            }
        }

        private GameObject CreateBreadcrumbItem(string label, float x, bool isEllipsis, bool isActive = false)
        {
            var go = new GameObject($"Breadcrumb_{label}");
            go.transform.SetParent(transform);
            go.transform.localPosition = new Vector3(x, 0, 0);
            var text = go.AddComponent<TextMeshPro>();
            text.text = label;
            text.fontSize = UI.DesignTokens.Typography.Body;
            text.font = UI.DesignTokens.Typography.SansFont;
            text.color = isActive ? UI.DesignTokens.Colors.Primary500 : UI.DesignTokens.Colors.Neutral700;
            text.alignment = TextAlignmentOptions.Center;
            // Accessibility: Add focus and tab navigation
            var nav = go.AddComponent<BreadcrumbItem>();
            nav.IsEllipsis = isEllipsis;
            nav.IsActive = isActive;
            nav.Index = breadcrumbItems.Count;
            nav.OnBreadcrumbSelected = OnBreadcrumbSelected;
            return go;
        }

        private void OnBreadcrumbSelected(int index)
        {
            // Truncate logic: if ellipsis is selected, expand all
            if (index == 0 && PathSegments.Count > MaxVisibleSegments)
            {
                MaxVisibleSegments = PathSegments.Count;
                UpdateBreadcrumbs();
            }
            else
            {
                // Navigate to selected segment
                // TODO: Integrate with routing/navigation system
            }
        }
    }
} 
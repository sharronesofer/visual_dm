using UnityEngine;
using UnityEngine.UI;

namespace VisualDM.UI
{
    /// <summary>
    /// Defines an interactive region for gesture detection. Ensures minimum size and accessibility.
    /// </summary>
    [RequireComponent(typeof(BoxCollider2D))]
    public class GestureArea : MonoBehaviour
    {
        public enum GestureType { Swipe, PullToRefresh, PinchToZoom }
        public GestureType gestureType;

        private void Awake()
        {
            // Ensure minimum size for accessibility
            var collider = GetComponent<BoxCollider2D>();
            collider.size = new Vector2(Mathf.Max(44, collider.size.x), Mathf.Max(44, collider.size.y));
        }

        private void OnEnable()
        {
            if (gestureType == GestureType.Swipe)
                GestureNavigationManager.Instance.OnSwipe += HandleSwipe;
            if (gestureType == GestureType.PullToRefresh)
                GestureNavigationManager.Instance.OnPullToRefresh += HandlePullToRefresh;
            if (gestureType == GestureType.PinchToZoom)
                GestureNavigationManager.Instance.OnPinchToZoom += HandlePinchToZoom;
        }

        private void OnDisable()
        {
            if (gestureType == GestureType.Swipe)
                GestureNavigationManager.Instance.OnSwipe -= HandleSwipe;
            if (gestureType == GestureType.PullToRefresh)
                GestureNavigationManager.Instance.OnPullToRefresh -= HandlePullToRefresh;
            if (gestureType == GestureType.PinchToZoom)
                GestureNavigationManager.Instance.OnPinchToZoom -= HandlePinchToZoom;
        }

        private void HandleSwipe(Vector2 direction)
        {
            // TODO: Implement navigation logic for swipe
        }

        private void HandlePullToRefresh()
        {
            // TODO: Implement refresh logic
        }

        private void HandlePinchToZoom(float delta)
        {
            // TODO: Implement zoom logic
        }
    }
} 
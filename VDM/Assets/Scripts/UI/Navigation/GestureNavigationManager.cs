using UnityEngine;
using System;

namespace VisualDM.UI
{
    /// <summary>
    /// Singleton service for detecting and processing mobile gestures: swipe, pull-to-refresh, pinch-to-zoom.
    /// </summary>
    public class GestureNavigationManager : MonoBehaviour
    {
        public static GestureNavigationManager Instance { get; private set; }

        public event Action<Vector2> OnSwipe;
        public event Action OnPullToRefresh;
        public event Action<float> OnPinchToZoom;

        private Vector2 swipeStartPos;
        private float swipeStartTime;
        private bool isSwiping = false;
        private float pinchStartDist = 0f;
        private bool isPinching = false;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(this);
                return;
            }
            Instance = this;
        }

        private void Update()
        {
#if UNITY_ANDROID || UNITY_IOS
            if (Core.touchCount == 1)
            {
                Touch touch = Core.GetTouch(0);
                switch (touch.phase)
                {
                    case TouchPhase.Began:
                        swipeStartPos = touch.position;
                        swipeStartTime = Time.time;
                        isSwiping = true;
                        break;
                    case TouchPhase.Moved:
                        // Could add visual feedback here
                        break;
                    case TouchPhase.Ended:
                        if (isSwiping)
                        {
                            Vector2 delta = touch.position - swipeStartPos;
                            float duration = Time.time - swipeStartTime;
                            if (delta.magnitude > 80f && duration < 0.5f)
                            {
                                OnSwipe?.Invoke(delta.normalized);
                            }
                            // Pull-to-refresh: downward swipe with vertical threshold
                            if (delta.y > 120f && Mathf.Abs(delta.x) < 60f)
                            {
                                OnPullToRefresh?.Invoke();
                            }
                        }
                        isSwiping = false;
                        break;
                }
            }
            else if (Core.touchCount == 2)
            {
                Touch t0 = Core.GetTouch(0);
                Touch t1 = Core.GetTouch(1);
                float currDist = Vector2.Distance(t0.position, t1.position);
                if (!isPinching)
                {
                    pinchStartDist = currDist;
                    isPinching = true;
                }
                else
                {
                    float pinchDelta = currDist - pinchStartDist;
                    if (Mathf.Abs(pinchDelta) > 20f)
                    {
                        OnPinchToZoom?.Invoke(pinchDelta * 0.01f);
                        pinchStartDist = currDist;
                    }
                }
            }
            else
            {
                isSwiping = false;
                isPinching = false;
            }
#endif
        }
    }
} 
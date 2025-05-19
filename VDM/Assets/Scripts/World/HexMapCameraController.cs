using UnityEngine;

namespace VisualDM.World
{
    /// <summary>
    /// Controls camera movement, zoom, and scale switching for multi-scale hex maps (region/POI).
    /// Runtime-only, no scene or prefab dependencies.
    /// </summary>
    public class HexMapCameraController : MonoBehaviour
    {
        public enum MapScale { Region, POI }
        public MapScale CurrentScale { get; private set; } = MapScale.Region;
        public Vector3 CurrentPosition { get; private set; } = Vector3.zero;
        public float RegionZoom = 10f;
        public float POIZoom = 2.5f;
        public float ZoomSpeed = 5f;
        public float PanSpeed = 10f;

        private Camera cam;
        private bool isTransitioning = false;
        private float targetZoom;
        private Vector3 targetPosition;
        private MapScale targetScale;

        void Awake()
        {
            cam = Camera.main;
            if (cam == null)
            {
                var camObj = new GameObject("MainCamera");
                cam = camObj.AddComponent<Camera>();
                cam.orthographic = true;
                camObj.tag = "MainCamera";
            }
            SetScale(MapScale.Region, Vector3.zero, instant: true);
        }

        void Update()
        {
            HandleCore();
            if (isTransitioning)
            {
                cam.orthographicSize = Mathf.Lerp(cam.orthographicSize, targetZoom, Time.deltaTime * ZoomSpeed);
                cam.transform.position = Vector3.Lerp(cam.transform.position, targetPosition, Time.deltaTime * ZoomSpeed);
                if (Mathf.Abs(cam.orthographicSize - targetZoom) < 0.01f && (cam.transform.position - targetPosition).sqrMagnitude < 0.01f)
                {
                    cam.orthographicSize = targetZoom;
                    cam.transform.position = targetPosition;
                    isTransitioning = false;
                    CurrentScale = targetScale;
                    CurrentPosition = targetPosition;
                }
            }
        }

        private void HandleCore()
        {
            // Pan
            float h = Core.GetAxis("Horizontal");
            float v = Core.GetAxis("Vertical");
            if (Mathf.Abs(h) > 0.01f || Mathf.Abs(v) > 0.01f)
            {
                var move = new Vector3(h, v, 0) * PanSpeed * Time.deltaTime;
                cam.transform.position += move;
                CurrentPosition = cam.transform.position;
            }
            // Zoom in/out (switch scale)
            if (Core.GetKeyDown(KeyCode.Z))
            {
                if (CurrentScale == MapScale.Region)
                    ZoomToScale(MapScale.POI, cam.transform.position);
                else
                    ZoomToScale(MapScale.Region, cam.transform.position);
            }
        }

        public void ZoomToScale(MapScale scale, Vector3 focusPosition)
        {
            targetScale = scale;
            targetPosition = new Vector3(focusPosition.x, focusPosition.y, -10f); // Keep camera at z=-10
            targetZoom = (scale == MapScale.Region) ? RegionZoom : POIZoom;
            isTransitioning = true;
        }

        public void SetScale(MapScale scale, Vector3 position, bool instant = false)
        {
            CurrentScale = scale;
            CurrentPosition = position;
            if (cam == null) cam = Camera.main;
            cam.orthographicSize = (scale == MapScale.Region) ? RegionZoom : POIZoom;
            cam.transform.position = new Vector3(position.x, position.y, -10f);
            if (instant) { targetZoom = cam.orthographicSize; targetPosition = cam.transform.position; isTransitioning = false; }
        }
    }
}
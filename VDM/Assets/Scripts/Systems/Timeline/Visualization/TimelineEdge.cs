using UnityEngine;

namespace VisualDM.Timeline.Visualization
{
    public class TimelineEdge : MonoBehaviour
    {
        private LineRenderer _lineRenderer;

        public void Initialize(Vector3 start, Vector3 end, Color color)
        {
            _lineRenderer = gameObject.AddComponent<LineRenderer>();
            _lineRenderer.positionCount = 2;
            _lineRenderer.SetPosition(0, start);
            _lineRenderer.SetPosition(1, end);
            _lineRenderer.startWidth = 0.05f;
            _lineRenderer.endWidth = 0.05f;
            _lineRenderer.material = new Material(Shader.Find("Sprites/Default"));
            _lineRenderer.startColor = color;
            _lineRenderer.endColor = color;
            _lineRenderer.sortingOrder = -1;
        }
    }
} 
using UnityEngine;

namespace VisualDM.Bounty
{
    [CreateAssetMenu(fileName = "POIDefinition", menuName = "Bounty/POIDefinition", order = 2)]
    public class POIDefinition : ScriptableObject
    {
        [Header("POI Info")]
        public string poiName;
        public float bountyMultiplier = 1f;
        public float witnessDensity = 1f;
        public string regionId;
        [Tooltip("Polygon boundary points in world space (clockwise order)")]
        public Vector2[] boundaryPoints;
    }
} 
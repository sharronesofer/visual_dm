using UnityEngine;

namespace VisualDM.Bounty
{
    public enum CrimeSeverity { Minor, Moderate, Major, Capital }

    [CreateAssetMenu(fileName = "CrimeTypeDefinition", menuName = "Bounty/CrimeTypeDefinition", order = 1)]
    public class CrimeTypeDefinition : ScriptableObject
    {
        [Header("Crime Info")]
        public string crimeName;
        public CrimeSeverity severity;
        public float baseBounty = 100f;
        public float severityMultiplier = 1f;
        public float decayRate = 0.1f; // per minute
        public bool isMajorCrime = false;
        public string regionId;
    }
} 
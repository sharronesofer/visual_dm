using UnityEngine;

namespace VDM.Systems.War
{
    /// <summary>
    /// ScriptableObject template for possible war outcomes and their effects.
    /// </summary>
    [CreateAssetMenu(fileName = "WarOutcomeTemplate", menuName = "VDM/War/War Outcome Template")]
    public class WarOutcomeTemplate : ScriptableObject
    {
        public string OutcomeName;
        [Range(0, 1)] public float ProbabilityWeight;
        public int ResourceChangeA;
        public int ResourceChangeB;
        public int TerritoryChangeA;
        public int TerritoryChangeB;
        [TextArea]
        public string Description;
    }
} 
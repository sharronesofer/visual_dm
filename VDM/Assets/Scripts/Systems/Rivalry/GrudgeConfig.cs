using System;
using UnityEngine;

namespace VisualDM.Systems.Rivalry
{
    [Serializable]
    public class GrudgeCategoryConfig
    {
        public string CategoryName;
        public int MinorValue = 5;
        public int ModerateValue = 20;
        public int MajorValue = 60;
        public float MinorDecayRate = 2f; // points per day
        public float ModerateDecayRate = 1f;
        public float MajorDecayRate = 0.5f;
    }

    [CreateAssetMenu(fileName = "GrudgeConfig", menuName = "VisualDM/Rivalry/GrudgeConfig", order = 1)]
    public class GrudgeConfig : ScriptableObject
    {
        [Tooltip("List of all grudge categories and their configuration.")]
        public GrudgeCategoryConfig[] Categories;

        [Tooltip("Default decay rate for categories not listed.")]
        public float DefaultDecayRate = 1f;

        [Tooltip("Thresholds for rivalry progression.")]
        public int AnnoyedThreshold = 10;
        public int AngryThreshold = 31;
        public int VengefulThreshold = 76;
        public int NemesisThreshold = 151;
    }
}
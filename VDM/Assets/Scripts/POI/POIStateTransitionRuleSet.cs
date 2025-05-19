using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.POI
{
    public enum POIStateType
    {
        Normal,
        Declining,
        Abandoned,
        Ruins,
        Dungeon
    }

    [Serializable]
    public struct StateTransitionRule
    {
        public POIStateType fromState;
        public POIStateType toState;
        [Range(0f, 1f)] public float populationThreshold; // As percent of max
        public bool oneWayOnly;
    }

    [CreateAssetMenu(fileName = "POIStateTransitionRuleSet", menuName = "VDM/POI/StateTransitionRuleSet")]
    public class POIStateTransitionRuleSet : ScriptableObject
    {
        [Header("State Transition Rules")]
        public List<StateTransitionRule> transitionRules = new List<StateTransitionRule>();

        [Header("Exempt POIs (by ID)")]
        public List<string> exemptPOIIds = new List<string>();

        [Header("Manual Overrides")]
        public bool manualOverride = false;
        public POIStateType overrideState;

        public StateTransitionRule? GetRule(POIStateType from, POIStateType to)
        {
            foreach (var rule in transitionRules)
            {
                if (rule.fromState == from && rule.toState == to)
                    return rule;
            }
            return null;
        }

        public bool IsExempt(string poiId)
        {
            return exemptPOIIds.Contains(poiId);
        }

        public bool IsManualOverrideActive(out POIStateType state)
        {
            state = overrideState;
            return manualOverride;
        }
    }
} 
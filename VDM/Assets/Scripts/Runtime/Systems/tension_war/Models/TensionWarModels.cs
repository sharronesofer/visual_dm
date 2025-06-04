using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Systems.TensionWar.Models
{
    /// <summary>
    /// Core tension and war system models for Unity frontend
    /// Mirrors backend tension_war system structure
    /// </summary>
    
    [Serializable]
    public class TensionLevel
    {
        public string factionId1;
        public string factionId2;
        public float tensionValue;
        public string tensionReason;
        public DateTime lastUpdated;
        public List<string> contributingFactors;
    }
    
    [Serializable]
    public class WarDeclaration
    {
        public string id;
        public string aggressorFactionId;
        public string defenderFactionId;
        public string warReason;
        public DateTime startDate;
        public WarStatus status;
        public List<string> allies;
    }
    
    [Serializable]
    public class Conflict
    {
        public string id;
        public string name;
        public List<string> involvedFactions;
        public Vector3 location;
        public ConflictType type;
        public ConflictStatus status;
        public float intensity;
    }
    
    [Serializable]
    public class DiplomaticAction
    {
        public string id;
        public string initiatorFactionId;
        public string targetFactionId;
        public DiplomaticActionType actionType;
        public string description;
        public float tensionModifier;
        public DateTime timestamp;
    }
    
    public enum WarStatus
    {
        Declared,
        Active,
        Ceasefire,
        Ended,
        Suspended
    }
    
    public enum ConflictType
    {
        Skirmish,
        Battle,
        Siege,
        Raid,
        Diplomatic
    }
    
    public enum ConflictStatus
    {
        Brewing,
        Active,
        Resolved,
        Escalating
    }
    
    public enum DiplomaticActionType
    {
        TradeAgreement,
        Alliance,
        Insult,
        Threat,
        PeaceOffer,
        Ultimatum
    }
} 
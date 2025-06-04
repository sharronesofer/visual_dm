using System;
using System.Collections.Generic;

namespace VDM.DTOs.Combat
{
    [Serializable]
    public class CombatActionDTO
    {
        public string id;
        public string name;
        public string description;
        public string actionType;
        public int damage;
        public int manaCost;
        public float cooldown;
        public List<string> effects;
    }

    [Serializable]
    public class CombatResultDTO
    {
        public string combatId;
        public string winnerId;
        public List<CombatEventDTO> events;
        public int duration;
        public Dictionary<string, object> metadata;
    }

    [Serializable]
    public class CombatEventDTO
    {
        public string eventId;
        public string eventType;
        public string actorId;
        public string targetId;
        public string actionId;
        public int damage;
        public string timestamp;
        public Dictionary<string, object> data;
    }

    [Serializable]
    public class CombatStatsDTO
    {
        public int health;
        public int mana;
        public int attack;
        public int defense;
        public int speed;
        public int accuracy;
        public int evasion;
        public Dictionary<string, int> resistances;
    }

    /// <summary>
    /// Types of combat actions that can be performed
    /// </summary>
    public enum CombatActionDTOType
    {
        Attack,
        CastSpell,
        UseItem,
        Move,
        Defend,
        Wait,
        Flee
    }
} 
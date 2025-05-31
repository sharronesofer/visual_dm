using System;
using System.Collections.Generic;

namespace VDM.DTOs.Equipment
{
    [Serializable]
    public class EquipmentItemDTO
    {
        public string id;
        public string name;
        public string description;
        public string equipmentType;
        public string rarity;
        public int level;
        public Dictionary<string, int> stats;
        public List<string> effects;
        public string iconPath;
        public bool isEquipped;
    }

    [Serializable]
    public class EquipmentSlotDTO
    {
        public string slotId;
        public string slotType;
        public string equippedItemId;
        public bool isLocked;
        public List<string> allowedTypes;
    }

    [Serializable]
    public class EquipmentSetDTO
    {
        public string setId;
        public string setName;
        public List<string> itemIds;
        public Dictionary<int, List<string>> setBonuses; // pieces required -> effects
    }

    [Serializable]
    public class WeaponDTO : EquipmentItemDTO
    {
        public int attackPower;
        public float attackSpeed;
        public string weaponClass;
        public List<string> specialAbilities;
    }

    [Serializable]
    public class ArmorDTO : EquipmentItemDTO
    {
        public int defense;
        public int magicResistance;
        public string armorType;
        public Dictionary<string, float> damageReduction;
    }
} 
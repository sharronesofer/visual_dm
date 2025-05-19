using UnityEngine;

namespace VDM.Systems.War
{
    /// <summary>
    /// ScriptableObject template for tension modifiers (e.g., trade, aggression, diplomacy).
    /// </summary>
    [CreateAssetMenu(fileName = "TensionModifierTemplate", menuName = "VDM/War/Tension Modifier Template")]
    public class TensionModifierTemplate : ScriptableObject, ITensionModifier
    {
        public string ActionType;
        public float ModifierValue;
        [TextArea]
        public string Description;

        public float GetModifier() => ModifierValue;
    }
} 
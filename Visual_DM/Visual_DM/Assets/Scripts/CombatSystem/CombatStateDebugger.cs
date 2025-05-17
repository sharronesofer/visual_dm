using UnityEngine;
using System.Text;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Debugging tool for inspecting combat state at runtime.
    /// </summary>
    public class CombatStateDebugger : MonoBehaviour
    {
        public float logInterval = 5f;
        private float timer = 0f;

        void Update()
        {
            timer += Time.deltaTime;
            if (timer >= logInterval)
            {
                timer = 0f;
                LogCombatState();
            }
        }

        private void LogCombatState()
        {
            var state = CombatStateManager.Instance;
            var sb = new StringBuilder();
            sb.AppendLine("--- Combat State Debug ---");
            sb.AppendLine($"Active Combatants: {state.GetType().GetField("activeCombatants", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).GetValue(state) as System.Collections.ICollection}");
            // Log current actions
            sb.AppendLine("Current Actions:");
            var actions = state.GetType().GetField("currentActions", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).GetValue(state) as System.Collections.IDictionary;
            if (actions != null)
            {
                foreach (System.Collections.DictionaryEntry entry in actions)
                {
                    sb.AppendLine($"  {entry.Key}: {entry.Value}");
                }
            }
            // Log status effects
            sb.AppendLine("Status Effects:");
            var effects = state.GetType().GetField("statusEffects", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).GetValue(state) as System.Collections.IDictionary;
            if (effects != null)
            {
                foreach (System.Collections.DictionaryEntry entry in effects)
                {
                    sb.AppendLine($"  {entry.Key}: {entry.Value}");
                }
            }
            Debug.Log(sb.ToString());
        }
    }
} 
using System.Collections.Generic;
using UnityEngine;
#if TMP_PRESENT
using TMPro;
#endif

namespace VDM.Combat
{
    /// <summary>
    /// Manages combat state, turn queue, and effect pipeline for tactical encounters.
    /// </summary>
    public class CombatManager : MonoBehaviour
    {
        public TurnQueue TurnQueue { get; private set; } = new TurnQueue();
        public EffectPipeline EffectPipeline { get; private set; } = new EffectPipeline();

        public bool IsCombatActive { get; private set; } = false;

        /// <summary>
        /// Event fired at the start of a combatant's turn.
        /// </summary>
        public event System.Action<ICombatant> OnTurnStart;
        /// <summary>
        /// Event fired at the end of a combatant's turn.
        /// </summary>
        public event System.Action<ICombatant> OnTurnEnd;

        // --- UI for turn order ---
#if TMP_PRESENT
        private readonly List<GameObject> _turnOrderLabels = new();
#endif

        /// <summary>
        /// Starts a new combat encounter with the given combatants.
        /// </summary>
        public void StartCombat(IEnumerable<ICombatant> combatants)
        {
            TurnQueue = new TurnQueue();
            foreach (var c in combatants)
                TurnQueue.AddCombatant(c);
            IsCombatActive = true;
            StartTurn();
        }

        /// <summary>
        /// Ends the current combat encounter.
        /// </summary>
        public void EndCombat()
        {
            IsCombatActive = false;
            TurnQueue = new TurnQueue();
            ClearTurnOrderUI();
        }

        /// <summary>
        /// Advances to the next turn in the queue, processing effect hooks.
        /// </summary>
        public void NextTurn()
        {
            if (!IsCombatActive) return;
            var current = TurnQueue.Current;
            // Process end-of-turn effects
            EffectPipeline.OnTurnEnd(current);
            OnTurnEnd?.Invoke(current);
            TurnQueue.NextTurn();
            StartTurn();
        }

        /// <summary>
        /// Starts the current combatant's turn, processing effect hooks.
        /// </summary>
        private void StartTurn()
        {
            var current = TurnQueue.Current;
            if (current == null)
            {
                EndCombat();
                return;
            }
            // Process start-of-turn effects
            EffectPipeline.OnTurnStart(current);
            OnTurnStart?.Invoke(current);
        }

        /// <summary>
        /// Adds a combatant to the ongoing combat.
        /// </summary>
        public void AddCombatant(ICombatant combatant)
        {
            TurnQueue.AddCombatant(combatant);
        }

        /// <summary>
        /// Removes a combatant from the ongoing combat.
        /// </summary>
        public void RemoveCombatant(ICombatant combatant)
        {
            TurnQueue.RemoveCombatant(combatant);
        }

#if TMP_PRESENT
        /// <summary>
        /// Displays the current turn order as floating TextMeshPro labels.
        /// </summary>
        /// <param name="parent">Parent transform for labels (e.g., a UI canvas or world object).</param>
        /// <param name="startPos">World position to start the turn order display.</param>
        public void ShowTurnOrder(Transform parent, Vector3 startPos)
        {
            ClearTurnOrderUI();
            float xOffset = 0f;
            float spacing = 1.5f;
            int idx = 0;
            foreach (var combatant in TurnQueue.Order)
            {
                var go = new GameObject($"TurnOrderLabel_{combatant.Name}");
                go.transform.SetParent(parent, false);
                go.transform.position = startPos + new Vector3(xOffset, 0, 0);
                var tmp = go.AddComponent<TextMeshPro>();
                tmp.text = $"{(idx == 0 ? "> " : "")}{combatant.Name}";
                tmp.fontSize = 2.5f;
                tmp.color = idx == 0 ? Color.yellow : Color.white;
                tmp.alignment = TextAlignmentOptions.Center;
                _turnOrderLabels.Add(go);
                xOffset += spacing;
                idx++;
            }
        }

        /// <summary>
        /// Removes all turn order UI labels.
        /// </summary>
        public void ClearTurnOrderUI()
        {
            foreach (var go in _turnOrderLabels)
            {
                if (go != null)
                    Destroy(go);
            }
            _turnOrderLabels.Clear();
        }
#endif
    }
} 
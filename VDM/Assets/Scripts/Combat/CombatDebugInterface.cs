using UnityEngine;
using System.Linq;

namespace VDM.Combat
{
    /// <summary>
    /// Provides debug and testing tools for the combat system.
    /// </summary>
    public class CombatDebugInterface : MonoBehaviour
    {
        private CombatManager _manager;
        private bool _showEffects = true;

        private void Awake()
        {
            _manager = FindObjectOfType<CombatManager>();
        }

        private void OnGUI()
        {
            if (_manager == null) return;
            GUILayout.BeginArea(new Rect(10, 10, 300, 400), "Combat Debug", GUI.skin.window);

            if (GUILayout.Button("Advance Turn"))
                _manager.NextTurn();

            if (GUILayout.Button("Add Dummy Combatant"))
                _manager.AddCombatant(new DummyCombatant("Dummy" + Random.Range(0, 1000)));

            if (GUILayout.Button("Remove Last Combatant"))
            {
                var last = _manager.TurnQueue.Order.LastOrDefault();
                if (last != null)
                    _manager.RemoveCombatant(last);
            }

            _showEffects = GUILayout.Toggle(_showEffects, "Show Effect Visuals");
            if (_showEffects)
            {
                var current = _manager.TurnQueue.Current;
                if (current != null)
                {
                    var vis = FindObjectOfType<EffectVisualizer>();
                    if (vis != null)
                        vis.ShowEffects(current, _manager.EffectPipeline.GetEffects(current));
                }
            }
            else
            {
                var vis = FindObjectOfType<EffectVisualizer>();
                if (vis != null)
                    vis.ClearEffects();
            }

            GUILayout.EndArea();
        }
    }

    /// <summary>
    /// Dummy combatant for debug/testing.
    /// </summary>
    public class DummyCombatant : ICombatant
    {
        public int Initiative { get; } = Random.Range(1, 20);
        public bool IsAlive { get; } = true;
        public string Name { get; }
        public DummyCombatant(string name) { Name = name; }
    }
} 
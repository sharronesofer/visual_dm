using UnityEngine;
using VisualDM.Entities;
using VisualDM.Systems.Inventory;
using VisualDM.Dialogue;
using VisualDM.Systems.Bounty;

namespace VisualDM.Entities
{
    public enum HunterArchetype { Melee, Ranged, Magic }

    public class BountyHunterNPC : NPCBase
    {
        public HunterArchetype Archetype { get; private set; }
        public int Level { get; private set; }
        public float Difficulty { get; private set; }
        public bool IsElite { get; private set; }
        public bool IsActive { get; private set; } = true;

        // AI state
        private float pursuitTime = 0f;
        private float maxPursuitTime = 180f;
        private Transform targetPlayer;

        public void Initialize(HunterArchetype archetype, int level, float difficulty, bool isElite, Transform player)
        {
            this.Archetype = archetype;
            this.Level = level;
            this.Difficulty = difficulty;
            this.IsElite = isElite;
            this.targetPlayer = player;
            // TODO: Assign equipment, stats, and visual appearance
            if (GetComponent<BountyHunterAIController>() == null)
                gameObject.AddComponent<BountyHunterAIController>();
        }

        void Update()
        {
            if (!IsActive) return;
            pursuitTime += Time.deltaTime;
            if (pursuitTime > maxPursuitTime)
            {
                GiveUp();
                return;
            }
            // TODO: Pathfinding and combat logic
            PursuePlayer();
        }

        private void PursuePlayer()
        {
            // TODO: Use navigation/pathfinding to move toward player
        }

        public void EngageCombat()
        {
            Debug.Log(BountyHunterDialogue.GetRandomTaunt());
            // TODO: Integrate with CombatSystem
        }

        public void GiveUp()
        {
            IsActive = false;
            Debug.Log(BountyHunterDialogue.GetRandomTaunt());
            BountyHunterManager.Instance.RemoveHunter(this);
            Destroy(this.gameObject);
        }
    }
} 
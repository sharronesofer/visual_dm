using UnityEngine;
using System.Collections.Generic;
using VisualDM.Bounty;
using VisualDM.NPC;
using VisualDM.World;
using VisualDM.CombatSystem;
using VisualDM.Inventory;
using VisualDM.Dialogue;
using VisualDM.BountyHunter;

namespace VisualDM.BountyHunter
{
    /// <summary>
    /// Manages the lifecycle, spawning, and scaling of bounty hunter NPCs.
    /// Singleton, runtime-generated, integrates with bounty and UI systems.
    /// </summary>
    public class BountyHunterManager : MonoBehaviour
    {
        /// <summary>
        /// Singleton instance of the BountyHunterManager.
        /// </summary>
        public static BountyHunterManager Instance { get; private set; }

        /// <summary>
        /// List of currently active bounty hunter NPCs.
        /// </summary>
        private List<BountyHunterNPC> activeHunters = new List<BountyHunterNPC>();
        /// <summary>
        /// Cooldown in seconds between hunter spawns.
        /// </summary>
        private float spawnCooldown = 120f;
        /// <summary>
        /// Time of last hunter spawn.
        /// </summary>
        private float lastSpawnTime = -9999f;
        /// <summary>
        /// Maximum number of simultaneous active hunters.
        /// </summary>
        private int maxHunters = 3;

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(this.gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(this.gameObject);
            BountyManager.OnBountyChanged += OnBountyChanged;
        }

        void OnDestroy()
        {
            BountyManager.OnBountyChanged -= OnBountyChanged;
        }

        private void OnBountyChanged(float newBounty, float oldBounty)
        {
            if (Time.time - lastSpawnTime < spawnCooldown) return;
            if (newBounty > 0 && newBounty > oldBounty)
            {
                TrySpawnHunter(newBounty);
            }
        }

        private void TrySpawnHunter(float bounty)
        {
            if (activeHunters.Count >= maxHunters) return;
            Vector2 spawnPos = BountyHunterSpawnPointSelector.GetSpawnPositionNearPlayer();
            var hunter = BountyHunterNPCFactory.CreateHunter(bounty, spawnPos);
            activeHunters.Add(hunter);
            lastSpawnTime = Time.time;
            BountyHunterSpawnNotifier.NotifyHunterSpawned(bounty, hunter.IsElite);
            var ui = FindObjectOfType<BountyHunterUIController>();
            if (ui != null) ui.AddHunter(hunter);
        }

        /// <summary>
        /// Removes a hunter from the active list, updates UI, and grants rewards.
        /// </summary>
        /// <param name="hunter">The hunter to remove.</param>
        public void RemoveHunter(BountyHunterNPC hunter)
        {
            if (activeHunters.Contains(hunter))
            {
                activeHunters.Remove(hunter);
                var ui = FindObjectOfType<BountyHunterUIController>();
                if (ui != null) ui.RemoveHunter(hunter);
                BountyHunterRewardSystem.GrantReward(hunter);
            }
        }
    }
} 
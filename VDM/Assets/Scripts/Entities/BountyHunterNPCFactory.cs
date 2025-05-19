using UnityEngine;
using VisualDM.Bounty;
using VisualDM.Entities;
using VisualDM.Systems.Inventory;

namespace VisualDM.Entities
{
    public static class BountyHunterNPCFactory
    {
        public static BountyHunterNPC CreateHunter(float playerBounty, Vector2 spawnPos)
        {
            // Determine archetype and difficulty
            var archetype = GetRandomArchetype();
            int playerLevel = GetPlayerLevel();
            float difficulty = CalculateDifficulty(playerBounty, playerLevel);
            bool isElite = ShouldSpawnElite(playerBounty);
            var player = GetPlayerTransform();

            GameObject hunterGO = new GameObject("BountyHunterNPC");
            var hunter = hunterGO.AddComponent<BountyHunterNPC>();
            hunter.Initialize(archetype, playerLevel, difficulty, isElite, player);
            hunterGO.transform.position = spawnPos;
            if (hunterGO.GetComponent<BountyHunterAIController>() == null)
                hunterGO.AddComponent<BountyHunterAIController>();
            // TODO: Assign equipment, visual, and stats
            return hunter;
        }

        private static HunterArchetype GetRandomArchetype()
        {
            var values = System.Enum.GetValues(typeof(HunterArchetype));
            return (HunterArchetype)values.GetValue(Random.Range(0, values.Length));
        }

        private static int GetPlayerLevel()
        {
            // TODO: Integrate with player progression system
            return 1;
        }

        private static float CalculateDifficulty(float bounty, int playerLevel)
        {
            // Example: scale with bounty and player level
            return playerLevel + (bounty / 100f);
        }

        private static bool ShouldSpawnElite(float bounty)
        {
            return bounty > 1000f;
        }

        private static Transform GetPlayerTransform()
        {
            // TODO: Find player GameObject in scene
            return null;
        }
    }
} 
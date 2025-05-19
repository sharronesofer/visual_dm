using UnityEngine;
using VisualDM.World;
using VisualDM.Bounty;

namespace VisualDM.Entities.BountyHunter
{
    public static class BountyHunterSpawnPointSelector
    {
        public static Vector2 GetSpawnPositionNearPlayer()
        {
            // TODO: Use POIManager and WorldManager to find logical spawn points (entrances, roads, etc.)
            // Placeholder: spawn at random offset from player
            var player = GetPlayerTransform();
            if (player == null) return Vector2.zero;
            Vector2 offset = Random.insideUnitCircle.normalized * 10f;
            return (Vector2)player.position + offset;
        }

        private static Transform GetPlayerTransform()
        {
            // TODO: Find player GameObject in scene
            return null;
        }
    }
} 
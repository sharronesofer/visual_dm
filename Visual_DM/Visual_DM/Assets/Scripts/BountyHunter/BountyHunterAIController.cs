using UnityEngine;

namespace VisualDM.BountyHunter
{
    public class BountyHunterAIController : MonoBehaviour
    {
        private BountyHunterNPC hunter;
        private Transform player;
        private float giveUpDistance = 30f;
        private float engageDistance = 3f;
        private float pursuitSpeed = 4f;

        void Awake()
        {
            hunter = GetComponent<BountyHunterNPC>();
            player = hunter != null ? hunter.transform : null;
        }

        void Update()
        {
            if (hunter == null || !hunter.IsActive) return;
            if (player == null) player = FindPlayer();
            if (player == null) return;

            float dist = Vector2.Distance(transform.position, player.position);
            if (dist > giveUpDistance)
            {
                hunter.GiveUp();
                return;
            }
            else if (dist < engageDistance)
            {
                hunter.EngageCombat();
            }
            else
            {
                MoveTowardsPlayer();
            }
        }

        private void MoveTowardsPlayer()
        {
            Vector2 dir = (player.position - transform.position).normalized;
            transform.position += (Vector3)(dir * pursuitSpeed * Time.deltaTime);
        }

        private Transform FindPlayer()
        {
            // TODO: Find player GameObject in scene
            return null;
        }
    }
} 
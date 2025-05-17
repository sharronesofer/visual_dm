using System.Collections.Generic;
using System.Threading;
using UnityEngine;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Manages cooldowns and resource (mana, stamina) for combat actors. Thread-safe.
    /// </summary>
    public class CombatResourceManager
    {
        private readonly Dictionary<GameObject, float> cooldowns = new Dictionary<GameObject, float>();
        private readonly Dictionary<GameObject, float> mana = new Dictionary<GameObject, float>();
        private readonly Dictionary<GameObject, float> stamina = new Dictionary<GameObject, float>();
        private readonly object lockObj = new object();

        public void SetCooldown(GameObject actor, float cooldown)
        {
            lock (lockObj)
            {
                cooldowns[actor] = cooldown;
            }
        }

        public float GetCooldown(GameObject actor)
        {
            lock (lockObj)
            {
                return cooldowns.TryGetValue(actor, out var value) ? value : 0f;
            }
        }

        public void SetMana(GameObject actor, float value)
        {
            lock (lockObj)
            {
                mana[actor] = value;
            }
        }

        public float GetMana(GameObject actor)
        {
            lock (lockObj)
            {
                return mana.TryGetValue(actor, out var value) ? value : 0f;
            }
        }

        public void SetStamina(GameObject actor, float value)
        {
            lock (lockObj)
            {
                stamina[actor] = value;
            }
        }

        public float GetStamina(GameObject actor)
        {
            lock (lockObj)
            {
                return stamina.TryGetValue(actor, out var value) ? value : 0f;
            }
        }

        public bool ConsumeMana(GameObject actor, float amount)
        {
            lock (lockObj)
            {
                if (GetMana(actor) >= amount)
                {
                    mana[actor] -= amount;
                    return true;
                }
                return false;
            }
        }

        public bool ConsumeStamina(GameObject actor, float amount)
        {
            lock (lockObj)
            {
                if (GetStamina(actor) >= amount)
                {
                    stamina[actor] -= amount;
                    return true;
                }
                return false;
            }
        }
    }
} 
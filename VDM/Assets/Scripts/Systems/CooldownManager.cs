using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Utilities
{
    public class CooldownManager
    {
        private readonly Dictionary<string, DateTime> _cooldowns = new();

        public void SetCooldown(string key, TimeSpan duration)
        {
            _cooldowns[key] = DateTime.UtcNow + duration;
        }

        public bool IsOnCooldown(string key)
        {
            if (_cooldowns.TryGetValue(key, out var until))
                return DateTime.UtcNow < until;
            return false;
        }

        public TimeSpan? GetRemaining(string key)
        {
            if (_cooldowns.TryGetValue(key, out var until))
            {
                var remaining = until - DateTime.UtcNow;
                return remaining > TimeSpan.Zero ? remaining : null;
            }
            return null;
        }

        public void ClearCooldown(string key)
        {
            _cooldowns.Remove(key);
        }

        public void ClearAll()
        {
            _cooldowns.Clear();
        }
    }
}
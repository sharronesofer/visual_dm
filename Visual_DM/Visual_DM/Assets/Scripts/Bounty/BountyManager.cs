using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Bounty
{
    public class BountyManager : MonoBehaviour
    {
        public static BountyManager Instance { get; private set; }

        [Serializable]
        public struct CrimeEvent
        {
            public CrimeTypeDefinition crimeType;
            public float timestamp;
            public string regionId;
            public bool isWitnessed;
        }

        private Dictionary<CrimeTypeDefinition, List<CrimeEvent>> playerCrimes = new();
        private float lastDecayTime;

        public event Action<float> OnBountyChanged;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            lastDecayTime = Time.time;
        }

        public void AddCrime(CrimeTypeDefinition crimeType, string regionId, bool isWitnessed)
        {
            if (!playerCrimes.ContainsKey(crimeType))
                playerCrimes[crimeType] = new List<CrimeEvent>();
            playerCrimes[crimeType].Add(new CrimeEvent
            {
                crimeType = crimeType,
                timestamp = Time.time,
                regionId = regionId,
                isWitnessed = isWitnessed
            });
            OnBountyChanged?.Invoke(GetCurrentBounty(regionId));
        }

        public float GetCurrentBounty(string regionId = null)
        {
            float total = 0f;
            foreach (var kvp in playerCrimes)
            {
                foreach (var crime in kvp.Value)
                {
                    if (regionId == null || crime.regionId == regionId)
                    {
                        float bounty = kvp.Key.baseBounty * kvp.Key.severityMultiplier;
                        if (kvp.Key.regionId == regionId)
                            bounty *= 1.2f; // Example: regional modifier
                        total += bounty;
                    }
                }
            }
            return total;
        }

        public void DecayBounties(float deltaTime)
        {
            foreach (var kvp in playerCrimes)
            {
                if (kvp.Key.severity == CrimeSeverity.Minor)
                {
                    kvp.Value.RemoveAll(crime => (Time.time - crime.timestamp) > (1f / kvp.Key.decayRate) * 60f);
                }
            }
            OnBountyChanged?.Invoke(GetCurrentBounty());
        }

        public string GetBountyStatus()
        {
            float bounty = GetCurrentBounty();
            if (bounty >= 1000f) return "Most Wanted";
            if (bounty >= 500f) return "Wanted";
            if (bounty > 0f) return "Minor Offender";
            return "No Bounty";
        }

        private void Update()
        {
            float now = Time.time;
            if (now - lastDecayTime > 60f)
            {
                DecayBounties(now - lastDecayTime);
                lastDecayTime = now;
            }
        }
    }
} 
using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Bounty
{
    public class WitnessManager : MonoBehaviour
    {
        public static WitnessManager Instance { get; private set; }
        private readonly List<WitnessNPCController> witnesses = new();

        public event Action<WitnessNPCController, CrimeTypeDefinition, Vector2, bool> OnCrimeReported;
        public event Action<WitnessNPCController, WitnessState> OnWitnessStateChanged;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        public void RegisterWitness(WitnessNPCController witness)
        {
            if (!witnesses.Contains(witness))
            {
                witnesses.Add(witness);
                witness.OnCrimeReported += HandleCrimeReported;
                witness.OnStateChanged += HandleWitnessStateChanged;
            }
        }

        public void UnregisterWitness(WitnessNPCController witness)
        {
            if (witnesses.Contains(witness))
            {
                witnesses.Remove(witness);
                witness.OnCrimeReported -= HandleCrimeReported;
                witness.OnStateChanged -= HandleWitnessStateChanged;
            }
        }

        public void BroadcastCrime(Vector2 crimePos, CrimeTypeDefinition crime, bool isLineOfSight)
        {
            foreach (var witness in witnesses)
            {
                witness.DetectCrime(crimePos, isLineOfSight);
            }
        }

        private void HandleCrimeReported(WitnessNPCController witness, CrimeTypeDefinition crime, Vector2 pos, bool isLineOfSight)
        {
            OnCrimeReported?.Invoke(witness, crime, pos, isLineOfSight);
            // Integrate with BountyManager
            if (crime != null && isLineOfSight)
            {
                BountyManager.Instance?.AddCrime(crime, null, true);
            }
        }

        private void HandleWitnessStateChanged(WitnessNPCController witness, WitnessState state)
        {
            OnWitnessStateChanged?.Invoke(witness, state);
        }

        public void CullWitnessesOutsideRange(Vector2 center, float range)
        {
            foreach (var witness in witnesses)
            {
                if (Vector2.Distance(center, witness.transform.position) > range)
                {
                    // Optionally disable or deprioritize witness
                }
            }
        }
    }
} 
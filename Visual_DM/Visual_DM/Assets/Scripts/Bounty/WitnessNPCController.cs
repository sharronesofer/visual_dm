using System;
using System.Collections;
using UnityEngine;

namespace VisualDM.Bounty
{
    public enum WitnessState { Idle, Investigating, Fleeing, Reporting, Intimidated, Eliminated }

    public class WitnessNPCController : MonoBehaviour
    {
        public float witnessRadius = 5f;
        public float memoryTimeout = 10f;
        public bool canReport = true;
        public bool isIntimidated = false;
        public bool isEliminated = false;
        public WitnessState state = WitnessState.Idle;

        private float lastCrimeTime = -1f;
        private Coroutine memoryCoroutine;

        public event Action<WitnessNPCController, WitnessState> OnStateChanged;
        public event Action<WitnessNPCController, CrimeTypeDefinition, Vector2, bool> OnCrimeReported;

        public void DetectCrime(Vector2 crimePos, bool isLineOfSight)
        {
            if (isEliminated || isIntimidated) return;
            float dist = Vector2.Distance(transform.position, crimePos);
            if (dist <= witnessRadius && isLineOfSight)
            {
                OnCrimeWitnessed(null, crimePos, isLineOfSight); // CrimeTypeDefinition to be set by caller
            }
        }

        public void OnCrimeWitnessed(CrimeTypeDefinition crime, Vector2 crimePos, bool isLineOfSight)
        {
            if (isEliminated || isIntimidated) return;
            state = WitnessState.Reporting;
            lastCrimeTime = Time.time;
            OnStateChanged?.Invoke(this, state);
            OnCrimeReported?.Invoke(this, crime, crimePos, isLineOfSight);
            if (memoryCoroutine != null) StopCoroutine(memoryCoroutine);
            memoryCoroutine = StartCoroutine(MemoryTimeoutRoutine());
        }

        public void PropagateReportToNearbyNPCs(float propagationRadius = 8f)
        {
            var allWitnesses = FindObjectsOfType<WitnessNPCController>();
            foreach (var npc in allWitnesses)
            {
                if (npc == this || npc.isEliminated || npc.isIntimidated) continue;
                float dist = Vector2.Distance(transform.position, npc.transform.position);
                if (dist <= propagationRadius)
                {
                    npc.OnCrimeWitnessed(null, transform.position, true); // CrimeTypeDefinition to be set by caller
                }
            }
        }

        public void Intimidate()
        {
            isIntimidated = true;
            state = WitnessState.Intimidated;
            OnStateChanged?.Invoke(this, state);
        }

        public void Eliminate()
        {
            isEliminated = true;
            state = WitnessState.Eliminated;
            OnStateChanged?.Invoke(this, state);
        }

        private IEnumerator MemoryTimeoutRoutine()
        {
            yield return new WaitForSeconds(memoryTimeout);
            state = WitnessState.Idle;
            OnStateChanged?.Invoke(this, state);
        }
    }
} 
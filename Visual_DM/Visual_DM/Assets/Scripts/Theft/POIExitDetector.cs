using System;
using UnityEngine;
using VisualDM.Bounty;

namespace VisualDM.Theft
{
    public class POIExitDetector : MonoBehaviour
    {
        public static POIExitDetector Instance { get; private set; }
        private POIManager poiManager;
        private float cooldown = 5f;
        private float lastExitTime = -100f;

        public event System.Action<string> OnPlayerExitPOI;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            poiManager = FindObjectOfType<POIManager>();
        }

        private void Update()
        {
            string currentPOI = poiManager.GetCurrentPOI();
            if (currentPOI == null && Time.time - lastExitTime > cooldown)
            {
                lastExitTime = Time.time;
                OnPlayerExitPOI?.Invoke(currentPOI);
                StolenStateManager.Instance?.Update(); // Trigger state reset logic
            }
        }
    }
} 
using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Bounty
{
    public class POIManager : MonoBehaviour
    {
        public static POIManager Instance { get; private set; }

        private List<POIDefinition> poiDefinitions = new();
        private List<PolygonCollider2D> poiColliders = new();
        private Dictionary<PolygonCollider2D, POIDefinition> colliderToPOI = new();
        private POIDefinition currentPOI;

        public event Action<POIDefinition> OnPlayerEnterPOI;
        public event Action<POIDefinition> OnPlayerExitPOI;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            LoadPOIs();
        }

        private void LoadPOIs()
        {
            poiDefinitions.Clear();
            poiColliders.Clear();
            colliderToPOI.Clear();
            var loaded = Resources.LoadAll<POIDefinition>("Bounty/POIs");
            foreach (var poi in loaded)
            {
                poiDefinitions.Add(poi);
                var go = new GameObject($"POI_{poi.poiName}_Collider");
                var collider = go.AddComponent<PolygonCollider2D>();
                collider.points = poi.boundaryPoints;
                collider.isTrigger = true;
                colliderToPOI[collider] = poi;
                poiColliders.Add(collider);
                go.hideFlags = HideFlags.HideAndDontSave;
            }
        }

        public bool IsPlayerInPOI(Vector2 playerPos, out POIDefinition poi)
        {
            foreach (var collider in poiColliders)
            {
                if (collider.OverlapPoint(playerPos))
                {
                    poi = colliderToPOI[collider];
                    return true;
                }
            }
            poi = null;
            return false;
        }

        public POIDefinition GetCurrentPOI(Vector2 playerPos)
        {
            IsPlayerInPOI(playerPos, out var poi);
            return poi;
        }

        public void UpdatePlayerPOI(Vector2 playerPos)
        {
            var prevPOI = currentPOI;
            var newPOI = GetCurrentPOI(playerPos);
            if (prevPOI != newPOI)
            {
                if (prevPOI != null)
                    OnPlayerExitPOI?.Invoke(prevPOI);
                if (newPOI != null)
                    OnPlayerEnterPOI?.Invoke(newPOI);
                currentPOI = newPOI;
            }
        }
    }
} 
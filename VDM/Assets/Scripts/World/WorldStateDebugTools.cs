using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.World
{
    public static class WorldStateDebugTools
    {
        // Log all global and regional world state properties to the Unity console
        public static void LogWorldState(WorldStateManager manager)
        {
            Debug.Log("[WorldState] Global Properties:");
            foreach (var kvp in manager.GetAllGlobalProperties())
            {
                Debug.Log($"  {kvp.Key}: {kvp.Value}");
            }
            Debug.Log("[WorldState] Regions:");
            foreach (var region in manager.GetAllRegions())
            {
                Debug.Log($"  Region: {region.Region.Name} ({region.Region.RegionId})");
                foreach (var prop in region.GetAllRegionalProperties())
                {
                    Debug.Log($"    {prop.Key}: {prop.Value}");
                }
            }
        }

        // Simulate a world state change (for testing arc responses)
        public static void SimulateWorldStateChange<T>(WorldStateManager manager, string key, T value)
        {
            Debug.Log($"[WorldState] Simulating change: {key} => {value}");
            manager.SetProperty(key, value);
        }

        // Simple runtime UI overlay for key world state properties
        private static bool _showOverlay = false;
        private static string _propertyKey = "Population";
        private static string _propertyValue = "100";

        public static void DrawOverlay(WorldStateManager manager)
        {
            if (!_showOverlay) return;
            GUI.Box(new Rect(10, 10, 300, 180), "World State Debug");
            GUILayout.BeginArea(new Rect(20, 40, 280, 140));
            GUILayout.Label("Global Properties:");
            foreach (var kvp in manager.GetAllGlobalProperties())
            {
                GUILayout.Label($"{kvp.Key}: {kvp.Value}");
            }
            GUILayout.Space(10);
            GUILayout.Label("Set Property:");
            _propertyKey = GUILayout.TextField(_propertyKey);
            _propertyValue = GUILayout.TextField(_propertyValue);
            if (GUILayout.Button("Set Int Property"))
            {
                if (int.TryParse(_propertyValue, out int intVal))
                {
                    manager.SetProperty(_propertyKey, intVal);
                }
            }
            if (GUILayout.Button("Set String Property"))
            {
                manager.SetProperty(_propertyKey, _propertyValue);
            }
            GUILayout.EndArea();
        }

        // Toggle overlay (callable from code or via hotkey)
        public static void ToggleOverlay()
        {
            _showOverlay = !_showOverlay;
        }
    }

    // Example MonoBehaviour to hook overlay into Unity runtime
    public class WorldStateDebugOverlay : MonoBehaviour
    {
        public WorldStateManager Manager;
        void OnGUI()
        {
            if (Manager != null)
                WorldStateDebugTools.DrawOverlay(Manager);
        }
        void Update()
        {
            if (Core.GetKeyDown(KeyCode.F9))
            {
                WorldStateDebugTools.ToggleOverlay();
            }
        }
    }
}
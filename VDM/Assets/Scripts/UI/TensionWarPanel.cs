using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace VDM.Systems.War
{
    /// <summary>
    /// Runtime UI panel for visualizing faction tensions and active wars.
    /// </summary>
    public class TensionWarPanel : MonoBehaviour
    {
        public RectTransform TensionListRoot;
        public RectTransform WarListRoot;
        public GameObject TensionEntryPrefab;
        public GameObject WarEntryPrefab;

        private readonly List<GameObject> _tensionEntries = new();
        private readonly List<GameObject> _warEntries = new();

        /// <summary>
        /// Update the tension list UI.
        /// </summary>
        public void UpdateTensionList(IEnumerable<(string, string, float)> tensions)
        {
            foreach (var go in _tensionEntries) Destroy(go);
            _tensionEntries.Clear();
            foreach (var (a, b, value) in tensions)
            {
                var entry = Instantiate(TensionEntryPrefab, TensionListRoot);
                entry.GetComponentInChildren<Text>().text = $"{a} vs {b}: {value:F1}";
                var slider = entry.GetComponentInChildren<Slider>();
                if (slider) slider.value = value / 100f;
                _tensionEntries.Add(entry);
            }
        }

        /// <summary>
        /// Update the war list UI.
        /// </summary>
        public void UpdateWarList(IEnumerable<(string, string, float, float, string)> wars)
        {
            foreach (var go in _warEntries) Destroy(go);
            _warEntries.Clear();
            foreach (var (a, b, exA, exB, lastEvent) in wars)
            {
                var entry = Instantiate(WarEntryPrefab, WarListRoot);
                entry.GetComponentInChildren<Text>().text = $"{a} vs {b} | Exhaustion: {exA:F1}/{exB:F1}\nLast: {lastEvent}";
                _warEntries.Add(entry);
            }
        }
    }
} 
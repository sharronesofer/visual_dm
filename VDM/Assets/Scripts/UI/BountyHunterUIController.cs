using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using VisualDM.UI;

namespace VisualDM.UI
{
    public class BountyHunterUIController : MonoBehaviour
    {
        private RectTransform panel;
        private Dictionary<BountyHunterNPC, GameObject> hunterEntries = new Dictionary<BountyHunterNPC, GameObject>();

        void Awake()
        {
            CreatePanel();
        }

        private void CreatePanel()
        {
            GameObject panelGO = new GameObject("BountyHunterStatusPanel");
            panel = panelGO.AddComponent<RectTransform>();
            panel.SetParent(UIManager.Instance.transform, false);
            // TODO: Style panel, set position, add background
        }

        public void AddHunter(BountyHunterNPC hunter)
        {
            GameObject entry = new GameObject($"HunterEntry_{hunter.GetInstanceID()}");
            entry.transform.SetParent(panel, false);
            Text text = entry.AddComponent<Text>();
            text.text = $"{hunter.Archetype} Hunter (Lvl {hunter.Level}) - {(hunter.IsElite ? "Elite" : "Standard")}";
            // TODO: Style text, add icons
            hunterEntries[hunter] = entry;
        }

        public void RemoveHunter(BountyHunterNPC hunter)
        {
            if (hunterEntries.TryGetValue(hunter, out var entry))
            {
                Destroy(entry);
                hunterEntries.Remove(hunter);
            }
        }
    }
} 
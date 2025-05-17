using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.ChainActionSystem;
using VisualDM.Systems.EventSystem;

namespace VisualDM.Systems.ChainActionSystem
{
    public class ChainActionUI : MonoBehaviour
    {
        private class ChainVisual
        {
            public GameObject Root;
            public List<GameObject> StepSprites = new();
            public float LastUpdateTime;
        }

        private readonly Dictionary<GameObject, ChainVisual> _activeVisuals = new();
        public Sprite StepSprite;
        public Sprite CompletedSprite;
        public Sprite InterruptedSprite;
        public Vector2 StartPosition = new(0, 0);
        public float StepSpacing = 1.2f;

        private void Awake()
        {
            EventBus.Instance.Subscribe<ChainStartedEvent>(OnChainStarted);
            EventBus.Instance.Subscribe<ChainEndedEvent>(OnChainEnded);
            EventBus.Instance.Subscribe<ChainInterruptedEvent>(OnChainInterrupted);
        }

        private void OnDestroy()
        {
            EventBus.Instance.Unsubscribe<ChainStartedEvent>(OnChainStarted);
            EventBus.Instance.Unsubscribe<ChainEndedEvent>(OnChainEnded);
            EventBus.Instance.Unsubscribe<ChainInterruptedEvent>(OnChainInterrupted);
        }

        private void OnChainStarted(ChainStartedEvent evt)
        {
            if (_activeVisuals.ContainsKey(evt.Owner)) return;
            var visual = new ChainVisual { Root = new GameObject($"ChainUI_{evt.Owner.name}") };
            visual.Root.transform.position = StartPosition;
            for (int i = 0; i < evt.Definition.Links.Count; i++)
            {
                var go = new GameObject($"Step_{i}");
                var sr = go.AddComponent<SpriteRenderer>();
                sr.sprite = StepSprite;
                go.transform.SetParent(visual.Root.transform);
                go.transform.localPosition = new Vector3(i * StepSpacing, 0, 0);
                visual.StepSprites.Add(go);
            }
            _activeVisuals[evt.Owner] = visual;
        }

        private void OnChainEnded(ChainEndedEvent evt)
        {
            if (_activeVisuals.TryGetValue(evt.Owner, out var visual))
            {
                for (int i = 0; i < visual.StepSprites.Count; i++)
                {
                    var sr = visual.StepSprites[i].GetComponent<SpriteRenderer>();
                    sr.sprite = evt.Interrupted ? InterruptedSprite : CompletedSprite;
                }
                Destroy(visual.Root, 1.5f);
                _activeVisuals.Remove(evt.Owner);
            }
        }

        private void OnChainInterrupted(ChainInterruptedEvent evt)
        {
            if (_activeVisuals.TryGetValue(evt.Owner, out var visual))
            {
                foreach (var go in visual.StepSprites)
                {
                    var sr = go.GetComponent<SpriteRenderer>();
                    sr.sprite = InterruptedSprite;
                }
            }
        }

        // Optionally, update progress in real time (e.g., highlight current step)
        private void Update()
        {
            foreach (var kvp in _activeVisuals)
            {
                var owner = kvp.Key;
                var visual = kvp.Value;
                // For demo: pulse the current step
                // (In a real system, get current step from ChainActionSystem)
                // This is a placeholder for future integration
            }
        }
    }
} 
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Combat
{
    /// <summary>
    /// Handles runtime visualization of active combat effects.
    /// </summary>
    public class EffectVisualizer : MonoBehaviour
    {
        private readonly List<GameObject> _activeIcons = new();
        private ObjectPool<GameObject> _iconPool;
        [SerializeField] private GameObject _iconPrefab; // Assignable at runtime

        private void Awake()
        {
            _iconPool = gameObject.AddComponent<ObjectPool<GameObject>>();
            if (_iconPrefab != null)
                _iconPool.Initialize(_iconPrefab, 8, this.transform);
        }

        /// <summary>
        /// Displays effect icons above the given combatant using pooled objects.
        /// </summary>
        public void ShowEffects(ICombatant combatant, IReadOnlyList<CombatEffect> effects)
        {
            ClearEffects();
            Vector3 basePos = GetCombatantWorldPosition(combatant);
            float yOffset = 1.5f;
            float xOffset = 0f;
            float spacing = 0.7f;
            foreach (var effect in effects)
            {
                var icon = _iconPool.Get();
                icon.transform.position = basePos + new Vector3(xOffset, yOffset, 0);
                var sr = icon.GetComponent<SpriteRenderer>();
                if (sr == null) sr = icon.AddComponent<SpriteRenderer>();
                sr.sprite = GetEffectSprite(effect.Type);
                sr.color = GetEffectColor(effect.Type);
                icon.SetActive(true);
                _activeIcons.Add(icon);
                xOffset += spacing;
            }
        }

        /// <summary>
        /// Releases all effect icons back to the pool.
        /// </summary>
        public void ClearEffects()
        {
            foreach (var icon in _activeIcons)
            {
                if (icon != null)
                    _iconPool.Release(icon);
            }
            _activeIcons.Clear();
        }

        /// <summary>
        /// Creates a runtime icon for the given effect (SpriteRenderer, runtime-generated).
        /// </summary>
        private GameObject CreateEffectIcon(CombatEffect effect)
        {
            var go = new GameObject($"EffectIcon_{effect.GetType().Name}");
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = GetEffectSprite(effect.Type);
            sr.sortingOrder = 100;
            sr.color = GetEffectColor(effect.Type);
            go.transform.localScale = Vector3.one * 0.5f;
            return go;
        }

        /// <summary>
        /// Returns a sprite for the given effect type (placeholder: colored square).
        /// </summary>
        private Sprite GetEffectSprite(EffectType type)
        {
            // Placeholder: create a 32x32 texture and convert to sprite
            Texture2D tex = new Texture2D(32, 32);
            Color c = GetEffectColor(type);
            for (int x = 0; x < 32; x++)
                for (int y = 0; y < 32; y++)
                    tex.SetPixel(x, y, c);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, 32, 32), new Vector2(0.5f, 0.5f));
        }

        /// <summary>
        /// Returns a color for the given effect type.
        /// </summary>
        private Color GetEffectColor(EffectType type)
        {
            return type switch
            {
                EffectType.Buff => Color.green,
                EffectType.Debuff => Color.red,
                EffectType.Status => Color.yellow,
                EffectType.Environmental => Color.cyan,
                _ => Color.white
            };
        }

        /// <summary>
        /// Gets the world position of the combatant (requires implementation based on your system).
        /// </summary>
        private Vector3 GetCombatantWorldPosition(ICombatant combatant)
        {
            // Placeholder: expects combatant to have a Transform property or similar
            if (combatant is MonoBehaviour mb)
                return mb.transform.position;
            // Otherwise, return origin
            return Vector3.zero;
        }
    }
} 
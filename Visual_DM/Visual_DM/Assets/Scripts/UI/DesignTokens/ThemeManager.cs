using System;
using UnityEngine;

namespace VisualDM.UI.DesignTokens
{
    public enum ThemeType { Light, Dark }

    public class ThemeManager : MonoBehaviour
    {
        public static ThemeManager Instance { get; private set; }
        public ThemeType CurrentTheme { get; private set; } = ThemeType.Light;
        public static event Action<ThemeType> OnThemeChanged;

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

        public void SetTheme(ThemeType theme)
        {
            if (CurrentTheme != theme)
            {
                CurrentTheme = theme;
                OnThemeChanged?.Invoke(theme);
            }
        }
    }

    // Example usage:
    // ThemeManager.Instance.SetTheme(ThemeType.Dark);
    // Subscribe to ThemeManager.OnThemeChanged to update UI elements at runtime.
} 
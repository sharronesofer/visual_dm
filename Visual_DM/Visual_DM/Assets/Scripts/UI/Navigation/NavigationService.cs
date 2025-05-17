using UnityEngine;
using System;
using System.Collections.Generic;

namespace VisualDM.UI.Navigation
{
    /// <summary>
    /// Manages navigation state, provides hooks for components, and persists state.
    /// </summary>
    public class NavigationService : MonoBehaviour
    {
        public static NavigationService Instance { get; private set; }
        public event Action<string> OnNavigationChanged;
        private string currentSection = "Home";
        private const string NavKey = "CurrentNavSection";

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(this);
                return;
            }
            Instance = this;
            currentSection = PlayerPrefs.GetString(NavKey, "Home");
        }

        public void NavigateTo(string section)
        {
            if (currentSection != section)
            {
                currentSection = section;
                PlayerPrefs.SetString(NavKey, section);
                PlayerPrefs.Save();
                OnNavigationChanged?.Invoke(section);
            }
        }

        public string GetCurrentSection()
        {
            return currentSection;
        }
    }
} 
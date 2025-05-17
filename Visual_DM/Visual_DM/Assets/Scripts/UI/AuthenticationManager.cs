using UnityEngine;
using System;

namespace VisualDM.UI
{
    /// <summary>
    /// Manages authentication and onboarding flows, including login, registration, password reset, and onboarding sequence.
    /// </summary>
    public class AuthenticationManager : MonoBehaviour
    {
        private enum AuthState { Login, Register, PasswordReset, Onboarding, Authenticated }
        private AuthState currentState = AuthState.Login;

        private GameObject currentPanel;
        private Transform uiRoot;

        private const string OnboardingCompleteKey = "OnboardingComplete";

        void Awake()
        {
            uiRoot = this.transform;
            ShowLogin();
        }

        private void ClearPanel()
        {
            if (currentPanel != null)
                Destroy(currentPanel);
        }

        public void ShowLogin()
        {
            ClearPanel();
            currentPanel = new GameObject("LoginPanel");
            currentPanel.transform.SetParent(uiRoot);
            var panel = currentPanel.AddComponent<LoginPanel>();
            panel.Initialize();
            // TODO: Wire up login logic, switch to onboarding or Authenticated on success
            currentState = AuthState.Login;
        }

        public void ShowRegister()
        {
            ClearPanel();
            currentPanel = new GameObject("RegistrationPanel");
            currentPanel.transform.SetParent(uiRoot);
            var panel = currentPanel.AddComponent<RegistrationPanel>();
            panel.Initialize();
            // TODO: Wire up registration logic, switch to onboarding on success
            currentState = AuthState.Register;
        }

        public void ShowPasswordReset()
        {
            ClearPanel();
            currentPanel = new GameObject("PasswordResetPanel");
            currentPanel.transform.SetParent(uiRoot);
            var panel = currentPanel.AddComponent<PasswordResetPanel>();
            panel.Initialize();
            // TODO: Wire up password reset logic, return to login on success
            currentState = AuthState.PasswordReset;
        }

        public void ShowOnboarding()
        {
            ClearPanel();
            currentPanel = new GameObject("OnboardingPanel");
            currentPanel.transform.SetParent(uiRoot);
            var panel = currentPanel.AddComponent<OnboardingPanel>();
            panel.Initialize();
            // TODO: Wire up onboarding completion logic
            currentState = AuthState.Onboarding;
        }

        public void CompleteOnboarding()
        {
            PlayerPrefs.SetInt(OnboardingCompleteKey, 1);
            PlayerPrefs.Save();
            // TODO: Transition to Authenticated state (main app UI)
            currentState = AuthState.Authenticated;
        }

        public bool IsOnboardingComplete()
        {
            return PlayerPrefs.GetInt(OnboardingCompleteKey, 0) == 1;
        }
    }
} 
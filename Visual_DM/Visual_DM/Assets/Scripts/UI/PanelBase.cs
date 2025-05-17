using UnityEngine;

namespace VisualDM.UI
{
    /// <summary>
    /// Base class for all runtime-generated UI panels. Handles show/hide and initialization logic.
    /// </summary>
    public abstract class PanelBase : MonoBehaviour
    {
        public virtual void Show()
        {
            gameObject.SetActive(true);
        }

        public virtual void Hide()
        {
            gameObject.SetActive(false);
        }

        public virtual void Initialize(params object[] args) { }

        protected virtual void OnEnable()
        {
            if (UIManager.Instance != null)
                UIManager.Instance.OnBreakpointChanged += OnBreakpointChanged;
            OnBreakpointChanged(UIManager.Instance.CurrentBreakpoint);
        }

        protected virtual void OnDisable()
        {
            if (UIManager.Instance != null)
                UIManager.Instance.OnBreakpointChanged -= OnBreakpointChanged;
        }

        /// <summary>
        /// Called when the UI breakpoint (screen size category) changes. Override in derived panels.
        /// </summary>
        public virtual void OnBreakpointChanged(UIManager.Breakpoint breakpoint) { }

        /// <summary>
        /// The required role to view this panel. Override in derived panels for protected UI.
        /// </summary>
        public virtual string RequiredRole => null; // null = visible for all

        /// <summary>
        /// Returns true if the given role is allowed to view this panel.
        /// </summary>
        public virtual bool VisibleForRole(string userRole)
        {
            return RequiredRole == null || userRole == RequiredRole;
        }

        /// <summary>
        /// Show or hide the panel based on the current user role.
        /// </summary>
        public void SetVisibleForRole(string userRole)
        {
            if (VisibleForRole(userRole)) Show();
            else Hide();
        }

        /// <summary>
        /// Called when an error occurs in the panel. Override to display custom error UI.
        /// </summary>
        public virtual void OnPanelError(string userMessage, string context)
        {
            // Default: log error. Derived panels can override to show error UI.
            Debug.LogError($"Panel error in {context}: {userMessage}");
        }

        /*
         * Error Handling Pattern for UI Panels:
         * - Wrap critical operations in try-catch blocks.
         * - Use ErrorHandlingService.Instance.LogException for logging.
         * - Call OnPanelError to display user-friendly error messages in the UI.
         * - Override OnPanelError in derived panels for custom error display.
         * - See PowerAnalysisDashboard and MonitoringDashboard for examples.
         */
    }
} 
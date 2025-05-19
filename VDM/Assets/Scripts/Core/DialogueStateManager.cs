using System;

namespace VisualDM.Core
{
    /// <summary>
    /// Represents the state of the dialogue system.
    /// </summary>
    public enum DialogueState
    {
        /// <summary>
        /// No dialogue is active.
        /// </summary>
        Idle,
        
        /// <summary>
        /// Dialogue is pending (loading).
        /// </summary>
        Pending,
        
        /// <summary>
        /// Dialogue has been received and is ready to display.
        /// </summary>
        Received,
        
        /// <summary>
        /// An error occurred during dialogue processing.
        /// </summary>
        Error
    }

    /// <summary>
    /// Manages dialogue state and notifies listeners of state changes.
    /// Tracks the current state and provides access to the latest dialogue text and error messages.
    /// </summary>
    public static class DialogueStateManager
    {
        private static DialogueState currentState = DialogueState.Idle;
        private static string latestText = "";
        private static string errorMessage = "";
        
        /// <summary>
        /// Event raised when the dialogue state changes.
        /// </summary>
        public static event Action<DialogueState, string, string> OnStateChanged;

        /// <summary>
        /// Sets the dialogue state and notifies listeners.
        /// </summary>
        /// <param name="state">The new dialogue state.</param>
        /// <param name="text">The dialogue text.</param>
        /// <param name="error">The error message, if any.</param>
        public static void SetState(DialogueState state, string text = "", string error = "")
        {
            currentState = state;
            latestText = text;
            errorMessage = error;
            OnStateChanged?.Invoke(currentState, latestText, errorMessage);
        }

        /// <summary>
        /// Gets the current dialogue state.
        /// </summary>
        /// <returns>The current dialogue state.</returns>
        public static DialogueState GetState() => currentState;
        
        /// <summary>
        /// Gets the latest dialogue text.
        /// </summary>
        /// <returns>The latest dialogue text.</returns>
        public static string GetLatestText() => latestText;
        
        /// <summary>
        /// Gets the current error message, if any.
        /// </summary>
        /// <returns>The current error message.</returns>
        public static string GetErrorMessage() => errorMessage;
    }
} 
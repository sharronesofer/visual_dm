using System;

namespace VisualDM.Core
{
    public enum DialogueState
    {
        Idle,
        Pending,
        Received,
        Error
    }

    public static class DialogueStateManager
    {
        private static DialogueState currentState = DialogueState.Idle;
        private static string latestText = "";
        private static string errorMessage = "";
        public static event Action<DialogueState, string, string> OnStateChanged;

        public static void SetState(DialogueState state, string text = "", string error = "")
        {
            currentState = state;
            latestText = text;
            errorMessage = error;
            OnStateChanged?.Invoke(currentState, latestText, errorMessage);
        }

        public static DialogueState GetState() => currentState;
        public static string GetLatestText() => latestText;
        public static string GetErrorMessage() => errorMessage;
    }
} 
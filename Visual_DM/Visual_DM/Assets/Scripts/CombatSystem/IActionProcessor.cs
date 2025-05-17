namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Interface for processing and resolving combat actions, for Action System integration.
    /// </summary>
    public interface IActionProcessor
    {
        /// <summary>
        /// Processes the action logic.
        /// </summary>
        void ProcessAction();

        /// <summary>
        /// Resolves the action outcome.
        /// </summary>
        void ResolveAction();
    }
} 
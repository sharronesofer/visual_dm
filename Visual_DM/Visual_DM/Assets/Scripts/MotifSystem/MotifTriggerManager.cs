using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace VisualDM.MotifSystem
{
    /// <summary>
    /// Handles registration, evaluation, and execution of motif triggers. Integrates with event system.
    /// </summary>
    public class MotifTriggerManager
    {
        public class MotifTrigger
        {
            public string TriggerType;
            public Func<Motif, bool> Condition;
            public Action<Motif> Action;
            public string Description;
        }

        private readonly List<MotifTrigger> _triggers = new();

        /// <summary>
        /// Registers a motif trigger.
        /// </summary>
        /// <param name="trigger">The motif trigger to register.</param>
        public void RegisterTrigger(MotifTrigger trigger)
        {
            if (trigger == null) return;
            _triggers.Add(trigger);
        }

        /// <summary>
        /// Unregisters a motif trigger.
        /// </summary>
        /// <param name="trigger">The motif trigger to unregister.</param>
        public void UnregisterTrigger(MotifTrigger trigger)
        {
            if (trigger == null) return;
            _triggers.Remove(trigger);
        }

        private void HandleError(Exception ex, string context)
        {
            VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, $"MotifTriggerManager error in {context}", context);
            VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
        }

        /// <summary>
        /// Evaluates and executes triggers for a motif. Skips invalid motifs and logs errors.
        /// </summary>
        /// <param name="motif">The motif to evaluate triggers for.</param>
        /// <param name="actor">The actor performing the evaluation.</param>
        /// <param name="context">The context for evaluation.</param>
        public void EvaluateAndExecute(Motif motif, string actor = null, string context = null)
        {
            if (!MotifValidator.ValidateMotif(motif))
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError($"MotifTriggerManager: Invalid motif in trigger evaluation: {motif?.Theme ?? "<null>"}", "MotifTriggerManager.EvaluateAndExecute");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return;
            }
            foreach (var trigger in _triggers)
            {
                try
                {
                    if (trigger.Condition(motif))
                    {
                        trigger.Action(motif);
                        MotifEventDispatcher.PublishTriggered(new MotifTriggeredEvent(
                            motif,
                            trigger.TriggerType,
                            actor,
                            context,
                            DateTime.UtcNow
                        ));
                    }
                }
                catch (Exception ex)
                {
                    HandleError(ex, $"EvaluateAndExecute trigger {trigger?.TriggerType ?? "<null>"}");
                }
            }
        }

        public async Task EvaluateAndExecuteAsync(Motif motif, string actor = null, string context = null)
        {
            foreach (var trigger in _triggers)
            {
                try
                {
                    if (trigger.Condition(motif))
                    {
                        trigger.Action(motif);
                        await MotifEventDispatcher.PublishTriggeredAsync(new MotifTriggeredEvent(
                            motif,
                            trigger.TriggerType,
                            actor,
                            context,
                            DateTime.UtcNow
                        ));
                    }
                }
                catch (Exception ex)
                {
                    HandleError(ex, $"EvaluateAndExecuteAsync trigger: {trigger?.TriggerType}");
                }
            }
        }
    }
}
using System;
using UnityEngine;
using VisualDM.CombatSystem;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Manages the multi-stage action resolution process for turn-based actions.
    /// </summary>
    public class ActionResolutionPipeline
    {
        public IPreProcessStrategy PreProcessStrategy { get; set; }
        public IExecutionStrategy ExecutionStrategy { get; set; }
        public IPostProcessStrategy PostProcessStrategy { get; set; }

        public ActionResolutionPipeline(IPreProcessStrategy pre, IExecutionStrategy exec, IPostProcessStrategy post)
        {
            PreProcessStrategy = pre;
            ExecutionStrategy = exec;
            PostProcessStrategy = post;
        }

        /// <summary>
        /// Runs the full action resolution pipeline for a given action and entity state.
        /// </summary>
        public bool Run(ActionRequest request, CharacterState state)
        {
            // Validation
            if (!PreProcessStrategy.PreProcess(request, state))
            {
                Debug.Log($"[ActionResolutionPipeline] Validation failed for action {request.ActionType}");
                return false;
            }
            // Execution
            ExecutionStrategy.Execute(request, state);
            // Post-processing
            PostProcessStrategy.PostProcess(request, state);
            // Optionally: Broadcast event for UI/animation
            EventBus.Instance.Publish(new ActionResolvedEvent(request, state));
            return true;
        }
    }

    /// <summary>
    /// Event for when an action has been fully resolved.
    /// </summary>
    public class ActionResolvedEvent
    {
        public ActionRequest Request;
        public CharacterState State;
        public ActionResolvedEvent(ActionRequest request, CharacterState state)
        {
            Request = request;
            State = state;
        }
    }
} 
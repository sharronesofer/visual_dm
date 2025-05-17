using System;
using UnityEngine;
using VisualDM.Feedback;
using VisualDM.CombatSystem;

public interface IPreProcessStrategy { bool PreProcess(ActionRequest request, CharacterState state); }
public interface IExecutionStrategy { void Execute(ActionRequest request, CharacterState state); }
public interface IPostProcessStrategy { void PostProcess(ActionRequest request, CharacterState state); }

public class ActionPipeline
{
    public IPreProcessStrategy PreProcessStrategy { get; set; }
    public IExecutionStrategy ExecutionStrategy { get; set; }
    public IPostProcessStrategy PostProcessStrategy { get; set; }

    public ActionPipeline(IPreProcessStrategy pre, IExecutionStrategy exec, IPostProcessStrategy post)
    {
        PreProcessStrategy = pre;
        ExecutionStrategy = exec;
        PostProcessStrategy = post;
    }

    public bool Run(ActionRequest request, CharacterState state)
    {
        float startTime = Time.realtimeSinceStartup;
        // Pre-processing
        if (!PreProcessStrategy.PreProcess(request, state))
        {
            Debug.Log($"PreProcess failed for action {request.ActionType}");
            // Report error for failed pre-processing
            ErrorDetector.Instance.ReportError(ActionErrorType.StateConflict, null, $"PreProcess failed for action {request.ActionType}", request);
            return false;
        }
        // Execution
        ExecutionStrategy.Execute(request, state);
        // Post-processing
        PostProcessStrategy.PostProcess(request, state);
        float elapsed = (Time.realtimeSinceStartup - startTime) * 1000f;
        Debug.Log($"Action {request.ActionType} pipeline completed in {elapsed:F2} ms");
        return true;
    }
}

// Example strategies (expand for real use)
public class DefaultPreProcess : IPreProcessStrategy
{
    private InputValidator _validator = new InputValidator();
    public bool PreProcess(ActionRequest request, CharacterState state)
    {
        // Validate input, check resources, prepare animation
        return _validator.IsValid(request, state);
    }
}

public class DefaultExecution : IExecutionStrategy
{
    public void Execute(ActionRequest request, CharacterState state)
    {
        // Perform action, apply effects, trigger feedback
        Debug.Log($"Executing action: {request.ActionType}");
        // Feedback: Action executed
        FeedbackManager.Instance?.TriggerFeedback(
            (ActionType)request.ActionType,
            5,
            state != null && state is MonoBehaviour mb ? (Vector2)mb.transform.position : Vector2.zero,
            new FeedbackContext { ExtraInfo = $"ActionPipeline_{request.ActionType}" }
        );
        // TODO: Animation, VFX, SFX, etc.
    }
}

public class DefaultPostProcess : IPostProcessStrategy
{
    public void PostProcess(ActionRequest request, CharacterState state)
    {
        // Update game state, reset cooldowns, trigger follow-ups
        Debug.Log($"Post-processing action: {request.ActionType}");
        // TODO: Update state, cooldowns, etc.
    }
} 
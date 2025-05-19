using System;
using UnityEngine;
using VisualDM.Systems;
using VisualDM.CombatSystem;

// Reference: See /docs/bible_qa.md for design rationale and requirements.
// This file is part of the Action Response Time System.
// Modular pipeline: PreProcess, Execute, PostProcess. Thread-safe for concurrent action execution.

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
        // Start performance timing for this action
        string actionKey = $"{request.ActionType}_{request.RequestId}";
        ActionPerformanceMonitor.Instance.StartTiming(actionKey);
        float startTime = Time.realtimeSinceStartup;
        // Pre-processing
        if (!PreProcessStrategy.PreProcess(request, state))
        {
            Debug.Log($"PreProcess failed for action {request.ActionType}");
            // Report error for failed pre-processing
            ErrorDetector.Instance.ReportError(ActionErrorType.StateConflict, null, $"PreProcess failed for action {request.ActionType}", request);
            // Stop timing on failure
            ActionPerformanceMonitor.Instance.StopTiming(actionKey, request.ActionType);
            return false;
        }
        // Execution
        ExecutionStrategy.Execute(request, state);
        // Post-processing
        PostProcessStrategy.PostProcess(request, state);
        float elapsed = (Time.realtimeSinceStartup - startTime) * 1000f;
        Debug.Log($"Action {request.ActionType} pipeline completed in {elapsed:F2} ms");
        // Stop performance timing for this action
        ActionPerformanceMonitor.Instance.StopTiming(actionKey, request.ActionType);
        return true;
    }
}

// Example strategies (expand for real use)
public class DefaultPreProcess : IPreProcessStrategy
{
    private CoreValidator _validator = new CoreValidator();
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
        // Systems: Action executed
        SystemsManager.Instance?.TriggerSystems(
            (ActionType)request.ActionType,
            5,
            state != null && state is MonoBehaviour mb ? (Vector2)mb.transform.position : Vector2.zero,
            new SystemsContext { ExtraInfo = $"ActionPipeline_{request.ActionType}" }
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

public class ChainActionExecutionStrategy : IExecutionStrategy
{
    public void Execute(ActionRequest request, CharacterState state)
    {
        // Extract chain context from request.Context
        if (request.Context is VisualDM.Systems.ChainActionSystem.ChainActionSystem.ChainActionContext chainCtx)
        {
            var chainSystem = VisualDM.Systems.ChainActionSystem.ChainActionSystem.Instance;
            if (chainSystem == null)
            {
                Debug.LogError("ChainActionSystem.Instance not found. Cannot execute chain action.");
                return;
            }
            // Start or resume the chain as needed
            chainSystem.StartChain(chainCtx.Definition, chainCtx.Context.Owner);
        }
        else
        {
            Debug.LogError("Invalid context for ChainActionExecutionStrategy. Context must be ChainActionContext.");
        }
    }
} 
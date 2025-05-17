using System;
using UnityEngine;

namespace VisualDM.CombatSystem
{
    public interface IRecoveryStrategy
    {
        void Recover(CombatActionHandler handler, ActionErrorType errorType, object context = null);
    }

    public class InvalidTargetRecovery : IRecoveryStrategy
    {
        public void Recover(CombatActionHandler handler, ActionErrorType errorType, object context = null)
        {
            // Suggest alternative targets (stub)
            Debug.Log("[Recovery] Invalid target. Suggesting alternative targets.");
            // TODO: Implement actual target suggestion logic
        }
    }

    public class InsufficientResourceRecovery : IRecoveryStrategy
    {
        public void Recover(CombatActionHandler handler, ActionErrorType errorType, object context = null)
        {
            // Suggest resource gathering (stub)
            Debug.Log("[Recovery] Insufficient resources. Suggesting resource gathering.");
            // TODO: Implement actual resource suggestion logic
        }
    }

    public class PathBlockedRecovery : IRecoveryStrategy
    {
        public void Recover(CombatActionHandler handler, ActionErrorType errorType, object context = null)
        {
            // Find alternative paths (stub)
            Debug.Log("[Recovery] Path blocked. Finding alternative path.");
            // TODO: Implement actual pathfinding logic
        }
    }

    public class RecoveryStrategyManager
    {
        private static RecoveryStrategyManager _instance;
        public static RecoveryStrategyManager Instance => _instance ?? (_instance = new RecoveryStrategyManager());

        private readonly IRecoveryStrategy _invalidTarget = new InvalidTargetRecovery();
        private readonly IRecoveryStrategy _insufficientResource = new InsufficientResourceRecovery();
        private readonly IRecoveryStrategy _pathBlocked = new PathBlockedRecovery();

        public void Recover(CombatActionHandler handler, ActionErrorType errorType, object context = null)
        {
            switch (errorType)
            {
                case ActionErrorType.InvalidTarget:
                    _invalidTarget.Recover(handler, errorType, context);
                    break;
                case ActionErrorType.InsufficientResources:
                    _insufficientResource.Recover(handler, errorType, context);
                    break;
                case ActionErrorType.StateConflict:
                    // Could be path blocked or other state issues
                    _pathBlocked.Recover(handler, errorType, context);
                    break;
                default:
                    Debug.Log("[Recovery] No recovery strategy for error type: " + errorType);
                    break;
            }
        }
    }
} 
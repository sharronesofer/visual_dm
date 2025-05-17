using System;

public class PriorityResolver
{
    // Returns a priority integer (higher = higher priority)
    public int GetPriority(ActionRequest request, CharacterState state)
    {
        // Example: Special > Basic > Contextual, can be extended
        switch (request.ActionType)
        {
            case ActionType.SpecialAbility:
                return 100;
            case ActionType.BasicAttack:
                return 50;
            case ActionType.ContextualAction:
                return 10;
            default:
                return 0;
        }
    }

    // For simultaneous actions, returns the one with highest priority
    public ActionRequest Resolve(ActionRequest[] requests, CharacterState state)
    {
        ActionRequest best = null;
        int bestPriority = int.MinValue;
        foreach (var req in requests)
        {
            int p = GetPriority(req, state);
            if (p > bestPriority)
            {
                best = req;
                bestPriority = p;
            }
        }
        return best;
    }
} 
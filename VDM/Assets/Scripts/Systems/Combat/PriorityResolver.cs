using System;

// Reference: See /docs/bible_qa.md for design rationale and requirements.
// This file is part of the Action Response Time System.
// Prioritization logic is extensible for new action types and contextual rules.

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
            case ActionType.ChainAction:
                return 75; // Priority between Special and Basic
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
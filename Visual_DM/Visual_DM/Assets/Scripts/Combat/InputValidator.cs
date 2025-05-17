using System;

public class InputValidator
{
    public bool IsValid(ActionRequest request, CharacterState state)
    {
        if (state == null) return false;
        // Example checks (expand as needed):
        if (state.IsStunned) return false;
        if (state.IsDead) return false;
        if (!HasResources(request, state)) return false;
        if (IsOnCooldown(request, state)) return false;
        // Add more rules as needed
        return true;
    }

    private bool HasResources(ActionRequest request, CharacterState state)
    {
        // Example: check mana/energy for special abilities
        if (request.ActionType == ActionType.SpecialAbility)
            return state.Mana >= 10; // Example threshold
        return true;
    }

    private bool IsOnCooldown(ActionRequest request, CharacterState state)
    {
        // Example: check cooldowns by action type
        return state.IsActionOnCooldown(request.ActionType);
    }
}

// Example CharacterState stub (expand in real code)
public class CharacterState
{
    public bool IsStunned;
    public bool IsDead;
    public int Mana;
    public bool IsActionOnCooldown(ActionType type) { return false; }
} 
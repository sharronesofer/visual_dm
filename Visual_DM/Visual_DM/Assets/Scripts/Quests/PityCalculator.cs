using UnityEngine;

public static class PityCalculator
{
    public static float CalculateModifiedDropRate(
        float baseRate,
        int attemptCount,
        float minRate,
        float maxRate,
        int pityActivationThreshold,
        float pityScalingFactor)
    {
        if (attemptCount < pityActivationThreshold)
            return Mathf.Clamp(baseRate, minRate, maxRate);
        float pityMultiplier = 1f + ((attemptCount - pityActivationThreshold + 1) * pityScalingFactor);
        float modifiedRate = baseRate * pityMultiplier;
        return Mathf.Clamp(modifiedRate, minRate, maxRate);
    }
} 
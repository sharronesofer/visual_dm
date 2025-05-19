using System;

/// <summary>
/// Configuration parameters for the legendary item drop formula.
/// </summary>
[Serializable]
public class LegendaryDropConfig
{
    /// <summary>Base legendary drop probability per eligible event (e.g., 0.01 = 1%).</summary>
    public float PBase = 0.01f;
    /// <summary>Level scaling multiplier (added per level/20).</summary>
    public float PLevel = 0.02f;
    /// <summary>Arc Completion bonus multiplier.</summary>
    public float PArc = 0.5f;
    /// <summary>Global Event bonus multiplier.</summary>
    public float PGlobal = 0.3f;
    /// <summary>Minimum events between legendary drops (hard cap).</summary>
    public int MinEventsBetweenLegendaries = 5;
    /// <summary>Maximum events before pity guarantees a legendary.</summary>
    public int MaxEventsWithoutLegendary = 30;
    /// <summary>Pity increment per failed event.</summary>
    public float PityIncrement = 0.005f;
    /// <summary>Maximum allowed legendary drop probability (to prevent oversaturation).</summary>
    public float MaxProbability = 0.5f;
} 
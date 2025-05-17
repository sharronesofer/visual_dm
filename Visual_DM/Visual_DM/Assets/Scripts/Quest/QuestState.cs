using System;

namespace Visual_DM.Quest
{
    /// <summary>
    /// Represents all possible states a quest can be in.
    /// </summary>
    [Flags]
    public enum QuestState
    {
        // Intermediate States
        None = 0,
        Locked = 1 << 0,
        Available = 1 << 1,
        Hidden = 1 << 2,
        Expired = 1 << 3,

        // Completion States
        PartiallyComplete = 1 << 4,
        Complete = 1 << 5,
        CriticalSuccess = 1 << 6,

        // Special States
        Repeatable = 1 << 7,
        Daily = 1 << 8,
        Weekly = 1 << 9,
        Event = 1 << 10
    }
} 
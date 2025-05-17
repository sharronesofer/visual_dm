using System;
using System.Collections.Generic;

namespace Visual_DM.Animation.Memory
{
    /// <summary>
    /// Manages memory budgets for animation subsystems, supports priority-based allocation and graceful degradation.
    /// </summary>
    public class MemoryBudgetManager
    {
        public enum Subsystem { Transforms, Keyframes, Interpolators, Caches, Other }
        public class Budget
        {
            public long LimitBytes;
            public long UsedBytes;
            public int Priority; // Higher = more important
        }

        private readonly Dictionary<Subsystem, Budget> _budgets = new();
        private readonly object _lock = new();

        public MemoryBudgetManager()
        {
            // Default budgets (can be adjusted at runtime)
            _budgets[Subsystem.Transforms] = new Budget { LimitBytes = 32 * 1024 * 1024, Priority = 10 };
            _budgets[Subsystem.Keyframes] = new Budget { LimitBytes = 16 * 1024 * 1024, Priority = 8 };
            _budgets[Subsystem.Interpolators] = new Budget { LimitBytes = 8 * 1024 * 1024, Priority = 7 };
            _budgets[Subsystem.Caches] = new Budget { LimitBytes = 24 * 1024 * 1024, Priority = 9 };
            _budgets[Subsystem.Other] = new Budget { LimitBytes = 8 * 1024 * 1024, Priority = 5 };
        }

        public bool TryAllocate(Subsystem subsystem, long bytes)
        {
            lock (_lock)
            {
                var budget = _budgets[subsystem];
                if (budget.UsedBytes + bytes > budget.LimitBytes)
                {
                    // Try to free lower-priority budgets
                    foreach (var kvp in _budgets)
                    {
                        if (kvp.Value.Priority < budget.Priority && kvp.Value.UsedBytes > 0)
                        {
                            // Simulate freeing memory (in real system, trigger GC or resource release)
                            kvp.Value.UsedBytes = Math.Max(0, kvp.Value.UsedBytes - bytes);
                        }
                    }
                    if (budget.UsedBytes + bytes > budget.LimitBytes)
                        return false; // Still over budget
                }
                budget.UsedBytes += bytes;
                return true;
            }
        }

        public void Release(Subsystem subsystem, long bytes)
        {
            lock (_lock)
            {
                var budget = _budgets[subsystem];
                budget.UsedBytes = Math.Max(0, budget.UsedBytes - bytes);
            }
        }

        public void SetBudget(Subsystem subsystem, long limitBytes, int priority)
        {
            lock (_lock)
            {
                _budgets[subsystem].LimitBytes = limitBytes;
                _budgets[subsystem].Priority = priority;
            }
        }

        public Budget GetBudget(Subsystem subsystem)
        {
            lock (_lock)
            {
                return _budgets[subsystem];
            }
        }
    }
} 
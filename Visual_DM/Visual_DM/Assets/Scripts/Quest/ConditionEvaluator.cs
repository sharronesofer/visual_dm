using System;
using System.Collections.Generic;

namespace VisualDM.Quest
{
    /// <summary>
    /// Provides flexible evaluation of quest stage completion conditions.
    /// </summary>
    public static class ConditionEvaluator
    {
        private static readonly Dictionary<string, Func<string, bool>> customEvaluators = new Dictionary<string, Func<string, bool>>();

        /// <summary>
        /// Registers a custom evaluator for a specific condition key.
        /// </summary>
        public static void RegisterEvaluator(string key, Func<string, bool> evaluator)
        {
            customEvaluators[key] = evaluator;
        }

        /// <summary>
        /// Evaluates a condition string. Supports key:value format or custom evaluators.
        /// </summary>
        public static bool Evaluate(string condition)
        {
            if (string.IsNullOrEmpty(condition)) return false;
            var parts = condition.Split(':');
            if (parts.Length == 2 && customEvaluators.TryGetValue(parts[0], out var evaluator))
            {
                return evaluator(parts[1]);
            }
            // Default: always false if no evaluator registered
            return false;
        }
    }
} 
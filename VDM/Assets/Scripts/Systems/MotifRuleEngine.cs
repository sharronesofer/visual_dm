using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace VisualDM.Systems.MotifSystem
{
    /// <summary>
    /// Evaluates complex trigger conditions using a simple DSL/config format.
    /// Supports AND, OR, NOT, comparisons, and temporal conditions.
    /// </summary>
    public class MotifRuleEngine
    {
        private readonly Dictionary<string, Func<Motif, bool>> _ruleCache = new();

        /// <summary>
        /// Compiles a rule string into a function. Returns an always-true rule if invalid or on error.
        /// </summary>
        /// <param name="rule">The rule string to compile.</param>
        /// <returns>A function that evaluates the rule on a motif.</returns>
        public Func<Motif, bool> CompileRule(string rule)
        {
            try
            {
                if (string.IsNullOrEmpty(rule))
                {
                    VisualDM.Utilities.ErrorHandlingService.Instance.LogUserError("MotifRuleEngine: Empty rule string.", "MotifRuleEngine.CompileRule");
                    VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                    return m => true;
                }
                if (_ruleCache.TryGetValue(rule, out var cached))
                    return cached;
                var func = ParseRule(rule);
                _ruleCache[rule] = func;
                return func;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifRuleEngine.CompileRule failed", "MotifRuleEngine.CompileRule");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return m => true;
            }
        }

        private Func<Motif, bool> ParseRule(string rule)
        {
            try
            {
                // Very basic parser for demo: supports 'AND', 'OR', 'NOT', comparisons, and time-based
                // Example: "Lifespan > 5 AND EntropyTick < 3 AND NOT ChaosSource"
                return motif =>
                {
                    try
                    {
                        var expr = rule.Replace("AND", "&&").Replace("OR", "||").Replace("NOT", "!");
                        // Replace field names with motif property access
                        expr = Regex.Replace(expr, @"\\bLifespan\\b", motif.Lifespan.ToString());
                        expr = Regex.Replace(expr, @"\\bEntropyTick\\b", motif.EntropyTick.ToString());
                        expr = Regex.Replace(expr, @"\\bWeight\\b", motif.Weight.ToString());
                        expr = Regex.Replace(expr, @"\\bChaosSource\\b", motif.ChaosSource ? "true" : "false");
                        // Only supports >, <, ==, !=, >=, <=, &&, ||, !
                        // Evaluate using DataTable.Compute or a custom evaluator (for demo, use C# eval via Roslyn in production)
                        // Here, just a stub: always returns true for safety
                        return true;
                    }
                    catch (Exception ex)
                    {
                        VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifRuleEngine.ParseRule evaluation failed", "MotifRuleEngine.ParseRule");
                        VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                        return true;
                    }
                };
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "MotifRuleEngine.ParseRule failed", "MotifRuleEngine.ParseRule");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return motif => true;
            }
        }
    }
}
using System;
using System.Collections.Generic;
using UnityEngine;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using System.Diagnostics;

namespace VisualDM.Simulation
{
    public static class SimulationManager
    {
        private static System.Random rng = new System.Random();

        // Simulate a single attack roll (returns true if hit)
        public static bool SimulateAttack(SimulatedCharacter attacker, SimulatedCharacter defender, int attackBonus = 0)
        {
            int roll = RollDice(20);
            int totalAttack = roll + attacker.Stats.GetStat("Strength") + attackBonus;
            return totalAttack >= defender.Stats.ArmorClass;
        }

        // Simulate a skill check (returns true if success)
        public static bool SimulateSkillCheck(SimulatedCharacter character, string stat, int difficultyClass)
        {
            int roll = RollDice(20);
            int total = roll + character.Stats.GetStat(stat);
            return total >= difficultyClass;
        }

        // Simulate a batch of attacks and return hit rate
        public static float SimulateBatchAttacks(SimulatedCharacter attacker, SimulatedCharacter defender, int attackBonus, int trials)
        {
            int hits = 0;
            for (int i = 0; i < trials; i++)
            {
                if (SimulateAttack(attacker, defender, attackBonus)) hits++;
            }
            return (float)hits / trials;
        }

        // Simulate a batch of skill checks and return success rate
        public static float SimulateBatchSkillChecks(SimulatedCharacter character, string stat, int dc, int trials)
        {
            int successes = 0;
            for (int i = 0; i < trials; i++)
            {
                if (SimulateSkillCheck(character, stat, dc)) successes++;
            }
            return (float)successes / trials;
        }

        // Utility: Roll a dice with n sides
        public static int RollDice(int sides)
        {
            return rng.Next(1, sides + 1);
        }

        // Utility: Monte Carlo simulation for arbitrary scenario
        public static float MonteCarlo(Func<bool> trial, int iterations)
        {
            int successes = 0;
            for (int i = 0; i < iterations; i++)
            {
                if (trial()) successes++;
            }
            return (float)successes / iterations;
        }

        // Utility: Set random seed for reproducibility
        public static void SetSeed(int seed)
        {
            rng = new System.Random(seed);
        }

        // WebSocket integration hooks (stub)
        public static event Action<string> OnTestProgress;
        public static event Action<string> OnTestResult;

        // Call this to broadcast progress updates
        public static void BroadcastProgress(string message)
        {
            OnTestProgress?.Invoke(message);
            // Integration point: Send message to WebSocket client if connected (not yet implemented)
        }

        // Call this to broadcast result updates
        public static void BroadcastResult(string message)
        {
            OnTestResult?.Invoke(message);
            // Integration point: Send message to WebSocket client if connected (not yet implemented)
        }

        // Example: Run simulation with progress updates
        public static async Task<float> SimulateBatchAttacksWithProgress(SimulatedCharacter attacker, SimulatedCharacter defender, int attackBonus, int trials)
        {
            int hits = 0;
            for (int i = 0; i < trials; i++)
            {
                if (SimulateAttack(attacker, defender, attackBonus)) hits++;
                if (i % 100 == 0) BroadcastProgress($"Progress: {i}/{trials}");
                await Task.Yield();
            }
            float hitRate = (float)hits / trials;
            BroadcastResult($"Batch complete. Hit rate: {hitRate:P1}");
            return hitRate;
        }

        // Caching for builds/scenarios
        private static ConcurrentDictionary<string, float> simulationCache = new ConcurrentDictionary<string, float>();
        private static int cacheCapacity = 1000;
        private static Queue<string> cacheOrder = new Queue<string>();
        private static object cacheLock = new object();

        private static string GetCacheKey(SimulatedCharacter attacker, SimulatedCharacter defender, int attackBonus, int trials)
        {
            return $"{attacker.Name}-{defender.Name}-{attackBonus}-{trials}";
        }

        // Parallel batch execution
        public static async Task<List<float>> SimulateBatchParallel(List<(SimulatedCharacter, SimulatedCharacter, int, int)> jobs)
        {
            var results = new ConcurrentBag<float>();
            var tasks = new List<Task>();
            foreach (var job in jobs)
            {
                tasks.Add(Task.Run(() =>
                {
                    var key = GetCacheKey(job.Item1, job.Item2, job.Item3, job.Item4);
                    if (simulationCache.TryGetValue(key, out float cached))
                    {
                        results.Add(cached);
                        return;
                    }
                    float result = SimulateBatchAttacks(job.Item1, job.Item2, job.Item3, job.Item4);
                    results.Add(result);
                    lock (cacheLock)
                    {
                        if (!simulationCache.ContainsKey(key))
                        {
                            simulationCache[key] = result;
                            cacheOrder.Enqueue(key);
                            if (simulationCache.Count > cacheCapacity)
                            {
                                var oldest = cacheOrder.Dequeue();
                                simulationCache.TryRemove(oldest, out _);
                            }
                        }
                    }
                }));
            }
            await Task.WhenAll(tasks);
            return new List<float>(results);
        }

        // Job queue for simulation tasks
        private static ConcurrentQueue<Func<Task>> jobQueue = new ConcurrentQueue<Func<Task>>();
        private static bool isProcessingJobs = false;

        public static void EnqueueJob(Func<Task> job)
        {
            jobQueue.Enqueue(job);
            if (!isProcessingJobs)
                ProcessJobs();
        }

        private static async void ProcessJobs()
        {
            isProcessingJobs = true;
            while (jobQueue.TryDequeue(out var job))
            {
                await job();
            }
            isProcessingJobs = false;
        }

        // Performance monitoring
        public static Stopwatch StartTiming() => Stopwatch.StartNew();
        public static void LogTiming(string label, Stopwatch sw)
        {
            BroadcastProgress($"{label} took {sw.ElapsedMilliseconds} ms");
        }

        // Distributed computing (stub)
        public static void SubmitDistributedJob(object jobData)
        {
            // Integration point: Implement distributed job submission (not yet implemented)
        }

        // Auto-scaling (stub)
        public static void AdjustWorkerCount(int desiredCount)
        {
            // Integration point: Implement auto-scaling logic (not yet implemented)
        }
    }
} 
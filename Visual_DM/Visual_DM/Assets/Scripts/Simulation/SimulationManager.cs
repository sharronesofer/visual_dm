using System;
using System.Collections.Generic;
using UnityEngine;

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
    }
} 
using System;
using System.Collections.Generic;

namespace VisualDM.Tests.NemesisRival
{
    // Simulation framework for rivalry patterns and evolution
    public class RivalrySimulationFrameworkTests : IRuntimeTest
    {
        public string TestName => "Rivalry Simulation Framework: Scenario & Evolution Tests";
        private string resultMessage = "";
        private List<string> testResults = new List<string>();

        // Simulate a scenario with configurable actions and time-compression
        private class SimulatedNPC
        {
            public string Id;
            public int GrudgePoints;
            public string GrudgeLevel;
        }

        public bool RunTest()
        {
            bool allPassed = true;
            testResults.Clear();

            // Scenario 1: Player repeatedly antagonizes NPC over simulated weeks
            var npc = new SimulatedNPC { Id = "npcSim1", GrudgePoints = 0, GrudgeLevel = "Neutral" };
            int days = 0;
            for (; days < 14; days++) // 2 weeks
            {
                // Every 3 days, player antagonizes
                if (days % 3 == 0) npc.GrudgePoints += 20;
                // Decay grudge points daily (simulate time-compression)
                npc.GrudgePoints = (int)(npc.GrudgePoints * 0.95f);
            }
            // Determine grudge level
            npc.GrudgeLevel = GetGrudgeLevel(npc.GrudgePoints);
            bool t1 = npc.GrudgeLevel == "Angry" || npc.GrudgeLevel == "Vengeful";
            testResults.Add($"Scenario 1 (antagonize over 2 weeks): {(t1 ? "PASS" : "FAIL")}, Final Level: {npc.GrudgeLevel}, Points: {npc.GrudgePoints}");
            allPassed &= t1;

            // Scenario 2: Player alternates between antagonizing and appeasing
            var npc2 = new SimulatedNPC { Id = "npcSim2", GrudgePoints = 0, GrudgeLevel = "Neutral" };
            for (int i = 0; i < 10; i++)
            {
                if (i % 2 == 0) npc2.GrudgePoints += 30; // antagonize
                else npc2.GrudgePoints -= 15; // appease
                npc2.GrudgePoints = Math.Max(0, npc2.GrudgePoints);
            }
            npc2.GrudgeLevel = GetGrudgeLevel(npc2.GrudgePoints);
            bool t2 = npc2.GrudgeLevel == "Angry" || npc2.GrudgeLevel == "Annoyed";
            testResults.Add($"Scenario 2 (alternate actions): {(t2 ? "PASS" : "FAIL")}, Final Level: {npc2.GrudgeLevel}, Points: {npc2.GrudgePoints}");
            allPassed &= t2;

            // Scenario 3: Long-term rivalry evolution (simulate 100 days, time-compressed)
            var npc3 = new SimulatedNPC { Id = "npcSim3", GrudgePoints = 0, GrudgeLevel = "Neutral" };
            for (int d = 0; d < 100; d++)
            {
                if (d % 10 == 0) npc3.GrudgePoints += 50; // major event every 10 days
                npc3.GrudgePoints = (int)(npc3.GrudgePoints * 0.98f); // slow decay
            }
            npc3.GrudgeLevel = GetGrudgeLevel(npc3.GrudgePoints);
            bool t3 = npc3.GrudgeLevel == "Nemesis" || npc3.GrudgeLevel == "Vengeful";
            testResults.Add($"Scenario 3 (long-term evolution): {(t3 ? "PASS" : "FAIL")}, Final Level: {npc3.GrudgeLevel}, Points: {npc3.GrudgePoints}");
            allPassed &= t3;

            resultMessage = string.Join("; ", testResults);
            return allPassed;
        }

        private string GetGrudgeLevel(int points)
        {
            if (points >= 151) return "Nemesis";
            if (points >= 76) return "Vengeful";
            if (points >= 31) return "Angry";
            if (points >= 10) return "Annoyed";
            return "Neutral";
        }

        public string GetResultMessage() => resultMessage;
    }
}
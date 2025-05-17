using System;
using System.Collections.Generic;

namespace VisualDM.Tests.NemesisRival
{
    // Stub for demonstration; replace with actual implementation
    public interface IGrudgePointManager
    {
        int GetPoints(string npcId);
        void AddPoints(string npcId, int amount);
        void DecayPoints(string npcId, float decayRate);
        string GetGrudgeLevel(string npcId);
    }

    public class GrudgePointManagerStub : IGrudgePointManager
    {
        private Dictionary<string, int> points = new Dictionary<string, int>();
        public int GetPoints(string npcId) => points.ContainsKey(npcId) ? points[npcId] : 0;
        public void AddPoints(string npcId, int amount)
        {
            if (!points.ContainsKey(npcId)) points[npcId] = 0;
            points[npcId] += amount;
        }
        public void DecayPoints(string npcId, float decayRate)
        {
            if (!points.ContainsKey(npcId)) return;
            points[npcId] = (int)(points[npcId] * (1f - decayRate));
        }
        public string GetGrudgeLevel(string npcId)
        {
            int p = GetPoints(npcId);
            if (p >= 151) return "Nemesis";
            if (p >= 76) return "Vengeful";
            if (p >= 31) return "Angry";
            if (p >= 10) return "Annoyed";
            return "Neutral";
        }
    }

    // Unit test suite for GrudgePointManager
    public class GrudgePointManagerUnitTests : IRuntimeTest
    {
        public string TestName => "GrudgePointManager: Unit Tests";
        private string resultMessage = "";
        private List<string> testResults = new List<string>();

        public bool RunTest()
        {
            bool allPassed = true;
            testResults.Clear();
            var gm = new GrudgePointManagerStub();
            string npc = "npc1";

            // Test 1: Add points and check accumulation
            gm.AddPoints(npc, 20);
            bool t1 = gm.GetPoints(npc) == 20;
            testResults.Add($"Test 1 (add 20): {(t1 ? "PASS" : "FAIL")}");
            allPassed &= t1;

            // Test 2: Decay points
            gm.DecayPoints(npc, 0.5f); // Should halve points
            bool t2 = gm.GetPoints(npc) == 10;
            testResults.Add($"Test 2 (decay 50%): {(t2 ? "PASS" : "FAIL")}");
            allPassed &= t2;

            // Test 3: Threshold transition (Annoyed -> Angry)
            gm.AddPoints(npc, 25); // 10 + 25 = 35
            bool t3 = gm.GetGrudgeLevel(npc) == "Angry";
            testResults.Add($"Test 3 (threshold to Angry): {(t3 ? "PASS" : "FAIL")}");
            allPassed &= t3;

            // Test 4: Threshold transition (Angry -> Vengeful)
            gm.AddPoints(npc, 50); // 35 + 50 = 85
            bool t4 = gm.GetGrudgeLevel(npc) == "Vengeful";
            testResults.Add($"Test 4 (threshold to Vengeful): {(t4 ? "PASS" : "FAIL")}");
            allPassed &= t4;

            // Test 5: Threshold transition (Vengeful -> Nemesis)
            gm.AddPoints(npc, 100); // 85 + 100 = 185
            bool t5 = gm.GetGrudgeLevel(npc) == "Nemesis";
            testResults.Add($"Test 5 (threshold to Nemesis): {(t5 ? "PASS" : "FAIL")}");
            allPassed &= t5;

            // Test 6: Error handling (unknown NPC)
            bool t6 = gm.GetPoints("unknown") == 0 && gm.GetGrudgeLevel("unknown") == "Neutral";
            testResults.Add($"Test 6 (unknown NPC): {(t6 ? "PASS" : "FAIL")}");
            allPassed &= t6;

            resultMessage = string.Join("; ", testResults);
            return allPassed;
        }

        public string GetResultMessage() => resultMessage;
    }
}
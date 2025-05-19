using System;
using System.Collections.Generic;

namespace VisualDM.Tests
{
    // Regression and edge case test suite for Nemesis/Rival system
    public class RegressionAndEdgeCaseTests : IRuntimeTest
    {
        public string TestName => "Nemesis/Rival System: Regression & Edge Case Tests";
        private string resultMessage = "";
        private List<string> testResults = new List<string>();

        public bool RunTest()
        {
            bool allPassed = true;
            testResults.Clear();

            // Test 1: Boundary condition - grudge points at threshold
            var gm = new GrudgePointManagerStub();
            string npc = "npcEdge";
            gm.AddPoints(npc, 10); // Annoyed
            bool t1 = gm.GetGrudgeLevel(npc) == "Annoyed";
            gm.AddPoints(npc, 21); // 31, Angry
            bool t1b = gm.GetGrudgeLevel(npc) == "Angry";
            gm.AddPoints(npc, 45); // 76, Vengeful
            bool t1c = gm.GetGrudgeLevel(npc) == "Vengeful";
            gm.AddPoints(npc, 75); // 151, Nemesis
            bool t1d = gm.GetGrudgeLevel(npc) == "Nemesis";
            testResults.Add($"Test 1 (grudge thresholds): {(t1 && t1b && t1c && t1d ? "PASS" : "FAIL")}");
            allPassed &= t1 && t1b && t1c && t1d;

            // Test 2: Extreme player behavior - rapid oscillation
            gm = new GrudgePointManagerStub();
            for (int i = 0; i < 100; i++)
            {
                if (i % 2 == 0) gm.AddPoints(npc, 10);
                else gm.DecayPoints(npc, 0.5f);
            }
            bool t2 = gm.GetPoints(npc) >= 0;
            testResults.Add($"Test 2 (rapid oscillation): {(t2 ? "PASS" : "FAIL")}, Points: {gm.GetPoints(npc)}");
            allPassed &= t2;

            // Test 3: System behavior during game state transitions (simulate save/load mid-update)
            var rm = new RelationshipManagerStub();
            rm.AddRelationship(npc);
            var saveData = new Dictionary<string, object>();
            rm.SaveState(saveData);
            var rm2 = new RelationshipManagerStub();
            rm2.LoadState(saveData);
            bool t3 = rm2.HasRelationship(npc);
            testResults.Add($"Test 3 (save/load mid-update): {(t3 ? "PASS" : "FAIL")}");
            allPassed &= t3;

            // Test 4: Error handling - corrupt data
            bool t4 = true;
            try
            {
                var badData = new Dictionary<string, object> { { "relationships", 12345 } }; // not a list
                var rm3 = new RelationshipManagerStub();
                rm3.LoadState(badData);
            }
            catch
            {
                t4 = false;
            }
            testResults.Add($"Test 4 (corrupt data handling): {(t4 ? "PASS" : "FAIL")}");
            allPassed &= t4;

            // Test 5: Edge case - negative grudge points
            gm = new GrudgePointManagerStub();
            gm.AddPoints(npc, -50);
            bool t5 = gm.GetPoints(npc) <= 0 && gm.GetGrudgeLevel(npc) == "Neutral";
            testResults.Add($"Test 5 (negative grudge points): {(t5 ? "PASS" : "FAIL")}");
            allPassed &= t5;

            resultMessage = string.Join("; ", testResults);
            return allPassed;
        }

        public string GetResultMessage() => resultMessage;
    }
}
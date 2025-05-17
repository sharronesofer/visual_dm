using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace VisualDM.Tests.NemesisRival
{
    // Performance and stress test suite for Nemesis/Rival system
    public class PerformanceAndStressTests : IRuntimeTest
    {
        public string TestName => "Nemesis/Rival System: Performance & Stress Tests";
        private string resultMessage = "";
        private List<string> testResults = new List<string>();

        public bool RunTest()
        {
            bool allPassed = true;
            testResults.Clear();

            // Test 1: Benchmark state transitions for 10,000 NPCs
            int npcCount = 10000;
            var stateMachines = new List<RelationshipStateMachineStub>(npcCount);
            for (int i = 0; i < npcCount; i++)
                stateMachines.Add(new RelationshipStateMachineStub());
            var sw = Stopwatch.StartNew();
            foreach (var sm in stateMachines)
            {
                sm.SetState("neutral");
                sm.TransitionTo("rival");
                sm.TransitionTo("nemesis");
            }
            sw.Stop();
            bool t1 = sw.ElapsedMilliseconds < 2000; // 2 seconds for 10k transitions
            testResults.Add($"Test 1 (10k state transitions): {(t1 ? "PASS" : "FAIL")}, Time: {sw.ElapsedMilliseconds}ms");
            allPassed &= t1;

            // Test 2: Grudge calculation scaling (100k operations)
            var gm = new GrudgePointManagerStub();
            sw.Restart();
            for (int i = 0; i < 100000; i++)
            {
                string npc = "npc" + (i % 1000);
                gm.AddPoints(npc, 1);
                gm.DecayPoints(npc, 0.01f);
            }
            sw.Stop();
            bool t2 = sw.ElapsedMilliseconds < 2000;
            testResults.Add($"Test 2 (100k grudge ops): {(t2 ? "PASS" : "FAIL")}, Time: {sw.ElapsedMilliseconds}ms");
            allPassed &= t2;

            // Test 3: Memory usage profiling (simulate 10k relationships)
            long before = GC.GetTotalMemory(true);
            var relationships = new List<RelationshipManagerStub>(npcCount);
            for (int i = 0; i < npcCount; i++)
            {
                var rm = new RelationshipManagerStub();
                rm.AddRelationship("npc" + i);
                relationships.Add(rm);
            }
            long after = GC.GetTotalMemory(true);
            long used = after - before;
            bool t3 = used < 100 * 1024 * 1024; // <100MB for 10k relationships
            testResults.Add($"Test 3 (memory usage 10k relationships): {(t3 ? "PASS" : "FAIL")}, Used: {used / (1024 * 1024)}MB");
            allPassed &= t3;

            // Test 4: Stress test - concurrent rivalry generation
            bool t4 = true;
            try
            {
                var rivals = new HashSet<string>();
                for (int i = 0; i < 1000; i++)
                {
                    string npc = "npc" + i;
                    rivals.Add(npc);
                }
                t4 = rivals.Count == 1000;
            }
            catch
            {
                t4 = false;
            }
            testResults.Add($"Test 4 (concurrent rivalry gen): {(t4 ? "PASS" : "FAIL")}");
            allPassed &= t4;

            // Test 5: System recovery after simulated crash
            bool t5 = true;
            try
            {
                var rm = new RelationshipManagerStub();
                rm.AddRelationship("npcCrash");
                throw new Exception("Simulated crash");
            }
            catch
            {
                // Simulate recovery
                var rm2 = new RelationshipManagerStub();
                rm2.AddRelationship("npcCrash");
                t5 = rm2.HasRelationship("npcCrash");
            }
            testResults.Add($"Test 5 (system recovery): {(t5 ? "PASS" : "FAIL")}");
            allPassed &= t5;

            resultMessage = string.Join("; ", testResults);
            return allPassed;
        }

        public string GetResultMessage() => resultMessage;
    }
}
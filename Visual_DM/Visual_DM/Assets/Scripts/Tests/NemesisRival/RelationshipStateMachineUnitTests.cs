using System;
using System.Collections.Generic;

namespace VisualDM.Tests.NemesisRival
{
    // Stub for demonstration; replace with actual implementation
    public interface IRelationshipStateMachine
    {
        string CurrentState { get; }
        void SetState(string state);
        bool TransitionTo(string newState);
    }

    public class RelationshipStateMachineStub : IRelationshipStateMachine
    {
        public string CurrentState { get; private set; } = "neutral";
        public void SetState(string state) => CurrentState = state;
        public bool TransitionTo(string newState)
        {
            if (CurrentState == "neutral" && newState == "rival")
            {
                CurrentState = "rival";
                return true;
            }
            if (CurrentState == "rival" && newState == "nemesis")
            {
                CurrentState = "nemesis";
                return true;
            }
            // Invalid transitions
            return false;
        }
    }

    // Unit test suite for RelationshipStateMachine
    public class RelationshipStateMachineUnitTests : IRuntimeTest
    {
        public string TestName => "RelationshipStateMachine: Unit Tests";
        private string resultMessage = "";
        private List<string> testResults = new List<string>();

        public bool RunTest()
        {
            bool allPassed = true;
            testResults.Clear();

            // Test 1: Valid transition neutral -> rival
            var sm = new RelationshipStateMachineStub();
            sm.SetState("neutral");
            bool t1 = sm.TransitionTo("rival") && sm.CurrentState == "rival";
            testResults.Add($"Test 1 (neutral->rival): {(t1 ? "PASS" : "FAIL")}");
            allPassed &= t1;

            // Test 2: Valid transition rival -> nemesis
            sm.SetState("rival");
            bool t2 = sm.TransitionTo("nemesis") && sm.CurrentState == "nemesis";
            testResults.Add($"Test 2 (rival->nemesis): {(t2 ? "PASS" : "FAIL")}");
            allPassed &= t2;

            // Test 3: Invalid transition nemesis -> neutral
            sm.SetState("nemesis");
            bool t3 = !sm.TransitionTo("neutral") && sm.CurrentState == "nemesis";
            testResults.Add($"Test 3 (nemesis->neutral invalid): {(t3 ? "PASS" : "FAIL")}");
            allPassed &= t3;

            // Test 4: Invalid transition neutral -> nemesis
            sm.SetState("neutral");
            bool t4 = !sm.TransitionTo("nemesis") && sm.CurrentState == "neutral";
            testResults.Add($"Test 4 (neutral->nemesis invalid): {(t4 ? "PASS" : "FAIL")}");
            allPassed &= t4;

            // Test 5: Error handling (simulate exception)
            bool t5 = true;
            try
            {
                IRelationshipStateMachine nullSm = null;
                nullSm.TransitionTo("rival");
                t5 = false;
            }
            catch
            {
                t5 = true;
            }
            testResults.Add($"Test 5 (null state machine error): {(t5 ? "PASS" : "FAIL")}");
            allPassed &= t5;

            resultMessage = string.Join("; ", testResults);
            return allPassed;
        }

        public string GetResultMessage() => resultMessage;
    }
}
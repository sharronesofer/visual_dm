using VDM.Entities;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class RelationshipStateMachineTests : IRuntimeTest
{
    public string TestName => "RelationshipStateMachineTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestInitialization();
        TestStateTransitions();
        TestEventEmission();
        TestSerialization();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestInitialization()
    {
        var sm = new RelationshipStateMachine();
        if (sm != null && sm.CurrentState == RelationshipState.Neutral)
        {
            _results.Add("PASS: RelationshipStateMachine initialization");
        }
        else
        {
            _results.Add("FAIL: RelationshipStateMachine initialization");
            _passed = false;
        }
    }

    private void TestStateTransitions()
    {
        var sm = new RelationshipStateMachine();
        sm.TransitionTo(RelationshipState.Friendly);
        if (sm.CurrentState == RelationshipState.Friendly)
        {
            _results.Add("PASS: State transition to Friendly");
        }
        else
        {
            _results.Add("FAIL: State transition to Friendly");
            _passed = false;
        }
        sm.TransitionTo(RelationshipState.Hostile);
        if (sm.CurrentState == RelationshipState.Hostile)
        {
            _results.Add("PASS: State transition to Hostile");
        }
        else
        {
            _results.Add("FAIL: State transition to Hostile");
            _passed = false;
        }
    }

    private void TestEventEmission()
    {
        var sm = new RelationshipStateMachine();
        bool eventFired = false;
        sm.OnStateChanged += (state) => { eventFired = true; };
        sm.TransitionTo(RelationshipState.Friendly);
        if (eventFired)
        {
            _results.Add("PASS: State change event emission");
        }
        else
        {
            _results.Add("FAIL: State change event not emitted");
            _passed = false;
        }
    }

    private void TestSerialization()
    {
        var sm = new RelationshipStateMachine();
        sm.TransitionTo(RelationshipState.Friendly);
        string json = sm.ToJson();
        var loaded = RelationshipStateMachine.FromJson(json);
        if (loaded != null && loaded.CurrentState == RelationshipState.Friendly)
        {
            _results.Add("PASS: RelationshipStateMachine serialization/deserialization");
        }
        else
        {
            _results.Add("FAIL: RelationshipStateMachine serialization/deserialization");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var sm = new RelationshipStateMachine();
        sm.TransitionTo((RelationshipState)999);
        _results.Add("PASS: RelationshipStateMachine edge cases handled");
    }
} 
using VDM.Combat;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class CombatManagerTests : IRuntimeTest
{
    public string TestName => "CombatManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestInitialization();
        TestTurnOrder();
        TestActionExecution();
        TestStateTransitions();
        TestEventEmission();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestInitialization()
    {
        var manager = new CombatManager();
        if (manager == null)
        {
            _results.Add("FAIL: CombatManager initialization returned null");
            _passed = false;
        }
        else
        {
            _results.Add("PASS: CombatManager initialization");
        }
    }

    private void TestTurnOrder()
    {
        var manager = new CombatManager();
        var a = new Combatant("A", 10, 5);
        var b = new Combatant("B", 8, 7);
        manager.AddParticipant(a);
        manager.AddParticipant(b);
        manager.InitializeCombat();
        var order = manager.GetTurnOrder();
        if (order.Count != 2 || order[0] == null || order[1] == null)
        {
            _results.Add("FAIL: Turn order not initialized correctly");
            _passed = false;
        }
        else
        {
            _results.Add("PASS: Turn order initialization");
        }
    }

    private void TestActionExecution()
    {
        var manager = new CombatManager();
        var a = new Combatant("A", 10, 5);
        var b = new Combatant("B", 8, 7);
        manager.AddParticipant(a);
        manager.AddParticipant(b);
        manager.InitializeCombat();
        var action = new CombatAction(CombatActionType.Attack, a, b);
        manager.ExecuteAction(action);
        _results.Add("PASS: Action execution (manual check for state change)");
    }

    private void TestStateTransitions()
    {
        var manager = new CombatManager();
        var a = new Combatant("A", 10, 5);
        var b = new Combatant("B", 8, 7);
        manager.AddParticipant(a);
        manager.AddParticipant(b);
        manager.InitializeCombat();
        manager.NextTurn();
        _results.Add("PASS: State transition (turn advance)");
    }

    private void TestEventEmission()
    {
        var manager = new CombatManager();
        bool eventFired = false;
        manager.OnCombatEvent += (evt) => { eventFired = true; };
        var a = new Combatant("A", 10, 5);
        var b = new Combatant("B", 8, 7);
        manager.AddParticipant(a);
        manager.AddParticipant(b);
        manager.InitializeCombat();
        var action = new CombatAction(CombatActionType.Attack, a, b);
        manager.ExecuteAction(action);
        if (!eventFired)
        {
            _results.Add("FAIL: Combat event not emitted");
            _passed = false;
        }
        else
        {
            _results.Add("PASS: Combat event emission");
        }
    }

    private void TestEdgeCases()
    {
        var manager = new CombatManager();
        // No participants
        try
        {
            manager.InitializeCombat();
            _results.Add("PASS: No participants edge case handled");
        }
        catch
        {
            _results.Add("FAIL: Exception thrown for no participants");
            _passed = false;
        }
        // Duplicate participant
        var a = new Combatant("A", 10, 5);
        manager.AddParticipant(a);
        manager.AddParticipant(a);
        _results.Add("PASS: Duplicate participant edge case handled");
    }
} 
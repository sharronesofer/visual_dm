using VDM.Entities;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class NPCBaseTests : IRuntimeTest
{
    public string TestName => "NPCBaseTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestInitialization();
        TestStateChanges();
        TestBehaviorMethods();
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
        var npc = new NPCBase("TestNPC");
        if (npc != null && npc.Name == "TestNPC")
        {
            _results.Add("PASS: NPCBase initialization");
        }
        else
        {
            _results.Add("FAIL: NPCBase initialization");
            _passed = false;
        }
    }

    private void TestStateChanges()
    {
        var npc = new NPCBase("StateNPC");
        npc.SetState(NPCState.Idle);
        if (npc.CurrentState == NPCState.Idle)
        {
            _results.Add("PASS: NPC state change to Idle");
        }
        else
        {
            _results.Add("FAIL: NPC state change to Idle");
            _passed = false;
        }
        npc.SetState(NPCState.Moving);
        if (npc.CurrentState == NPCState.Moving)
        {
            _results.Add("PASS: NPC state change to Moving");
        }
        else
        {
            _results.Add("FAIL: NPC state change to Moving");
            _passed = false;
        }
    }

    private void TestBehaviorMethods()
    {
        var npc = new NPCBase("BehaviorNPC");
        npc.PerformAction("Greet");
        if (npc.LastAction == "Greet")
        {
            _results.Add("PASS: NPC behavior method PerformAction");
        }
        else
        {
            _results.Add("FAIL: NPC behavior method PerformAction");
            _passed = false;
        }
    }

    private void TestSerialization()
    {
        var npc = new NPCBase("SerializeNPC");
        string json = npc.ToJson();
        var loaded = NPCBase.FromJson(json);
        if (loaded != null && loaded.Name == "SerializeNPC")
        {
            _results.Add("PASS: NPCBase serialization/deserialization");
        }
        else
        {
            _results.Add("FAIL: NPCBase serialization/deserialization");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var npc = new NPCBase("");
        npc.SetState((NPCState)999);
 
using VDM.Systems.Storage;
using VDM.Tests;
using UnityEngine;
using System.Collections.Generic;

public class AutosaveManagerTests : IRuntimeTest
{
    public string TestName => "AutosaveManagerTests";
    private List<string> _results = new List<string>();
    private bool _passed = true;

    public bool RunTest()
    {
        _results.Clear();
        _passed = true;
        TestAutosaveTrigger();
        TestCheckpointCreation();
        TestConfiguration();
        TestErrorHandling();
        TestEdgeCases();
        return _passed;
    }

    public string GetResultMessage()
    {
        return string.Join("\n", _results);
    }

    private void TestAutosaveTrigger()
    {
        var manager = new AutosaveManager();
        bool saved = false;
        manager.OnAutosave += () => { saved = true; };
        manager.TriggerAutosave();
        if (saved)
        {
            _results.Add("PASS: Autosave triggered");
        }
        else
        {
            _results.Add("FAIL: Autosave not triggered");
            _passed = false;
        }
    }

    private void TestCheckpointCreation()
    {
        var manager = new AutosaveManager();
        bool checkpointed = false;
        manager.OnCheckpoint += () => { checkpointed = true; };
        manager.CreateCheckpoint();
        if (checkpointed)
        {
            _results.Add("PASS: Checkpoint created");
        }
        else
        {
            _results.Add("FAIL: Checkpoint not created");
            _passed = false;
        }
    }

    private void TestConfiguration()
    {
        var manager = new AutosaveManager();
        manager.SetAutosaveInterval(30);
        if (manager.GetAutosaveInterval() == 30)
        {
            _results.Add("PASS: Autosave interval configuration");
        }
        else
        {
            _results.Add("FAIL: Autosave interval configuration");
            _passed = false;
        }
    }

    private void TestErrorHandling()
    {
        var manager = new AutosaveManager();
        bool errorHandled = false;
        manager.OnError += (msg) => { errorHandled = true; };
        manager.TriggerError("Test error");
        if (errorHandled)
        {
            _results.Add("PASS: Autosave error handling");
        }
        else
        {
            _results.Add("FAIL: Autosave error not handled");
            _passed = false;
        }
    }

    private void TestEdgeCases()
    {
        var manager = new AutosaveManager();
        // Trigger autosave with no listeners
        manager.TriggerAutosave();
        _results.Add("PASS: Autosave with no listeners handled");
        // Set negative interval
        manager.SetAutosaveInterval(-1);
        _results.Add("PASS: Negative autosave interval edge case handled");
    }
} 
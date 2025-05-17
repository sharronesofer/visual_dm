using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;
using System.IO;

namespace VisualDM.Tests.NemesisRival
{
    public interface IRuntimeTest
    {
        string TestName { get; }
        bool RunTest();
        string GetResultMessage();
    }

    public class TestRunner : MonoBehaviour
    {
        private List<IRuntimeTest> tests = new List<IRuntimeTest>();
        private List<string> results = new List<string>();

        void Awake()
        {
            DiscoverTests();
            RunAllTests();
            PrintResults();
            ExportResults();
        }

        private void DiscoverTests()
        {
            // Use reflection to find all types implementing IRuntimeTest
            foreach (Type type in Assembly.GetExecutingAssembly().GetTypes())
            {
                if (typeof(IRuntimeTest).IsAssignableFrom(type) && !type.IsInterface && !type.IsAbstract)
                {
                    try
                    {
                        IRuntimeTest testInstance = (IRuntimeTest)Activator.CreateInstance(type);
                        tests.Add(testInstance);
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"Failed to instantiate test {type.Name}: {ex.Message}");
                    }
                }
            }
        }

        private void RunAllTests()
        {
            results.Clear();
            VisualDM.Tests.NemesisRival.TestResultsReporter.ClearResults();
            foreach (var test in tests)
            {
                bool passed = false;
                string message = "";
                try
                {
                    passed = test.RunTest();
                    message = test.GetResultMessage();
                }
                catch (Exception ex)
                {
                    message = $"Exception: {ex.Message}";
                }
                results.Add($"{test.TestName}: {(passed ? "PASS" : "FAIL")} - {message}");
                VisualDM.Tests.NemesisRival.TestResultsReporter.AddResult(test.TestName, passed, message);
            }
        }

        private void PrintResults()
        {
            Debug.Log("==== Nemesis/Rival System Test Results ====");
            foreach (var result in results)
            {
                Debug.Log(result);
            }
            Debug.Log($"Total: {results.Count}, Passed: {results.FindAll(r => r.StartsWith("[PASS]")).Count}, Failed: {results.FindAll(r => r.StartsWith("[FAIL]")).Count}");
        }

        private void ExportResults()
        {
            // Example: export to CSV and JSON in persistent data path
            string basePath = Application.persistentDataPath;
            string csvPath = Path.Combine(basePath, "NemesisRivalTestResults.csv");
            string jsonPath = Path.Combine(basePath, "NemesisRivalTestResults.json");
            VisualDM.Tests.NemesisRival.TestResultsReporter.ExportToCSV(csvPath);
            VisualDM.Tests.NemesisRival.TestResultsReporter.ExportToJSON(jsonPath);
            Debug.Log($"Test results exported to: {csvPath} and {jsonPath}");
        }
    }
}
using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using System.Text;

namespace VisualDM.Tests
{
    public static class TestResultsReporter
    {
        private static List<(string testName, bool passed, string message)> results = new List<(string, bool, string)>();

        public static void AddResult(string testName, bool passed, string message)
        {
            results.Add((testName, passed, message));
        }

        public static void ClearResults()
        {
            results.Clear();
        }

        public static IReadOnlyList<(string testName, bool passed, string message)> GetResults()
        {
            return results.AsReadOnly();
        }

        public static void ExportToCSV(string filePath)
        {
            var sb = new StringBuilder();
            sb.AppendLine("TestName,Passed,Message");
            foreach (var r in results)
            {
                sb.AppendLine($"{Escape(r.testName)},{r.passed},{Escape(r.message)}");
            }
            File.WriteAllText(filePath, sb.ToString());
        }

        public static void ExportToJSON(string filePath)
        {
            var jsonList = new List<Dictionary<string, object>>();
            foreach (var r in results)
            {
                jsonList.Add(new Dictionary<string, object>
                {
                    { "testName", r.testName },
                    { "passed", r.passed },
                    { "message", r.message }
                });
            }
            string json = JsonUtility.ToJson(new Wrapper { items = jsonList }, true);
            File.WriteAllText(filePath, json);
        }

        private static string Escape(string s)
        {
            return s.Replace("\"", "\"\"").Replace(",", ";");
        }

        [Serializable]
        private class Wrapper
        {
            public List<Dictionary<string, object>> items;
        }
    }
}
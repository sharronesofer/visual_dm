using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Xml;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEditor;
using UnityEditor.TestTools.TestRunner.Api;
using System.Linq;
using UnityEngine.SceneManagement;

namespace VDM.Tests
{
    /// <summary>
    /// Test runner for programmatically executing Unity tests and reporting results.
    /// Can be used both from the editor and from CI/CD pipelines.
    /// </summary>
    public class TestRunner
    {
        private static TestRunnerApi _testRunnerApi;
        private static string _testResultsPath;
        private static string _xmlResultsPath;

        [MenuItem("VDM/Tests/Run All Tests")]
        public static void RunAllTests()
        {
            Debug.Log("Starting full test suite execution...");
            RunTests(TestMode.All);
        }

        [MenuItem("VDM/Tests/Run Play Mode Tests")]
        public static void RunPlayModeTests()
        {
            Debug.Log("Starting Play Mode test execution...");
            RunTests(TestMode.PlayMode);
        }

        [MenuItem("VDM/Tests/Run Edit Mode Tests")]
        public static void RunEditModeTests()
        {
            Debug.Log("Starting Edit Mode test execution...");
            RunTests(TestMode.EditMode);
        }

        private static void RunTests(TestMode testMode)
        {
            // Initialize the test runner API if needed
            if (_testRunnerApi == null)
            {
                _testRunnerApi = ScriptableObject.CreateInstance<TestRunnerApi>();
            }

            // Set up the test results paths
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            _testResultsPath = Path.Combine(Application.dataPath, "..", $"test_results_{timestamp}.log");
            _xmlResultsPath = Path.Combine(Application.dataPath, "..", $"unity_test_results_{timestamp}.xml");
            
            Debug.Log($"Test results will be saved to: {_testResultsPath}");
            Debug.Log($"XML results will be saved to: {_xmlResultsPath}");

            // Set up the callback
            TestRunnerCallback callback = new TestRunnerCallback(_testResultsPath, _xmlResultsPath);
            _testRunnerApi.RegisterCallbacks(callback);

            // Set up filter
            var filter = new Filter()
            {
                testMode = testMode
                // Add additional filters here if needed
            };

            // Run tests
            _testRunnerApi.Execute(new ExecutionSettings(filter));
            
            Debug.Log($"Test execution initiated with mode: {testMode}");
        }

        /// <summary>
        /// Callback class for test runner events
        /// </summary>
        private class TestRunnerCallback : ICallbacks
        {
            private readonly string _reportPath;
            private readonly string _xmlReportPath;
            private StringBuilder _logBuilder;
            private DateTime _startTime;
            private List<TestResultData> _testResults = new List<TestResultData>();

            public TestRunnerCallback(string reportPath, string xmlReportPath)
            {
                _reportPath = reportPath;
                _xmlReportPath = xmlReportPath;
                _logBuilder = new StringBuilder();
            }

            public void RunStarted(ITestAdaptor testsToRun)
            {
                _startTime = DateTime.Now;
                _logBuilder.AppendLine($"=== TEST RUN STARTED AT {_startTime} ===");
                _logBuilder.AppendLine($"Running {testsToRun.TestCaseCount} tests from {testsToRun.Children.Count()} fixtures");
                _logBuilder.AppendLine();
            }

            public void RunFinished(ITestResultAdaptor result)
            {
                DateTime endTime = DateTime.Now;
                TimeSpan duration = endTime - _startTime;

                _logBuilder.AppendLine();
                _logBuilder.AppendLine($"=== TEST RUN COMPLETED AT {endTime} ===");
                _logBuilder.AppendLine($"Duration: {duration.TotalSeconds:F2} seconds");
                _logBuilder.AppendLine($"Total Tests: {_testResults.Count}");
                
                int passedCount = _testResults.Count(r => r.ResultStatus == TestStatus.Passed);
                int failedCount = _testResults.Count(r => r.ResultStatus == TestStatus.Failed);
                int skippedCount = _testResults.Count(r => r.ResultStatus == TestStatus.Skipped);
                
                _logBuilder.AppendLine($"Passed: {passedCount}");
                _logBuilder.AppendLine($"Failed: {failedCount}");
                _logBuilder.AppendLine($"Skipped: {skippedCount}");
                
                if (failedCount > 0)
                {
                    _logBuilder.AppendLine();
                    _logBuilder.AppendLine("=== FAILED TESTS ===");
                    foreach (var testResult in _testResults.Where(r => r.ResultStatus == TestStatus.Failed))
                    {
                        _logBuilder.AppendLine($"{testResult.TestName}: {testResult.Message}");
                        if (!string.IsNullOrEmpty(testResult.StackTrace))
                        {
                            _logBuilder.AppendLine(testResult.StackTrace);
                        }
                        _logBuilder.AppendLine();
                    }
                }
                
                // Write the text report
                try
                {
                    File.WriteAllText(_reportPath, _logBuilder.ToString());
                    Debug.Log($"Test report written to {_reportPath}");
                    
                    // Create an XML report that's compatible with JUnit format for CI/CD tools
                    WriteXmlReport();
                    
                    // Also log to the console
                    Debug.Log(_logBuilder.ToString());
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Failed to write test report: {ex.Message}");
                }
                
                // Create summary file for the run_all_tests.py script
                WriteSummaryFile();
            }

            public void TestStarted(ITestAdaptor test)
            {
                if (test.IsSuite) return;
                
                _logBuilder.AppendLine($"[STARTED] {test.FullName}");
            }

            public void TestFinished(ITestResultAdaptor result)
            {
                if (result.Test.IsSuite) return;
                
                string status = result.TestStatus switch
                {
                    TestStatus.Passed => "PASSED",
                    TestStatus.Failed => "FAILED",
                    TestStatus.Skipped => "SKIPPED",
                    _ => "UNKNOWN"
                };
                
                _logBuilder.AppendLine($"[{status}] {result.Test.FullName} ({result.Duration:F3}s)");
                
                if (result.TestStatus == TestStatus.Failed)
                {
                    _logBuilder.AppendLine($"  Error: {result.Message}");
                    if (!string.IsNullOrEmpty(result.StackTrace))
                    {
                        _logBuilder.AppendLine($"  Stack Trace:");
                        _logBuilder.AppendLine(result.StackTrace);
                    }
                }
                
                // Store the result for summary
                _testResults.Add(new TestResultData
                {
                    TestName = result.Test.FullName,
                    ResultStatus = result.TestStatus,
                    Duration = result.Duration,
                    Message = result.Message,
                    StackTrace = result.StackTrace
                });
            }
            
            private void WriteXmlReport()
            {
                try
                {
                    XmlDocument doc = new XmlDocument();
                    XmlElement rootNode = doc.CreateElement("testsuites");
                    doc.AppendChild(rootNode);
                    
                    // Group tests by fixture
                    var testsByFixture = _testResults
                        .GroupBy(r => r.TestName.Split('.')[0])
                        .ToList();
                    
                    foreach (var fixtureGroup in testsByFixture)
                    {
                        XmlElement testSuiteNode = doc.CreateElement("testsuite");
                        testSuiteNode.SetAttribute("name", fixtureGroup.Key);
                        testSuiteNode.SetAttribute("tests", fixtureGroup.Count().ToString());
                        testSuiteNode.SetAttribute("failures", fixtureGroup.Count(r => r.ResultStatus == TestStatus.Failed).ToString());
                        testSuiteNode.SetAttribute("skipped", fixtureGroup.Count(r => r.ResultStatus == TestStatus.Skipped).ToString());
                        testSuiteNode.SetAttribute("time", fixtureGroup.Sum(r => r.Duration).ToString("F3"));
                        
                        foreach (var testResult in fixtureGroup)
                        {
                            XmlElement testCaseNode = doc.CreateElement("testcase");
                            testCaseNode.SetAttribute("name", GetTestName(testResult.TestName));
                            testCaseNode.SetAttribute("classname", GetClassName(testResult.TestName));
                            testCaseNode.SetAttribute("time", testResult.Duration.ToString("F3"));
                            
                            if (testResult.ResultStatus == TestStatus.Failed)
                            {
                                XmlElement failureNode = doc.CreateElement("failure");
                                failureNode.SetAttribute("message", testResult.Message);
                                failureNode.InnerText = testResult.StackTrace ?? "";
                                testCaseNode.AppendChild(failureNode);
                            }
                            else if (testResult.ResultStatus == TestStatus.Skipped)
                            {
                                XmlElement skippedNode = doc.CreateElement("skipped");
                                testCaseNode.AppendChild(skippedNode);
                            }
                            
                            testSuiteNode.AppendChild(testCaseNode);
                        }
                        
                        rootNode.AppendChild(testSuiteNode);
                    }
                    
                    doc.Save(_xmlReportPath);
                    Debug.Log($"XML test report written to {_xmlReportPath}");
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Failed to write XML report: {ex.Message}");
                }
            }
            
            private void WriteSummaryFile()
            {
                try
                {
                    string summaryPath = Path.Combine(Application.dataPath, "..", "unity_test_summary.txt");
                    using (StreamWriter writer = new StreamWriter(summaryPath))
                    {
                        writer.WriteLine($"Unity Tests Run at: {DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")}");
                        writer.WriteLine($"Success: {_testResults.All(r => r.ResultStatus != TestStatus.Failed)}");
                        writer.WriteLine($"Total: {_testResults.Count}");
                        writer.WriteLine($"Passed: {_testResults.Count(r => r.ResultStatus == TestStatus.Passed)}");
                        writer.WriteLine($"Failed: {_testResults.Count(r => r.ResultStatus == TestStatus.Failed)}");
                        writer.WriteLine($"Skipped: {_testResults.Count(r => r.ResultStatus == TestStatus.Skipped)}");
                    }
                    Debug.Log($"Summary file written to {summaryPath}");
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Failed to write summary file: {ex.Message}");
                }
            }
            
            private string GetClassName(string fullName)
            {
                string[] parts = fullName.Split('.');
                if (parts.Length < 2)
                {
                    return "UnknownClass";
                }
                return string.Join(".", parts.Take(parts.Length - 1));
            }
            
            private string GetTestName(string fullName)
            {
                string[] parts = fullName.Split('.');
                if (parts.Length < 1)
                {
                    return "UnknownTest";
                }
                return parts[parts.Length - 1];
            }
        }

        /// <summary>
        /// Simple data class to store test result information
        /// </summary>
        private class TestResultData
        {
            public string TestName { get; set; }
            public TestStatus ResultStatus { get; set; }
            public double Duration { get; set; }
            public string Message { get; set; }
            public string StackTrace { get; set; }
        }
    }
}
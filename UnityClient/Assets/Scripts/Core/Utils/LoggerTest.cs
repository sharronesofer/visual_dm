using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;

namespace Core.Utils.Tests
{
    public class LoggerTest : MonoBehaviour
    {
        private Logger logger;

        void Start()
        {
            // Get the logger instance
            logger = Logger.Instance;
            
            // Run the tests
            TestBasicLogging();
            TestContextLogging();
            TestChildLoggers();
            TestErrorLogging();
            TestLogLevels();
            TestFileLogging();
            TestAsyncLogging();
            
            Debug.Log("Logger tests complete!");
        }

        void TestBasicLogging()
        {
            Debug.Log("Running basic logging test...");
            
            // Log messages at different levels
            logger.Debug("This is a debug message");
            logger.Info("This is an info message");
            logger.Warn("This is a warning message");
            logger.Error("This is an error message");
            logger.Critical("This is a critical message");
        }

        void TestContextLogging()
        {
            Debug.Log("Running context logging test...");
            
            // Create a context dictionary
            var context = new Dictionary<string, object>
            {
                { "userId", 12345 },
                { "action", "login" },
                { "timestamp", DateTime.UtcNow }
            };
            
            // Log with context
            logger.Info("User logged in", context);
        }

        void TestChildLoggers()
        {
            Debug.Log("Running child loggers test...");
            
            // Create child loggers
            var authLogger = logger.CreateChild("Auth");
            var apiLogger = logger.CreateChild("API");
            var dbLogger = authLogger.CreateChild("Database");
            
            // Log messages with different loggers
            authLogger.Info("Authentication service started");
            apiLogger.Info("API service started");
            dbLogger.Info("Connected to database");
        }

        void TestErrorLogging()
        {
            Debug.Log("Running error logging test...");
            
            try
            {
                // Simulate an error
                throw new InvalidOperationException("Something went wrong!");
            }
            catch (Exception ex)
            {
                // Log the error with the exception
                logger.Error("An error occurred during operation", ex);
            }
        }

        void TestLogLevels()
        {
            Debug.Log("Running log levels test...");
            
            // Create a new logger config
            var config = new LoggerConfig
            {
                MinLevel = LogLevel.WARNING,
                EnableConsole = true
            };
            
            // Configure the logger
            logger.Configure(config);
            
            // These should not appear in the output
            logger.Debug("This debug message should not appear");
            logger.Info("This info message should not appear");
            
            // These should appear
            logger.Warn("This warning message should appear");
            logger.Error("This error message should appear");
            
            // Reset to default
            config.MinLevel = LogLevel.DEBUG;
            logger.Configure(config);
        }

        void TestFileLogging()
        {
            Debug.Log("Running file logging test...");
            
            // Create a new logger config with file output
            var config = new LoggerConfig
            {
                EnableConsole = true,
                EnableFileOutput = true,
                LogFilePath = Application.persistentDataPath + "/test_log.txt"
            };
            
            // Configure the logger
            logger.Configure(config);
            
            // Log some messages that should go to file
            logger.Info("This message should go to the log file");
            logger.Warn("This warning should go to the log file");
            
            Debug.Log($"Log file should be created at: {Application.persistentDataPath}/test_log.txt");
        }

        void TestAsyncLogging()
        {
            Debug.Log("Running async logging test...");
            
            // Log some messages asynchronously
            logger.InfoAsync("This is an async info message");
            logger.WarnAsync("This is an async warning message");
            logger.ErrorAsync("This is an async error message");
            
            // Log with context asynchronously
            var context = new Dictionary<string, object>
            {
                { "asyncTest", true },
                { "timestamp", DateTime.UtcNow }
            };
            
            logger.InfoAsync("Async message with context", context);
        }
    }
} 
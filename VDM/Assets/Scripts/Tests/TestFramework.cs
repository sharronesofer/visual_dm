using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;

namespace VDM.Tests
{
    /// <summary>
    /// Base class for all test classes that provides common setup, teardown, and utility methods.
    /// </summary>
    public abstract class TestFramework
    {
        protected GameObject _testContainer;
        
        [SetUp]
        public virtual void Setup()
        {
            // Create a test container that will be automatically cleaned up after tests
            _testContainer = new GameObject("TestContainer");
            
            // Log test start
            Debug.Log($"Starting test: {TestContext.CurrentContext.Test.Name}");
        }
        
        [TearDown]
        public virtual void TearDown()
        {
            // Log test end with status
            Debug.Log($"Finished test: {TestContext.CurrentContext.Test.Name} - Status: {(TestContext.CurrentContext.Result.Status)}");
            
            // Destroy test container and all child objects
            if (_testContainer != null)
            {
                GameObject.Destroy(_testContainer);
            }
            
            // Force a GC collection to clean up any lingering references
            System.GC.Collect();
        }
        
        /// <summary>
        /// Creates a GameObject as a child of the test container.
        /// </summary>
        /// <param name="name">The name of the GameObject to create.</param>
        /// <returns>The created GameObject.</returns>
        protected GameObject CreateGameObject(string name)
        {
            GameObject obj = new GameObject(name);
            obj.transform.SetParent(_testContainer.transform);
            return obj;
        }
        
        /// <summary>
        /// Creates a component of type T on a new GameObject as a child of the test container.
        /// </summary>
        /// <typeparam name="T">The type of component to create.</typeparam>
        /// <param name="name">The name of the GameObject to create.</param>
        /// <returns>The created component.</returns>
        protected T CreateComponent<T>(string name) where T : Component
        {
            GameObject obj = CreateGameObject(name);
            return obj.AddComponent<T>();
        }
        
        /// <summary>
        /// Waits for a condition to be true, with timeout.
        /// </summary>
        /// <param name="condition">The condition to check.</param>
        /// <param name="timeout">The maximum time to wait in seconds.</param>
        /// <param name="checkInterval">The interval between condition checks in seconds.</param>
        /// <returns>An IEnumerator for use with StartCoroutine.</returns>
        protected IEnumerator WaitForCondition(Func<bool> condition, float timeout = 5f, float checkInterval = 0.1f)
        {
            float startTime = Time.time;
            
            while (!condition() && (Time.time - startTime) < timeout)
            {
                yield return new WaitForSeconds(checkInterval);
            }
            
            if (!condition())
            {
                Debug.LogWarning($"Condition not met after {timeout} seconds");
            }
        }
        
        /// <summary>
        /// Asserts that a condition becomes true within a timeout period.
        /// </summary>
        /// <param name="condition">The condition to check.</param>
        /// <param name="message">The message to display if the assertion fails.</param>
        /// <param name="timeout">The maximum time to wait in seconds.</param>
        /// <returns>An IEnumerator for use with Unity tests.</returns>
        protected IEnumerator AssertEventually(Func<bool> condition, string message, float timeout = 5f)
        {
            float startTime = Time.time;
            bool conditionMet = false;
            
            while (!conditionMet && (Time.time - startTime) < timeout)
            {
                conditionMet = condition();
                if (conditionMet) break;
                yield return null;
            }
            
            Assert.IsTrue(conditionMet, $"{message} (timed out after {timeout} seconds)");
        }
        
        /// <summary>
        /// Creates a test exception for testing error handling.
        /// </summary>
        /// <param name="message">The exception message.</param>
        /// <returns>A new Exception.</returns>
        protected Exception CreateTestException(string message = "Test exception")
        {
            return new Exception(message);
        }
        
        /// <summary>
        /// Logs a test step message with the current test name.
        /// </summary>
        /// <param name="step">The test step description.</param>
        protected void LogTestStep(string step)
        {
            Debug.Log($"[{TestContext.CurrentContext.Test.Name}] {step}");
        }
    }
} 
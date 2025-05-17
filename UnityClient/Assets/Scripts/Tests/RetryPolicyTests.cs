using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Core.Utils;
using Cysharp.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Tests
{
    public class RetryPolicyTests
    {
        private class TestRetryableException : Exception
        {
            public TestRetryableException(string message) : base(message) { }
        }

        private class NonRetryableException : Exception
        {
            public NonRetryableException(string message) : base(message) { }
        }

        private Logger _logger;
        private LogHandler _logHandler;

        // Setup method to create a logger for tests
        [SetUp]
        public void Setup()
        {
            _logHandler = new TestLogHandler();
            _logger = new Logger("RetryTests");
            _logger.AddHandler(_logHandler);
        }

        // Test helper to create a mock function that fails a specified number of times
        private Func<T> CreateFailingFunc<T>(T result, int failCount, Exception exception)
        {
            int counter = 0;
            return () =>
            {
                counter++;
                if (counter <= failCount)
                {
                    throw exception;
                }
                return result;
            };
        }

        private Task<T> DelayedTask<T>(T result, int delayMs = 10)
        {
            return Task.Delay(delayMs).ContinueWith(_ => result);
        }

        private async UniTask<T> DelayedUniTask<T>(T result, int delayMs = 10)
        {
            await UniTask.Delay(delayMs);
            return result;
        }

        [Test]
        public void Execute_SucceedsFirstAttempt_ReturnsResult()
        {
            // Arrange
            var policy = new RetryPolicy(new RetryOptions(), _logger);
            
            // Act
            int result = policy.Execute(() => 42);
            
            // Assert
            Assert.AreEqual(42, result);
        }

        [Test]
        public void Execute_SucceedsAfterRetries_ReturnsResult()
        {
            // Arrange
            var policy = new RetryPolicy(new RetryOptions
            {
                MaxAttempts = 3,
                InitialDelayMs = 10,
                Jitter = false
            }, _logger);
            
            var func = CreateFailingFunc(42, 2, new TestRetryableException("Temporary error"));
            
            // Act
            int result = policy.Execute(func);
            
            // Assert
            Assert.AreEqual(42, result);
        }

        [Test]
        public void Execute_MaxAttemptsExceeded_ThrowsException()
        {
            // Arrange
            var policy = new RetryPolicy(new RetryOptions
            {
                MaxAttempts = 3,
                InitialDelayMs = 10,
                Jitter = false
            }, _logger);
            
            var func = CreateFailingFunc(42, 4, new TestRetryableException("Persistent error"));
            
            // Act & Assert
            Assert.Throws<TestRetryableException>(() => policy.Execute(func));
        }

        [Test]
        public void Execute_NonRetryableException_DoesNotRetry()
        {
            // Arrange
            var policy = new RetryPolicy(new RetryOptions
            {
                MaxAttempts = 3,
                InitialDelayMs = 10,
                RetryableExceptions = new[] { typeof(TestRetryableException) }
            }, _logger);
            
            var counter = 0;
            Func<int> func = () =>
            {
                counter++;
                if (counter == 1)
                {
                    throw new NonRetryableException("Not retryable");
                }
                return 42;
            };
            
            // Act & Assert
            Assert.Throws<NonRetryableException>(() => policy.Execute(func));
            Assert.AreEqual(1, counter, "Function should only be called once for non-retryable exceptions");
        }

        [Test]
        public void Execute_CallsOnRetryCallback()
        {
            // Arrange
            var callbackCounter = 0;
            var exceptions = new List<Exception>();
            
            var policy = new RetryPolicy(new RetryOptions
            {
                MaxAttempts = 3,
                InitialDelayMs = 10,
                OnRetry = (attempt, ex) =>
                {
                    callbackCounter++;
                    exceptions.Add(ex);
                }
            }, _logger);
            
            var func = CreateFailingFunc(42, 2, new TestRetryableException("Error"));
            
            // Act
            policy.Execute(func);
            
            // Assert
            Assert.AreEqual(2, callbackCounter, "OnRetry should be called for each retry");
            Assert.AreEqual(2, exceptions.Count);
            Assert.IsTrue(exceptions[0] is TestRetryableException);
            Assert.IsTrue(exceptions[1] is TestRetryableException);
        }

        [UnityTest]
        public IEnumerator ExecuteAsync_SucceedsFirstAttempt_ReturnsResult() => UniTask.ToCoroutine(async () =>
        {
            // Arrange
            var policy = new RetryPolicy(new RetryOptions(), _logger);
            
            // Act
            int result = await policy.ExecuteAsync(() => DelayedTask(42));
            
            // Assert
            Assert.AreEqual(42, result);
        });

        [UnityTest]
        public IEnumerator ExecuteAsync_SucceedsAfterRetries_ReturnsResult() => UniTask.ToCoroutine(async () =>
        {
            // Arrange
            var policy = new RetryPolicy(new RetryOptions
            {
                MaxAttempts = 3,
                InitialDelayMs = 10,
                Jitter = false
            }, _logger);
            
            int counter = 0;
            Func<Task<int>> func = async () =>
            {
                counter++;
                if (counter <= 2)
                {
                    throw new TestRetryableException($"Error {counter}");
                }
                return await DelayedTask(42);
            };
            
            // Act
            int result = await policy.ExecuteAsync(func);
            
            // Assert
            Assert.AreEqual(42, result);
            Assert.AreEqual(3, counter);
        });

        [UnityTest]
        public IEnumerator ExecuteAsync_MaxAttemptsExceeded_ThrowsException() => UniTask.ToCoroutine(async () =>
        {
            // Arrange
            var policy = new RetryPolicy(new RetryOptions
            {
                MaxAttempts = 2,
                InitialDelayMs = 10
            }, _logger);
            
            int counter = 0;
            Func<Task<int>> func = async () =>
            {
                counter++;
                throw new TestRetryableException("Persistent error");
            };
            
            // Act & Assert
            TestRetryableException ex = null;
            try
            {
                await policy.ExecuteAsync(func);
            }
            catch (TestRetryableException e)
            {
                ex = e;
            }
            
            Assert.IsNotNull(ex);
            Assert.AreEqual(2, counter);
        });

        [UnityTest]
        public IEnumerator ExecuteAsync_CancellationRequested_ThrowsOperationCanceledException() => UniTask.ToCoroutine(async () =>
        {
            // Arrange
            var policy = new RetryPolicy(new RetryOptions
            {
                MaxAttempts = 3,
                InitialDelayMs = 10
            }, _logger);
            
            var cts = new CancellationTokenSource();
            
            int counter = 0;
            Func<Task<int>> func = async () =>
            {
                counter++;
                if (counter == 1)
                {
                    // Cancel after the first failure
                    cts.Cancel();
                    throw new TestRetryableException("Error");
                }
                return await DelayedTask(42);
            };
            
            // Act & Assert
            bool wasCancelled = false;
            try
            {
                await policy.ExecuteAsync(func, cts.Token);
            }
            catch (OperationCanceledException)
            {
                wasCancelled = true;
            }
            
            Assert.IsTrue(wasCancelled, "Should throw OperationCanceledException when cancellation is requested");
            Assert.AreEqual(1, counter, "Function should only be called once when cancelled");
        });

        [UnityTest]
        public IEnumerator ExecuteUniTask_SucceedsAfterRetries_ReturnsResult() => UniTask.ToCoroutine(async () =>
        {
            // Arrange
            var policy = new RetryPolicy(new RetryOptions
            {
                MaxAttempts = 3,
                InitialDelayMs = 10,
                Jitter = false
            }, _logger);
            
            int counter = 0;
            Func<UniTask<int>> func = async () =>
            {
                counter++;
                if (counter <= 2)
                {
                    throw new TestRetryableException($"Error {counter}");
                }
                return await DelayedUniTask(42);
            };
            
            // Act
            int result = await policy.ExecuteUniTask(func);
            
            // Assert
            Assert.AreEqual(42, result);
            Assert.AreEqual(3, counter);
        });

        [Test]
        public void WithRetry_ExtensionMethod_SucceedsAfterRetry()
        {
            // Arrange
            int counter = 0;
            Func<int> func = () =>
            {
                counter++;
                if (counter == 1)
                {
                    throw new TestRetryableException("Error");
                }
                return 42;
            };
            
            var options = new RetryOptions
            {
                MaxAttempts = 2,
                InitialDelayMs = 10
            };
            
            // Act
            int result = func.WithRetry(options);
            
            // Assert
            Assert.AreEqual(42, result);
            Assert.AreEqual(2, counter);
        }

        [UnityTest]
        public IEnumerator WithRetryAsync_ExtensionMethod_SucceedsAfterRetry() => UniTask.ToCoroutine(async () =>
        {
            // Arrange
            int counter = 0;
            Func<Task<int>> func = async () =>
            {
                counter++;
                if (counter == 1)
                {
                    throw new TestRetryableException("Error");
                }
                return await DelayedTask(42);
            };
            
            var options = new RetryOptions
            {
                MaxAttempts = 2,
                InitialDelayMs = 10
            };
            
            // Act
            int result = await func.WithRetryAsync(options);
            
            // Assert
            Assert.AreEqual(42, result);
            Assert.AreEqual(2, counter);
        });

        [UnityTest]
        public IEnumerator WithRetryUniTask_ExtensionMethod_SucceedsAfterRetry() => UniTask.ToCoroutine(async () =>
        {
            // Arrange
            int counter = 0;
            Func<UniTask<int>> func = async () =>
            {
                counter++;
                if (counter == 1)
                {
                    throw new TestRetryableException("Error");
                }
                return await DelayedUniTask(42);
            };
            
            var options = new RetryOptions
            {
                MaxAttempts = 2,
                InitialDelayMs = 10
            };
            
            // Act
            int result = await func.WithRetryUniTask(options);
            
            // Assert
            Assert.AreEqual(42, result);
            Assert.AreEqual(2, counter);
        });
    }

    // Test log handler that collects log messages
    public class TestLogHandler : LogHandler
    {
        public List<(LogLevel, string, Dictionary<string, object>)> Logs { get; } = new();
        
        public override void Handle(LogLevel level, string message, Dictionary<string, object> context)
        {
            Logs.Add((level, message, context));
        }
    }
} 
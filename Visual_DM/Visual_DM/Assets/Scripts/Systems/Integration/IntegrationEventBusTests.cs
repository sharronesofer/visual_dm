using System;
using System.Diagnostics;
using NUnit.Framework;

namespace Systems.Integration.Tests
{
    public class IntegrationEventBusTests
    {
        private int _receivedCount;
        private string _lastMessage;

        [SetUp]
        public void SetUp()
        {
            _receivedCount = 0;
            _lastMessage = null;
        }

        [Test]
        public void TestMessageDelivery()
        {
            IntegrationEventBus.Instance.Subscribe<string>(OnStringMessage);
            IntegrationEventBus.Instance.Publish("test");
            Assert.AreEqual(1, _receivedCount);
            Assert.AreEqual("test", _lastMessage);
            IntegrationEventBus.Instance.Unsubscribe<string>(OnStringMessage);
        }

        [Test]
        public void TestErrorHandling()
        {
            IntegrationEventBus.Instance.Subscribe<string>(ThrowingHandler);
            Assert.DoesNotThrow(() => IntegrationEventBus.Instance.PublishWithRetry("fail", 2, 10));
            IntegrationEventBus.Instance.Unsubscribe<string>(ThrowingHandler);
        }

        [Test]
        public void TestPerformanceUnderLoad()
        {
            int count = 10000;
            int received = 0;
            void Handler(string msg) { received++; }
            IntegrationEventBus.Instance.Subscribe<string>(Handler);
            var sw = Stopwatch.StartNew();
            for (int i = 0; i < count; i++)
                IntegrationEventBus.Instance.Publish($"msg{i}");
            sw.Stop();
            Assert.AreEqual(count, received);
            Assert.Less(sw.ElapsedMilliseconds, 2000); // Should process 10k messages in under 2s
            IntegrationEventBus.Instance.Unsubscribe<string>(Handler);
        }

        private void OnStringMessage(string msg)
        {
            _receivedCount++;
            _lastMessage = msg;
        }

        private void ThrowingHandler(string msg)
        {
            throw new Exception("Handler failed");
        }
    }
} 
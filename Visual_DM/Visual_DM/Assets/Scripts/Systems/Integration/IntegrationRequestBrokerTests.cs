using System;
using NUnit.Framework;

namespace Systems.Integration.Tests
{
    public class IntegrationRequestBrokerTests
    {
        private IntegrationRequestBroker _broker;
        private int _callbackCount;
        private string _lastResponse;

        [SetUp]
        public void SetUp()
        {
            _broker = new IntegrationRequestBroker();
            _callbackCount = 0;
            _lastResponse = null;
        }

        [Test]
        public void TestRequestResponse()
        {
            var id = _broker.SendRequest<string, string>("request", OnResponse);
            _broker.CompleteRequest<string>(id, "response");
            Assert.AreEqual(1, _callbackCount);
            Assert.AreEqual("response", _lastResponse);
        }

        [Test]
        public void TestErrorHandlingAndRetry()
        {
            Assert.DoesNotThrow(() => _broker.SendRequestWithRetry<string, string>("fail", OnResponse, 2, 10));
        }

        private void OnResponse(string response)
        {
            _callbackCount++;
            _lastResponse = response;
        }
    }
} 
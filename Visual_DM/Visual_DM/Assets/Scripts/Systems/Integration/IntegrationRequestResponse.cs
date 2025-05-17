using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;
using System.Threading;

namespace Systems.Integration
{
    public class IntegrationRequest<TRequest, TResponse>
    {
        public TRequest Request;
        public Action<TResponse> Callback;
    }

    public class IntegrationRequestBroker
    {
        private readonly ConcurrentDictionary<Guid, TaskCompletionSource<object>> _pendingRequests = new ConcurrentDictionary<Guid, TaskCompletionSource<object>>();

        public Guid SendRequest<TRequest, TResponse>(TRequest request, Action<TResponse> callback)
        {
            var id = Guid.NewGuid();
            var tcs = new TaskCompletionSource<object>();
            _pendingRequests[id] = tcs;
            IntegrationEventBus.Instance.Publish(new IntegrationRequest<TRequest, TResponse> { Request = request, Callback = callback });
            return id;
        }

        public void CompleteRequest<TResponse>(Guid id, TResponse response)
        {
            if (_pendingRequests.TryRemove(id, out var tcs))
            {
                tcs.SetResult(response);
            }
        }

        public Guid SendRequestWithRetry<TRequest, TResponse>(TRequest request, Action<TResponse> callback, int maxRetries = 3, int retryDelayMs = 100)
        {
            int attempt = 0;
            bool success = false;
            Exception lastException = null;
            Guid id = Guid.Empty;
            while (attempt < maxRetries && !success)
            {
                try
                {
                    id = SendRequest(request, callback);
                    success = true;
                }
                catch (Exception ex)
                {
                    lastException = ex;
                    IntegrationLogger.Log($"[RequestBroker] SendRequest failed (attempt {attempt + 1}): {ex.Message}", LogLevel.Warn);
                    Thread.Sleep(retryDelayMs);
                }
                attempt++;
            }
            if (!success && lastException != null)
            {
                IntegrationLogger.Log($"[RequestBroker] SendRequest ultimately failed after {maxRetries} attempts: {lastException.Message}", LogLevel.Error);
                IntegrationAlerting.Alert($"RequestBroker send failure: {lastException.Message}", LogLevel.Error);
            }
            return id;
        }
    }
} 
using System;
using System.Threading.Tasks;

namespace VisualDM.Core
{
    public class RateLimiter
    {
        private int _tokens;
        private readonly int _maxTokensPerMinute = 60000; // Example: 60,000 tokens/min
        private DateTime _lastRefill = DateTime.UtcNow;
        private readonly object _lock = new object();
        private int _backoffMs = 1000;
        private const int MaxBackoffMs = 30000;
        private const int MinBackoffMs = 1000;

        public RateLimiter()
        {
            _tokens = _maxTokensPerMinute;
        }

        public bool CanProceed(int tokensNeeded = 1000)
        {
            if (tokensNeeded <= 0)
            {
                throw new ArgumentException("tokensNeeded must be positive");
            }
            lock (_lock)
            {
                Refill();
                return _tokens >= tokensNeeded;
            }
        }

        public void RegisterRequest(int tokensUsed = 1000)
        {
            if (tokensUsed <= 0)
            {
                throw new ArgumentException("tokensUsed must be positive");
            }
            lock (_lock)
            {
                _tokens = Math.Max(0, _tokens - tokensUsed);
            }
        }

        public async Task WaitForAvailabilityAsync(int tokensNeeded = 1000)
        {
            while (!CanProceed(tokensNeeded))
            {
                await Task.Delay(_backoffMs);
                _backoffMs = Math.Min(_backoffMs * 2, MaxBackoffMs); // Exponential backoff
                Refill();
            }
            _backoffMs = MinBackoffMs; // Reset after success
        }

        private void Refill()
        {
            var now = DateTime.UtcNow;
            var minutes = (now - _lastRefill).TotalMinutes;
            if (minutes > 0)
            {
                int refillAmount = (int)(_maxTokensPerMinute * minutes);
                _tokens = Math.Min(_maxTokensPerMinute, _tokens + refillAmount);
                _lastRefill = now;
            }
        }

        // TODO: Add exponential backoff and dynamic adjustment
    }
}
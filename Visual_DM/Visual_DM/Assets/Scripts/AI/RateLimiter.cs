using System;
using System.Threading.Tasks;

namespace AI
{
    public class RateLimiter
    {
        private int _tokens;
        private readonly int _maxTokensPerMinute = 60000; // Example: 60,000 tokens/min
        private DateTime _lastRefill = DateTime.UtcNow;
        private readonly object _lock = new object();

        public RateLimiter()
        {
            _tokens = _maxTokensPerMinute;
        }

        public bool CanProceed(int tokensNeeded = 1000)
        {
            lock (_lock)
            {
                Refill();
                return _tokens >= tokensNeeded;
            }
        }

        public void RegisterRequest(int tokensUsed = 1000)
        {
            lock (_lock)
            {
                _tokens = Math.Max(0, _tokens - tokensUsed);
            }
        }

        public async Task WaitForAvailabilityAsync(int tokensNeeded = 1000)
        {
            while (!CanProceed(tokensNeeded))
            {
                await Task.Delay(1000);
                Refill();
            }
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
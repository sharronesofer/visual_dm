const Redis = require('ioredis');

// Configuration for rate limits per tier
const RATE_LIMITS = {
  free: { window: 60, max: 60 }, // 60 requests per minute
  premium: { window: 60, max: 600 }, // 600 requests per minute
  enterprise: { window: 60, max: 6000 }, // 6000 requests per minute
};

// Redis client for distributed rate limiting (configure as needed)
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

/**
 * Get user tier from request (customize as needed)
 */
function getUserTier(req) {
  // Example: extract from req.user, API key, or header
  if (req.headers['x-api-tier'] === 'enterprise') return 'enterprise';
  if (req.headers['x-api-tier'] === 'premium') return 'premium';
  return 'free';
}

/**
 * Rate limiting middleware (token bucket algorithm, Redis-backed)
 */
function rateLimit(req, res, next) {
  (async () => {
    try {
      const tier = getUserTier(req);
      const window = RATE_LIMITS[tier].window;
      const max = RATE_LIMITS[tier].max;
      const key = `ratelimit:${tier}:${req.ip}`;
      const now = Math.floor(Date.now() / 1000);
      const reset = now + window;
      const current = await redis.incr(key);
      if (current === 1) {
        await redis.expire(key, window);
      }
      const remaining = Math.max(0, max - current);
      res.setHeader('X-RateLimit-Limit', max.toString());
      res.setHeader('X-RateLimit-Remaining', remaining.toString());
      res.setHeader('X-RateLimit-Reset', reset.toString());
      if (current > max) {
        res.status(429).json({
          error: 'Too Many Requests',
          message: `Rate limit exceeded. Try again in ${window} seconds.`,
        });
        return;
      }
      next();
    } catch (err) {
      // Fail open: allow requests if Redis is down, but log error
      console.error('Rate limiting error:', err);
      next();
    }
  })();
}

module.exports = { rateLimit }; 
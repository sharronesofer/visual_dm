const crypto = require('crypto');
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
// TODO: Use production logger once available as JS module
// const { Logger } = require('./utils/logger');
// const logger = Logger.getInstance();

const API_KEY_PREFIX = 'apikey:';
const USER_KEYS_PREFIX = 'userkeys:';
const API_KEY_BYTES = 32; // 256 bits

/**
 * Generate a cryptographically secure API key
 */
function generateApiKey() {
  return crypto.randomBytes(API_KEY_BYTES).toString('hex');
}

/**
 * Hash an API key for storage (never store raw keys)
 */
function hashApiKey(apiKey) {
  return crypto.createHash('sha256').update(apiKey).digest('hex');
}

/**
 * Store a new API key for a user
 * @param {string} userId
 * @param {string} [scope] - Optional scope/permissions
 * @returns {Promise<string>} The raw API key (to show to user ONCE)
 */
async function createApiKey(userId, scope = 'default') {
  const apiKey = generateApiKey();
  const hashed = hashApiKey(apiKey);
  const keyId = crypto.randomUUID();
  const now = Date.now();
  const keyData = {
    userId,
    keyId,
    scope,
    createdAt: now,
    revoked: false,
  };
  await redis.hmset(API_KEY_PREFIX + hashed, keyData);
  await redis.sadd(USER_KEYS_PREFIX + userId, hashed);
  // Log API key creation (never log raw key)
  console.log(`[APIKEY] Created key for user ${userId}, keyId ${keyId}, scope ${scope}`);
  return apiKey; // Only show to user ONCE
}

/**
 * Validate an API key and return metadata if valid
 * @param {string} apiKey
 * @returns {Promise<object|null>} Key metadata or null if invalid/revoked
 */
async function validateApiKey(apiKey) {
  const hashed = hashApiKey(apiKey);
  const keyData = await redis.hgetall(API_KEY_PREFIX + hashed);
  if (!keyData || !keyData.userId || keyData.revoked === 'true') {
    console.log(`[APIKEY] Validation failed for key hash ${hashed}`);
    return null;
  }
  console.log(`[APIKEY] Validated key for user ${keyData.userId}, keyId ${keyData.keyId}`);
  return keyData;
}

/**
 * Revoke an API key
 * @param {string} apiKey
 * @returns {Promise<boolean>} True if revoked
 */
async function revokeApiKey(apiKey) {
  const hashed = hashApiKey(apiKey);
  const exists = await redis.exists(API_KEY_PREFIX + hashed);
  if (!exists) {
    console.log(`[APIKEY] Attempted to revoke non-existent key hash ${hashed}`);
    return false;
  }
  await redis.hset(API_KEY_PREFIX + hashed, 'revoked', true);
  const keyData = await redis.hgetall(API_KEY_PREFIX + hashed);
  console.log(`[APIKEY] Revoked key for user ${keyData.userId}, keyId ${keyData.keyId}`);
  return true;
}

/**
 * Rotate (revoke old, create new) API key for a user
 * @param {string} userId
 * @param {string} oldApiKey
 * @param {string} [scope]
 * @returns {Promise<string|null>} New API key or null if old not found
 */
async function rotateApiKey(userId, oldApiKey, scope = 'default') {
  const valid = await revokeApiKey(oldApiKey);
  if (!valid) return null;
  const newKey = await createApiKey(userId, scope);
  console.log(`[APIKEY] Rotated key for user ${userId}`);
  return newKey;
}

/**
 * List all API keys for a user (hashed, for admin/debug)
 * @param {string} userId
 * @returns {Promise<Array<string>>}
 */
async function listUserApiKeys(userId) {
  const keys = await redis.smembers(USER_KEYS_PREFIX + userId);
  console.log(`[APIKEY] Listed ${keys.length} keys for user ${userId}`);
  return keys;
}

module.exports = {
  createApiKey,
  validateApiKey,
  revokeApiKey,
  rotateApiKey,
  listUserApiKeys,
}; 
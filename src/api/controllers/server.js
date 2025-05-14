const express = require('express');
const { rateLimit } = require('../middleware/rateLimit.js');
const ApiKeyService = require('../services/ApiKeyService.js');
const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('../../swagger.config.js').default || require('../../swagger.config.js');
const userService = require('../services/UserService.js');
// Import log routes controller
const { registerLogRoutes } = require('../controllers/logApi.ts');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

// Apply rate limiting middleware globally
app.use(rateLimit);

// API Key Management Endpoints (must be registered BEFORE API key middleware)
app.post('/api/apikeys', async (req, res) => {
  const { userId, scope } = req.body;
  if (!userId) return res.status(400).json({ error: 'userId is required' });
  try {
    const apiKey = await ApiKeyService.createApiKey(userId, scope);
    res.json({ apiKey }); // Only show ONCE
  } catch (err) {
    res.status(500).json({ error: 'Failed to create API key', details: err.message });
  }
});

app.post('/api/apikeys/validate', async (req, res) => {
  const { apiKey } = req.body;
  if (!apiKey) return res.status(400).json({ error: 'apiKey is required' });
  try {
    const keyData = await ApiKeyService.validateApiKey(apiKey);
    if (!keyData) return res.status(401).json({ valid: false });
    res.json({ valid: true, keyData });
  } catch (err) {
    res.status(500).json({ error: 'Failed to validate API key', details: err.message });
  }
});

app.post('/api/apikeys/revoke', async (req, res) => {
  const { apiKey } = req.body;
  if (!apiKey) return res.status(400).json({ error: 'apiKey is required' });
  try {
    const revoked = await ApiKeyService.revokeApiKey(apiKey);
    res.json({ revoked });
  } catch (err) {
    res.status(500).json({ error: 'Failed to revoke API key', details: err.message });
  }
});

app.post('/api/apikeys/rotate', async (req, res) => {
  const { userId, oldApiKey, scope } = req.body;
  if (!userId || !oldApiKey) return res.status(400).json({ error: 'userId and oldApiKey are required' });
  try {
    const newApiKey = await ApiKeyService.rotateApiKey(userId, oldApiKey, scope);
    if (!newApiKey) return res.status(404).json({ error: 'Old API key not found' });
    res.json({ apiKey: newApiKey });
  } catch (err) {
    res.status(500).json({ error: 'Failed to rotate API key', details: err.message });
  }
});

app.get('/api/apikeys/:userId', async (req, res) => {
  const { userId } = req.params;
  try {
    const keys = await ApiKeyService.listUserApiKeys(userId);
    res.json({ keys });
  } catch (err) {
    res.status(500).json({ error: 'Failed to list API keys', details: err.message });
  }
});

// Serve OpenAPI spec as JSON
app.get('/api/openapi.json', (req, res) => {
  res.json(swaggerDocument);
});

// Serve Swagger UI
app.use('/api/docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// Register API key validation middleware AFTER /api/apikeys and docs endpoints
app.use('/api', requireApiKey);

// Register RBAC log routes with tamper-proof audit trails
registerLogRoutes(app);

// Example endpoint (must be registered AFTER API key middleware to be protected)
app.get('/api/test', (req, res) => {
  res.json({ message: 'Rate limiting is working!' });
});

// MFA endpoints
app.post('/api/users/:userId/mfa/setup', authenticateToken, async (req, res) => {
  try {
    const userId = req.params.userId;
    // Ensure user can only setup MFA for themselves
    if (req.user.userId !== userId) {
      return res.status(403).json({ message: 'Unauthorized' });
    }

    const result = await userService.setupMfa(userId);

    if (!result.success) {
      return res.status(400).json({ message: result.error });
    }

    // Generate QR code
    const qrCode = await require('qrcode').toDataURL(result.data.otpauth_url);
    result.data.qrcode = qrCode;

    res.json(result.data);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

app.post('/api/users/:userId/mfa/enable', authenticateToken, async (req, res) => {
  try {
    const userId = req.params.userId;
    const { token } = req.body;

    // Ensure user can only enable MFA for themselves
    if (req.user.userId !== userId) {
      return res.status(403).json({ message: 'Unauthorized' });
    }

    if (!token) {
      return res.status(400).json({ message: 'Token is required' });
    }

    const result = await userService.enableMfa(userId, token);

    if (!result.success) {
      return res.status(400).json({ message: result.error });
    }

    res.json(result.data);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

app.post('/api/mfa/verify', async (req, res) => {
  try {
    const { userId, token, isBackupCode } = req.body;

    if (!userId || !token) {
      return res.status(400).json({ message: 'User ID and token are required' });
    }

    const result = await userService.verifyMfa({
      userId,
      token,
      isBackupCode: isBackupCode || false
    });

    if (!result.success) {
      return res.status(400).json({ message: result.error });
    }

    res.json(result.data);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

app.post('/api/users/:userId/mfa/disable', authenticateToken, requireMfa, async (req, res) => {
  try {
    const userId = req.params.userId;

    // Ensure user can only disable MFA for themselves
    if (req.user.userId !== userId) {
      return res.status(403).json({ message: 'Unauthorized' });
    }

    const result = await userService.disableMfa(userId);

    if (!result.success) {
      return res.status(400).json({ message: result.error });
    }

    res.json(result.data);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

app.get('/api/users/:userId/mfa/backup-codes', authenticateToken, requireMfa, async (req, res) => {
  try {
    const userId = req.params.userId;

    // Ensure user can only view their own backup codes
    if (req.user.userId !== userId) {
      return res.status(403).json({ message: 'Unauthorized' });
    }

    const userResult = await userService.findById(userId);

    if (!userResult.success || !userResult.data) {
      return res.status(404).json({ message: 'User not found' });
    }

    const user = userResult.data;

    if (!user.mfaEnabled || !user.mfaBackupCodes) {
      return res.status(400).json({ message: 'MFA is not enabled or backup codes not available' });
    }

    res.json(user.mfaBackupCodes);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

app.post('/api/users/:userId/mfa/backup-codes/regenerate', authenticateToken, requireMfa, async (req, res) => {
  try {
    const userId = req.params.userId;

    // Ensure user can only regenerate their own backup codes
    if (req.user.userId !== userId) {
      return res.status(403).json({ message: 'Unauthorized' });
    }

    const userResult = await userService.findById(userId);

    if (!userResult.success || !userResult.data) {
      return res.status(404).json({ message: 'User not found' });
    }

    const user = userResult.data;

    if (!user.mfaEnabled) {
      return res.status(400).json({ message: 'MFA is not enabled' });
    }

    // Generate new backup codes
    const backupCodes = require('../../utils/mfa').generateBackupCodes();

    // Update the user with new backup codes
    const updateResult = await userService.update(userId, {
      mfaBackupCodes: backupCodes
    });

    if (!updateResult.success) {
      return res.status(400).json({ message: updateResult.error });
    }

    res.json(backupCodes);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

function requireApiKey(req, res, next) {
  console.log('API key middleware:', req.path);
  // Allow open access to API key management endpoints and docs
  if (req.path.startsWith('/apikeys') || req.path.startsWith('/docs') || req.path.startsWith('/openapi.json')) return next();
  const apiKey = req.headers['x-api-key'];
  if (!apiKey) return res.status(401).json({ error: 'API key required' });
  ApiKeyService.validateApiKey(apiKey)
    .then(keyData => {
      if (!keyData) return res.status(401).json({ error: 'Invalid or revoked API key' });
      req.apiKeyData = keyData; // Attach key data to request for downstream use
      next();
    })
    .catch(() => res.status(500).json({ error: 'API key validation error' }));
}

app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`);
}); 
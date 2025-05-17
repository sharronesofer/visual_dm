const express = require('express');
const { rateLimit } = require('../../middleware/rateLimit.js');
// const ApiKeyService = require('../services/ApiKeyService.js'); // TODO: Re-implement or restore when available
const swaggerUi = require('swagger-ui-express');
const swaggerDocument = require('../../swagger.config.js').default || require('../../swagger.config.js');
const userService = require('../services/UserService.js');
// Import log routes controller
const { registerLogRoutes } = require('../controllers/logApi.ts');
const { registerEmotionRoutes, emotionEventBus } = require('./emotionApi');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

// Apply rate limiting middleware globally
app.use(rateLimit);

// Serve OpenAPI spec as JSON
app.get('/api/openapi.json', (req, res) => {
  res.json(swaggerDocument);
});

// Serve Swagger UI
app.use('/api/docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

// Register emotion API routes
registerEmotionRoutes(app);

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

// --- WebSocket server for emotion events ---
const http = require('http');
const WebSocket = require('ws');
const server = http.createServer(app);
const wss = new WebSocket.Server({ server, path: '/ws/emotions' });

const clients = new Set();

wss.on('connection', ws => {
  clients.add(ws);
  ws.on('close', () => clients.delete(ws));
});

emotionEventBus.subscribe(event => {
  const data = JSON.stringify(event);
  for (const ws of clients) {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(data);
    }
  }
});

server.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`);
  console.log(`WebSocket server running on ws://localhost:${PORT}/ws/emotions`);
}); 
# Security Reference

## Security Controls
- All sensitive data stored in Kubernetes Secrets
- TLS/SSL enforced via cert-manager and Let's Encrypt
- Ingress configured for HTTPS-only access
- Pod security contexts enforce non-root, drop all capabilities, and read-only root filesystems
- Default-deny NetworkPolicy restricts pod communication

## RBAC
- Role-based access control implemented with least privilege
- Service accounts scoped to namespace and role
- RoleBindings documented in `k8s/rbac.yaml`

## Network Policies
- Default deny all ingress/egress
- Explicit allow rules for web-to-db, web-to-redis, and monitoring/logging
- NetworkPolicy manifests in `k8s/networkpolicy.yaml`

## Image Scanning
- Trivy integrated in CI/CD pipeline for vulnerability scanning
- Build fails on critical/high vulnerabilities
- Regular scheduled scans recommended

## Secret Management
- Use Kubernetes Secrets for all sensitive values
- For production, recommend external secret manager (e.g., HashiCorp Vault)
- Rotate secrets and monitor for exposure 

# Security Implementation Guide

This document outlines the security measures implemented in the Visual DM Backend application.

## Overview

The application implements multiple layers of security through middleware components:
- Cross-Origin Resource Sharing (CORS) configuration
- Essential security headers
- Advanced security features
- Rate limiting

## CORS Configuration

CORS is configured in `app/core/middleware/security.py` through the `setup_cors` function.

### Key Features
- Environment-aware configuration using `config.api.cors_origins`
- Default development origin: `http://localhost:3000`
- Restricted HTTP methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
- Specific allowed headers for security
- Preflight request caching (1 hour)

### Example Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        # ... other headers
    ]
)
```

## Security Headers

Security headers are implemented in `app/core/middleware/security.py` through the `SecurityHeadersMiddleware`.

### Basic Security Headers
- **X-Content-Type-Options**: `nosniff`
  - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY`
  - Prevents clickjacking attacks
- **X-XSS-Protection**: `1; mode=block`
  - Additional XSS protection
- **Referrer-Policy**: `strict-origin-when-cross-origin`
  - Controls referrer information

### Advanced Security Headers
- **Permissions-Policy**
  - Restricts browser feature access
  - Disabled features: accelerometer, camera, geolocation, etc.
- **Cross-Origin Policies**
  - Embedder-Policy: `require-corp`
  - Opener-Policy: `same-origin`
  - Resource-Policy: `same-origin`

### Production-Only Headers
- **Strict-Transport-Security (HSTS)**
  - Max age: 1 year
  - Includes subdomains
- **Expect-CT**
  - Enforces Certificate Transparency
  - Max age: 24 hours
- **Content-Security-Policy (CSP)**
  - Restrictive default-src
  - Limited script and style sources
  - Frame ancestors disabled
  - Form submissions restricted
  - Object/plugin execution disabled
  - Trusted Types enabled

## Rate Limiting

Rate limiting is implemented in `app/core/middleware/rate_limit.py` through the `RateLimitMiddleware`.

### Features
- IP-based rate limiting
- Default: 60 requests per minute
- X-Forwarded-For support
- Only active in production
- Rate limit headers:
  - X-RateLimit-Limit
  - X-RateLimit-Remaining

### Example Response Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
```

## Cookie Security

Secure cookie configuration is applied in production:
- HttpOnly: Prevents JavaScript access
- Secure: HTTPS-only
- SameSite=Strict: CSRF protection
- Path=/: Root path scope

## Cache Control

API endpoints (`/api/*`) include cache prevention headers:
- Cache-Control: no-store, no-cache, must-revalidate
- Pragma: no-cache
- Expires: 0

## Environment-Specific Configuration

The security implementation adapts based on the environment:

### Development
- CORS allows localhost
- Rate limiting disabled
- Some security headers relaxed

### Production
- Strict CORS configuration
- Rate limiting enabled
- Full security headers
- HSTS enabled
- CSP enforced
- Secure cookies required

## Implementation Files

- `app/core/middleware/security.py`: CORS and security headers
- `app/core/middleware/rate_limit.py`: Rate limiting
- `app/main.py`: Middleware configuration
- `app/core/config.py`: Environment configuration

## Testing Security Implementation

### Manual Testing
1. Use browser developer tools to verify headers
2. Test CORS with cross-origin requests
3. Verify rate limiting functionality
4. Check CSP restrictions

### Automated Testing
1. Use OWASP ZAP for security scanning
2. Run penetration tests
3. Verify header presence and values
4. Test rate limiting thresholds

### Security Tools
- [Mozilla Observatory](https://observatory.mozilla.org/)
- [SecurityHeaders.com](https://securityheaders.com)
- [OWASP ZAP](https://www.zaproxy.org/)

## Best Practices

1. **Regular Auditing**
   - Monitor security headers
   - Review rate limiting effectiveness
   - Update CSP as needed

2. **Environment Awareness**
   - Use strict settings in production
   - Maintain development flexibility
   - Never expose sensitive data

3. **Maintenance**
   - Keep dependencies updated
   - Monitor security advisories
   - Update configurations as needed

## Troubleshooting

### Common Issues

1. CORS Errors
   ```
   Access-Control-Allow-Origin header missing
   ```
   - Verify origin in config
   - Check CORS middleware configuration

2. Rate Limiting
   ```
   429 Too Many Requests
   ```
   - Check client IP detection
   - Verify rate limit settings

3. CSP Violations
   ```
   Content Security Policy violation
   ```
   - Review CSP directives
   - Check browser console for details

## Security Contacts

For security concerns or questions:
- Security Team: security@visualdm.com
- Bug Reports: https://github.com/visualdm/backend/security 

# Replay/Exploit Protection System

## Overview
This system prevents replay attacks and malicious reuse of valid requests for all critical actions (e.g., purchases, combat, permission changes) by requiring a unique action ID with each request. The backend validates, stores, and enforces a time window for each action ID, rejecting duplicates or expired IDs.

## Action ID Generation

### Python (Backend)
Use the `generate_action_id(session_id)` function from `app/core/validation/helpers.py`:
```python
action_id = generate_action_id(user_id)
```
- Combines high-precision timestamp, cryptographically secure random nonce, and user/session ID.

### C# (Unity Client)
Use the `IdGenerator.GenerateActionId(sessionId)` method:
```csharp
string actionId = IdGenerator.GenerateActionId(sessionId);
```
- Same structure as backend: timestamp, secure random nonce, session/user ID.

## Validation and Storage
- Backend endpoints require `action_id` in the request payload for all critical actions.
- The backend validates:
  - Action ID is present
  - Not previously used (checked via Redis or in-memory fallback)
  - Within a 5-minute window (configurable)
- Used action IDs are stored with a TTL (time-to-live) to prevent replay.

## Integration Points
- **Backend:**
  - `app/api/routes/player_actions.py` (purchases, combat, etc.)
  - Decorators and middleware enforce validation and storage.
- **Unity Client:**
  - `ActionQueue`, `CombatStateManager`, and all critical request senders include the action ID in payloads.

## Logging and Auditing
- All rejected replay attempts (missing, duplicate, or expired action IDs) are logged via the `log_replay_attempt` function/module.
- Logs include user ID, action type, reason, and request data for security auditing.

## Best Practices
- Always generate a new action ID for each critical action.
- Never reuse action IDs.
- Ensure the session/user ID is unique and consistent across client and server.
- Extend replay protection to any new critical endpoints or actions.

## Example: Python Backend
```python
from app.core.validation.helpers import generate_action_id
from app.core.replay_protection import validate_action_id, store_action_id

# In endpoint:
action_id = request.json.get('action_id')
user_id = get_jwt_identity()
if not action_id or not validate_action_id(action_id, user_id):
    raise ValidationError("Invalid or replayed action_id.")
store_action_id(action_id, user_id)
```

## Example: C# Unity Client
```csharp
string actionId = IdGenerator.GenerateActionId(sessionId);
request.action_id = actionId;
// Send request to backend
```

## Troubleshooting & FAQ
- **Q: What if Redis is unavailable?**
  - The backend falls back to an in-memory store (not recommended for production).
- **Q: What if the client clock is skewed?**
  - The backend enforces a time window; ensure client clocks are reasonably accurate.
- **Q: How do I extend replay protection to a new endpoint?**
  - Require `action_id` in the request, validate and store it using the provided helpers.

For further details, see the implementation in `app/core/validation/helpers.py`, `app/core/replay_protection.py`, and `Visual_DM/Visual_DM/Assets/Scripts/Core/IdGenerator.cs`. 
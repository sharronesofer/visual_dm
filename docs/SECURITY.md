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
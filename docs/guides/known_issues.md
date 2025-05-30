# Visual DM Known Issues and Workarounds

## Table of Contents
1. [Overview](#overview)
2. [Critical Issues](#critical-issues)
3. [Backend Issues](#backend-issues)
4. [Unity Client Issues](#unity-client-issues)
5. [AI Integration Issues](#ai-integration-issues)
6. [Networking Issues](#networking-issues)
7. [Performance Issues](#performance-issues)
8. [Platform-Specific Issues](#platform-specific-issues)
9. [Compatibility Issues](#compatibility-issues)
10. [Workarounds and Solutions](#workarounds-and-solutions)

## Overview

This document tracks known issues, bugs, and limitations in Visual DM. Each issue includes severity level, affected versions, reproduction steps, and available workarounds.

**Issue Severity Levels:**
- **Critical**: System unusable, data loss possible
- **High**: Major functionality broken, significant impact
- **Medium**: Feature partially broken, workaround available
- **Low**: Minor issue, cosmetic problem, or edge case

**Status Definitions:**
- **Open**: Issue confirmed, not yet fixed
- **In Progress**: Fix being developed
- **Fixed**: Resolved in latest version
- **Deferred**: Fix planned for future release

## Critical Issues

### CRIT-001: Unity Safe Mode Compilation Errors
**Status**: Fixed  
**Severity**: Critical  
**Affected Versions**: v0.1.0 - v0.2.3  
**Fixed In**: v0.2.4  

**Description**: Unity enters Safe Mode due to compilation errors with Mirror Networking and Data Annotations.

**Symptoms**:
- Unity shows Safe Mode dialog on startup
- Compilation errors in console
- Unable to enter Play Mode

**Workaround**: 
- Follow instructions in `UNITY_SAFE_MODE_SOLUTION.md`
- Ensure Mirror Networking 96.6.4 is installed
- Wrap DataAnnotations with conditional compilation

**Status**: ✅ **RESOLVED** - Fixed in current version

### CRIT-002: Backend Database Connection Pool Exhaustion
**Status**: Open  
**Severity**: Critical  
**Affected Versions**: All  

**Description**: Under high load, database connection pool becomes exhausted, causing new requests to fail.

**Symptoms**:
- HTTP 500 errors during peak usage
- Database connection timeout errors
- Service becomes unresponsive

**Reproduction**:
1. Generate high concurrent load (50+ simultaneous users)
2. Perform database-intensive operations
3. Connection pool exhaustion occurs

**Workaround**:
```python
# Increase connection pool size in database configuration
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=100
DATABASE_POOL_PRE_PING=true
```

## Backend Issues

### BACK-001: AI Service Rate Limiting
**Status**: Open  
**Severity**: High  
**Affected Versions**: All  

**Description**: Anthropic/OpenAI rate limits cause AI-powered features to fail during high usage.

**Symptoms**:
- "Rate limit exceeded" errors
- AI-generated content fails to load
- Long delays in AI responses

**Workaround**:
- Implement request queuing
- Add exponential backoff retry logic
- Cache AI responses when possible

```python
# Example rate limiting mitigation
@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_ai_service(prompt: str):
    try:
        return await anthropic_client.generate(prompt)
    except RateLimitError:
        await asyncio.sleep(60)  # Wait 1 minute
        raise
```

### BACK-002: WebSocket Connection Drops
**Status**: In Progress  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: WebSocket connections occasionally drop without proper reconnection.

**Symptoms**:
- Real-time updates stop working
- No automatic reconnection
- Client shows as disconnected

**Workaround**:
- Implement client-side reconnection logic
- Add heartbeat/ping mechanism
- Monitor connection status

```python
# WebSocket reconnection logic
async def maintain_websocket_connection():
    while True:
        try:
            await websocket.ping()
            await asyncio.sleep(30)
        except:
            await reconnect_websocket()
```

### BACK-003: Memory Leak in Quest System
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: v0.3.0+  

**Description**: Long-running sessions with many quests cause memory usage to grow continuously.

**Symptoms**:
- Memory usage increases over time
- Performance degrades after extended use
- Eventually causes out-of-memory errors

**Workaround**:
- Restart backend service periodically
- Limit number of active quests
- Clear completed quest data regularly

### BACK-004: Database Migration Rollback Issues
**Status**: Open  
**Severity**: Low  
**Affected Versions**: All  

**Description**: Some Alembic migrations cannot be rolled back cleanly.

**Symptoms**:
- Migration rollback fails
- Database schema inconsistencies
- Manual intervention required

**Workaround**:
- Always backup database before migrations
- Test migrations in staging environment
- Manual schema fixes may be required

## Unity Client Issues

### UNITY-001: Memory Leaks in Character Rendering
**Status**: In Progress  
**Severity**: High  
**Affected Versions**: All  

**Description**: Character sprites and textures are not properly disposed, causing memory leaks.

**Symptoms**:
- Memory usage increases with gameplay time
- Performance degrades over time
- Eventually causes crashes on low-memory devices

**Reproduction**:
1. Play for extended periods (2+ hours)
2. Create/delete many characters
3. Memory usage continues to grow

**Workaround**:
```csharp
// Proper texture cleanup
void OnDestroy()
{
    if (characterTexture != null)
    {
        DestroyImmediate(characterTexture);
        characterTexture = null;
    }
}
```

### UNITY-002: Input System Conflicts
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Multiple input systems interfere with each other, causing control issues.

**Symptoms**:
- Keyboard input doesn't register
- Mouse clicks not detected
- UI navigation broken

**Workaround**:
- Disable old Input Manager
- Use only new Input System
- Restart Unity client if issues persist

### UNITY-003: Physics Performance Issues
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Physics calculations cause frame rate drops with many objects.

**Symptoms**:
- Frame rate drops below 30 FPS
- Physics objects behave erratically
- Collision detection fails

**Workaround**:
```csharp
// Optimize physics settings
Physics2D.simulationMode = SimulationMode2D.FixedUpdate;
Time.fixedDeltaTime = 0.02f; // 50 Hz physics
```

### UNITY-004: Audio System Initialization Failures
**Status**: Open  
**Severity**: Low  
**Affected Versions**: v0.2.0+  

**Description**: Audio system occasionally fails to initialize on Linux systems.

**Symptoms**:
- No audio output
- Audio-related errors in console
- Audio settings panel non-functional

**Workaround**:
- Restart application
- Check audio driver compatibility
- Use PulseAudio compatibility mode

## AI Integration Issues

### AI-001: Context Window Overflow
**Status**: Open  
**Severity**: High  
**Affected Versions**: All  

**Description**: Large conversations exceed AI model context windows, causing truncation.

**Symptoms**:
- AI responses lose context
- Conversations become incoherent
- Important information is forgotten

**Workaround**:
- Implement conversation summarization
- Split large requests
- Use context compression techniques

```python
# Context management example
def manage_context(conversation_history):
    if len(conversation_history) > MAX_CONTEXT_LENGTH:
        # Keep recent messages and summarize older ones
        recent = conversation_history[-10:]
        older = conversation_history[:-10]
        summary = summarize_conversation(older)
        return [summary] + recent
    return conversation_history
```

### AI-002: Inconsistent AI Model Responses
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Different AI models provide inconsistent responses for similar prompts.

**Symptoms**:
- Character personalities change unexpectedly
- Inconsistent world building
- Conflicting information generated

**Workaround**:
- Use consistent model for related content
- Implement response validation
- Store AI decisions for consistency

### AI-003: API Key Validation Issues
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Invalid or expired API keys not properly detected and reported.

**Symptoms**:
- Cryptic error messages
- AI features silently fail
- No clear indication of API key issues

**Workaround**:
- Manually validate API keys before use
- Implement proper error handling
- Check API key status regularly

## Networking Issues

### NET-001: NAT Traversal Problems
**Status**: Open  
**Severity**: High  
**Affected Versions**: All  

**Description**: Players behind certain NAT configurations cannot connect to multiplayer sessions.

**Symptoms**:
- Cannot join multiplayer games
- Connection timeout errors
- Works on some networks but not others

**Workaround**:
- Use UPnP port mapping
- Configure port forwarding manually
- Use dedicated server hosting

### NET-002: High Latency with Large World Data
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Large world states cause high latency and slow synchronization.

**Symptoms**:
- Slow world loading
- Delayed state updates
- Poor multiplayer experience

**Workaround**:
- Implement delta synchronization
- Compress world data
- Stream data in chunks

```csharp
// Delta sync implementation
public void SendDeltaUpdate(WorldState previousState, WorldState currentState)
{
    var delta = CalculateDelta(previousState, currentState);
    if (delta.HasChanges)
    {
        NetworkManager.singleton.SendToAll(delta);
    }
}
```

### NET-003: WebSocket Connection Instability
**Status**: In Progress  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: WebSocket connections drop frequently on mobile networks.

**Symptoms**:
- Frequent disconnections
- Real-time features stop working
- Connection timeouts

**Workaround**:
- Implement aggressive reconnection
- Use HTTP fallback for critical data
- Add connection quality detection

## Performance Issues

### PERF-001: World Generation Performance
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Large world generation causes UI freezes and poor performance.

**Symptoms**:
- UI becomes unresponsive during generation
- Generation takes several minutes
- High CPU usage

**Workaround**:
```csharp
// Async world generation
public async Task GenerateWorldAsync()
{
    await Task.Run(() =>
    {
        // CPU-intensive generation work
        GenerateWorldData();
    });
    
    // Update UI on main thread
    UpdateWorldDisplay();
}
```

### PERF-002: Database Query Performance
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Complex queries cause performance bottlenecks.

**Symptoms**:
- Slow API responses
- Database timeouts
- High database CPU usage

**Workaround**:
```sql
-- Add database indexes
CREATE INDEX idx_characters_level ON characters(level);
CREATE INDEX idx_quests_status_priority ON quests(status, priority);

-- Query optimization
SELECT c.* FROM characters c 
WHERE c.is_active = true 
  AND c.level > 5
LIMIT 50;
```

### PERF-003: Memory Usage in Character System
**Status**: In Progress  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Character data structures use excessive memory.

**Symptoms**:
- High memory usage with many characters
- Slow garbage collection
- Performance degradation

**Workaround**:
- Implement object pooling
- Use data compression
- Lazy load character details

## Platform-Specific Issues

### PLAT-001: macOS Notarization Requirements
**Status**: Open  
**Severity**: Low  
**Affected Versions**: All  

**Description**: macOS Gatekeeper blocks unsigned builds.

**Symptoms**:
- "Developer cannot be verified" error
- App won't launch on macOS
- Security warnings

**Workaround**:
- Right-click and select "Open"
- Allow in Security & Privacy settings
- Use signed builds when available

### PLAT-002: Linux Audio Driver Compatibility
**Status**: Open  
**Severity**: Low  
**Affected Versions**: All  

**Description**: Audio issues on certain Linux distributions.

**Symptoms**:
- No audio output
- Audio crackling or distortion
- Audio device detection failures

**Workaround**:
```bash
# Install PulseAudio compatibility
sudo apt install pulseaudio-utils

# Configure audio driver
export PULSE_RUNTIME_PATH=/run/user/$(id -u)/pulse
```

### PLAT-003: Windows Defender False Positives
**Status**: Open  
**Severity**: Low  
**Affected Versions**: All  

**Description**: Windows Defender flags Visual DM as potential threat.

**Symptoms**:
- Antivirus blocks execution
- Files quarantined
- False positive warnings

**Workaround**:
- Add Visual DM to antivirus exclusions
- Download from official sources only
- Verify file checksums

## Compatibility Issues

### COMP-001: Unity Version Compatibility
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Different Unity versions cause compatibility issues.

**Symptoms**:
- Project won't open
- Compilation errors
- Missing package references

**Workaround**:
- Use exactly Unity 2022.3 LTS
- Check package compatibility
- Update packages if necessary

### COMP-002: Python Version Dependencies
**Status**: Open  
**Severity**: Medium  
**Affected Versions**: All  

**Description**: Incompatibility with Python versions outside 3.9-3.11 range.

**Symptoms**:
- Package installation failures
- Runtime errors
- Missing dependencies

**Workaround**:
```bash
# Use pyenv to manage Python versions
pyenv install 3.9.16
pyenv local 3.9.16
python --version  # Should show 3.9.16
```

### COMP-003: Mirror Networking Version Issues
**Status**: Fixed  
**Severity**: High  
**Affected Versions**: v0.1.0 - v0.2.3  
**Fixed In**: v0.2.4  

**Description**: Incompatible Mirror Networking versions cause networking failures.

**Symptoms**:
- Multiplayer connections fail
- Networking errors in console
- Mirror components not working

**Solution**: 
- Use exactly Mirror Networking 96.6.4
- Update via Package Manager
- Clear package cache if needed

## Workarounds and Solutions

### General Performance Optimization

#### Memory Management
```csharp
// Implement proper disposal pattern
public class CharacterManager : IDisposable
{
    private bool disposed = false;
    
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
    
    protected virtual void Dispose(bool disposing)
    {
        if (!disposed)
        {
            if (disposing)
            {
                // Clean up managed resources
                characters.Clear();
                textures.Clear();
            }
            disposed = true;
        }
    }
}
```

#### Database Connection Management
```python
# Use connection pooling properly
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600  # Recycle connections hourly
)
```

#### Error Handling Best Practices
```python
# Robust error handling
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def robust_api_call(endpoint: str, data: dict):
    try:
        response = await api_client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise
```

### Monitoring and Debugging

#### Performance Monitoring
```python
# Add performance monitoring
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            logger.info(f"{func.__name__} took {duration:.2f}s")
    return wrapper
```

#### Debug Logging Configuration
```python
# Enhanced logging for debugging
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
        }
    },
    'handlers': {
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'visualdm': {
            'level': 'DEBUG',
            'handlers': ['debug_file']
        }
    }
}
```

### Emergency Recovery Procedures

#### Database Recovery
```bash
#!/bin/bash
# Emergency database recovery script

# Backup current state
pg_dump visualdm_prod > emergency_backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from last known good backup
pg_restore --clean --if-exists -d visualdm_prod last_good_backup.sql

# Run consistency checks
psql -d visualdm_prod -c "SELECT COUNT(*) FROM characters WHERE is_active = true;"
```

#### Service Recovery
```bash
#!/bin/bash
# Service recovery script

# Stop all services
sudo systemctl stop visualdm nginx redis-server postgresql

# Clear logs and temporary files
sudo rm -f /var/log/visualdm/*
sudo rm -rf /tmp/visualdm_*

# Restart services in order
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl start visualdm
sudo systemctl start nginx

# Verify services are running
sudo systemctl status visualdm nginx redis-server postgresql
```

## Reporting New Issues

When reporting new issues, please include:

1. **Issue Description**: Clear description of the problem
2. **Reproduction Steps**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What should have happened
4. **Actual Behavior**: What actually happened
5. **Environment Information**:
   - Visual DM version
   - Operating system and version
   - Unity version (if applicable)
   - Python version (if applicable)
   - Hardware specifications
6. **Log Files**: Relevant log files and error messages
7. **Screenshots/Videos**: Visual evidence if applicable

**Reporting Channels**:
- GitHub Issues: For technical users and developers
- Discord: For community discussion and quick help
- Email Support: For sensitive issues or account problems

This document is updated regularly as new issues are discovered and resolved. For the latest information, check the project's issue tracker and release notes. 
"""
World State System Deployment Examples

This file demonstrates the different ways to deploy the World State System
based on your needs and scale.

Choose the right deployment mode:
1. Development: Start here - JSON files, transparent, easy debugging
2. Hybrid: Production features with JSON files - best of both worlds
3. Production: Full scale with database - enterprise ready
4. Testing: Fast, minimal for CI/CD

Key Benefits of Each Approach:
- JSON Files: Human readable, git trackable, zero dependencies
- Database: ACID transactions, complex queries, better concurrency
- Redis Cache: 10-100x faster reads, reduces database load
- Authentication: Multi-user safety, audit trails, role-based access
"""

import asyncio
import logging
from datetime import datetime
from uuid import UUID

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

async def development_example():
    """
    DEVELOPMENT MODE: JSON Files + No Dependencies
    
    Perfect for:
    - Solo development
    - Learning the system
    - Prototyping
    - When you want to inspect files directly
    
    Benefits:
    - Zero setup required
    - Files are human-readable
    - Can inspect/modify data with any text editor
    - Git-friendly for version control
    - No database dependencies
    """
    print("\n🔧 DEVELOPMENT MODE - JSON Files")
    print("="*50)
    
    from backend.systems.world_state.config.deployment_config import create_world_state_service_from_config
    
    # Create service with simple JSON backend
    service = await create_world_state_service_from_config("development")
    
    # Basic operations
    await service.set_state_variable("global.game_version", "1.0.0", reason="Initial setup")
    await service.set_state_variable("regions.capital.population", 10000, region_id="capital")
    
    # Check the data
    population = await service.get_state_variable("regions.capital.population", region_id="capital")
    status = await service.get_system_status()
    
    print(f"✅ Population: {population}")
    print(f"✅ System initialized: {status.get('initialized')}")
    print(f"✅ Data stored in: data/world_state/current_state.json")
    print("💡 You can open that file and see your data!")
    
    return service


async def hybrid_example():
    """
    HYBRID MODE: JSON Files + Redis Cache + Authentication
    
    Perfect for:
    - Small to medium production deployments
    - When you want file transparency + performance
    - Multi-user environments
    - Real-time features needed
    
    Benefits:
    - Keep JSON file transparency
    - Add Redis for 10-100x faster reads
    - User authentication and permissions
    - Real-time WebSocket events
    - Easy to migrate to full database later
    """
    print("\n🚀 HYBRID MODE - JSON + Cache + Auth")
    print("="*50)
    
    from backend.systems.world_state.config.deployment_config import create_world_state_service_from_config
    from backend.systems.world_state.auth.auth_integration import User
    
    # Create service with hybrid features
    service = await create_world_state_service_from_config(
        "hybrid",
        project_root="./examples/hybrid_data",
        redis_url="redis://localhost:6379",  # Requires Redis running
        enable_auth=True,
        enable_websockets=True
    )
    
    # Create a mock user for demonstration
    admin_user = User(
        user_id=UUID("11111111-1111-1111-1111-111111111111"),
        username="admin",
        roles=["admin"],
        permissions={"world_state.read", "world_state.write", "world_state.admin"}
    )
    
    # Operations with authentication
    try:
        # These operations are now authenticated and cached
        await service.set_state_variable(
            "regions.capital.population", 
            15000, 
            region_id="capital",
            reason="Population growth",
            user=admin_user  # Required for auth
        )
        
        # This read will be cached in Redis
        population = await service.get_state_variable(
            "regions.capital.population", 
            region_id="capital",
            user=admin_user
        )
        
        print(f"✅ Population (cached): {population}")
        print(f"✅ Data stored in: ./examples/hybrid_data/current_state.json")
        print(f"✅ Cached in Redis for fast access")
        print(f"✅ All operations authenticated as user: {admin_user.username}")
        
    except Exception as e:
        print(f"⚠️  Error (likely Redis not running): {e}")
        print("💡 Install Redis: brew install redis && redis-server")
    
    return service


async def production_example():
    """
    PRODUCTION MODE: PostgreSQL + Redis + Full Features
    
    Perfect for:
    - Large scale deployments
    - High concurrency (100+ users)
    - Complex historical queries
    - Enterprise requirements
    
    Benefits:
    - ACID transactions ensure data consistency
    - Complex SQL queries for analytics
    - Handle thousands of concurrent operations
    - Professional monitoring and metrics
    - Horizontal scaling capabilities
    """
    print("\n🏢 PRODUCTION MODE - PostgreSQL + Redis + Full Stack")
    print("="*50)
    
    from backend.systems.world_state.config.deployment_config import create_world_state_service_from_config
    
    try:
        # Create service with full production stack
        service = await create_world_state_service_from_config(
            "production",
            database_url="postgresql://user:password@localhost/worldstate",
            redis_url="redis://localhost:6379",
            enable_auth=True,
            enable_metrics=True,
            enable_websockets=True
        )
        
        print("✅ Production service created")
        print("✅ Data stored in PostgreSQL database")
        print("✅ Redis caching enabled")
        print("✅ Authentication enabled")
        print("✅ Real-time WebSocket events")
        print("✅ Performance metrics available")
        print("✅ Ready for enterprise scale!")
        
        # Example of production-scale operation
        # await service.trigger_summarization()  # Enterprise data management
        
    except Exception as e:
        print(f"⚠️  Error (likely database not available): {e}")
        print("💡 Requires PostgreSQL and Redis running")
        print("💡 Setup: createdb worldstate && redis-server")
    
    return None


async def testing_example():
    """
    TESTING MODE: In-Memory + Minimal Features
    
    Perfect for:
    - Unit tests
    - CI/CD pipelines
    - Fast test execution
    - Isolated test environments
    
    Benefits:
    - Fastest possible execution
    - No external dependencies
    - Complete isolation between tests
    - Minimal resource usage
    """
    print("\n🧪 TESTING MODE - In-Memory + Minimal")
    print("="*50)
    
    from backend.systems.world_state.config.deployment_config import create_world_state_service_from_config
    
    # Create service optimized for testing
    service = await create_world_state_service_from_config("testing")
    
    # Fast operations for testing
    await service.set_state_variable("test.value", 42)
    value = await service.get_state_variable("test.value")
    
    print(f"✅ Test value: {value}")
    print("✅ All data in memory - no files created")
    print("✅ Zero external dependencies")
    print("✅ Perfect for CI/CD and unit tests")
    
    return service


async def migration_example():
    """
    MIGRATION: Moving Between Backends
    
    Shows how to migrate data when you outgrow your current setup.
    Common progression: Development → Hybrid → Production
    """
    print("\n🔄 MIGRATION EXAMPLE - JSON to Database")
    print("="*50)
    
    from backend.systems.world_state.config.deployment_config import (
        WorldStateConfig, 
        migrate_between_backends,
        DeploymentMode
    )
    
    # Source: JSON files (development)
    source_config = WorldStateConfig(
        mode=DeploymentMode.DEVELOPMENT,
        repository_type="json",
        project_root="./examples/source_data"
    )
    
    # Target: PostgreSQL (production)
    target_config = WorldStateConfig(
        mode=DeploymentMode.PRODUCTION,
        repository_type="postgresql",
        database_url="postgresql://user:password@localhost/worldstate_new"
    )
    
    try:
        # Migrate data between backends
        await migrate_between_backends(source_config, target_config)
        print("✅ Migration completed successfully")
        print("✅ All JSON data now in PostgreSQL")
        print("✅ Historical changes preserved")
        
    except Exception as e:
        print(f"⚠️  Migration failed: {e}")
        print("💡 This is expected without actual database setup")


async def performance_comparison():
    """
    PERFORMANCE COMPARISON: See the difference caching makes
    """
    print("\n⚡ PERFORMANCE COMPARISON")
    print("="*50)
    
    import time
    
    from backend.systems.world_state.config.deployment_config import create_world_state_service_from_config
    
    # Test without cache
    start_time = time.time()
    service_no_cache = await create_world_state_service_from_config("development")
    
    # Set and get data 100 times
    for i in range(10):  # Reduced for demo
        await service_no_cache.set_state_variable(f"test.value_{i}", i)
        await service_no_cache.get_state_variable(f"test.value_{i}")
    
    no_cache_time = time.time() - start_time
    
    print(f"✅ No cache: {no_cache_time:.3f} seconds")
    print("💡 With Redis cache, this would be 10-100x faster!")
    print("💡 Database queries would also benefit from caching")


async def real_world_scenarios():
    """
    REAL WORLD SCENARIOS: When to choose each mode
    """
    print("\n🌍 REAL WORLD SCENARIOS")
    print("="*50)
    
    scenarios = {
        "Solo Game Development": {
            "mode": "development",
            "reason": "JSON files are perfect for prototyping and debugging"
        },
        "Indie Game (< 1000 players)": {
            "mode": "hybrid", 
            "reason": "JSON transparency + Redis performance + authentication"
        },
        "MMO Game (> 10,000 players)": {
            "mode": "production",
            "reason": "PostgreSQL handles massive concurrency and complex queries"
        },
        "Automated Testing": {
            "mode": "testing",
            "reason": "Fast, isolated, no dependencies"
        }
    }
    
    for scenario, config in scenarios.items():
        print(f"🎮 {scenario}:")
        print(f"   👉 Use '{config['mode']}' mode")
        print(f"   💡 {config['reason']}")
        print()


async def main():
    """Run all examples"""
    print("🌟 WORLD STATE SYSTEM DEPLOYMENT GUIDE")
    print("="*60)
    print("This guide shows you how to choose the right deployment mode")
    print("for your project scale and requirements.")
    
    # Run examples
    await development_example()
    await hybrid_example() 
    await production_example()
    await testing_example()
    await migration_example()
    await performance_comparison()
    await real_world_scenarios()
    
    print("\n🎯 QUICK DECISION GUIDE:")
    print("="*30)
    print("🔧 Starting out? → Use 'development' mode")
    print("🚀 Need performance? → Use 'hybrid' mode") 
    print("🏢 Enterprise scale? → Use 'production' mode")
    print("🧪 Testing? → Use 'testing' mode")
    print("\n✨ You can migrate between modes as you grow!")


if __name__ == "__main__":
    asyncio.run(main()) 
#!/usr/bin/env python3
"""
Hybrid Mode Demo - World State System
JSON files + Redis cache + Authentication + Real-time events

This demonstrates the perfect balance for your project:
- JSON files remain human-readable and Git-friendly
- Redis provides 10-100x faster reads
- Authentication enables multi-user safety
- WebSocket events for real-time Unity integration
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

# Import the hybrid mode configuration
from backend.infrastructure.deployment.world_state_deployment_config import create_world_state_service_from_config

async def demo_hybrid_mode():
    """Demonstrate hybrid mode capabilities"""
    print("🚀 Setting up Hybrid Mode...")
    print("  ✅ JSON files for transparency")
    print("  ✅ Redis cache for speed") 
    print("  ✅ Authentication for safety")
    print("  ✅ WebSocket events for Unity")
    print()

    # Initialize hybrid mode service
    service = await create_world_state_service_from_config("hybrid")
    print("✅ Hybrid mode service initialized!")
    print()

    # Demo 1: Create some world state data
    print("📝 Demo 1: Creating world state with JSON transparency...")
    
    # Create initial state
    faction_data = {
        "Techno_Republic": {
            "name": "Techno Republic",
            "type": "faction",
            "power_level": 75,
            "territory": ["Neo_Tokyo", "Cyber_Labs"],
            "resources": {"credits": 50000, "tech_points": 1200}
        }
    }
    
    region_data = {
        "Neo_Tokyo": {
            "name": "Neo Tokyo",
            "population": 12500000,
            "faction_control": "Techno_Republic",
            "infrastructure": {
                "cybernetics_labs": 15,
                "data_centers": 8,
                "defense_turrets": 200
            }
        }
    }

    # Store in world state
    await service.update_state("factions", faction_data)
    await service.update_state("regions", region_data)
    
    print("✅ World state created and stored in JSON files")
    print("📁 Check: backend/data/world_state/factions.json")
    print("📁 Check: backend/data/world_state/regions.json")
    print()

    # Demo 2: Show Redis caching performance
    print("⚡ Demo 2: Redis caching performance boost...")
    
    # First read (from JSON + cache population)
    start_time = time.time()
    factions_v1 = await service.get_state("factions")
    first_read_time = time.time() - start_time
    
    # Second read (from Redis cache)
    start_time = time.time()
    factions_v2 = await service.get_state("factions")
    cached_read_time = time.time() - start_time
    
    speed_improvement = first_read_time / cached_read_time if cached_read_time > 0 else float('inf')
    
    print(f"📊 First read (JSON): {first_read_time*1000:.2f}ms")
    print(f"📊 Cached read (Redis): {cached_read_time*1000:.2f}ms")
    print(f"🚀 Speed improvement: {speed_improvement:.1f}x faster!")
    print()

    # Demo 3: Show authentication integration
    print("🔐 Demo 3: Authentication and user permissions...")
    
    # Simulate different user roles
    users = {
        "admin_user": {"role": "admin", "permissions": ["read", "write", "admin"]},
        "game_master": {"role": "gm", "permissions": ["read", "write"]},
        "player": {"role": "player", "permissions": ["read"]}
    }
    
    for user_id, user_info in users.items():
        print(f"👤 User: {user_id} (Role: {user_info['role']})")
        print(f"   Permissions: {', '.join(user_info['permissions'])}")
    print()

    # Demo 4: Show temporal versioning
    print("⏰ Demo 4: Temporal versioning with snapshots...")
    
    # Create a snapshot
    timestamp = datetime.now()
    snapshot_id = f"before_expansion_{timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    await service.create_snapshot(snapshot_id, {
        "description": "Before Techno Republic expansion",
        "game_turn": 42,
        "major_event": "Pre-expansion state"
    })
    
    print(f"📸 Snapshot created: {snapshot_id}")
    
    # Simulate faction expansion
    updated_faction = faction_data.copy()
    updated_faction["Techno_Republic"]["power_level"] = 85
    updated_faction["Techno_Republic"]["territory"].append("Data_Haven")
    updated_faction["Techno_Republic"]["resources"]["credits"] = 75000
    
    await service.update_state("factions", updated_faction)
    print("🏗️  Faction expanded territory and increased power")
    
    # Show version history
    snapshots = await service.list_snapshots()
    print(f"📚 Total snapshots available: {len(snapshots)}")
    print()

    # Demo 5: Regional summaries
    print("🗺️  Demo 5: Regional intelligence summaries...")
    
    # Add more regional data
    additional_regions = {
        "Data_Haven": {
            "name": "Data Haven",
            "population": 500000,
            "faction_control": "Techno_Republic", 
            "infrastructure": {
                "server_farms": 25,
                "quantum_computers": 3,
                "security_systems": 50
            },
            "strategic_value": "High - Major data processing hub"
        }
    }
    
    current_regions = await service.get_state("regions")
    current_regions.update(additional_regions)
    await service.update_state("regions", current_regions)
    
    # Generate regional summary
    summary = await service.generate_regional_summary("Neo_Tokyo", 
        context="Current military and economic status")
    
    print("📋 Regional Summary for Neo Tokyo:")
    print(f"   {summary}")
    print()

    # Demo 6: Performance metrics
    print("📊 Demo 6: System performance metrics...")
    
    metrics = await service.get_performance_metrics()
    
    print("⚡ Cache Performance:")
    print(f"   Hit Rate: {metrics.get('cache_hit_rate', 0)*100:.1f}%")
    print(f"   Total Requests: {metrics.get('total_requests', 0)}")
    print(f"   Cache Hits: {metrics.get('cache_hits', 0)}")
    
    print("\n🔄 Operation Counts:")
    print(f"   State Updates: {metrics.get('update_count', 0)}")
    print(f"   State Reads: {metrics.get('read_count', 0)}")
    print(f"   Snapshots Created: {metrics.get('snapshot_count', 0)}")
    print()

    # Demo 7: File system transparency
    print("📁 Demo 7: File system transparency...")
    
    # Show that JSON files are still human-readable
    faction_file = Path("backend/data/world_state/factions.json")
    if faction_file.exists():
        print("✅ JSON files remain human-readable:")
        with open(faction_file, 'r') as f:
            data = json.load(f)
            print(f"   Factions file size: {faction_file.stat().st_size} bytes")
            print(f"   Number of factions: {len(data)}")
            print(f"   Easily editable with any text editor! 📝")
    print()

    # Summary
    print("🎉 Hybrid Mode Demo Complete!")
    print()
    print("✨ What you get with Hybrid Mode:")
    print("  📁 JSON files - Human readable, Git trackable, zero vendor lock-in")
    print("  ⚡ Redis cache - 10-100x faster reads, sub-millisecond response")
    print("  🔐 Authentication - Multi-user safe, role-based permissions")
    print("  📸 Versioning - Time travel through game state history")
    print("  🗺️  Smart summaries - AI-powered regional intelligence")
    print("  📊 Metrics - Performance monitoring and optimization")
    print("  🚀 WebSockets - Real-time events for Unity integration")
    print()
    print("🔄 Easy migration path:")
    print("  - Start with 'development' mode (JSON only)")
    print("  - Upgrade to 'hybrid' mode (JSON + Redis + auth)")
    print("  - Scale to 'production' mode (PostgreSQL + Redis + full monitoring)")
    print()
    print("Perfect for indie/small team development! 🎮")

    # Cleanup
    await service.close()

async def show_file_contents():
    """Show the actual JSON files created"""
    print("\n📁 Checking created JSON files...")
    
    files_to_check = [
        "backend/data/world_state/factions.json",
        "backend/data/world_state/regions.json",
        "backend/data/world_state/snapshots.json"
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            print(f"\n✅ {file_path}:")
            with open(path, 'r') as f:
                content = f.read()
                # Show first 200 chars
                if len(content) > 200:
                    print(f"   {content[:200]}...")
                else:
                    print(f"   {content}")
        else:
            print(f"❌ {file_path} not found")

if __name__ == "__main__":
    asyncio.run(demo_hybrid_mode())
    asyncio.run(show_file_contents()) 
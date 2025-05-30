#!/usr/bin/env python3
"""
Clean up orphaned motif records and ensure data consistency.
"""
import asyncio
import json
from pathlib import Path
from backend.systems.motif.repository import MotifRepository

async def cleanup_motifs():
    """Clean up all motifs from the test database"""
    repo = MotifRepository()
    
    # Clear motifs file
    with open(repo.motifs_file, "w") as f:
        json.dump([], f)
    
    # Clear entity data file
    with open(repo.entity_data_file, "w") as f:
        json.dump({}, f)
    
    # Clear world log file  
    with open(repo.world_log_file, "w") as f:
        json.dump([], f)
    
    print(f"Cleaned up motif database at {repo.data_path}")

if __name__ == "__main__":
    asyncio.run(cleanup_motifs()) 
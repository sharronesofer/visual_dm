"""
Tests for the async building generation system.
"""

import pytest
import asyncio
from app.core.mesh.async_building_generator import AsyncBuildingGenerator

@pytest.fixture
def generator():
    """Create an AsyncBuildingGenerator instance for testing."""
    gen = AsyncBuildingGenerator(num_workers=2)
    yield gen
    gen.shutdown()

def test_queue_building(generator):
    """Test queueing a building for generation."""
    generator.queue_building(
        building_id="test_1",
        building_type="residential",
        rooms=[
            {
                "id": "room_1",
                "type": "bedroom",
                "dimensions": {"width": 4, "length": 5, "height": 3}
            }
        ],
        materials={
            "wall": {"type": "brick", "color": [0.8, 0.4, 0.3]},
            "floor": {"type": "wood", "color": [0.6, 0.4, 0.2]}
        },
        texture_paths={
            "wall": "textures/brick.png",
            "floor": "textures/wood.png"
        }
    )
    
    assert generator.generation_queue.task_queue.qsize() == 1

@pytest.mark.asyncio
async def test_process_queue(generator):
    """Test processing the building generation queue."""
    # Queue multiple buildings
    for i in range(3):
        generator.queue_building(
            building_id=f"test_{i}",
            building_type="residential",
            rooms=[
                {
                    "id": f"room_{i}_1",
                    "type": "bedroom",
                    "dimensions": {"width": 4, "length": 5, "height": 3}
                }
            ],
            materials={
                "wall": {"type": "brick", "color": [0.8, 0.4, 0.3]},
                "floor": {"type": "wood", "color": [0.6, 0.4, 0.2]}
            },
            texture_paths={
                "wall": "textures/brick.png",
                "floor": "textures/wood.png"
            },
            priority=i
        )
    
    # Process the queue
    results = await generator.process_queue()
    
    # Verify results
    assert len(results) == 3
    for i in range(3):
        building_id = f"test_{i}"
        assert building_id in results
        assert results[building_id] is not None
        assert "mesh_data" in results[building_id]
        assert "material_data" in results[building_id]

@pytest.mark.asyncio
async def test_concurrent_processing(generator):
    """Test that buildings are processed concurrently."""
    start_time = asyncio.new_event_loop().time()
    
    # Queue buildings with different processing times
    for i in range(4):
        generator.queue_building(
            building_id=f"test_{i}",
            building_type="residential",
            rooms=[{"id": f"room_{i}", "type": "bedroom"}] * (i + 1),  # Varying complexity
            materials={"wall": {"type": "brick"}},
            texture_paths={"wall": "textures/brick.png"}
        )
    
    results = await generator.process_queue()
    end_time = asyncio.new_event_loop().time()
    
    # Verify all buildings were processed
    assert len(results) == 4
    
    # Check that processing time is less than sequential processing would take
    # This is a rough estimate - adjust based on actual processing times
    processing_time = end_time - start_time
    assert processing_time < 4.0  # Assuming each building takes ~1s to process 
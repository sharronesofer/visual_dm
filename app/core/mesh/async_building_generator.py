"""
Asynchronous building generation system.
Implements multi-threading and async processing for building generation tasks.
"""

import threading
import queue
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from app.core.profiling.building_profiler import building_profiler
from app.core.mesh.optimized_mesh_generator import OptimizedMeshGenerator, AABB
from app.core.textures.texture_atlas import MaterialManager, TextureAtlas
from app.core.mesh.optimized_renderer import OptimizedMeshRenderer

logger = logging.getLogger(__name__)

@dataclass
class BuildingGenerationTask:
    """Represents a building generation task."""
    building_id: str
    building_type: str
    rooms: List[Dict]
    materials: Dict[str, Dict]
    texture_paths: Dict[str, str]
    lod: int = 2
    priority: int = 1

class BuildingGenerationQueue:
    """Manages the queue of building generation tasks."""
    
    def __init__(self, num_workers: int = 4):
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.result_queue: queue.Queue = queue.Queue()
        self.num_workers = num_workers
        self.workers: List[threading.Thread] = []
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        
        # Shared resources
        self.material_manager = MaterialManager()
        self.mesh_generator = OptimizedMeshGenerator()
        self._resource_lock = threading.Lock()
    
    def start(self) -> None:
        """Start the worker threads."""
        self.running = True
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self._worker_loop)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def stop(self) -> None:
        """Stop all worker threads."""
        self.running = False
        # Add empty tasks to unblock workers
        for _ in range(self.num_workers):
            self.task_queue.put((0, None))
        for worker in self.workers:
            worker.join()
        self.workers.clear()
    
    @building_profiler.track_component("task_processing")
    def _worker_loop(self) -> None:
        """Main worker thread loop."""
        while self.running:
            try:
                priority, task = self.task_queue.get(timeout=1)
                if task is None:
                    break
                    
                try:
                    # Process the building generation task
                    result = self._process_task(task)
                    self.result_queue.put((task.building_id, result))
                except Exception as e:
                    logger.error(f"Error processing building {task.building_id}: {e}")
                    self.result_queue.put((task.building_id, None))
                finally:
                    self.task_queue.task_done()
                    
            except queue.Empty:
                continue
    
    @building_profiler.track_component("task_processing")
    def _process_task(self, task: BuildingGenerationTask) -> Dict[str, Any]:
        """Process a single building generation task."""
        with self._resource_lock:
            # Load materials and textures
            for material_id, properties in task.materials.items():
                self.material_manager.create_material(material_id, properties)
                if material_id in task.texture_paths:
                    self.material_manager.load_material_textures(
                        material_id,
                        {material_id: task.texture_paths[material_id]}
                    )
            
            # Generate mesh
            mesh_data = self.mesh_generator.generate_building_mesh(
                task.rooms,
                task.lod
            )
            
            # Get material properties and UV coordinates
            material_data = {
                material_id: self.material_manager.get_material(material_id)
                for material_id in mesh_data.keys()
            }
            
            return {
                'mesh_data': mesh_data,
                'material_data': material_data
            }
    
    def add_task(
        self,
        building_id: str,
        building_type: str,
        rooms: List[Dict],
        materials: Dict[str, Dict],
        texture_paths: Dict[str, str],
        lod: int = 2,
        priority: int = 1
    ) -> None:
        """Add a building generation task to the queue."""
        task = BuildingGenerationTask(
            building_id=building_id,
            building_type=building_type,
            rooms=rooms,
            materials=materials,
            texture_paths=texture_paths,
            lod=lod,
            priority=priority
        )
        self.task_queue.put((-priority, task))  # Negative for highest priority first
    
    async def process_async(self) -> Dict[str, Any]:
        """Process tasks asynchronously and return results."""
        loop = asyncio.get_event_loop()
        results = {}
        
        while not (self.task_queue.empty() and self.result_queue.empty()):
            try:
                # Check for completed tasks
                building_id, result = await loop.run_in_executor(
                    None,
                    self.result_queue.get_nowait
                )
                results[building_id] = result
                self.result_queue.task_done()
            except queue.Empty:
                await asyncio.sleep(0.1)
        
        return results

class AsyncBuildingGenerator:
    """High-level interface for asynchronous building generation."""
    
    def __init__(self, num_workers: int = 4):
        self.generation_queue = BuildingGenerationQueue(num_workers)
        self.generation_queue.start()
    
    def queue_building(
        self,
        building_id: str,
        building_type: str,
        rooms: List[Dict],
        materials: Dict[str, Dict],
        texture_paths: Dict[str, str],
        lod: int = 2,
        priority: int = 1
    ) -> None:
        """Queue a building for generation."""
        self.generation_queue.add_task(
            building_id,
            building_type,
            rooms,
            materials,
            texture_paths,
            lod,
            priority
        )
    
    async def process_queue(self) -> Dict[str, Any]:
        """Process all queued buildings and return results."""
        return await self.generation_queue.process_async()
    
    def shutdown(self) -> None:
        """Shut down the generator and clean up resources."""
        self.generation_queue.stop()

# Global instance
building_generator = AsyncBuildingGenerator() 
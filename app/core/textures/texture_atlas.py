"""
Texture atlas system for efficient texture management.
Implements texture packing and atlas generation.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from PIL import Image
import logging
from dataclasses import dataclass
from app.core.profiling.building_profiler import building_profiler

logger = logging.getLogger(__name__)

@dataclass
class AtlasRegion:
    """Represents a region in the texture atlas."""
    x: int
    y: int
    width: int
    height: int
    texture_id: str
    uv_coords: Tuple[float, float, float, float]  # (u1, v1, u2, v2)

class TextureAtlas:
    """Manages texture atlases for efficient rendering."""
    
    def __init__(self, atlas_size: int = 2048):
        self.atlas_size = atlas_size
        self.regions: Dict[str, AtlasRegion] = {}
        self.atlas_image: Optional[Image.Image] = None
        self.next_x = 0
        self.next_y = 0
        self.current_row_height = 0
    
    @building_profiler.track_component("texture_loading")
    def add_texture(
        self,
        texture_id: str,
        image: Image.Image
    ) -> Optional[AtlasRegion]:
        """Add a texture to the atlas."""
        if texture_id in self.regions:
            return self.regions[texture_id]
        
        # Create atlas image if it doesn't exist
        if not self.atlas_image:
            self.atlas_image = Image.new('RGBA', (self.atlas_size, self.atlas_size))
        
        # Check if texture fits in current row
        if self.next_x + image.width > self.atlas_size:
            # Move to next row
            self.next_x = 0
            self.next_y += self.current_row_height
            self.current_row_height = 0
        
        # Check if texture fits in atlas
        if self.next_y + image.height > self.atlas_size:
            logger.warning(f"Texture {texture_id} doesn't fit in atlas")
            return None
        
        # Update current row height
        self.current_row_height = max(self.current_row_height, image.height)
        
        # Add texture to atlas
        self.atlas_image.paste(image, (self.next_x, self.next_y))
        
        # Calculate UV coordinates
        u1 = self.next_x / self.atlas_size
        v1 = self.next_y / self.atlas_size
        u2 = (self.next_x + image.width) / self.atlas_size
        v2 = (self.next_y + image.height) / self.atlas_size
        
        # Create region
        region = AtlasRegion(
            x=self.next_x,
            y=self.next_y,
            width=image.width,
            height=image.height,
            texture_id=texture_id,
            uv_coords=(u1, v1, u2, v2)
        )
        
        self.regions[texture_id] = region
        
        # Update next position
        self.next_x += image.width
        
        return region
    
    @building_profiler.track_component("texture_loading")
    def load_textures(self, texture_paths: Dict[str, str]) -> None:
        """Load multiple textures into the atlas."""
        for texture_id, path in texture_paths.items():
            try:
                with Image.open(path) as img:
                    # Convert to RGBA if necessary
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # Resize if too large
                    max_texture_size = self.atlas_size // 4  # Maximum quarter of atlas size
                    if img.width > max_texture_size or img.height > max_texture_size:
                        aspect = img.width / img.height
                        if img.width > img.height:
                            new_width = max_texture_size
                            new_height = int(max_texture_size / aspect)
                        else:
                            new_height = max_texture_size
                            new_width = int(max_texture_size * aspect)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    self.add_texture(texture_id, img)
            except Exception as e:
                logger.error(f"Failed to load texture {texture_id} from {path}: {e}")
    
    def get_uv_coords(self, texture_id: str) -> Optional[Tuple[float, float, float, float]]:
        """Get UV coordinates for a texture in the atlas."""
        region = self.regions.get(texture_id)
        return region.uv_coords if region else None
    
    @building_profiler.track_component("texture_loading")
    def save_atlas(self, path: str) -> None:
        """Save the texture atlas to a file."""
        if self.atlas_image:
            self.atlas_image.save(path)
    
    @building_profiler.track_component("texture_loading")
    def load_atlas(self, path: str) -> None:
        """Load a pre-generated texture atlas."""
        self.atlas_image = Image.open(path)
        self.atlas_size = self.atlas_image.width  # Assume square atlas

class MaterialManager:
    """Manages materials and their textures."""
    
    def __init__(self):
        self.texture_atlas = TextureAtlas()
        self.materials: Dict[str, Dict] = {}
    
    @building_profiler.track_component("material_loading")
    def create_material(
        self,
        material_id: str,
        properties: Dict
    ) -> None:
        """Create a new material."""
        self.materials[material_id] = properties
    
    def get_material(self, material_id: str) -> Optional[Dict]:
        """Get material properties."""
        return self.materials.get(material_id)
    
    @building_profiler.track_component("material_loading")
    def load_material_textures(
        self,
        material_id: str,
        texture_paths: Dict[str, str]
    ) -> None:
        """Load textures for a material."""
        if material_id not in self.materials:
            logger.warning(f"Material {material_id} not found")
            return
        
        # Load textures into atlas
        self.texture_atlas.load_textures(texture_paths)
        
        # Update material with UV coordinates
        material = self.materials[material_id]
        material['textures'] = {}
        
        for texture_type, texture_id in texture_paths.items():
            uv_coords = self.texture_atlas.get_uv_coords(texture_id)
            if uv_coords:
                material['textures'][texture_type] = {
                    'atlas_coords': uv_coords,
                    'texture_id': texture_id
                }
    
    @building_profiler.track_component("material_loading")
    def save_material_library(self, path: str) -> None:
        """Save material library to a file."""
        import json
        
        # Save texture atlas
        atlas_path = f"{path}_atlas.png"
        self.texture_atlas.save_atlas(atlas_path)
        
        # Save material definitions
        material_data = {
            'materials': self.materials,
            'atlas_path': atlas_path
        }
        
        with open(f"{path}_materials.json", 'w') as f:
            json.dump(material_data, f, indent=2)
    
    @building_profiler.track_component("material_loading")
    def load_material_library(self, path: str) -> None:
        """Load material library from a file."""
        import json
        
        try:
            # Load material definitions
            with open(f"{path}_materials.json", 'r') as f:
                material_data = json.load(f)
            
            self.materials = material_data['materials']
            
            # Load texture atlas
            self.texture_atlas.load_atlas(material_data['atlas_path'])
        except Exception as e:
            logger.error(f"Failed to load material library: {e}")

# Default material properties
DEFAULT_MATERIALS = {
    'floor': {
        'diffuse_color': (0.8, 0.7, 0.6),
        'specular_color': (0.2, 0.2, 0.2),
        'roughness': 0.7,
        'metallic': 0.0
    },
    'wall': {
        'diffuse_color': (0.9, 0.9, 0.9),
        'specular_color': (0.1, 0.1, 0.1),
        'roughness': 0.8,
        'metallic': 0.0
    },
    'ceiling': {
        'diffuse_color': (0.95, 0.95, 0.95),
        'specular_color': (0.1, 0.1, 0.1),
        'roughness': 0.9,
        'metallic': 0.0
    }
} 
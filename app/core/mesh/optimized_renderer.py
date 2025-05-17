"""
Optimized renderer for building meshes.
Handles efficient rendering of batched geometry.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
import logging
from app.core.profiling.building_profiler import building_profiler

logger = logging.getLogger(__name__)

# Vertex shader for basic rendering
VERTEX_SHADER = """
#version 330
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 texcoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 frag_position;
out vec3 frag_normal;
out vec2 frag_texcoord;

void main() {
    frag_position = vec3(model * vec4(position, 1.0));
    frag_normal = mat3(transpose(inverse(model))) * normal;
    frag_texcoord = texcoord;
    gl_Position = projection * view * model * vec4(position, 1.0);
}
"""

# Fragment shader with basic lighting
FRAGMENT_SHADER = """
#version 330
in vec3 frag_position;
in vec3 frag_normal;
in vec2 frag_texcoord;

uniform vec3 light_pos;
uniform vec3 view_pos;
uniform vec3 light_color;
uniform vec3 object_color;
uniform sampler2D texture_diffuse;
uniform bool use_texture;

out vec4 frag_color;

void main() {
    // Ambient
    float ambient_strength = 0.1;
    vec3 ambient = ambient_strength * light_color;
    
    // Diffuse
    vec3 norm = normalize(frag_normal);
    vec3 light_dir = normalize(light_pos - frag_position);
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * light_color;
    
    // Specular
    float specular_strength = 0.5;
    vec3 view_dir = normalize(view_pos - frag_position);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32);
    vec3 specular = specular_strength * spec * light_color;
    
    vec3 base_color;
    if (use_texture) {
        base_color = vec3(texture(texture_diffuse, frag_texcoord));
    } else {
        base_color = object_color;
    }
    
    vec3 result = (ambient + diffuse + specular) * base_color;
    frag_color = vec4(result, 1.0);
}
"""

class Material:
    """Represents a material with textures and properties."""
    
    def __init__(
        self,
        diffuse_texture: Optional[int] = None,
        color: Tuple[float, float, float] = (0.8, 0.8, 0.8)
    ):
        self.diffuse_texture = diffuse_texture
        self.color = color
        self.use_texture = diffuse_texture is not None

class BatchRenderer:
    """Handles efficient rendering of batched geometry with configurable cache size and LRU eviction."""
    
    def __init__(self, cache_size_limit: int = 32):
        self.shader_program = self._create_shader_program()
        self.vao_cache: Dict[str, List[Tuple[int, int, int]]] = {}  # material_id -> list of (vao, vbo, ebo)
        self.materials: Dict[str, Material] = {}
        self.cache_size_limit = cache_size_limit
        self._vao_usage_order: List[Tuple[str, int]] = []  # (material_id, batch_idx)
        
        # Get uniform locations
        self.uniforms = {
            'model': glGetUniformLocation(self.shader_program, 'model'),
            'view': glGetUniformLocation(self.shader_program, 'view'),
            'projection': glGetUniformLocation(self.shader_program, 'projection'),
            'light_pos': glGetUniformLocation(self.shader_program, 'light_pos'),
            'view_pos': glGetUniformLocation(self.shader_program, 'view_pos'),
            'light_color': glGetUniformLocation(self.shader_program, 'light_color'),
            'object_color': glGetUniformLocation(self.shader_program, 'object_color'),
            'use_texture': glGetUniformLocation(self.shader_program, 'use_texture')
        }
    
    def _create_shader_program(self) -> int:
        """Create and compile the shader program."""
        vertex_shader = shaders.compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        
        program = shaders.compileProgram(vertex_shader, fragment_shader)
        
        # Clean up
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        
        return program
    
    def set_cache_size_limit(self, limit: int):
        """Set the maximum number of VAOs allowed in the cache."""
        self.cache_size_limit = limit
        self._evict_if_needed()

    def _evict_if_needed(self):
        """Evict least recently used VAOs if cache exceeds the size limit."""
        total_vaos = sum(len(batches) for batches in self.vao_cache.values())
        while total_vaos > self.cache_size_limit and self._vao_usage_order:
            # Pop the least recently used
            material_id, batch_idx = self._vao_usage_order.pop(0)
            if material_id in self.vao_cache and batch_idx < len(self.vao_cache[material_id]):
                vao, vbo, ebo = self.vao_cache[material_id][batch_idx]
                glDeleteVertexArrays(1, [vao])
                glDeleteBuffers(1, [vbo])
                glDeleteBuffers(1, [ebo])
                del self.vao_cache[material_id][batch_idx]
                if not self.vao_cache[material_id]:
                    del self.vao_cache[material_id]
                logger.info(f"Evicted VAO batch {batch_idx} for material {material_id} due to cache size limit.")
            total_vaos = sum(len(batches) for batches in self.vao_cache.values())

    @building_profiler.track_component("buffer_creation")
    def create_buffers(
        self,
        material_id: str,
        batch_data: List[Tuple[np.ndarray, np.ndarray]]
    ) -> None:
        """
        Create VAO, VBO, and EBO for each batch of a material.
        Applies LRU eviction if cache size limit is exceeded.
        """
        if material_id not in self.vao_cache:
            self.vao_cache[material_id] = []
        for batch_idx, (vertices, indices) in enumerate(batch_data):
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
            ebo = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
            glEnableVertexAttribArray(2)
            glBindVertexArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            self.vao_cache[material_id].append((vao, vbo, ebo))
            self._vao_usage_order.append((material_id, len(self.vao_cache[material_id]) - 1))
            self._evict_if_needed()
        building_profiler.log_cache_utilization('vao_cache', sum(len(v) for v in self.vao_cache.values()))
    
    def set_material(self, material_id: str, material: Material) -> None:
        """Set material properties for a batch."""
        self.materials[material_id] = material
    
    @building_profiler.track_component("render")
    def render(
        self,
        material_id: str,
        model_matrix: np.ndarray,
        view_matrix: np.ndarray,
        projection_matrix: np.ndarray,
        light_pos: np.ndarray,
        view_pos: np.ndarray,
        light_color: np.ndarray,
        num_indices_list: List[int]
    ) -> None:
        """
        Render all batches for a material.
        num_indices_list: list of index counts for each batch.
        """
        if material_id not in self.vao_cache:
            logger.warning(f"No geometry found for material {material_id}")
            return
        material = self.materials.get(material_id)
        if not material:
            logger.warning(f"No material found for {material_id}")
            return
        glUseProgram(self.shader_program)
        glUniformMatrix4fv(self.uniforms['model'], 1, GL_FALSE, model_matrix)
        glUniformMatrix4fv(self.uniforms['view'], 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(self.uniforms['projection'], 1, GL_FALSE, projection_matrix)
        glUniform3fv(self.uniforms['light_pos'], 1, light_pos)
        glUniform3fv(self.uniforms['view_pos'], 1, view_pos)
        glUniform3fv(self.uniforms['light_color'], 1, light_color)
        glUniform3fv(self.uniforms['object_color'], 1, material.color)
        glUniform1i(self.uniforms['use_texture'], material.use_texture)
        if material.use_texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, material.diffuse_texture)
        for (vao, _, _), num_indices in zip(self.vao_cache[material_id], num_indices_list):
            glBindVertexArray(vao)
            glDrawElements(GL_TRIANGLES, num_indices, GL_UNSIGNED_INT, None)
            building_profiler.log_draw_call()
            glBindVertexArray(0)
        if material.use_texture:
            glBindTexture(GL_TEXTURE_2D, 0)
    
    def cleanup(self) -> None:
        """Clean up OpenGL resources."""
        for vao, vbo, ebo in self.vao_cache.values():
            glDeleteVertexArrays(1, [vao])
            glDeleteBuffers(1, [vbo])
            glDeleteBuffers(1, [ebo])
        glDeleteProgram(self.shader_program)
        self.vao_cache.clear()

@building_profiler.track_component("mesh_rendering")
class OptimizedMeshRenderer:
    """High-level renderer for optimized building meshes."""
    
    def __init__(self):
        self.batch_renderer = BatchRenderer()
        self.initialized = False
        
        # Default materials
        self.default_materials = {
            'floor': Material(color=(0.8, 0.7, 0.6)),
            'wall': Material(color=(0.9, 0.9, 0.9)),
            'ceiling': Material(color=(0.95, 0.95, 0.95))
        }
    
    def initialize(self, mesh_data: Dict[str, List[Tuple[np.ndarray, np.ndarray]]]) -> None:
        """
        Initialize renderer with mesh data.
        mesh_data: dict of material_id -> list of (vertices, indices) batches.
        """
        if self.initialized:
            logger.warning("Renderer already initialized")
            return
        for material_id, batch_list in mesh_data.items():
            self.batch_renderer.create_buffers(material_id, batch_list)
            material = self.default_materials.get(
                material_id.split('_')[0],
                Material()
            )
            self.batch_renderer.set_material(material_id, material)
        self.initialized = True
    
    @building_profiler.track_component("render_frame")
    def render_frame(
        self,
        view_matrix: np.ndarray,
        projection_matrix: np.ndarray,
        light_pos: np.ndarray,
        view_pos: np.ndarray,
        mesh_data: Dict[str, List[Tuple[np.ndarray, np.ndarray]]]
    ) -> None:
        """
        Render a complete frame.
        mesh_data: dict of material_id -> list of (vertices, indices) batches.
        """
        if not self.initialized:
            logger.error("Renderer not initialized")
            return
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        light_color = np.array([1.0, 1.0, 1.0])
        for material_id, batch_list in mesh_data.items():
            model_matrix = np.identity(4)
            num_indices_list = [indices.shape[0] for _, indices in batch_list]
            self.batch_renderer.render(
                material_id,
                model_matrix,
                view_matrix,
                projection_matrix,
                light_pos,
                view_pos,
                light_color,
                num_indices_list
            )
    
    def cleanup(self) -> None:
        """Clean up renderer resources."""
        if self.initialized:
            self.batch_renderer.cleanup()
            self.initialized = False 
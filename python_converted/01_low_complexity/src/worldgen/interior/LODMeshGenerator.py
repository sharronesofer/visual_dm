from typing import Any



class LODMeshGenerator {
  generate(layout: InteriorLayout, lod: float): InteriorMesh {
    return {
      vertices: [],
      faces: [],
      lod
    }
  }
} 
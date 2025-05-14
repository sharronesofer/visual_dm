import { InteriorLayout, InteriorMesh } from './types';

export class LODMeshGenerator {
  generate(layout: InteriorLayout, lod: number): InteriorMesh {
    // TODO: Implement mesh generation and LOD simplification
    return {
      vertices: [],
      faces: [],
      lod
    };
  }
} 
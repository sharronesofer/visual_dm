# Character Customization System

## Overview
This module provides a modular, extensible framework for character customization, supporting swappable meshes, blend shapes, dynamic materials, serialization, randomization, and preset management.

## Directory Structure
- `model.py`: Core CharacterModel class and data structures
- `mesh.py`: Mesh loading, swapping, and slot management
- `blendshapes.py`: Blend shape definitions and morphing logic
- `materials.py`: Dynamic material system for skin tones and textures
- `animation.py`: Animation compatibility layer
- `serialization.py`: Serialization/deserialization utilities
- `randomization.py`: Random character generation system
- `presets.py`: Character preset management

## Key Concepts
- **MeshSlot**: Attachment points for swappable meshes (face, hair, armor, etc.)
- **BlendShape**: Morph targets for facial/body feature adjustment
- **MaterialAssignment**: Dynamic material property assignment
- **CharacterModel**: Orchestrates mesh, blend shape, and material management
- **RandomCharacterGenerator**: Generates random but coherent character appearances
- **CharacterPresetManager**: CRUD and metadata for character presets

## Extension Points
- Add new mesh types or races by extending `MeshSlot` and providing new assets
- Add new blend shapes for additional customization
- Extend material properties for new visual effects
- Integrate with UI or game engine for real-time preview and editing

## Example Usage
```python
from character.model import CharacterModel
from character.randomization import RandomCharacterGenerator

# Create a character model
char = CharacterModel(race="elf", base_mesh="elf_base")
char.swap_mesh("hair", "long_elf_hair")
char.set_blendshape("nose_width", 0.3)
char.assign_material("skin", "elf_skin_01", {"color": "#ffeedd"})

# Serialize/deserialize
from character.serialization import serialize_character, deserialize_character
json_str = serialize_character(char)
char2 = deserialize_character(json_str, CharacterModel)

# Random generation
feature_weights = {
    "hair_color": {"blonde": 0.2, "black": 0.5, "red": 0.3},
    "eye_color": {"blue": 0.4, "green": 0.3, "brown": 0.3},
}
gen = RandomCharacterGenerator(feature_weights)
random_features = gen.generate(locked={"eye_color": "green"})
```

## Asset Guidelines
- All meshes should use a common skeleton for animation compatibility
- Blend shapes should be named consistently across races and body types
- Materials should support parameterization for color, roughness, metallic, etc.

## Performance
- Use mesh and texture LODs for optimization
- Profile memory and CPU usage for large numbers of customized characters

## License
MIT or project-specific 
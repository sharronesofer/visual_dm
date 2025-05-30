"""
Tests for backend.systems.character.models.visual_model

Tests for the visual model classes including CharacterModel, MeshSlot, BlendShape, 
MaterialAssignment, and AnimationState.
"""

import pytest
from unittest.mock import Mock, patch
from random import uniform

# Import the module being tested
from backend.systems.character.models.visual_model import (
    CharacterModel, MeshSlot, BlendShape, MaterialAssignment, AnimationState
)


def test_module_imports(): pass
    """Test that the module can be imported without errors."""
    from backend.systems.character.models import visual_model
    assert visual_model is not None


class TestMeshSlot: pass
    """Test class for MeshSlot"""
    
    def test_init_with_defaults(self): pass
        """Test initializing MeshSlot with default values."""
        slot = MeshSlot("head")
        assert slot.name == "head"
        assert slot.mesh_id is None
        assert slot.compatible_types == []
    
    def test_init_with_values(self): pass
        """Test initializing MeshSlot with all values."""
        slot = MeshSlot("torso", "armor_01", ["light", "medium"])
        assert slot.name == "torso"
        assert slot.mesh_id == "armor_01"
        assert slot.compatible_types == ["light", "medium"]


class TestBlendShape: pass
    """Test class for BlendShape"""
    
    def test_init_with_default(self): pass
        """Test initializing BlendShape with default value."""
        blend = BlendShape("jaw_width")
        assert blend.name == "jaw_width"
        assert blend.value == 0.0
    
    def test_init_with_value(self): pass
        """Test initializing BlendShape with custom value."""
        blend = BlendShape("eye_size", 0.75)
        assert blend.name == "eye_size"
        assert blend.value == 0.75


class TestMaterialAssignment: pass
    """Test class for MaterialAssignment"""
    
    def test_init_with_defaults(self): pass
        """Test initializing MaterialAssignment with default values."""
        mat = MaterialAssignment("skin", "human_skin_01")
        assert mat.slot == "skin"
        assert mat.material_id == "human_skin_01"
        assert mat.properties == {}
    
    def test_init_with_properties(self): pass
        """Test initializing MaterialAssignment with properties."""
        props = {"roughness": 0.5, "color": "#f5d7b4"}
        mat = MaterialAssignment("skin", "human_skin_01", props)
        assert mat.slot == "skin"
        assert mat.material_id == "human_skin_01"
        assert mat.properties == props


class TestAnimationState: pass
    """Test class for AnimationState"""
    
    def test_init_with_defaults(self): pass
        """Test initializing AnimationState with default values."""
        anim = AnimationState("idle")
        assert anim.animation_id == "idle"
        assert anim.speed == 1.0
        assert anim.weight == 1.0
        assert anim.loop is True
        assert anim.transition_time == 0.25
        assert anim.time == 0.0
        assert anim.is_playing is False
    
    def test_init_with_values(self): pass
        """Test initializing AnimationState with custom values."""
        anim = AnimationState("run", speed=1.5, weight=0.8, loop=False, transition_time=0.5)
        assert anim.animation_id == "run"
        assert anim.speed == 1.5
        assert anim.weight == 0.8
        assert anim.loop is False
        assert anim.transition_time == 0.5
        assert anim.time == 0.0
        assert anim.is_playing is False


class TestCharacterModel: pass
    """Test class for CharacterModel"""
    
    def test_init_with_defaults(self): pass
        """Test initializing CharacterModel with minimum required values."""
        model = CharacterModel("human", "human_base")
        assert model.race == "human"
        assert model.base_mesh == "human_base"
        assert model.mesh_slots == {}
        assert model.blendshapes == {}
        assert model.materials == {}
        assert model.animations == {}
        assert model.scale == {"height": 1.0, "build": 0.5}
        assert model.current_animation is None
    
    def test_init_with_all_values(self): pass
        """Test initializing CharacterModel with all values."""
        mesh_slots = {
            "head": MeshSlot("head", "head_01"),
            "body": MeshSlot("body", "body_01")
        }
        blendshapes = {
            "jaw": BlendShape("jaw", 0.3),
            "eyes": BlendShape("eyes", 0.7)
        }
        materials = {
            "skin": MaterialAssignment("skin", "skin_01", {"color": "#f5d7b4"}),
            "hair": MaterialAssignment("hair", "hair_01", {"color": "#8B4513"})
        }
        animations = {
            "idle": AnimationState("idle_01", loop=True),
            "walk": AnimationState("walk_01", speed=1.2)
        }
        scale = {"height": 1.2, "build": 0.7}
        
        model = CharacterModel(
            "elf", 
            "elf_base", 
            mesh_slots, 
            blendshapes, 
            materials, 
            animations, 
            scale
        )
        
        assert model.race == "elf"
        assert model.base_mesh == "elf_base"
        assert model.mesh_slots == mesh_slots
        assert model.blendshapes == blendshapes
        assert model.materials == materials
        assert model.animations == animations
        assert model.scale == scale
        assert model.current_animation is None
    
    def test_swap_mesh_existing_slot(self): pass
        """Test swapping a mesh in an existing slot."""
        model = CharacterModel("human", "human_base")
        model.mesh_slots = {"head": MeshSlot("head", "head_01")}
        
        model.swap_mesh("head", "head_02")
        
        assert model.mesh_slots["head"].mesh_id == "head_02"
    
    def test_swap_mesh_new_slot(self): pass
        """Test swapping a mesh in a new slot."""
        model = CharacterModel("human", "human_base")
        
        model.swap_mesh("torso", "torso_01")
        
        assert "torso" in model.mesh_slots
        assert model.mesh_slots["torso"].mesh_id == "torso_01"
    
    def test_set_blendshape_existing(self): pass
        """Test setting an existing blendshape."""
        model = CharacterModel("human", "human_base")
        model.blendshapes = {"jaw": BlendShape("jaw", 0.3)}
        
        model.set_blendshape("jaw", 0.5)
        
        assert model.blendshapes["jaw"].value == 0.5
    
    def test_set_blendshape_new(self): pass
        """Test setting a new blendshape."""
        model = CharacterModel("human", "human_base")
        
        model.set_blendshape("nose", 0.7)
        
        assert "nose" in model.blendshapes
        assert model.blendshapes["nose"].value == 0.7
    
    def test_assign_material(self): pass
        """Test assigning a material."""
        model = CharacterModel("human", "human_base")
        
        model.assign_material("skin", "skin_02", {"roughness": 0.3})
        
        assert "skin" in model.materials
        assert model.materials["skin"].material_id == "skin_02"
        assert model.materials["skin"].properties == {"roughness": 0.3}
    
    def test_play_animation_new(self): pass
        """Test playing a new animation."""
        model = CharacterModel("human", "human_base")
        
        model.play_animation("walk", 1.2, 0.3)
        
        assert "walk" in model.animations
        assert model.animations["walk"].animation_id == "walk"
        assert model.animations["walk"].speed == 1.2
        assert model.animations["walk"].transition_time == 0.3
        assert model.animations["walk"].is_playing is True
        assert model.current_animation == "walk"
    
    def test_play_animation_existing(self): pass
        """Test playing an existing animation."""
        model = CharacterModel("human", "human_base")
        model.animations = {
            "walk": AnimationState("walk_01", speed=1.0, transition_time=0.25)
        }
        
        model.play_animation("walk", 1.5, 0.4)
        
        assert model.animations["walk"].speed == 1.5
        assert model.animations["walk"].transition_time == 0.4
        assert model.animations["walk"].is_playing is True
        assert model.current_animation == "walk"
    
    def test_stop_animation_specific(self): pass
        """Test stopping a specific animation."""
        model = CharacterModel("human", "human_base")
        model.animations = {
            "idle": AnimationState("idle_01"),
            "walk": AnimationState("walk_01")
        }
        model.animations["walk"].is_playing = True
        model.current_animation = "walk"
        
        model.stop_animation("walk")
        
        assert model.animations["walk"].is_playing is False
        assert model.current_animation is None
    
    def test_stop_animation_current(self): pass
        """Test stopping the current animation when none is specified."""
        model = CharacterModel("human", "human_base")
        model.animations = {
            "idle": AnimationState("idle_01"),
            "walk": AnimationState("walk_01")
        }
        model.animations["walk"].is_playing = True
        model.current_animation = "walk"
        
        model.stop_animation()
        
        assert model.animations["walk"].is_playing is False
        assert model.current_animation is None
    
    def test_to_dict(self): pass
        """Test serializing the model to a dictionary."""
        model = CharacterModel("human", "human_base")
        model.mesh_slots = {
            "head": MeshSlot("head", "head_01"),
            "body": MeshSlot("body", "body_01")
        }
        model.blendshapes = {
            "jaw": BlendShape("jaw", 0.3),
            "eyes": BlendShape("eyes", 0.7)
        }
        model.materials = {
            "skin": MaterialAssignment("skin", "skin_01"),
            "hair": MaterialAssignment("hair", "hair_01")
        }
        model.animations = {
            "idle": AnimationState("idle_01", speed=1.0, weight=1.0, loop=True),
            "walk": AnimationState("walk_01", speed=1.2, weight=0.8, loop=True)
        }
        model.animations["idle"].is_playing = True
        model.current_animation = "idle"
        model.scale = {"height": 1.2, "build": 0.7}
        
        result = model.to_dict()
        
        assert result["race"] == "human"
        assert result["base_mesh"] == "human_base"
        assert result["mesh_slots"] == {"head": "head_01", "body": "body_01"}
        assert result["blendshapes"] == {"jaw": 0.3, "eyes": 0.7}
        assert result["materials"] == {"skin": "skin_01", "hair": "hair_01"}
        assert result["animations"]["idle"]["animation_id"] == "idle_01"
        assert result["animations"]["idle"]["speed"] == 1.0
        assert result["animations"]["idle"]["weight"] == 1.0
        assert result["animations"]["idle"]["loop"] is True
        assert result["animations"]["idle"]["is_playing"] is True
        assert result["animations"]["walk"]["animation_id"] == "walk_01"
        assert result["animations"]["walk"]["speed"] == 1.2
        assert result["current_animation"] == "idle"
        assert result["scale"] == {"height": 1.2, "build": 0.7}
    
    def test_from_dict(self): pass
        """Test creating a model from a dictionary."""
        data = {
            "race": "dwarf",
            "base_mesh": "dwarf_base",
            "mesh_slots": {"head": "dwarf_head", "body": "dwarf_body"},
            "blendshapes": {"beard": 0.8, "brow": 0.6},
            "materials": {"skin": "dwarf_skin", "hair": "dwarf_hair"},
            "animations": {
                "idle": {
                    "animation_id": "dwarf_idle",
                    "speed": 0.9,
                    "weight": 1.0,
                    "loop": True,
                    "is_playing": True
                },
                "walk": "dwarf_walk"  # Test string format too
            },
            "current_animation": "idle",
            "scale": {"height": 0.8, "build": 0.9}
        }
        
        model = CharacterModel.from_dict(data)
        
        assert model.race == "dwarf"
        assert model.base_mesh == "dwarf_base"
        assert "head" in model.mesh_slots and model.mesh_slots["head"].mesh_id == "dwarf_head"
        assert "body" in model.mesh_slots and model.mesh_slots["body"].mesh_id == "dwarf_body"
        assert "beard" in model.blendshapes and model.blendshapes["beard"].value == 0.8
        assert "brow" in model.blendshapes and model.blendshapes["brow"].value == 0.6
        assert "skin" in model.materials and model.materials["skin"].material_id == "dwarf_skin"
        assert "hair" in model.materials and model.materials["hair"].material_id == "dwarf_hair"
        assert "idle" in model.animations
        assert model.animations["idle"].animation_id == "dwarf_idle"
        assert model.animations["idle"].speed == 0.9
        assert model.animations["idle"].is_playing is True
        assert "walk" in model.animations
        assert model.animations["walk"].animation_id == "walk"  # Should use key as default
        assert model.current_animation == "idle"
        assert model.scale == {"height": 0.8, "build": 0.9}
    
    def test_from_dict_with_defaults(self): pass
        """Test creating a model from a dictionary with minimal values."""
        data = {
            "race": "elf",
            "base_mesh": "elf_base"
        }
        
        model = CharacterModel.from_dict(data)
        
        assert model.race == "elf"
        assert model.base_mesh == "elf_base"
        assert model.mesh_slots == {}
        assert model.blendshapes == {}
        assert model.materials == {}
        assert model.animations == {}
        assert model.scale == {"height": 1.0, "build": 0.5}
        assert model.current_animation is None
    
    def test_apply_preset(self): pass
        """Test applying a preset to the character model."""
        model = CharacterModel("human", "human_base")
        
        preset_data = {
            "mesh_slots": {"head": "head_02", "body": "body_02"},
            "blendshapes": {"nose": 0.6, "ears": 0.4},
            "materials": {
                "skin": {"id": "skin_02", "properties": {"roughness": 0.7}},
                "hair": "hair_02"  # Test string format too
            },
            "scale": {"height": 1.1}
        }
        
        model.apply_preset(preset_data)
        
        # Check mesh slots were updated
        assert model.mesh_slots["head"].mesh_id == "head_02"
        assert model.mesh_slots["body"].mesh_id == "body_02"
        
        # Check blendshapes were updated
        assert model.blendshapes["nose"].value == 0.6
        assert model.blendshapes["ears"].value == 0.4
        
        # Check materials were updated
        assert model.materials["skin"].material_id == "skin_02"
        assert model.materials["skin"].properties == {"roughness": 0.7}
        assert model.materials["hair"].material_id == "hair_02"
        
        # Check scale was updated (partial)
        assert model.scale["height"] == 1.1
        assert model.scale["build"] == 0.5  # Unchanged
    
    @patch('random.uniform')
    def test_randomize_without_constraints(self, mock_uniform): pass
        """Test randomizing character appearance without constraints."""
        # Set up our mocks
        mock_uniform.side_effect = lambda min_val, max_val: 0.5
        
        model = CharacterModel("human", "human_base")
        model.blendshapes = {
            "jaw": BlendShape("jaw", 0.3),
            "eyes": BlendShape("eyes", 0.7)
        }
        
        model.randomize()
        
        # Check blendshapes were randomized
        assert model.blendshapes["jaw"].value == 0.5
        assert model.blendshapes["eyes"].value == 0.5
        
        # Verify our mocks were called
        assert mock_uniform.call_count == 2
    
    @patch('random.uniform')
    def test_randomize_with_constraints(self, mock_uniform): pass
        """Test randomizing character appearance with constraints."""
        # Set up our mocks
        mock_uniform.side_effect = lambda min_val, max_val: (min_val + max_val) / 2
        
        model = CharacterModel("human", "human_base")
        model.blendshapes = {
            "jaw": BlendShape("jaw", 0.3),
            "eyes": BlendShape("eyes", 0.7),
            "nose": BlendShape("nose", 0.4)
        }
        
        constraints = {
            "blendshapes": {
                "jaw": {"min": 0.2, "max": 0.6},
                "eyes": {"min": 0.1, "max": 0.3}
                # nose not constrained
            }
        }
        
        model.randomize(constraints)
        
        # Check constrained blendshapes
        assert model.blendshapes["jaw"].value == 0.4  # (0.2 + 0.6) / 2
        assert model.blendshapes["eyes"].value == 0.2  # (0.1 + 0.3) / 2
        # Nose should not be changed since it's not in the constraints
        assert model.blendshapes["nose"].value == 0.4

"""
HandcraftedRegionGenerator - Template-based region generation

This module provides the HandcraftedRegionGenerator class responsible for
creating regions based on pre-designed templates.
"""
from typing import Dict, List, Any, Optional, Tuple
import json
import time
import os
import logging

from python_converted.src.worldgen.core.IWorldGenerator import (
    IHandcraftedRegionGenerator, GeneratorType, Region, Cell,
    RegionGeneratorOptions, PointOfInterest, Resource, RegionTemplate
)
from python_converted.src.worldgen.core.simple_test import DeterministicRNG
from python_converted.src.worldgen.region.BaseRegionGenerator import BaseRegionGenerator

# Create logger
logger = logging.getLogger("worldgen.generators.handcrafted")

class HandcraftedRegionGeneratorOptions(RegionGeneratorOptions):
    """
    Extended options for handcrafted region generation.
    
    This class extends the base RegionGeneratorOptions with properties
    specific to handcrafted, template-based generation.
    
    Attributes:
        template_id (str): The ID of the template to use
        variation_amount (float): How much to vary from the exact template (0.0-1.0)
        randomize_resources (bool): Whether to randomize resource positions
        randomize_pois (bool): Whether to randomize point of interest positions
    """
    
    def __init__(self, 
                 template_id: str,
                 variation_amount: float = 0.2,
                 randomize_resources: bool = True,
                 randomize_pois: bool = False,
                 **kwargs):
        """
        Initialize handcrafted region generation options.
        
        Args:
            template_id (str): The ID of the template to use
            variation_amount (float, optional): How much to vary from the template. Defaults to 0.2.
            randomize_resources (bool, optional): Whether to randomize resources. Defaults to True.
            randomize_pois (bool, optional): Whether to randomize POIs. Defaults to False.
            **kwargs: Additional options passed to the parent class
        """
        super().__init__(**kwargs)
        self.template_id = template_id
        self.variation_amount = variation_amount
        self.randomize_resources = randomize_resources
        self.randomize_pois = randomize_pois

class HandcraftedRegionGenerator(BaseRegionGenerator, IHandcraftedRegionGenerator):
    """
    Handcrafted region generator that creates terrain from templates.
    
    This generator creates regions based on pre-designed templates with
    optional variations to add some controlled randomness.
    
    Attributes:
        templates (Dict[str, RegionTemplate]): Dictionary of available templates
        template_dir (str): Directory where templates are stored
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the handcrafted region generator.
        
        Args:
            template_dir (Optional[str], optional): Directory containing templates.
                If None, looks for a 'templates' directory relative to this file.
        """
        super().__init__()
        
        # Store templates in a dictionary keyed by template ID
        self.templates: Dict[str, RegionTemplate] = {}
        
        # Set template directory
        if template_dir is None:
            # Default to a templates directory in the same location as this file
            self.template_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "templates"
            )
        else:
            self.template_dir = template_dir
            
        # Try to load templates from the directory
        self._load_templates_from_directory()
    
    def get_type(self) -> GeneratorType:
        """Get the type of this generator"""
        return GeneratorType.HANDCRAFTED
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this generator"""
        return {
            "templated_generation": True,
            "controlled_variation": True,
            "exact_reproduction": True,
            "supports_custom_templates": True
        }
    
    def register_template(self, template: RegionTemplate) -> bool:
        """
        Register a new template with this generator.
        
        Args:
            template (RegionTemplate): The template to register
            
        Returns:
            bool: True if successful, False if the template ID already exists
        """
        if template.id in self.templates:
            logger.warning(f"Template with ID '{template.id}' already exists")
            return False
        
        self.templates[template.id] = template
        logger.info(f"Registered template '{template.id}' ({template.name})")
        return True
    
    def get_template(self, template_id: str) -> Optional[RegionTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id (str): The ID of the template to retrieve
            
        Returns:
            Optional[RegionTemplate]: The template, or None if not found
        """
        return self.templates.get(template_id)
    
    def get_templates(self) -> List[RegionTemplate]:
        """
        Get all templates.
        
        Returns:
            List[RegionTemplate]: List of all templates
        """
        return list(self.templates.values())
    
    def _load_templates_from_directory(self) -> None:
        """
        Load templates from the template directory.
        
        This method scans the template directory for JSON files and
        attempts to load them as templates.
        """
        if not os.path.exists(self.template_dir):
            logger.warning(f"Template directory not found: {self.template_dir}")
            # Create the directory
            try:
                os.makedirs(self.template_dir)
                logger.info(f"Created template directory: {self.template_dir}")
                
                # Create a sample template
                self._create_sample_template()
            except Exception as e:
                logger.error(f"Error creating template directory: {e}")
            return
        
        # Scan directory for JSON files
        try:
            template_files = [f for f in os.listdir(self.template_dir) 
                             if f.endswith('.json')]
            
            for filename in template_files:
                file_path = os.path.join(self.template_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        template_json = f.read()
                        
                    template = RegionTemplate.from_json(template_json)
                    self.register_template(template)
                    
                except Exception as e:
                    logger.error(f"Error loading template {filename}: {e}")
            
            logger.info(f"Loaded {len(self.templates)} templates from {self.template_dir}")
            
            # If no templates were loaded, create a sample one
            if not self.templates:
                self._create_sample_template()
                
        except Exception as e:
            logger.error(f"Error scanning template directory: {e}")
    
    def _create_sample_template(self) -> None:
        """Create a sample template and save it to the template directory."""
        try:
            # Create a simple sample template
            sample = RegionTemplate(
                id="sample_template",
                name="Sample Region Template",
                width=16,
                height=16,
                description="A sample template with basic terrain features"
            )
            
            # Add some basic terrain cells
            for y in range(sample.height):
                for x in range(sample.width):
                    # Create a simple terrain pattern
                    if x < 3 or x >= sample.width - 3 or y < 3 or y >= sample.height - 3:
                        # Border mountains
                        terrain_type = "mountains"
                        elevation = 0.7
                    elif 5 <= x <= 10 and 5 <= y <= 10:
                        # Central lake
                        terrain_type = "shallow_water"
                        elevation = 0.2
                    else:
                        # Plains elsewhere
                        terrain_type = "plains"
                        elevation = 0.4
                    
                    # Add the cell
                    sample.cells.append({
                        "x": x,
                        "y": y,
                        "terrain_type": terrain_type,
                        "elevation": elevation,
                        "biome": "forest" if terrain_type == "plains" else (
                            "alpine" if terrain_type == "mountains" else "lake"
                        )
                    })
            
            # Add some points of interest
            sample.points_of_interest = [
                {
                    "x": 8,
                    "y": 8,
                    "poi_type": "village",
                    "name": "Lakeside Village",
                    "description": "A peaceful village beside the central lake."
                },
                {
                    "x": 2,
                    "y": 2,
                    "poi_type": "watchtower",
                    "name": "Northern Watchtower",
                    "description": "A watchtower guarding the northern approach."
                },
                {
                    "x": 13,
                    "y": 13,
                    "poi_type": "ruins",
                    "name": "Ancient Ruins",
                    "description": "The crumbling remains of an ancient civilization."
                }
            ]
            
            # Add some resources
            sample.resources = [
                {
                    "resource_type": "wood",
                    "x": 7,
                    "y": 4,
                    "quantity": 100,
                    "quality": 3
                },
                {
                    "resource_type": "stone",
                    "x": 3,
                    "y": 12,
                    "quantity": 80,
                    "quality": 4
                },
                {
                    "resource_type": "fish",
                    "x": 8,
                    "y": 8,
                    "quantity": 50,
                    "quality": 5
                }
            ]
            
            # Save the template
            file_path = os.path.join(self.template_dir, "sample_template.json")
            with open(file_path, 'w') as f:
                f.write(sample.to_json())
            
            # Register the template
            self.register_template(sample)
            logger.info(f"Created sample template 'sample_template' at {file_path}")
            
        except Exception as e:
            logger.error(f"Error creating sample template: {e}")
    
    def _generate_region(self, options: RegionGeneratorOptions, 
                        rng: DeterministicRNG) -> Region:
        """
        Generate a region from a template with optional variations.
        
        Args:
            options (RegionGeneratorOptions): The generation options
            rng (DeterministicRNG): The random number generator
            
        Returns:
            Region: The generated region
        """
        # Cast to handcrafted options if possible, otherwise use defaults
        if isinstance(options, HandcraftedRegionGeneratorOptions):
            handcrafted_options = options
        else:
            # Create handcrafted options with defaults
            template_id = options.template_id if options.template_id else "sample_template"
            handcrafted_options = HandcraftedRegionGeneratorOptions(
                template_id=template_id,
                width=options.width,
                height=options.height,
                seed=options.seed
            )
        
        # Get the template
        template_id = handcrafted_options.template_id
        template = self.get_template(template_id)
        
        if template is None:
            # Try to find any template if the specified one doesn't exist
            if self.templates:
                template_id = list(self.templates.keys())[0]
                template = self.templates[template_id]
                logger.warning(f"Template '{handcrafted_options.template_id}' not found, using '{template_id}' instead")
            else:
                raise ValueError(f"No templates available")
        
        # Create region ID and name
        region_id = self._generate_region_id(options, rng)
        region_name = template.name
        
        # Set dimensions
        width = options.width if options.width > 0 else template.width
        height = options.height if options.height > 0 else template.height
        
        # Create the base region object
        region = Region(
            id=region_id,
            name=region_name,
            width=width,
            height=height
        )
        
        # Apply the template with variations
        variation_amount = handcrafted_options.variation_amount
        
        # Generate derived RNGs for different aspects
        terrain_rng = self._derive_child_rng(rng, "terrain")
        resource_rng = self._derive_child_rng(rng, "resources")
        poi_rng = self._derive_child_rng(rng, "poi")
        
        # Generate cells (terrain)
        region.cells = self._generate_cells_from_template(
            template, width, height, variation_amount, terrain_rng
        )
        
        # Generate resources
        region.resources = self._generate_resources_from_template(
            template, region.cells, handcrafted_options.randomize_resources,
            variation_amount, resource_rng
        )
        
        # Generate points of interest
        region.points_of_interest = self._generate_pois_from_template(
            template, region.cells, handcrafted_options.randomize_pois,
            variation_amount, poi_rng
        )
        
        # Add metadata
        region.metadata = {
            "generator": "handcrafted",
            "template_id": template.id,
            "template_name": template.name,
            "generation_time": time.time(),
            "seed": options.seed,
            "variation_amount": variation_amount
        }
        
        return region
    
    def _derive_child_rng(self, parent_rng: DeterministicRNG, purpose: str) -> DeterministicRNG:
        """
        Create a derived RNG for a specific purpose.
        
        Args:
            parent_rng (DeterministicRNG): The parent RNG
            purpose (str): The purpose of this RNG (e.g., 'terrain', 'resources')
            
        Returns:
            DeterministicRNG: A new deterministic RNG
        """
        if hasattr(parent_rng, 'create_child'):
            # If the RNG supports child derivation directly
            return parent_rng.create_child(purpose)
        else:
            # Otherwise, derive a new seed and create a new RNG
            seed_value = self.seed_manager.derive_seed(
                f"{purpose}_seed", 
                parent_name=parent_rng.config.name
            )
            return DeterministicRNG({
                "seed": seed_value,
                "name": f"{parent_rng.config.name}_{purpose}"
            })
    
    def _generate_cells_from_template(self, template: RegionTemplate, 
                                     width: int, height: int,
                                     variation_amount: float,
                                     rng: DeterministicRNG) -> List[Cell]:
        """
        Generate cells from a template with optional scaling and variations.
        
        Args:
            template (RegionTemplate): The template to use
            width (int): The target width
            height (int): The target height
            variation_amount (float): How much to vary from the template (0.0-1.0)
            rng (DeterministicRNG): The random number generator
            
        Returns:
            List[Cell]: The generated cells
        """
        cells = []
        
        # Determine if we need to scale the template
        scale_x = width / template.width
        scale_y = height / template.height
        
        # Create a map for quick lookup of template cells
        template_cell_map = {}
        for cell_data in template.cells:
            key = (cell_data["x"], cell_data["y"])
            template_cell_map[key] = cell_data
        
        # Generate cells for the region
        for y in range(height):
            for x in range(width):
                # Map the coordinates back to the template
                template_x = int(x / scale_x)
                template_y = int(y / scale_y)
                
                # Clamp to valid template coordinates
                template_x = max(0, min(template_x, template.width - 1))
                template_y = max(0, min(template_y, template.height - 1))
                
                # Look up the template cell
                template_cell = template_cell_map.get((template_x, template_y))
                
                if template_cell:
                    # Get values from template
                    terrain_type = template_cell.get("terrain_type", "plains")
                    elevation = template_cell.get("elevation", 0.5)
                    moisture = template_cell.get("moisture", 0.5)
                    temperature = template_cell.get("temperature", 0.5)
                    biome = template_cell.get("biome", "grassland")
                    
                    # Apply variations if requested
                    if variation_amount > 0:
                        # Vary elevation within limits
                        elevation_variation = rng.uniform(-0.1, 0.1) * variation_amount
                        elevation = max(0.0, min(1.0, elevation + elevation_variation))
                        
                        # Vary moisture within limits
                        moisture_variation = rng.uniform(-0.1, 0.1) * variation_amount
                        moisture = max(0.0, min(1.0, moisture + moisture_variation))
                        
                        # Vary temperature within limits
                        temp_variation = rng.uniform(-0.1, 0.1) * variation_amount
                        temperature = max(0.0, min(1.0, temperature + temp_variation))
                        
                        # Potentially change terrain type for border cells
                        if rng.uniform(0, 1) < variation_amount * 0.2:
                            # Only change terrain if it wouldn't drastically alter the layout
                            # (e.g., don't turn water into mountains)
                            if "water" not in terrain_type:
                                terrain_options = ["plains", "hills", "forest", "mountains"]
                                terrain_type = rng.choice(terrain_options)
                            
                        # Update biome based on modified elevation/moisture/temperature
                        if rng.uniform(0, 1) < variation_amount * 0.3:
                            biome_options = [
                                "forest", "grassland", "desert", "tundra", 
                                "mountains", "hills", "swamp"
                            ]
                            # Keep water biomes if terrain is water
                            if "water" in terrain_type:
                                biome_options = ["lake", "ocean", "river"]
                            
                            biome = rng.choice(biome_options)
                else:
                    # Default values for cells not in template
                    terrain_type = "plains"
                    elevation = 0.5
                    moisture = 0.5
                    temperature = 0.5
                    biome = "grassland"
                
                # Create the cell
                cell = Cell(
                    x=x,
                    y=y,
                    terrain_type=terrain_type,
                    elevation=elevation,
                    moisture=moisture,
                    temperature=temperature,
                    biome=biome
                )
                
                cells.append(cell)
        
        return cells
    
    def _generate_resources_from_template(self, template: RegionTemplate,
                                         cells: List[Cell],
                                         randomize_positions: bool,
                                         variation_amount: float,
                                         rng: DeterministicRNG) -> List[Resource]:
        """
        Generate resources from a template with optional randomization.
        
        Args:
            template (RegionTemplate): The template to use
            cells (List[Cell]): The cells in the region
            randomize_positions (bool): Whether to randomize resource positions
            variation_amount (float): How much to vary from the template (0.0-1.0)
            rng (DeterministicRNG): The random number generator
            
        Returns:
            List[Resource]: The generated resources
        """
        resources = []
        
        # Create cell lookup by coordinates
        cell_map = {(cell.x, cell.y): cell for cell in cells}
        
        # Get template resources
        template_resources = template.resources
        
        # Copy resources from template, optionally with variations
        for res_data in template_resources:
            # Get basic values from template
            resource_type = res_data.get("resource_type", "generic")
            x = res_data.get("x", 0)
            y = res_data.get("y", 0)
            quantity = res_data.get("quantity", 50)
            quality = res_data.get("quality", 3)
            
            # Randomize position if requested
            if randomize_positions:
                # Choose a random cell
                valid_cells = [cell for cell in cells 
                              if "water" not in cell.terrain_type]  # Skip water cells
                
                if valid_cells:
                    random_cell = rng.choice(valid_cells)
                    x = random_cell.x
                    y = random_cell.y
            
            # Apply variations to quantity and quality
            if variation_amount > 0:
                quantity_variation = rng.uniform(-20, 20) * variation_amount
                quantity = max(1, quantity + quantity_variation)
                
                quality_variation = rng.choice([-1, 0, 1]) * variation_amount
                quality = max(1, min(5, quality + quality_variation))
            
            # Create the resource
            resource = Resource(
                resource_type=resource_type,
                x=x,
                y=y,
                quantity=quantity,
                quality=quality
            )
            
            resources.append(resource)
        
        # Add some additional resources if variation is high
        if variation_amount > 0.5:
            extra_count = int(len(template_resources) * variation_amount * 0.5)
            
            for _ in range(extra_count):
                # Choose a random cell that doesn't have a resource yet
                valid_cells = [cell for cell in cells 
                              if "water" not in cell.terrain_type and 
                              not any(r.x == cell.x and r.y == cell.y for r in resources)]
                
                if valid_cells:
                    cell = rng.choice(valid_cells)
                    
                    # Create a random resource
                    resource_types = [
                        "wood", "stone", "iron", "gold", "herbs", 
                        "crystal", "copper", "silver"
                    ]
                    
                    resource = Resource(
                        resource_type=rng.choice(resource_types),
                        x=cell.x,
                        y=cell.y,
                        quantity=rng.uniform(10, 100),
                        quality=rng.randint(1, 5)
                    )
                    
                    resources.append(resource)
        
        return resources
    
    def _generate_pois_from_template(self, template: RegionTemplate,
                                    cells: List[Cell],
                                    randomize_positions: bool,
                                    variation_amount: float,
                                    rng: DeterministicRNG) -> List[PointOfInterest]:
        """
        Generate points of interest from a template with optional randomization.
        
        Args:
            template (RegionTemplate): The template to use
            cells (List[Cell]): The cells in the region
            randomize_positions (bool): Whether to randomize POI positions
            variation_amount (float): How much to vary from the template (0.0-1.0)
            rng (DeterministicRNG): The random number generator
            
        Returns:
            List[PointOfInterest]: The generated points of interest
        """
        pois = []
        
        # Get template POIs
        template_pois = template.points_of_interest
        
        # Copy POIs from template, optionally with variations
        for poi_data in template_pois:
            # Get basic values from template
            poi_type = poi_data.get("poi_type", "landmark")
            x = poi_data.get("x", 0)
            y = poi_data.get("y", 0)
            name = poi_data.get("name", f"Unknown {poi_type.capitalize()}")
            description = poi_data.get("description", "")
            
            # Randomize position if requested
            if randomize_positions:
                # Choose a random cell
                valid_cells = [cell for cell in cells]
                
                if valid_cells:
                    random_cell = rng.choice(valid_cells)
                    x = random_cell.x
                    y = random_cell.y
            
            # Apply variations to name and description
            if variation_amount > 0 and rng.uniform(0, 1) < variation_amount:
                # Name prefixes and suffixes for variation
                prefixes = [
                    "Ancient", "Forgotten", "Hidden", "Mysterious", "Sacred",
                    "Cursed", "Blessed", "Abandoned", "Royal", "Enchanted"
                ]
                
                # Modify the name
                if " " in name:
                    # Replace the first word with a random prefix
                    parts = name.split(" ", 1)
                    name = f"{rng.choice(prefixes)} {parts[1]}"
            
            # Create the POI
            poi = PointOfInterest(
                x=x,
                y=y,
                poi_type=poi_type,
                name=name,
                description=description
            )
            
            # Copy attributes if any
            if "attributes" in poi_data:
                poi.attributes = poi_data["attributes"]
            
            pois.append(poi)
        
        # Add some additional POIs if variation is high
        if variation_amount > 0.7:
            extra_count = int(len(template_pois) * variation_amount * 0.3)
            
            for _ in range(extra_count):
                # Choose a random cell that doesn't have a POI yet
                valid_cells = [cell for cell in cells 
                              if not any(p.x == cell.x and p.y == cell.y for p in pois)]
                
                if valid_cells:
                    cell = rng.choice(valid_cells)
                    
                    # Create a random POI
                    poi_types = [
                        "ruins", "cave", "shrine", "outpost", "watchtower", 
                        "standing_stone", "campsite", "grave", "monument"
                    ]
                    
                    name_prefixes = [
                        "Lost", "Hidden", "Forgotten", "Ancient", "Mysterious",
                        "Abandoned", "Lonely", "Forlorn", "Desolate", "Wild"
                    ]
                    
                    name_suffixes = {
                        "ruins": "Ruins",
                        "cave": "Cave",
                        "shrine": "Shrine",
                        "outpost": "Outpost",
                        "watchtower": "Watchtower",
                        "standing_stone": "Stone",
                        "campsite": "Camp",
                        "grave": "Grave",
                        "monument": "Monument"
                    }
                    
                    poi_type = rng.choice(poi_types)
                    name = f"{rng.choice(name_prefixes)} {name_suffixes.get(poi_type, 'Place')}"
                    
                    description = f"A {poi_type} discovered during exploration."
                    
                    poi = PointOfInterest(
                        x=cell.x,
                        y=cell.y,
                        poi_type=poi_type,
                        name=name,
                        description=description
                    )
                    
                    pois.append(poi)
        
        return pois 
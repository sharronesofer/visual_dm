using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using VDM.Systems.Region;
using VDM.Runtime.Region;
using VisualDM.DTOs.World.Region;

namespace VDM.Runtime.Graphics
{
    /// <summary>
    /// Comprehensive sprite planning system for Task 7 systems.
    /// Analyzes implemented systems and generates sprite requirements for visual representation.
    /// </summary>
    public class SpritePlanner : MonoBehaviour
    {
        [Header("Sprite Planning Configuration")]
        [SerializeField] private bool _autoGeneratePlans = true;
        [SerializeField] private bool _includeRegionSprites = true;
        [SerializeField] private bool _includeUISprites = true;
        [SerializeField] private bool _includeIconSprites = true;
        [SerializeField] private bool _includeEffectSprites = true;
        
        [Header("Generated Sprite Plans")]
        [SerializeField] private int _totalSpritesPlanned = 0;
        [SerializeField] private int _regionSprites = 0;
        [SerializeField] private int _uiSprites = 0;
        [SerializeField] private int _iconSprites = 0;
        [SerializeField] private int _effectSprites = 0;
        
        // Sprite planning data
        private SpritePlan _currentPlan;
        private List<SpriteCategory> _spriteCategories;
        private Dictionary<string, List<SpriteRequirement>> _systemSpriteRequirements;
        
        // System references
        private RegionSystemController _regionController;
        
        // Events
        public event Action<SpritePlan> OnSpritePlanGenerated;
        public event Action<SpriteRequirement> OnSpriteRequirementAdded;
        
        #region Unity Lifecycle
        
        private void Start()
        {
            InitializeSpritePlanner();
            
            if (_autoGeneratePlans)
            {
                GenerateComprehensiveSpritePlan();
            }
        }
        
        #endregion
        
        #region Initialization
        
        private void InitializeSpritePlanner()
        {
            // Initialize data structures
            _spriteCategories = new List<SpriteCategory>();
            _systemSpriteRequirements = new Dictionary<string, List<SpriteRequirement>>();
            
            // Find system references
            _regionController = FindObjectOfType<RegionSystemController>();
            
            // Initialize sprite categories
            InitializeSpriteCategories();
            
            Debug.Log("[SpritePlanner] Sprite planner initialized successfully");
        }
        
        private void InitializeSpriteCategories()
        {
            // Region System Sprites
            _spriteCategories.Add(new SpriteCategory
            {
                Name = "Region Biomes",
                Description = "Sprites for different biome types and terrain",
                Priority = SpritePriority.High,
                EstimatedCount = 15
            });
            
            _spriteCategories.Add(new SpriteCategory
            {
                Name = "Region Maps",
                Description = "Tile sprites for region map generation",
                Priority = SpritePriority.High,
                EstimatedCount = 25
            });
            
            // Data System Sprites
            _spriteCategories.Add(new SpriteCategory
            {
                Name = "Data Icons",
                Description = "Icons for data types, entities, and mod content",
                Priority = SpritePriority.Medium,
                EstimatedCount = 20
            });
            
            // API System Sprites
            _spriteCategories.Add(new SpriteCategory
            {
                Name = "API Status",
                Description = "Visual indicators for API connection and status",
                Priority = SpritePriority.Medium,
                EstimatedCount = 8
            });
            
            // Integration System Sprites
            _spriteCategories.Add(new SpriteCategory
            {
                Name = "Integration UI",
                Description = "UI elements for backend integration interface",
                Priority = SpritePriority.Medium,
                EstimatedCount = 12
            });
            
            // Performance System Sprites
            _spriteCategories.Add(new SpriteCategory
            {
                Name = "Performance Visualization",
                Description = "Charts, graphs, and indicators for system performance",
                Priority = SpritePriority.Low,
                EstimatedCount = 10
            });
        }
        
        #endregion
        
        #region Sprite Plan Generation
        
        /// <summary>
        /// Generate a comprehensive sprite plan for all Task 7 systems
        /// </summary>
        [ContextMenu("Generate Sprite Plan")]
        public void GenerateComprehensiveSpritePlan()
        {
            Debug.Log("[SpritePlanner] Generating comprehensive sprite plan...");
            
            _currentPlan = new SpritePlan
            {
                PlanName = "Task 7 Systems Sprite Plan",
                GeneratedAt = DateTime.UtcNow,
                Requirements = new List<SpriteRequirement>()
            };
            
            // Generate requirements for each system
            if (_includeRegionSprites)
                GenerateRegionSystemSprites();
                
            if (_includeUISprites)
                GenerateUISystemSprites();
                
            if (_includeIconSprites)
                GenerateIconSystemSprites();
                
            if (_includeEffectSprites)
                GenerateEffectSystemSprites();
            
            // Calculate totals
            CalculateSpriteTotals();
            
            // Generate sprite specification documents
            GenerateSpriteSpecifications();
            
            Debug.Log($"[SpritePlanner] Generated sprite plan with {_currentPlan.Requirements.Count} total sprite requirements");
            
            OnSpritePlanGenerated?.Invoke(_currentPlan);
        }
        
        #endregion
        
        #region Region System Sprites
        
        private void GenerateRegionSystemSprites()
        {
            Debug.Log("[SpritePlanner] Generating region system sprite requirements...");
            
            var regionRequirements = new List<SpriteRequirement>();
            
            // Biome terrain sprites
            var biomeTypes = new[] { "Forest", "Desert", "Mountain", "Plains", "Swamp", "Tundra", "Coastal", "Volcanic" };
            foreach (var biome in biomeTypes)
            {
                regionRequirements.Add(new SpriteRequirement
                {
                    Name = $"{biome}_Terrain_Base",
                    Category = "Region Biomes",
                    Description = $"Base terrain sprite for {biome} biome",
                    Dimensions = new Vector2Int(64, 64),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.High,
                    Usage = SpriteUsage.Tile,
                    Tags = new List<string> { "biome", biome.ToLower(), "terrain" },
                    ColorPalette = GetBiomeColorPalette(biome),
                    StyleNotes = $"Tileable {biome.ToLower()} terrain with seamless edges. Should convey {GetBiomeCharacteristics(biome)}."
                });
                
                // Biome variation sprites
                for (int i = 1; i <= 3; i++)
                {
                    regionRequirements.Add(new SpriteRequirement
                    {
                        Name = $"{biome}_Terrain_Variant_{i}",
                        Category = "Region Biomes",
                        Description = $"Terrain variation {i} for {biome} biome",
                        Dimensions = new Vector2Int(64, 64),
                        Format = SpriteFormat.PNG,
                        Priority = SpritePriority.Medium,
                        Usage = SpriteUsage.Tile,
                        Tags = new List<string> { "biome", biome.ToLower(), "terrain", "variant" },
                        ColorPalette = GetBiomeColorPalette(biome),
                        StyleNotes = $"Variation of base {biome.ToLower()} terrain for visual diversity."
                    });
                }
            }
            
            // Region map tiles
            var mapTileTypes = new[] { "Grass", "Stone", "Water", "Sand", "Snow", "Lava", "Mud", "Ice" };
            foreach (var tileType in mapTileTypes)
            {
                regionRequirements.Add(new SpriteRequirement
                {
                    Name = $"MapTile_{tileType}",
                    Category = "Region Maps",
                    Description = $"Map tile sprite for {tileType} terrain",
                    Dimensions = new Vector2Int(32, 32),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.High,
                    Usage = SpriteUsage.Tile,
                    Tags = new List<string> { "map", "tile", tileType.ToLower() },
                    ColorPalette = GetTileColorPalette(tileType),
                    StyleNotes = $"Small map tile for {tileType.ToLower()} terrain. Should be recognizable at small scale."
                });
            }
            
            // Region transition sprites
            var transitionTypes = new[] { "ForestToDesert", "MountainToPlains", "CoastalToOcean", "TundraToTaiga" };
            foreach (var transition in transitionTypes)
            {
                regionRequirements.Add(new SpriteRequirement
                {
                    Name = $"Transition_{transition}",
                    Category = "Region Biomes",
                    Description = $"Transition sprite between {transition.Replace("To", " and ")} biomes",
                    Dimensions = new Vector2Int(64, 64),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Medium,
                    Usage = SpriteUsage.Tile,
                    Tags = new List<string> { "transition", "biome", "blend" },
                    ColorPalette = GetTransitionColorPalette(transition),
                    StyleNotes = $"Seamless transition between biomes. Should blend naturally with adjacent tiles."
                });
            }
            
            // Climate indicator sprites
            var climateTypes = new[] { "Hot", "Cold", "Humid", "Dry", "Temperate", "Extreme" };
            foreach (var climate in climateTypes)
            {
                regionRequirements.Add(new SpriteRequirement
                {
                    Name = $"Climate_{climate}_Indicator",
                    Category = "Region Maps",
                    Description = $"Visual indicator for {climate} climate zones",
                    Dimensions = new Vector2Int(16, 16),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Low,
                    Usage = SpriteUsage.Icon,
                    Tags = new List<string> { "climate", "indicator", climate.ToLower() },
                    ColorPalette = GetClimateColorPalette(climate),
                    StyleNotes = $"Small overlay icon indicating {climate.ToLower()} climate. Should be subtle but recognizable."
                });
            }
            
            _systemSpriteRequirements["RegionSystem"] = regionRequirements;
            _currentPlan.Requirements.AddRange(regionRequirements);
            
            Debug.Log($"[SpritePlanner] Generated {regionRequirements.Count} region system sprite requirements");
        }
        
        #endregion
        
        #region UI System Sprites
        
        private void GenerateUISystemSprites()
        {
            Debug.Log("[SpritePlanner] Generating UI system sprite requirements...");
            
            var uiRequirements = new List<SpriteRequirement>();
            
            // Backend integration UI
            var integrationElements = new[] 
            {
                ("Connection_Status_Connected", "Green indicator for successful backend connection"),
                ("Connection_Status_Disconnected", "Red indicator for failed backend connection"),
                ("Connection_Status_Connecting", "Yellow indicator for connection in progress"),
                ("Service_Health_Good", "Green indicator for healthy service status"),
                ("Service_Health_Warning", "Yellow indicator for service warnings"),
                ("Service_Health_Error", "Red indicator for service errors"),
                ("Data_Sync_Active", "Icon showing active data synchronization"),
                ("Data_Sync_Idle", "Icon showing idle synchronization state"),
                ("Mock_Server_Badge", "Badge indicating mock server is active"),
                ("Real_Server_Badge", "Badge indicating real server connection")
            };
            
            foreach (var (name, description) in integrationElements)
            {
                uiRequirements.Add(new SpriteRequirement
                {
                    Name = name,
                    Category = "Integration UI",
                    Description = description,
                    Dimensions = new Vector2Int(24, 24),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Medium,
                    Usage = SpriteUsage.Icon,
                    Tags = new List<string> { "ui", "integration", "status" },
                    ColorPalette = GetStatusColorPalette(name),
                    StyleNotes = "Clean, modern icon style. Should be clear at small sizes."
                });
            }
            
            // Performance monitoring UI
            var performanceElements = new[]
            {
                ("FPS_Meter_Background", "Background for FPS display meter"),
                ("Memory_Usage_Bar", "Progress bar for memory usage visualization"),
                ("Performance_Graph_Grid", "Grid background for performance graphs"),
                ("Optimization_Running", "Animated icon for optimization in progress"),
                ("Alert_Warning", "Warning alert icon for performance issues"),
                ("Alert_Critical", "Critical alert icon for severe performance issues")
            };
            
            foreach (var (name, description) in performanceElements)
            {
                uiRequirements.Add(new SpriteRequirement
                {
                    Name = name,
                    Category = "Performance Visualization",
                    Description = description,
                    Dimensions = GetPerformanceUIDimensions(name),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Low,
                    Usage = SpriteUsage.UI,
                    Tags = new List<string> { "ui", "performance", "monitoring" },
                    ColorPalette = GetPerformanceColorPalette(name),
                    StyleNotes = "Technical, dashboard-style visuals. Should convey performance data clearly."
                });
            }
            
            // Integration test UI
            var testingElements = new[]
            {
                ("Test_Passed", "Green checkmark for passed tests"),
                ("Test_Failed", "Red X for failed tests"),
                ("Test_Running", "Animated spinner for running tests"),
                ("Test_Category_Region", "Icon representing region system tests"),
                ("Test_Category_Data", "Icon representing data system tests"),
                ("Test_Category_API", "Icon representing API tests"),
                ("Test_Category_Integration", "Icon representing integration tests")
            };
            
            foreach (var (name, description) in testingElements)
            {
                uiRequirements.Add(new SpriteRequirement
                {
                    Name = name,
                    Category = "Integration UI",
                    Description = description,
                    Dimensions = new Vector2Int(20, 20),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Medium,
                    Usage = SpriteUsage.Icon,
                    Tags = new List<string> { "ui", "testing", "status" },
                    ColorPalette = GetTestingColorPalette(name),
                    StyleNotes = "Clear, recognizable test status indicators."
                });
            }
            
            _systemSpriteRequirements["UISystem"] = uiRequirements;
            _currentPlan.Requirements.AddRange(uiRequirements);
            
            Debug.Log($"[SpritePlanner] Generated {uiRequirements.Count} UI system sprite requirements");
        }
        
        #endregion
        
        #region Icon System Sprites
        
        private void GenerateIconSystemSprites()
        {
            Debug.Log("[SpritePlanner] Generating icon system sprite requirements...");
            
            var iconRequirements = new List<SpriteRequirement>();
            
            // Data system icons
            var dataIcons = new[]
            {
                ("Entity_Character", "Icon for character entities"),
                ("Entity_Item", "Icon for item entities"),
                ("Entity_Quest", "Icon for quest entities"),
                ("Entity_Region", "Icon for region entities"),
                ("Mod_Loaded", "Icon for loaded mod content"),
                ("Mod_Error", "Icon for mod loading errors"),
                ("Data_Validation_Pass", "Icon for successful data validation"),
                ("Data_Validation_Fail", "Icon for failed data validation")
            };
            
            foreach (var (name, description) in dataIcons)
            {
                iconRequirements.Add(new SpriteRequirement
                {
                    Name = name,
                    Category = "Data Icons",
                    Description = description,
                    Dimensions = new Vector2Int(32, 32),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Medium,
                    Usage = SpriteUsage.Icon,
                    Tags = new List<string> { "icon", "data", "entity" },
                    ColorPalette = GetDataIconColorPalette(name),
                    StyleNotes = "Clean, recognizable icons suitable for lists and menus."
                });
            }
            
            // System status icons
            var systemIcons = new[]
            {
                ("System_Region_Active", "Icon for active region system"),
                ("System_Data_Active", "Icon for active data system"),
                ("System_API_Active", "Icon for active API system"),
                ("System_Integration_Active", "Icon for active integration system"),
                ("System_Optimization_Active", "Icon for active optimization system"),
                ("System_Error", "Icon for system errors"),
                ("System_Initializing", "Icon for system initialization")
            };
            
            foreach (var (name, description) in systemIcons)
            {
                iconRequirements.Add(new SpriteRequirement
                {
                    Name = name,
                    Category = "API Status",
                    Description = description,
                    Dimensions = new Vector2Int(28, 28),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Medium,
                    Usage = SpriteUsage.Icon,
                    Tags = new List<string> { "icon", "system", "status" },
                    ColorPalette = GetSystemIconColorPalette(name),
                    StyleNotes = "Professional system status icons with clear visual hierarchy."
                });
            }
            
            _systemSpriteRequirements["IconSystem"] = iconRequirements;
            _currentPlan.Requirements.AddRange(iconRequirements);
            
            Debug.Log($"[SpritePlanner] Generated {iconRequirements.Count} icon system sprite requirements");
        }
        
        #endregion
        
        #region Effect System Sprites
        
        private void GenerateEffectSystemSprites()
        {
            Debug.Log("[SpritePlanner] Generating effect system sprite requirements...");
            
            var effectRequirements = new List<SpriteRequirement>();
            
            // Region generation effects
            var regionEffects = new[]
            {
                ("Region_Generation_Particles", "Particle effect for region generation"),
                ("Biome_Transition_Glow", "Glow effect for biome transitions"),
                ("Map_Loading_Spinner", "Animated loading effect for map generation"),
                ("Procedural_Generation_Sparks", "Spark effects for procedural generation")
            };
            
            foreach (var (name, description) in regionEffects)
            {
                effectRequirements.Add(new SpriteRequirement
                {
                    Name = name,
                    Category = "Region Effects",
                    Description = description,
                    Dimensions = new Vector2Int(64, 64),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Low,
                    Usage = SpriteUsage.Effect,
                    Tags = new List<string> { "effect", "region", "animation" },
                    ColorPalette = GetEffectColorPalette(name),
                    StyleNotes = "Animated sprite sheet with multiple frames. Should enhance the sense of dynamic world generation."
                });
            }
            
            // Data system effects
            var dataEffects = new[]
            {
                ("Data_Sync_Pulse", "Pulsing effect for data synchronization"),
                ("Entity_Creation_Flash", "Flash effect for entity creation"),
                ("Mod_Loading_Progress", "Progress effect for mod loading"),
                ("Validation_Success_Glow", "Success glow for data validation")
            };
            
            foreach (var (name, description) in dataEffects)
            {
                effectRequirements.Add(new SpriteRequirement
                {
                    Name = name,
                    Category = "Data Effects",
                    Description = description,
                    Dimensions = new Vector2Int(32, 32),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Low,
                    Usage = SpriteUsage.Effect,
                    Tags = new List<string> { "effect", "data", "animation" },
                    ColorPalette = GetEffectColorPalette(name),
                    StyleNotes = "Subtle effects that provide visual feedback for data operations."
                });
            }
            
            // API connection effects
            var apiEffects = new[]
            {
                ("Connection_Establishing", "Animated effect for connection establishment"),
                ("Data_Transfer_Flow", "Flow effect showing data transfer"),
                ("Mock_Server_Indicator", "Visual indicator for mock server mode"),
                ("Real_Server_Indicator", "Visual indicator for real server mode")
            };
            
            foreach (var (name, description) in apiEffects)
            {
                effectRequirements.Add(new SpriteRequirement
                {
                    Name = name,
                    Category = "API Effects",
                    Description = description,
                    Dimensions = new Vector2Int(24, 24),
                    Format = SpriteFormat.PNG,
                    Priority = SpritePriority.Low,
                    Usage = SpriteUsage.Effect,
                    Tags = new List<string> { "effect", "api", "connection" },
                    ColorPalette = GetEffectColorPalette(name),
                    StyleNotes = "Technical effects that communicate network activity and server connections."
                });
            }
            
            _systemSpriteRequirements["EffectSystem"] = effectRequirements;
            _currentPlan.Requirements.AddRange(effectRequirements);
            
            Debug.Log($"[SpritePlanner] Generated {effectRequirements.Count} effect system sprite requirements");
        }
        
        #endregion
        
        #region Color Palette Generation
        
        private List<string> GetBiomeColorPalette(string biome)
        {
            return biome switch
            {
                "Forest" => new List<string> { "#2D5016", "#4A7C59", "#6B8E23", "#228B22", "#32CD32" },
                "Desert" => new List<string> { "#F4A460", "#D2691E", "#CD853F", "#DEB887", "#F5DEB3" },
                "Mountain" => new List<string> { "#696969", "#A9A9A9", "#D3D3D3", "#708090", "#2F4F4F" },
                "Plains" => new List<string> { "#9ACD32", "#ADFF2F", "#7CFC00", "#98FB98", "#90EE90" },
                "Swamp" => new List<string> { "#556B2F", "#6B8E23", "#8FBC8F", "#2E8B57", "#3CB371" },
                "Tundra" => new List<string> { "#F0F8FF", "#E6E6FA", "#D3D3D3", "#B0C4DE", "#87CEEB" },
                "Coastal" => new List<string> { "#4682B4", "#5F9EA0", "#87CEEB", "#B0E0E6", "#AFEEEE" },
                "Volcanic" => new List<string> { "#8B0000", "#DC143C", "#FF4500", "#FF6347", "#FFA500" },
                _ => new List<string> { "#808080", "#A0A0A0", "#C0C0C0", "#D0D0D0", "#E0E0E0" }
            };
        }
        
        private List<string> GetTileColorPalette(string tileType)
        {
            return tileType switch
            {
                "Grass" => new List<string> { "#228B22", "#32CD32", "#7CFC00" },
                "Stone" => new List<string> { "#696969", "#A9A9A9", "#D3D3D3" },
                "Water" => new List<string> { "#0000FF", "#1E90FF", "#87CEEB" },
                "Sand" => new List<string> { "#F4A460", "#DEB887", "#F5DEB3" },
                "Snow" => new List<string> { "#FFFAFA", "#F0F8FF", "#E6E6FA" },
                "Lava" => new List<string> { "#DC143C", "#FF4500", "#FFA500" },
                "Mud" => new List<string> { "#8B4513", "#A0522D", "#CD853F" },
                "Ice" => new List<string> { "#B0E0E6", "#AFEEEE", "#E0FFFF" },
                _ => new List<string> { "#808080", "#A0A0A0", "#C0C0C0" }
            };
        }
        
        private List<string> GetTransitionColorPalette(string transition)
        {
            // Blend colors from both biomes
            return new List<string> { "#7B9B42", "#A8B568", "#D4E094", "#8FA168", "#B5C478" };
        }
        
        private List<string> GetClimateColorPalette(string climate)
        {
            return climate switch
            {
                "Hot" => new List<string> { "#FF4500", "#FF6347", "#FFA500" },
                "Cold" => new List<string> { "#87CEEB", "#B0E0E6", "#E0FFFF" },
                "Humid" => new List<string> { "#4682B4", "#5F9EA0", "#87CEEB" },
                "Dry" => new List<string> { "#DEB887", "#F5DEB3", "#FFFACD" },
                "Temperate" => new List<string> { "#9ACD32", "#ADFF2F", "#98FB98" },
                "Extreme" => new List<string> { "#DC143C", "#FF1493", "#FF6347" },
                _ => new List<string> { "#808080", "#A0A0A0", "#C0C0C0" }
            };
        }
        
        private List<string> GetStatusColorPalette(string name)
        {
            if (name.Contains("Connected") || name.Contains("Good"))
                return new List<string> { "#228B22", "#32CD32", "#90EE90" };
            if (name.Contains("Warning") || name.Contains("Connecting"))
                return new List<string> { "#FFD700", "#FFA500", "#FFFF00" };
            if (name.Contains("Error") || name.Contains("Disconnected"))
                return new List<string> { "#DC143C", "#FF4500", "#FF6347" };
            
            return new List<string> { "#4682B4", "#5F9EA0", "#87CEEB" };
        }
        
        private List<string> GetPerformanceColorPalette(string name)
        {
            if (name.Contains("Warning"))
                return new List<string> { "#FFD700", "#FFA500", "#FFFF00" };
            if (name.Contains("Critical"))
                return new List<string> { "#DC143C", "#FF4500", "#FF6347" };
            
            return new List<string> { "#4682B4", "#5F9EA0", "#87CEEB" };
        }
        
        private List<string> GetTestingColorPalette(string name)
        {
            if (name.Contains("Passed"))
                return new List<string> { "#228B22", "#32CD32", "#90EE90" };
            if (name.Contains("Failed"))
                return new List<string> { "#DC143C", "#FF4500", "#FF6347" };
            if (name.Contains("Running"))
                return new List<string> { "#4682B4", "#5F9EA0", "#87CEEB" };
            
            return new List<string> { "#808080", "#A0A0A0", "#C0C0C0" };
        }
        
        private List<string> GetDataIconColorPalette(string name)
        {
            if (name.Contains("Character"))
                return new List<string> { "#4169E1", "#6495ED", "#87CEEB" };
            if (name.Contains("Item"))
                return new List<string> { "#FFD700", "#FFA500", "#FFFF00" };
            if (name.Contains("Quest"))
                return new List<string> { "#32CD32", "#90EE90", "#98FB98" };
            if (name.Contains("Region"))
                return new List<string> { "#8B4513", "#A0522D", "#CD853F" };
            
            return new List<string> { "#808080", "#A0A0A0", "#C0C0C0" };
        }
        
        private List<string> GetSystemIconColorPalette(string name)
        {
            if (name.Contains("Active"))
                return new List<string> { "#228B22", "#32CD32", "#90EE90" };
            if (name.Contains("Error"))
                return new List<string> { "#DC143C", "#FF4500", "#FF6347" };
            if (name.Contains("Initializing"))
                return new List<string> { "#4682B4", "#5F9EA0", "#87CEEB" };
            
            return new List<string> { "#808080", "#A0A0A0", "#C0C0C0" };
        }
        
        private List<string> GetEffectColorPalette(string name)
        {
            if (name.Contains("Generation") || name.Contains("Creation"))
                return new List<string> { "#32CD32", "#90EE90", "#98FB98" };
            if (name.Contains("Transfer") || name.Contains("Flow"))
                return new List<string> { "#4682B4", "#5F9EA0", "#87CEEB" };
            if (name.Contains("Success") || name.Contains("Glow"))
                return new List<string> { "#FFD700", "#FFA500", "#FFFF00" };
            
            return new List<string> { "#9370DB", "#BA55D3", "#DDA0DD" };
        }
        
        #endregion
        
        #region Helper Methods
        
        private Vector2Int GetPerformanceUIDimensions(string name)
        {
            return name switch
            {
                "FPS_Meter_Background" => new Vector2Int(100, 30),
                "Memory_Usage_Bar" => new Vector2Int(200, 20),
                "Performance_Graph_Grid" => new Vector2Int(300, 200),
                _ => new Vector2Int(32, 32)
            };
        }
        
        private string GetBiomeCharacteristics(string biome)
        {
            return biome switch
            {
                "Forest" => "lush vegetation and dense tree coverage",
                "Desert" => "arid landscape with sandy terrain",
                "Mountain" => "rocky peaks and steep terrain",
                "Plains" => "wide open grasslands",
                "Swamp" => "wetlands with murky water",
                "Tundra" => "frozen ground with sparse vegetation",
                "Coastal" => "shoreline with beaches and cliffs",
                "Volcanic" => "active lava flows and ash",
                _ => "generic terrain features"
            };
        }
        
        private void CalculateSpriteTotals()
        {
            _totalSpritesPlanned = _currentPlan.Requirements.Count;
            _regionSprites = _currentPlan.Requirements.Count(r => r.Category.Contains("Region"));
            _uiSprites = _currentPlan.Requirements.Count(r => r.Category.Contains("UI") || r.Category.Contains("Integration") || r.Category.Contains("Performance"));
            _iconSprites = _currentPlan.Requirements.Count(r => r.Category.Contains("Icon") || r.Category.Contains("Status") || r.Category.Contains("Data"));
            _effectSprites = _currentPlan.Requirements.Count(r => r.Category.Contains("Effect"));
        }
        
        private void GenerateSpriteSpecifications()
        {
            // Group requirements by category for better organization
            var categorizedRequirements = _currentPlan.Requirements
                .GroupBy(r => r.Category)
                .ToDictionary(g => g.Key, g => g.ToList());
            
            _currentPlan.Specifications = new SpriteSpecificationDocument
            {
                ProjectName = "Visual DM - Task 7 Systems",
                TotalSprites = _totalSpritesPlanned,
                Categories = categorizedRequirements,
                StyleGuide = GenerateStyleGuide(),
                ProductionNotes = GenerateProductionNotes()
            };
        }
        
        private List<string> GenerateStyleGuide()
        {
            return new List<string>
            {
                "Art Style: Modern pixel art with clean lines and clear readability",
                "Color Depth: 24-bit color with alpha transparency support",
                "Consistency: Maintain consistent lighting and perspective across all sprites",
                "Scaling: All sprites should look good at 100% and 200% scale",
                "Animation: Effects should use 4-8 frame animations at 12-15 FPS",
                "Contrast: Ensure sufficient contrast for accessibility",
                "File Format: PNG with transparency, optimized for web",
                "Naming Convention: CategoryName_ElementName_Variant (e.g., Region_Forest_Base)"
            };
        }
        
        private List<string> GenerateProductionNotes()
        {
            return new List<string>
            {
                $"Total sprite count: {_totalSpritesPlanned} sprites across {_spriteCategories.Count} categories",
                $"Priority breakdown: {_currentPlan.Requirements.Count(r => r.Priority == SpritePriority.High)} high, {_currentPlan.Requirements.Count(r => r.Priority == SpritePriority.Medium)} medium, {_currentPlan.Requirements.Count(r => r.Priority == SpritePriority.Low)} low priority",
                "Region sprites should be created first as they form the visual foundation",
                "UI sprites can be created iteratively based on interface development",
                "Effect sprites are lowest priority and can be added for polish",
                "Consider creating a sprite atlas for performance optimization",
                "All sprites should be tested at target resolution in Unity",
                "Maintain source files in vector format where possible for future scaling"
            };
        }
        
        #endregion
        
        #region Public API
        
        /// <summary>
        /// Get the current sprite plan
        /// </summary>
        public SpritePlan GetCurrentSpritePlan()
        {
            return _currentPlan;
        }
        
        /// <summary>
        /// Get sprite requirements for a specific system
        /// </summary>
        public List<SpriteRequirement> GetSystemRequirements(string systemName)
        {
            return _systemSpriteRequirements.ContainsKey(systemName) 
                ? _systemSpriteRequirements[systemName] 
                : new List<SpriteRequirement>();
        }
        
        /// <summary>
        /// Export sprite plan to JSON format
        /// </summary>
        public string ExportSpritePlanToJSON()
        {
            return JsonUtility.ToJson(_currentPlan, true);
        }
        
        #endregion
        
        #region Data Classes
        
        [Serializable]
        public class SpritePlan
        {
            public string PlanName;
            public DateTime GeneratedAt;
            public List<SpriteRequirement> Requirements;
            public SpriteSpecificationDocument Specifications;
        }
        
        [Serializable]
        public class SpriteRequirement
        {
            public string Name;
            public string Category;
            public string Description;
            public Vector2Int Dimensions;
            public SpriteFormat Format;
            public SpritePriority Priority;
            public SpriteUsage Usage;
            public List<string> Tags;
            public List<string> ColorPalette;
            public string StyleNotes;
        }
        
        [Serializable]
        public class SpriteCategory
        {
            public string Name;
            public string Description;
            public SpritePriority Priority;
            public int EstimatedCount;
        }
        
        [Serializable]
        public class SpriteSpecificationDocument
        {
            public string ProjectName;
            public int TotalSprites;
            public Dictionary<string, List<SpriteRequirement>> Categories;
            public List<string> StyleGuide;
            public List<string> ProductionNotes;
        }
        
        public enum SpriteFormat
        {
            PNG,
            JPG,
            TGA
        }
        
        public enum SpritePriority
        {
            Low,
            Medium,
            High
        }
        
        public enum SpriteUsage
        {
            Tile,
            Icon,
            UI,
            Effect,
            Character,
            Environment
        }
        
        #endregion
    }
} 
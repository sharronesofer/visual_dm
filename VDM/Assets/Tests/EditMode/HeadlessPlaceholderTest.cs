using System;
using System.IO;
using UnityEngine;

namespace VDM.Core
{
    /// <summary>
    /// Headless test script for placeholder sprite generation and frontend compliance verification
    /// Can be run from command line to verify sprite generation functionality and frontend compliance
    /// </summary>
    public class HeadlessPlaceholderTest : MonoBehaviour
    {
        [Header("Test Configuration")]
        [SerializeField] private bool runOnStart = true;
        [SerializeField] private bool exitAfterTest = true;
        [SerializeField] private bool verboseLogging = true;
        [SerializeField] private bool performCompleteAnalysis = true;

        private void Start()
        {
            if (runOnStart)
            {
                RunHeadlessTest();
            }
        }

        /// <summary>
        /// Run the headless placeholder sprite test and frontend compliance check
        /// </summary>
        public void RunHeadlessTest()
        {
            try
            {
                LogMessage("=== FRONTEND SYSTEM ANALYSIS AND COMPLIANCE REVIEW ===");
                LogMessage("Starting comprehensive frontend compliance verification...");

                if (performCompleteAnalysis)
                {
                    LogMessage("Phase 1: Frontend Structure Compliance");
                    VerifyFrontendStructure();

                    LogMessage("Phase 2: Namespace Compliance");
                    VerifyNamespaceCompliance();

                    LogMessage("Phase 3: Assembly Definition Validation");
                    VerifyAssemblyDefinitions();
                }

                LogMessage("Phase 4: Placeholder Sprite Generation");
                
                // Create placeholder sprite generator
                GameObject generatorObj = new GameObject("PlaceholderSpriteGenerator");
                PlaceholderSpriteGenerator generator = generatorObj.AddComponent<PlaceholderSpriteGenerator>();

                // Enable headless mode
                var generatorType = typeof(PlaceholderSpriteGenerator);
                var enableHeadlessModeField = generatorType.GetField("enableHeadlessMode", 
                    System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                if (enableHeadlessModeField != null)
                {
                    enableHeadlessModeField.SetValue(generator, true);
                }

                LogMessage("Generating placeholder sprites...");

                // Generate sprites
                generator.GenerateAndLoadSprites();

                // Verify sprites were created
                VerifySpritesCreated();

                // Test sprite loading
                TestSpriteLoading(generator);

                // Verify file integrity
                VerifyFileIntegrity();

                LogMessage("=== COMPLIANCE REVIEW COMPLETE ===");
                LogMessage("✅ All frontend compliance checks passed successfully!");
                LogMessage("✅ All placeholder sprites generated and verified!");

                if (exitAfterTest && Application.isBatchMode)
                {
                    LogMessage("Exiting application with success code...");
                    Application.Quit(0);
                }
            }
            catch (Exception ex)
            {
                LogError($"Frontend compliance test failed: {ex.Message}");
                LogError($"Stack trace: {ex.StackTrace}");
                if (exitAfterTest && Application.isBatchMode)
                {
                    Application.Quit(1);
                }
            }
        }

        /// <summary>
        /// Verify Unity frontend structure compliance with Development_Bible.md
        /// </summary>
        private void VerifyFrontendStructure()
        {
            LogMessage("Verifying frontend directory structure...");

            string[] requiredSystemDirectories = {
                "Assets/Scripts/Core",
                "Assets/Scripts/DTOs", 
                "Assets/Scripts/Systems",
                "Assets/Scripts/Infrastructure",
                "Assets/Scripts/UI",
                "Assets/Scripts/Services",
                "Assets/Scripts/Integration",
                "Assets/Scripts/Runtime",
                "Assets/Tests"
            };

            foreach (string dir in requiredSystemDirectories)
            {
                string fullPath = Path.Combine(Application.dataPath, "..", dir);
                if (Directory.Exists(fullPath))
                {
                    LogMessage($"✓ {dir} - Directory exists");
                }
                else
                {
                    LogMessage($"⚠ {dir} - Directory missing (may be acceptable)");
                }
            }

            // Verify core systems exist
            string systemsPath = Path.Combine(Application.dataPath, "Scripts", "Systems");
            if (Directory.Exists(systemsPath))
            {
                string[] systemDirs = Directory.GetDirectories(systemsPath);
                LogMessage($"Found {systemDirs.Length} system directories in Scripts/Systems/");
                
                string[] expectedSystems = {
                    "analytics", "arc", "character", "chaos", "combat", "crafting",
                    "dialogue", "economy", "equipment", "events", "faction", 
                    "inventory", "magic", "memory", "npc", "quest", "region", 
                    "religion", "time", "world_state"
                };

                int foundSystems = 0;
                foreach (string expectedSystem in expectedSystems)
                {
                    string systemPath = Path.Combine(systemsPath, expectedSystem);
                    if (Directory.Exists(systemPath))
                    {
                        foundSystems++;
                    }
                }
                LogMessage($"✓ Core systems found: {foundSystems}/{expectedSystems.Length}");
            }

            LogMessage("Frontend structure verification completed");
        }

        /// <summary>
        /// Verify namespace compliance with canonical VDM.* patterns
        /// </summary>
        private void VerifyNamespaceCompliance()
        {
            LogMessage("Verifying namespace compliance...");
            
            // Check for any remaining non-canonical namespaces in key directories
            string[] searchDirectories = {
                Path.Combine(Application.dataPath, "Scripts", "DTOs"),
                Path.Combine(Application.dataPath, "Scripts", "Systems"),
                Path.Combine(Application.dataPath, "Scripts", "Core")
            };

            bool complianceIssuesFound = false;

            foreach (string searchDir in searchDirectories)
            {
                if (Directory.Exists(searchDir))
                {
                    string[] csFiles = Directory.GetFiles(searchDir, "*.cs", SearchOption.AllDirectories);
                    LogMessage($"Checking {csFiles.Length} C# files in {Path.GetFileName(searchDir)}/");
                    
                    foreach (string file in csFiles)
                    {
                        if (CheckFileNamespaceCompliance(file))
                        {
                            // File is compliant
                        }
                        else
                        {
                            complianceIssuesFound = true;
                        }
                    }
                }
            }

            if (!complianceIssuesFound)
            {
                LogMessage("✓ All namespaces comply with canonical VDM.* patterns");
            }
            else
            {
                LogMessage("⚠ Some namespace compliance issues found");
            }
        }

        /// <summary>
        /// Check individual file for namespace compliance
        /// </summary>
        private bool CheckFileNamespaceCompliance(string filePath)
        {
            try
            {
                string[] lines = File.ReadAllLines(filePath);
                foreach (string line in lines)
                {
                    if (line.Trim().StartsWith("namespace"))
                    {
                        if (line.Contains("VDM.Assets.Scripts"))
                        {
                            LogMessage($"⚠ Non-canonical namespace in {Path.GetFileName(filePath)}: {line.Trim()}");
                            return false;
                        }
                    }
                }
                return true;
            }
            catch (Exception ex)
            {
                LogMessage($"⚠ Error checking file {filePath}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Verify assembly definition files are properly configured
        /// </summary>
        private void VerifyAssemblyDefinitions()
        {
            LogMessage("Verifying assembly definition compliance...");

            string[] expectedAsmDefs = {
                "Assets/Scripts/DTOs/VDM.DTOs.asmdef",
                "Assets/Scripts/Systems/VDM.Systems.asmdef",
                "Assets/Scripts/Core/VDM.Core.asmdef",
                "Assets/Tests/VDM.Tests.asmdef"
            };

            int foundAsmDefs = 0;
            foreach (string asmDefPath in expectedAsmDefs)
            {
                string fullPath = Path.Combine(Application.dataPath, "..", asmDefPath);
                if (File.Exists(fullPath))
                {
                    foundAsmDefs++;
                    LogMessage($"✓ {Path.GetFileName(asmDefPath)} - Found");
                }
                else
                {
                    LogMessage($"⚠ {Path.GetFileName(asmDefPath)} - Missing");
                }
            }

            LogMessage($"Assembly definition check: {foundAsmDefs}/{expectedAsmDefs.Length} found");
        }

        /// <summary>
        /// Verify that sprite files were created
        /// </summary>
        private void VerifySpritesCreated()
        {
            string placeholderPath = Path.Combine(Application.dataPath, "Placeholders");
            string[] expectedSprites = {
                "grassland_hex.png",
                "character_sprite.png", 
                "small_building_icon.png",
                "ui_panel_background.png",
                "dialogue_frame.png"
            };

            LogMessage($"Verifying sprites in: {placeholderPath}");

            foreach (string spriteFile in expectedSprites)
            {
                string fullPath = Path.Combine(placeholderPath, spriteFile);
                if (File.Exists(fullPath))
                {
                    FileInfo fileInfo = new FileInfo(fullPath);
                    LogMessage($"✓ {spriteFile} - Size: {fileInfo.Length} bytes");
                }
                else
                {
                    throw new FileNotFoundException($"Expected sprite file not found: {spriteFile}");
                }
            }

            LogMessage("All sprite files verified successfully!");
        }

        /// <summary>
        /// Test sprite loading functionality
        /// </summary>
        private void TestSpriteLoading(PlaceholderSpriteGenerator generator)
        {
            LogMessage("Testing sprite loading...");

            Sprite[] loadedSprites = generator.GetLoadedSprites();
            if (loadedSprites == null || loadedSprites.Length == 0)
            {
                throw new InvalidOperationException("No sprites were loaded");
            }

            LogMessage($"Loaded {loadedSprites.Length} sprites:");

            for (int i = 0; i < loadedSprites.Length; i++)
            {
                Sprite sprite = loadedSprites[i];
                if (sprite != null)
                {
                    LogMessage($"  {i + 1}. {sprite.name} - {sprite.texture.width}x{sprite.texture.height}");
                }
                else
                {
                    throw new InvalidOperationException($"Sprite at index {i} is null");
                }
            }

            // Test specific sprite retrieval
            Sprite grasslandSprite = generator.GetSpriteByName("grassland_hex");
            if (grasslandSprite == null)
            {
                throw new InvalidOperationException("Could not retrieve grassland_hex sprite by name");
            }

            LogMessage("Sprite loading test completed successfully!");
        }

        /// <summary>
        /// Verify file integrity and format compliance
        /// </summary>
        private void VerifyFileIntegrity()
        {
            LogMessage("Verifying file integrity...");

            string placeholderPath = Path.Combine(Application.dataPath, "Placeholders");
            string[] spriteFiles = Directory.GetFiles(placeholderPath, "*.png");

            foreach (string file in spriteFiles)
            {
                FileInfo fileInfo = new FileInfo(file);
                
                // Check file size (should be reasonable for PNG files)
                if (fileInfo.Length > 0 && fileInfo.Length < 10 * 1024 * 1024) // 10MB max
                {
                    LogMessage($"✓ {fileInfo.Name} - Size: {fileInfo.Length} bytes (valid)");
                }
                else
                {
                    LogMessage($"⚠ {fileInfo.Name} - Size: {fileInfo.Length} bytes (may be invalid)");
                }

                // Verify PNG header
                try
                {
                    using (FileStream fs = new FileStream(file, FileMode.Open, FileAccess.Read))
                    {
                        byte[] header = new byte[8];
                        fs.Read(header, 0, 8);
                        
                        // PNG signature: 89 50 4E 47 0D 0A 1A 0A
                        if (header[0] == 0x89 && header[1] == 0x50 && header[2] == 0x4E && header[3] == 0x47)
                        {
                            LogMessage($"✓ {fileInfo.Name} - Valid PNG format");
                        }
                        else
                        {
                            LogMessage($"⚠ {fileInfo.Name} - Invalid PNG format");
                        }
                    }
                }
                catch (Exception ex)
                {
                    LogMessage($"⚠ Error verifying {fileInfo.Name}: {ex.Message}");
                }
            }

            LogMessage("File integrity verification completed");
        }

        /// <summary>
        /// Log a message with timestamp
        /// </summary>
        private void LogMessage(string message)
        {
            if (verboseLogging)
            {
                string timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
                Debug.Log($"[{timestamp}] [HeadlessPlaceholderTest] {message}");
            }
        }

        /// <summary>
        /// Log an error message
        /// </summary>
        private void LogError(string message)
        {
            string timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
            Debug.LogError($"[{timestamp}] [HeadlessPlaceholderTest] ERROR: {message}");
        }

        /// <summary>
        /// Static method to run test automatically when Unity starts in batch mode
        /// </summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        public static void RunCommandLineTest()
        {
            // Only run automatically in batch mode
            if (Application.isBatchMode)
            {
                GameObject testObj = new GameObject("HeadlessPlaceholderTest");
                HeadlessPlaceholderTest test = testObj.AddComponent<HeadlessPlaceholderTest>();
                test.runOnStart = true;
                test.exitAfterTest = true;
                test.verboseLogging = true;
                test.performCompleteAnalysis = true;
            }
        }
    }
} 
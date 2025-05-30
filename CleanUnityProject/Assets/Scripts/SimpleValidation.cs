using UnityEngine;
using VisualDM.Data;
using VisualDM.Systems;

/// <summary>
/// Simple validation to ensure our core systems work
/// </summary>
public class SimpleValidation : MonoBehaviour
{
    void Start()
    {
        Debug.Log("🧪 Testing core systems...");
        
        try
        {
            // Test data classes
            var entity = new Entity("TestEntity");
            var stateManager = new StateManager();
            stateManager.SetState("test", "working");
            Debug.Log("✅ VisualDM.Data namespace working");
            
            // Test system classes
            var systemManager = new SystemManager();
            systemManager.Initialize();
            Debug.Log("✅ VisualDM.Systems namespace working");
            
            Debug.Log("🎉 Core validation successful!");
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"❌ Validation failed: {ex.Message}");
        }
        
        // Clean up
        Destroy(gameObject);
    }
} 
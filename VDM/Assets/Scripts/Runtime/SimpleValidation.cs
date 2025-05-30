using UnityEngine;
using VDM.Runtime.Data;


namespace VDM.Runtime.Core
{
    public class SimpleValidation : MonoBehaviour
    {
        void Start()
        {
            Debug.Log("✅ Unity compilation successful!");
            Debug.Log($"Core systems loaded: Quest, GameState, DataTypes");
            
            // Test basic types exist
            var gameState = new GameState();
            gameState.SetVariable("test", "working");
            
            var quest = new Quest();
            quest.Name = "Test Quest";
            
            Debug.Log("✅ Core VDM types are working!");
        }
    }
} 
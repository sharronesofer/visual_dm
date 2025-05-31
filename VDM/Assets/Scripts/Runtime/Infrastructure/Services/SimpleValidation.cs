using UnityEngine;
using VDM.Systems.Quest.Models;
using VDM.DTOs.Core.Shared;

namespace VDM.Infrastructure.Core
{
    public class SimpleValidation : MonoBehaviour
    {
        void Start()
        {
            Debug.Log("✅ Unity compilation successful!");
            Debug.Log($"Core systems loaded: Quest, DTOs, Systems");
            
            // Test basic types exist
            var questDto = new VDM.DTOs.Content.Quest.QuestDTO();
            questDto.Title = "Test Quest";
            questDto.Description = "A test quest to verify compilation";
            
            var commonDto = new CommonDTO();
            commonDto.Id = "test-id";
            
            Debug.Log("✅ Core VDM types are working!");
            Debug.Log($"Quest: {questDto.Title}");
            Debug.Log($"Common DTO ID: {commonDto.Id}");
        }
    }
} 
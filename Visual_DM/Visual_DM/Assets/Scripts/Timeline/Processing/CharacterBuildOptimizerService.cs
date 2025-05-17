using System.Collections.Generic;
using Visual_DM.Timeline.Models;
using VisualDM.Simulation;
using UnityEngine;

namespace Visual_DM.Timeline.Processing
{
    public class CharacterBuildOptimizerService : MonoBehaviour
    {
        private CharacterBuildOptimizer _optimizer;
        private FeatDataProcessor _featDataProcessor;

        void Awake()
        {
            _featDataProcessor = new FeatDataProcessor();
            // Assume feats are loaded elsewhere or add async load here
            _optimizer = new CharacterBuildOptimizer(_featDataProcessor.DataSet);
        }

        // API: Recommend feats for a given build
        public List<Feat> GetRecommendations(CharacterBuild build, int maxFeats = 10)
        {
            return _optimizer.RecommendFeats(build, maxFeats);
        }

        // WebSocket: Push real-time updates (stub for now)
        public void PushRecommendations(CharacterBuild build, int maxFeats = 10)
        {
            var recommendations = GetRecommendations(build, maxFeats);
            // Integration point: Send recommendations to frontend via WebSocket (not yet implemented)
            Debug.Log($"Pushing {recommendations.Count} recommendations for build {build.Name}");
        }
    }
} 
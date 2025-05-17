using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using Visual_DM.Timeline.Models;
using Visual_DM.Timeline.Processing;
using Visual_DM.Timeline.Visualization;

namespace Visual_DM.Timeline.Visualization.Tests
{
    public class FeatTimelineVisualizerPlayModeTests
    {
        private GameObject _visualizerGO;
        private FeatTimelineVisualizer _visualizer;
        private FeatDataProcessor _processor;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            _visualizerGO = new GameObject("Visualizer");
            _visualizer = _visualizerGO.AddComponent<FeatTimelineVisualizer>();
            _processor = new FeatDataProcessor();
            _visualizer.DataProcessor = _processor;
            yield return null;
        }

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            Object.Destroy(_visualizerGO);
            yield return null;
        }

        [UnityTest]
        public IEnumerator RendersNodesAndEdges_WithMockData()
        {
            // Arrange
            var mockFeats = new List<Feat>
            {
                new Feat { Id = "f1", Name = "Power Attack", Description = "Deal extra damage.", Category = FeatCategory.Combat, LevelRequirement = 1 },
                new Feat { Id = "f2", Name = "Spell Focus", Description = "Boost spell DC.", Category = FeatCategory.Magic, LevelRequirement = 2, Prerequisites = new List<string>{"f1"} },
                new Feat { Id = "f3", Name = "Stealthy", Description = "Move unseen.", Category = FeatCategory.Utility, LevelRequirement = 3 },
                new Feat { Id = "f4", Name = "Diplomat", Description = "Persuade NPCs.", Category = FeatCategory.Social, LevelRequirement = 4, Prerequisites = new List<string>{"f3"} },
            };
            _processor.DataSet.Feats = mockFeats;
            _processor.IsLoaded = true;

            // Act
            _visualizer.SendMessage("RenderTimeline");
            yield return null;

            // Assert
            var nodes = Object.FindObjectsOfType<TimelineNode>();
            var edges = Object.FindObjectsOfType<TimelineEdge>();
            Assert.AreEqual(4, nodes.Length, "Should render 4 nodes");
            Assert.AreEqual(2, edges.Length, "Should render 2 edges");
        }

        [UnityTest]
        public IEnumerator TooltipAppears_OnNodeHover()
        {
            // Arrange
            var feat = new Feat { Id = "f1", Name = "Power Attack", Description = "Deal extra damage.", Category = FeatCategory.Combat, LevelRequirement = 1 };
            _processor.DataSet.Feats = new List<Feat> { feat };
            _processor.IsLoaded = true;
            _visualizer.SendMessage("RenderTimeline");
            yield return null;
            var node = Object.FindObjectOfType<TimelineNode>();
            var tooltip = Object.FindObjectOfType<TooltipPanel>();

            // Act
            node.SendMessage("OnMouseEnter");
            yield return null;

            // Assert
            Assert.IsTrue(tooltip.gameObject.activeSelf, "Tooltip should be active on hover");
            Assert.IsTrue(tooltip.Text.text.Contains("Power Attack"), "Tooltip should show feat name");
        }

        [UnityTest]
        public IEnumerator PathHighlighting_WorksOnClick()
        {
            // Arrange
            var mockFeats = new List<Feat>
            {
                new Feat { Id = "f1", Name = "A", Category = FeatCategory.Combat, LevelRequirement = 1 },
                new Feat { Id = "f2", Name = "B", Category = FeatCategory.Magic, LevelRequirement = 2, Prerequisites = new List<string>{"f1"} },
            };
            _processor.DataSet.Feats = mockFeats;
            _processor.IsLoaded = true;
            _visualizer.SendMessage("RenderTimeline");
            yield return null;
            var nodes = Object.FindObjectsOfType<TimelineNode>();
            var nodeB = System.Array.Find(nodes, n => n.FeatData.Id == "f2");

            // Act
            nodeB.SendMessage("OnMouseDown");
            yield return null;

            // Assert
            Assert.IsTrue(nodeB.IsHighlighted, "Clicked node should be highlighted");
            var nodeA = System.Array.Find(nodes, n => n.FeatData.Id == "f1");
            Assert.IsTrue(nodeA.IsHighlighted, "Prerequisite node should be highlighted");
        }

        [UnityTest]
        public IEnumerator GapAndClusterMarkers_AppearCorrectly()
        {
            // Arrange
            var mockFeats = new List<Feat>
            {
                new Feat { Id = "f1", Name = "A", Category = FeatCategory.Combat, LevelRequirement = 1 },
                new Feat { Id = "f2", Name = "B", Category = FeatCategory.Magic, LevelRequirement = 1 },
                new Feat { Id = "f3", Name = "C", Category = FeatCategory.Utility, LevelRequirement = 1 },
                new Feat { Id = "f4", Name = "D", Category = FeatCategory.Social, LevelRequirement = 1 },
                new Feat { Id = "f5", Name = "E", Category = FeatCategory.Exploration, LevelRequirement = 1 },
            };
            _processor.DataSet.Feats = mockFeats;
            _processor.IsLoaded = true;
            _visualizer.SendMessage("RenderTimeline");
            yield return null;

            // Act
            var clusterMarkers = GameObject.FindObjectsOfType<GameObject>();
            bool foundCluster = false, foundGap = false;
            foreach (var go in clusterMarkers)
            {
                if (go.name.Contains("ClusterMarker")) foundCluster = true;
                if (go.name.Contains("GapMarker")) foundGap = true;
            }

            // Assert
            Assert.IsTrue(foundCluster, "Should render cluster marker for level 1");
            Assert.IsTrue(foundGap, "Should render at least one gap marker");
        }
    }
} 
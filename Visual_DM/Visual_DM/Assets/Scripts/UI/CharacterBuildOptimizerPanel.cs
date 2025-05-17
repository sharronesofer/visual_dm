using UnityEngine;
using System.Collections.Generic;
using Visual_DM.Timeline.Models;
using Visual_DM.Timeline.Processing;
using System;

namespace VisualDM.UI
{
    public class CharacterBuildOptimizerPanel : PanelBase
    {
        private GameObject titleObj;
        private GameObject recommendationsListObj;
        private GameObject roleDropdownObj;
        private GameObject playstyleDropdownObj;
        private GameObject refreshButtonObj;
        private float width = 700f;
        private float height = 500f;
        private Color bgColor = new Color(0.14f, 0.14f, 0.18f, 0.98f);

        private CharacterBuildOptimizerService optimizerService;
        private CharacterBuild currentBuild;
        private List<Feat> recommendations = new List<Feat>();

        public override void Initialize(params object[] args)
        {
            try
            {
                // Background
                var sr = gameObject.AddComponent<SpriteRenderer>();
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
                sr.sortingOrder = 120;

                // Title
                titleObj = new GameObject("Title");
                titleObj.transform.SetParent(transform);
                titleObj.transform.localPosition = new Vector3(0, height/2 - 30, 0);
                // TODO: Add text rendering for title

                // Role dropdown
                roleDropdownObj = new GameObject("RoleDropdown");
                roleDropdownObj.transform.SetParent(transform);
                roleDropdownObj.transform.localPosition = new Vector3(-width/2 + 120, height/2 - 80, 0);
                // TODO: Add dropdown logic for roles

                // Playstyle dropdown
                playstyleDropdownObj = new GameObject("PlaystyleDropdown");
                playstyleDropdownObj.transform.SetParent(transform);
                playstyleDropdownObj.transform.localPosition = new Vector3(-width/2 + 320, height/2 - 80, 0);
                // TODO: Add dropdown logic for playstyles

                // Refresh button
                refreshButtonObj = new GameObject("RefreshButton");
                refreshButtonObj.transform.SetParent(transform);
                refreshButtonObj.transform.localPosition = new Vector3(width/2 - 80, height/2 - 80, 0);
                // TODO: Add button logic to trigger optimization

                // Recommendations list
                recommendationsListObj = new GameObject("RecommendationsList");
                recommendationsListObj.transform.SetParent(transform);
                recommendationsListObj.transform.localPosition = new Vector3(0, 0, 0);
                // TODO: Add list rendering for recommended feats

                // Get optimizer service
                optimizerService = FindObjectOfType<CharacterBuildOptimizerService>();
                if (optimizerService == null)
                {
                    var go = new GameObject("CharacterBuildOptimizerService");
                    optimizerService = go.AddComponent<CharacterBuildOptimizerService>();
                }

                // Initialize with a default build (for demo)
                currentBuild = new CharacterBuild
                {
                    Name = "Demo Build",
                    Stats = new Simulation.CharacterStats(),
                    Role = "DPS",
                    Playstyle = "Aggressive",
                    Level = 5
                };
                RefreshRecommendations();
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to initialize Character Build Optimizer Panel.", "CharacterBuildOptimizerPanel.Initialize");
                // Optionally show a user-friendly error UI here
            }
        }

        private void RefreshRecommendations()
        {
            recommendations = optimizerService.GetRecommendations(currentBuild, 10);
using UnityEngine;
using System.Collections.Generic;
using Visual_DM.Timeline.Models;
using Visual_DM.Timeline.Processing;

namespace VisualDM.UI
{
    public class CharacterBuildOptimizerPanel : PanelBase
    {
        private GameObject titleObj;
        private GameObject recommendationsListObj;
        private GameObject roleDropdownObj;
        private GameObject playstyleDropdownObj;
        private GameObject refreshButtonObj;
        private float width = 700f;
        private float height = 500f;
        private Color bgColor = new Color(0.14f, 0.14f, 0.18f, 0.98f);

        private CharacterBuildOptimizerService optimizerService;
        private CharacterBuild currentBuild;
        private List<Feat> recommendations = new List<Feat>();

        public override void Initialize(params object[] args)
        {
            // Background
            var sr = gameObject.AddComponent<SpriteRenderer>();
            sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            sr.sortingOrder = 120;

            // Title
            titleObj = new GameObject("Title");
            titleObj.transform.SetParent(transform);
            titleObj.transform.localPosition = new Vector3(0, height/2 - 30, 0);
            // TODO: Add text rendering for title

            // Role dropdown
            roleDropdownObj = new GameObject("RoleDropdown");
            roleDropdownObj.transform.SetParent(transform);
            roleDropdownObj.transform.localPosition = new Vector3(-width/2 + 120, height/2 - 80, 0);
            // TODO: Add dropdown logic for roles

            // Playstyle dropdown
            playstyleDropdownObj = new GameObject("PlaystyleDropdown");
            playstyleDropdownObj.transform.SetParent(transform);
            playstyleDropdownObj.transform.localPosition = new Vector3(-width/2 + 320, height/2 - 80, 0);
            // TODO: Add dropdown logic for playstyles

            // Refresh button
            refreshButtonObj = new GameObject("RefreshButton");
            refreshButtonObj.transform.SetParent(transform);
            refreshButtonObj.transform.localPosition = new Vector3(width/2 - 80, height/2 - 80, 0);
            // TODO: Add button logic to trigger optimization

            // Recommendations list
            recommendationsListObj = new GameObject("RecommendationsList");
            recommendationsListObj.transform.SetParent(transform);
            recommendationsListObj.transform.localPosition = new Vector3(0, 0, 0);
            // TODO: Add list rendering for recommended feats

            // Get optimizer service
            optimizerService = FindObjectOfType<CharacterBuildOptimizerService>();
            if (optimizerService == null)
            {
                var go = new GameObject("CharacterBuildOptimizerService");
                optimizerService = go.AddComponent<CharacterBuildOptimizerService>();
            }

            // Initialize with a default build (for demo)
            currentBuild = new CharacterBuild
            {
                Name = "Demo Build",
                Stats = new Simulation.CharacterStats(),
                Role = "DPS",
                Playstyle = "Aggressive",
                Level = 5
            };
            RefreshRecommendations();
        }

        private void RefreshRecommendations()
        {
            recommendations = optimizerService.GetRecommendations(currentBuild, 10);
            // TODO: Update recommendationsListObj with new recommendations and explanations
        }
    }
} 
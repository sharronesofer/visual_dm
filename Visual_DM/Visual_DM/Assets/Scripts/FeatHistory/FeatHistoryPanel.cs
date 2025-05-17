using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;

namespace Visual_DM.FeatHistory
{
    public class FeatHistoryPanel : MonoBehaviour
    {
        private Canvas canvas;
        private RectTransform panel;
        private ScrollRect timelineScroll;
        private RectTransform timelineContent;
        private Text dashboardText;
        private RectTransform recommendationsPanel;
        private Dropdown filterDropdown;
        private InputField searchField;
        private Button helpButton;
        private FeatEventTracker tracker;
        private FeatHistoryAnalyzer analyzer;
        private FeatRecommendationEngine recommender;
        private List<Feat> allFeats = new List<Feat>(); // Should be loaded from game data
        private string characterId = "A"; // For demo/testing

        void Start()
        {
            tracker = FeatEventTracker.Instance;
            if (tracker == null)
            {
                Debug.LogError("[FeatHistoryPanel] FeatEventTracker not found.");
                return;
            }
            allFeats = LoadAllFeats();
            analyzer = new FeatHistoryAnalyzer(tracker.GetHistoryForCharacter(characterId));
            recommender = new FeatRecommendationEngine(allFeats, tracker.GetHistoryForCharacter(characterId));
            BuildUI();
            RefreshUI();
        }

        private List<Feat> LoadAllFeats()
        {
            // TODO: Replace with actual feat loading logic
            return new List<Feat>
            {
                new Feat { Id = "power1", Name = "Power Strike", Description = "A strong attack.", Metadata = new Dictionary<string, string> { { "type", "attack" } } },
                new Feat { Id = "defense1", Name = "Shield Wall", Description = "A defensive stance.", Metadata = new Dictionary<string, string> { { "type", "defense" } } },
                new Feat { Id = "explore1", Name = "Explorer", Description = "Explore new areas.", Metadata = new Dictionary<string, string> { { "type", "explore" } } },
                new Feat { Id = "rare1", Name = "Rare Gem", Description = "A rare feat.", Metadata = new Dictionary<string, string> { { "type", "rare" } } },
                new Feat { Id = "power2", Name = "Power Bash", Description = "Another strong attack.", Metadata = new Dictionary<string, string> { { "type", "attack" } } }
            };
        }

        private void BuildUI()
        {
            // Canvas
            canvas = new GameObject("FeatHistoryCanvas").AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.gameObject.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            canvas.gameObject.AddComponent<GraphicRaycaster>();
            DontDestroyOnLoad(canvas.gameObject);

            // Main Panel
            panel = new GameObject("Panel").AddComponent<RectTransform>();
            panel.SetParent(canvas.transform, false);
            panel.sizeDelta = new Vector2(800, 600);
            panel.anchoredPosition = new Vector2(0, 0);
            Image panelImage = panel.gameObject.AddComponent<Image>();
            panelImage.color = new Color(0.1f, 0.1f, 0.1f, 0.95f);

            // Dashboard
            dashboardText = new GameObject("DashboardText").AddComponent<Text>();
            dashboardText.transform.SetParent(panel, false);
            dashboardText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            dashboardText.fontSize = 20;
            dashboardText.color = Color.white;
            dashboardText.alignment = TextAnchor.UpperLeft;
            dashboardText.rectTransform.anchoredPosition = new Vector2(10, -10);
            dashboardText.rectTransform.sizeDelta = new Vector2(780, 80);

            // Timeline Scroll
            timelineScroll = new GameObject("TimelineScroll").AddComponent<ScrollRect>();
            timelineScroll.transform.SetParent(panel, false);
            timelineScroll.viewport = timelineScroll.gameObject.AddComponent<RectTransform>();
            timelineScroll.viewport.sizeDelta = new Vector2(780, 200);
            timelineScroll.viewport.anchoredPosition = new Vector2(0, -100);
            timelineContent = new GameObject("TimelineContent").AddComponent<RectTransform>();
            timelineContent.SetParent(timelineScroll.viewport, false);
            timelineScroll.content = timelineContent;
            timelineScroll.horizontal = false;
            timelineScroll.vertical = true;

            // Recommendations Panel
            recommendationsPanel = new GameObject("RecommendationsPanel").AddComponent<RectTransform>();
            recommendationsPanel.SetParent(panel, false);
            recommendationsPanel.anchoredPosition = new Vector2(0, -320);
            recommendationsPanel.sizeDelta = new Vector2(780, 120);
            Image recImage = recommendationsPanel.gameObject.AddComponent<Image>();
            recImage.color = new Color(0.2f, 0.2f, 0.3f, 0.9f);

            // Filter Dropdown
            filterDropdown = new GameObject("FilterDropdown").AddComponent<Dropdown>();
            filterDropdown.transform.SetParent(panel, false);
            filterDropdown.options = new List<Dropdown.OptionData> { new Dropdown.OptionData("All Types"), new Dropdown.OptionData("Attack"), new Dropdown.OptionData("Defense"), new Dropdown.OptionData("Explore"), new Dropdown.OptionData("Rare") };
            filterDropdown.value = 0;
            filterDropdown.onValueChanged.AddListener(_ => RefreshUI());
            filterDropdown.GetComponent<RectTransform>().anchoredPosition = new Vector2(600, -10);

            // Search Field
            searchField = new GameObject("SearchField").AddComponent<InputField>();
            searchField.transform.SetParent(panel, false);
            searchField.placeholder = new GameObject("Placeholder").AddComponent<Text>();
            searchField.placeholder.text = "Search feats...";
            searchField.placeholder.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            searchField.textComponent = new GameObject("Text").AddComponent<Text>();
            searchField.textComponent.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            searchField.onValueChanged.AddListener(_ => RefreshUI());
            searchField.GetComponent<RectTransform>().anchoredPosition = new Vector2(400, -10);

            // Help Button
            helpButton = new GameObject("HelpButton").AddComponent<Button>();
            helpButton.transform.SetParent(panel, false);
            var helpText = new GameObject("HelpText").AddComponent<Text>();
            helpText.transform.SetParent(helpButton.transform, false);
            helpText.text = "?";
            helpText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            helpText.fontSize = 24;
            helpText.color = Color.yellow;
            helpButton.GetComponent<RectTransform>().anchoredPosition = new Vector2(760, -10);
            helpButton.onClick.AddListener(ShowHelp);
        }

        private void RefreshUI()
        {
            // Update dashboard
            analyzer = new FeatHistoryAnalyzer(tracker.GetHistoryForCharacter(characterId));
            var stats = analyzer.GetSummaryStatistics();
            dashboardText.text = $"Total Events: {stats["TotalEvents"]}\nUnique Feats: {stats["UniqueFeats"]}\nPlayer Type: {analyzer.ClassifyPlayerTypes().GetValueOrDefault(characterId, "Unknown")}";

            // Update timeline
            foreach (Transform child in timelineContent) Destroy(child.gameObject);
            var events = tracker.GetHistoryForCharacter(characterId);
            var filtered = events.Where(e =>
                (filterDropdown.value == 0 || allFeats.FirstOrDefault(f => f.Id == e.FeatId)?.Metadata?.GetValueOrDefault("type", "")?.ToLower() == filterDropdown.options[filterDropdown.value].text.ToLower()) &&
                (string.IsNullOrEmpty(searchField.text) || allFeats.FirstOrDefault(f => f.Id == e.FeatId)?.Name.ToLower().Contains(searchField.text.ToLower()) == true)
            ).OrderByDescending(e => e.Timestamp).ToList();
            foreach (var featEvent in filtered)
            {
                var feat = allFeats.FirstOrDefault(f => f.Id == featEvent.FeatId);
                var row = new GameObject("TimelineRow").AddComponent<Text>();
                row.transform.SetParent(timelineContent, false);
                row.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
                row.fontSize = 16;
                row.color = Color.cyan;
                row.text = $"[{featEvent.Timestamp:HH:mm}] {feat?.Name ?? featEvent.FeatId} (Lvl {featEvent.CharacterLevel})";
                row.rectTransform.sizeDelta = new Vector2(760, 24);
            }

            // Update recommendations
            foreach (Transform child in recommendationsPanel) Destroy(child.gameObject);
            var recs = recommender.GetRecommendations(characterId, 3);
            int y = 0;
            foreach (var rec in recs)
            {
                var recText = new GameObject("RecText").AddComponent<Text>();
                recText.transform.SetParent(recommendationsPanel, false);
                recText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
                recText.fontSize = 18;
                recText.color = Color.green;
                recText.rectTransform.anchoredPosition = new Vector2(10, -y);
                recText.text = $"Recommended: {rec.Name} - {rec.Description}";
                // Accept button
                var acceptBtn = new GameObject("AcceptBtn").AddComponent<Button>();
                acceptBtn.transform.SetParent(recommendationsPanel, false);
                acceptBtn.GetComponent<RectTransform>().anchoredPosition = new Vector2(400, -y);
                var acceptText = new GameObject("AcceptText").AddComponent<Text>();
                acceptText.transform.SetParent(acceptBtn.transform, false);
                acceptText.text = "Accept";
                acceptText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
                acceptText.fontSize = 16;
                acceptText.color = Color.white;
                acceptBtn.onClick.AddListener(() => recommender.RecordFeedback(characterId, rec.Id, true));
                // Ignore button
                var ignoreBtn = new GameObject("IgnoreBtn").AddComponent<Button>();
                ignoreBtn.transform.SetParent(recommendationsPanel, false);
                ignoreBtn.GetComponent<RectTransform>().anchoredPosition = new Vector2(500, -y);
                var ignoreText = new GameObject("IgnoreText").AddComponent<Text>();
                ignoreText.transform.SetParent(ignoreBtn.transform, false);
                ignoreText.text = "Ignore";
                ignoreText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
                ignoreText.fontSize = 16;
                ignoreText.color = Color.gray;
                ignoreBtn.onClick.AddListener(() => recommender.RecordFeedback(characterId, rec.Id, false));
                y += 40;
            }
        }

        private void ShowHelp()
        {
            // Show a simple help dialog (runtime-generated)
            var helpPanel = new GameObject("HelpPanel").AddComponent<RectTransform>();
            helpPanel.SetParent(panel, false);
            helpPanel.sizeDelta = new Vector2(600, 300);
            helpPanel.anchoredPosition = new Vector2(100, -100);
            var img = helpPanel.gameObject.AddComponent<Image>();
            img.color = new Color(0, 0, 0, 0.95f);
            var helpText = new GameObject("HelpText").AddComponent<Text>();
            helpText.transform.SetParent(helpPanel, false);
            helpText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            helpText.fontSize = 18;
            helpText.color = Color.white;
            helpText.text = "Feat History Panel\n\n- Timeline: Shows your feat achievements in order.\n- Dashboard: Stats and player type.\n- Recommendations: Personalized suggestions.\n- Filter/Search: Find feats by type or name.\n- Accept/Ignore: Give feedback to improve recommendations.";
            helpText.rectTransform.anchoredPosition = new Vector2(10, -10);
            helpText.rectTransform.sizeDelta = new Vector2(580, 280);
            // Close button
            var closeBtn = new GameObject("CloseBtn").AddComponent<Button>();
            closeBtn.transform.SetParent(helpPanel, false);
            closeBtn.GetComponent<RectTransform>().anchoredPosition = new Vector2(550, -10);
            var closeText = new GameObject("CloseText").AddComponent<Text>();
            closeText.transform.SetParent(closeBtn.transform, false);
            closeText.text = "X";
            closeText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            closeText.fontSize = 20;
            closeText.color = Color.red;
            closeBtn.onClick.AddListener(() => Destroy(helpPanel.gameObject));
        }
    }
} 
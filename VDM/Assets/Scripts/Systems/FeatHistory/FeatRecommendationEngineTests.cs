using NUnit.Framework;
using System;
using System.Collections.Generic;
using VisualDM.FeatHistory;

public class FeatRecommendationEngineTests
{
    private List<Feat> feats;
    private List<FeatAchievementEvent> events;
    private FeatRecommendationEngine engine;

    [SetUp]
    public void SetUp()
    {
        feats = new List<Feat>
        {
            new Feat { Id = "power1", Name = "Power Strike", Metadata = new Dictionary<string, string> { { "type", "attack" } } },
            new Feat { Id = "defense1", Name = "Shield Wall", Metadata = new Dictionary<string, string> { { "type", "defense" } } },
            new Feat { Id = "explore1", Name = "Explorer", Metadata = new Dictionary<string, string> { { "type", "explore" } } },
            new Feat { Id = "rare1", Name = "Rare Gem", Metadata = new Dictionary<string, string> { { "type", "rare" } } },
            new Feat { Id = "power2", Name = "Power Bash", Metadata = new Dictionary<string, string> { { "type", "attack" } } }
        };
        events = new List<FeatAchievementEvent>
        {
            new FeatAchievementEvent { Id = "1", CharacterId = "A", FeatId = "power1", Timestamp = DateTime.UtcNow.AddMinutes(-30) },
            new FeatAchievementEvent { Id = "2", CharacterId = "A", FeatId = "defense1", Timestamp = DateTime.UtcNow.AddMinutes(-20) },
            new FeatAchievementEvent { Id = "3", CharacterId = "B", FeatId = "power1", Timestamp = DateTime.UtcNow.AddMinutes(-10) },
            new FeatAchievementEvent { Id = "4", CharacterId = "B", FeatId = "explore1", Timestamp = DateTime.UtcNow.AddMinutes(-5) },
            new FeatAchievementEvent { Id = "5", CharacterId = "C", FeatId = "rare1", Timestamp = DateTime.UtcNow.AddMinutes(-2) }
        };
        engine = new FeatRecommendationEngine(feats, events);
    }

    [Test]
    public void TestCollaborativeFiltering()
    {
        var recs = engine.GetRecommendations("A", 2, RecommendationStrategy.Collaborative);
        Assert.IsTrue(recs.Count <= 2);
    }

    [Test]
    public void TestContentBasedFiltering()
    {
        var recs = engine.GetRecommendations("A", 2, RecommendationStrategy.ContentBased);
        Assert.IsTrue(recs.Count <= 2);
    }

    [Test]
    public void TestHybridScoring()
    {
        var recs = engine.GetRecommendations("A", 3, RecommendationStrategy.Hybrid);
        Assert.IsTrue(recs.Count <= 3);
    }

    [Test]
    public void TestABAssignmentConsistency()
    {
        var strat1 = engine.GetRecommendations("A");
        var strat2 = engine.GetRecommendations("A");
        Assert.AreEqual(strat1, strat2);
    }

    [Test]
    public void TestSystemsCapture()
    {
        Assert.DoesNotThrow(() => engine.RecordSystems("A", "power1", true));
    }
} 
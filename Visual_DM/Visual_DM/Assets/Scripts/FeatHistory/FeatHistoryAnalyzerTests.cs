using NUnit.Framework;
using System;
using System.Collections.Generic;
using Visual_DM.FeatHistory;

public class FeatHistoryAnalyzerTests
{
    private List<FeatAchievementEvent> sampleEvents;
    private FeatHistoryAnalyzer analyzer;

    [SetUp]
    public void SetUp()
    {
        sampleEvents = new List<FeatAchievementEvent>
        {
            new FeatAchievementEvent { Id = "1", CharacterId = "A", FeatId = "power1", Timestamp = DateTime.UtcNow.AddMinutes(-30), CharacterLevel = 1 },
            new FeatAchievementEvent { Id = "2", CharacterId = "A", FeatId = "defense1", Timestamp = DateTime.UtcNow.AddMinutes(-20), CharacterLevel = 2 },
            new FeatAchievementEvent { Id = "3", CharacterId = "A", FeatId = "power1", Timestamp = DateTime.UtcNow.AddMinutes(-10), CharacterLevel = 3 },
            new FeatAchievementEvent { Id = "4", CharacterId = "B", FeatId = "explore1", Timestamp = DateTime.UtcNow.AddMinutes(-25), CharacterLevel = 1 },
            new FeatAchievementEvent { Id = "5", CharacterId = "B", FeatId = "power1", Timestamp = DateTime.UtcNow.AddMinutes(-5), CharacterLevel = 2 },
            new FeatAchievementEvent { Id = "6", CharacterId = "C", FeatId = "rare1", Timestamp = DateTime.UtcNow.AddMinutes(-2), CharacterLevel = 1 }
        };
        analyzer = new FeatHistoryAnalyzer(sampleEvents);
    }

    [Test]
    public void TestMostFrequentFeatsGlobal()
    {
        var topFeats = analyzer.GetMostFrequentFeatsGlobal(2);
        Assert.IsTrue(topFeats.ContainsKey("power1"));
        Assert.AreEqual(3, topFeats["power1"]);
    }

    [Test]
    public void TestMostFrequentFeatsPerCharacter()
    {
        var perChar = analyzer.GetMostFrequentFeatsPerCharacter(1);
        Assert.AreEqual(1, perChar["A"].Count);
        Assert.IsTrue(perChar["A"].ContainsKey("power1") || perChar["A"].ContainsKey("defense1"));
    }

    [Test]
    public void TestAcquisitionStreaks()
    {
        var streaks = analyzer.GetAcquisitionStreaks(TimeSpan.FromMinutes(15));
        Assert.IsTrue(streaks.ContainsKey("A"));
        Assert.IsTrue(streaks["A"].Count >= 1);
    }

    [Test]
    public void TestClassifyPlayerTypes()
    {
        var types = analyzer.ClassifyPlayerTypes();
        Assert.AreEqual("Aggressive", types["A"]);
        Assert.AreEqual("Aggressive", types["B"]);
        Assert.AreEqual("Balanced", types["C"]);
    }

    [Test]
    public void TestDetectAnomalies()
    {
        var anomalies = analyzer.DetectAnomalies(1);
        Assert.IsTrue(anomalies.Exists(e => e.FeatId == "rare1"));
    }

    [Test]
    public void TestSummaryStatistics()
    {
        var stats = analyzer.GetSummaryStatistics();
        Assert.AreEqual(6, stats["TotalEvents"]);
        Assert.AreEqual(3, stats["UniqueCharacters"]);
        Assert.AreEqual(5, stats["UniqueFeats"]);
    }
} 
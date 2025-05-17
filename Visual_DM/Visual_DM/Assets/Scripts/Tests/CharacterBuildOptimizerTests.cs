using NUnit.Framework;
using Visual_DM.Timeline.Models;
using Visual_DM.Timeline.Processing;
using VisualDM.Simulation;
using System.Collections.Generic;

public class CharacterBuildOptimizerTests
{
    private FeatDataSet CreateMockFeatDataSet()
    {
        return new FeatDataSet
        {
            Feats = new List<Feat>
            {
                new Feat { Id = "1", Name = "Power Attack", Category = FeatCategory.Combat, LevelRequirement = 1, Metadata = new Dictionary<string, object>{{"Stat", "Strength"}} },
                new Feat { Id = "2", Name = "Arcane Mastery", Category = FeatCategory.Magic, LevelRequirement = 1, Metadata = new Dictionary<string, object>{{"Stat", "Intelligence"}} },
                new Feat { Id = "3", Name = "Quick Reflexes", Category = FeatCategory.Utility, LevelRequirement = 1, Metadata = new Dictionary<string, object>{{"Stat", "Dexterity"}} },
            }
        };
    }

    [Test]
    public void RecommendFeats_TankRole_PrefersCombatFeats()
    {
        var dataSet = CreateMockFeatDataSet();
        var optimizer = new CharacterBuildOptimizer(dataSet);
        var build = new CharacterBuild
        {
            Name = "Tanky",
            Stats = new CharacterStats(str: 16, dex: 10, con: 14, intel: 8, wis: 10, cha: 10),
            Role = "Tank",
            Playstyle = "Defensive",
            Level = 1
        };
        var recommendations = optimizer.RecommendFeats(build, 2);
        Assert.IsTrue(recommendations.Exists(f => f.Name == "Power Attack"));
    }

    [Test]
    public void RecommendFeats_DPSRole_PrefersMagicFeats()
    {
        var dataSet = CreateMockFeatDataSet();
        var optimizer = new CharacterBuildOptimizer(dataSet);
        var build = new CharacterBuild
        {
            Name = "Blaster",
            Stats = new CharacterStats(str: 8, dex: 10, con: 10, intel: 16, wis: 10, cha: 10),
            Role = "DPS",
            Playstyle = "Aggressive",
            Level = 1
        };
        var recommendations = optimizer.RecommendFeats(build, 2);
        Assert.IsTrue(recommendations.Exists(f => f.Name == "Arcane Mastery"));
    }

    [Test]
    public void RecommendFeats_UtilityPlaystyle_PrefersUtilityFeats()
    {
        var dataSet = CreateMockFeatDataSet();
        var optimizer = new CharacterBuildOptimizer(dataSet);
        var build = new CharacterBuild
        {
            Name = "Trickster",
            Stats = new CharacterStats(str: 10, dex: 16, con: 10, intel: 10, wis: 10, cha: 10),
            Role = "Support",
            Playstyle = "Utility",
            Level = 1
        };
        var recommendations = optimizer.RecommendFeats(build, 2);
        Assert.IsTrue(recommendations.Exists(f => f.Name == "Quick Reflexes"));
    }
} 
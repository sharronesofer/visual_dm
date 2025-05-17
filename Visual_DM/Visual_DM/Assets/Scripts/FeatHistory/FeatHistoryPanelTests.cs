using NUnit.Framework;
using UnityEngine;
using Visual_DM.FeatHistory;

public class FeatHistoryPanelTests
{
    private GameObject panelObj;
    private FeatHistoryPanel panel;

    [SetUp]
    public void SetUp()
    {
        panelObj = new GameObject("TestFeatHistoryPanel");
        panel = panelObj.AddComponent<FeatHistoryPanel>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(panelObj);
    }

    [Test]
    public void TestPanelBuildsUI()
    {
        Assert.DoesNotThrow(() => panel.Start());
    }

    [Test]
    public void TestPanelRefreshesUI()
    {
        panel.Start();
        Assert.DoesNotThrow(() => panel.GetType().GetMethod("RefreshUI", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).Invoke(panel, null));
    }

    [Test]
    public void TestHelpButtonShowsHelp()
    {
        panel.Start();
        Assert.DoesNotThrow(() => panel.GetType().GetMethod("ShowHelp", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).Invoke(panel, null));
    }
} 
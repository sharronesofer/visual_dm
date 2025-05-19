using NUnit.Framework;
using UnityEngine;
using VisualDM.FeatHistory;
using System.Collections.Generic;

public class FeatEventTrackerTests
{
    private GameObject trackerObj;
    private FeatEventTracker tracker;

    [SetUp]
    public void SetUp()
    {
        trackerObj = new GameObject("TestFeatEventTracker");
        tracker = trackerObj.AddComponent<FeatEventTracker>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(trackerObj);
    }

    [Test]
    public void TestRecordFeatAcquisition_EnqueuesEvent()
    {
        var snapshot = new CharacterSnapshot { Level = 5, Health = 100 };
        tracker.RecordFeatAcquisition("char1", "feat1", snapshot, "test context");
        tracker.FlushBuffer();
        var history = tracker.GetHistoryForCharacter("char1");
        Assert.IsTrue(history.Exists(e => e.FeatId == "feat1" && e.CharacterId == "char1"));
    }

    [Test]
    public void TestFlushBuffer_EmptiesQueue()
    {
        var snapshot = new CharacterSnapshot { Level = 2 };
        tracker.RecordFeatAcquisition("char2", "feat2", snapshot);
        tracker.FlushBuffer();
        var history = tracker.GetHistoryForCharacter("char2");
        Assert.AreEqual(1, history.Count);
    }

    [Test]
    public void TestErrorHandling_InvalidCore()
    {
        // Should not throw, should log error
        Assert.DoesNotThrow(() => tracker.RecordFeatAcquisition(null, null, null));
    }
} 
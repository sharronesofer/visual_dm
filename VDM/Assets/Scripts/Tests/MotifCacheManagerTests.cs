using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using NUnit.Framework;
using VDM.Motifs;

public class MockMotifApiClient : MotifApiClient
{
    private readonly Dictionary<int, Motif> _store = new();
    public MockMotifApiClient() : base("http://mock") { }
    public void AddMotif(Motif m) => _store[m.Id ?? 0] = m;
    public override async Task<Motif> GetMotifByIdAsync(int id) => _store.ContainsKey(id) ? _store[id] : null;
    public override async Task<List<Motif>> GetMotifsAsync(string query = "") => new List<Motif>(_store.Values);
}

[TestFixture]
public class MotifCacheManagerTests
{
    private MotifCacheManager _cache;
    private MockMotifApiClient _mockApi;

    [SetUp]
    public void Setup()
    {
        _mockApi = new MockMotifApiClient();
        _cache = new MotifCacheManager(_mockApi, ttlSeconds: 0.1f); // short TTL for test
        _mockApi.AddMotif(new Motif { Id = 1, Name = "Hope" });
    }

    [Test]
    public async Task TestCacheHitMiss()
    {
        var motif1 = await _cache.GetMotifByIdAsync(1);
        Assert.AreEqual("Hope", motif1.Name);
        // Remove from API, should still get from cache
        _mockApi._store.Remove(1);
        var motif2 = await _cache.GetMotifByIdAsync(1);
        Assert.AreEqual("Hope", motif2.Name);
    }

    [Test]
    public async Task TestCacheExpiry()
    {
        var motif1 = await _cache.GetMotifByIdAsync(1);
        Assert.AreEqual("Hope", motif1.Name);
        await Task.Delay(200); // wait for TTL to expire
        _mockApi._store[1].Name = "Despair";
        var motif2 = await _cache.GetMotifByIdAsync(1);
        Assert.AreEqual("Despair", motif2.Name);
    }

    [Test]
    public async Task TestInvalidateMotif()
    {
        var motif1 = await _cache.GetMotifByIdAsync(1);
        _cache.InvalidateMotif(1);
        _mockApi._store[1].Name = "Changed";
        var motif2 = await _cache.GetMotifByIdAsync(1);
        Assert.AreEqual("Changed", motif2.Name);
    }

    [Test]
    public async Task TestBackgroundRefresh()
    {
        _cache.StartBackgroundRefresh(1, refreshInterval: 0.05f);
        var motif1 = await _cache.GetMotifByIdAsync(1);
        _mockApi._store[1].Name = "Evolved";
        await Task.Delay(120); // allow background refresh
        var motif2 = await _cache.GetMotifByIdAsync(1);
        Assert.AreEqual("Evolved", motif2.Name);
        _cache.StopBackgroundRefresh(1);
    }
} 
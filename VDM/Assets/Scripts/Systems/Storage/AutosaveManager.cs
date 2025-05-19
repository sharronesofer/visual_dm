using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Timers;

namespace VisualDM.Storage
{
    /// <summary>
    /// Manages autosave and checkpoint operations for IStorable objects.
    /// </summary>
    public class AutosaveManager
    {
        private static AutosaveManager _instance;
        public static AutosaveManager Instance => _instance ??= new AutosaveManager();

        private Timer _autosaveTimer;
        private int _autosaveIntervalSeconds = 300; // Default: 5 minutes
        private int _maxRetainedSaves = 5;
        private readonly Queue<Func<Task>> _saveQueue = new Queue<Func<Task>>();
        private bool _isSaving = false;
        private readonly List<IStorable> _autosaveTargets = new List<IStorable>();

        private AutosaveManager() { }

        public void Configure(int intervalSeconds, int maxRetainedSaves)
        {
            _autosaveIntervalSeconds = intervalSeconds;
            _maxRetainedSaves = maxRetainedSaves;
            if (_autosaveTimer != null)
            {
                _autosaveTimer.Stop();
                _autosaveTimer.Dispose();
            }
            _autosaveTimer = new Timer(_autosaveIntervalSeconds * 1000);
            _autosaveTimer.Elapsed += async (s, e) => await TriggerAutosave();
            _autosaveTimer.AutoReset = true;
            _autosaveTimer.Start();
        }

        public void RegisterAutosaveTarget(IStorable storable)
        {
            if (!_autosaveTargets.Contains(storable))
                _autosaveTargets.Add(storable);
        }

        public void UnregisterAutosaveTarget(IStorable storable)
        {
            _autosaveTargets.Remove(storable);
        }

        public async Task TriggerAutosave()
        {
            foreach (var storable in _autosaveTargets)
            {
                QueueSave(() => SaveWithRetention(storable));
            }
            await ProcessQueue();
        }

        public async Task TriggerCheckpoint(string checkpointName)
        {
            foreach (var storable in _autosaveTargets)
            {
                QueueSave(() => SaveCheckpoint(storable, checkpointName));
            }
            await ProcessQueue();
        }

        private void QueueSave(Func<Task> saveFunc)
        {
            _saveQueue.Enqueue(saveFunc);
        }

        private async Task ProcessQueue()
        {
            if (_isSaving) return;
            _isSaving = true;
            while (_saveQueue.Count > 0)
            {
                var saveFunc = _saveQueue.Dequeue();
                try { await saveFunc(); } catch (Exception ex) { /* Log error */ }
            }
            _isSaving = false;
        }

        private async Task SaveWithRetention(IStorable storable)
        {
            var timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
            var key = $"autosave_{storable.GetStorageKey()}_{timestamp}";
            await PersistenceManager.Instance.SaveAsync(new AutosaveWrapper(storable, key));
            // Retention: delete oldest if over max
            var saves = await PersistenceManager.Instance.ListSavesAsync("");
            var autosaves = new List<string>();
            foreach (var s in saves) if (s.StartsWith($"autosave_{storable.GetStorageKey()}_")) autosaves.Add(s);
            autosaves.Sort();
            while (autosaves.Count > _maxRetainedSaves)
            {
                await PersistenceManager.Instance.DeleteAsync(new AutosaveWrapper(storable, autosaves[0]));
                autosaves.RemoveAt(0);
            }
        }

        private async Task SaveCheckpoint(IStorable storable, string checkpointName)
        {
            var key = $"checkpoint_{storable.GetStorageKey()}_{checkpointName}_{DateTime.UtcNow:yyyyMMdd_HHmmss}";
            await PersistenceManager.Instance.SaveAsync(new AutosaveWrapper(storable, key));
        }

        // Wrapper to allow custom key for autosave/checkpoint
        private class AutosaveWrapper : IStorable
        {
            private readonly IStorable _inner;
            private readonly string _key;
            public AutosaveWrapper(IStorable inner, string key) { _inner = inner; _key = key; }
            public string GetStorageKey() => _key;
            public byte[] Serialize() => _inner.Serialize();
            public void Deserialize(byte[] data) => _inner.Deserialize(data);
            public int DataVersion => _inner.DataVersion;
        }
    }
} 
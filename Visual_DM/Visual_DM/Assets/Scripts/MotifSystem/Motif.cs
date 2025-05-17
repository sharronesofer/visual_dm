using System;
using System.Collections.Generic;
using Systems.Integration; // For validation/transaction patterns

namespace VisualDM.MotifSystem
{
    /// <summary>
    /// Represents a single Motif with validation, versioning, and transaction support.
    /// </summary>
    [Serializable]
    public class Motif
    {
        public string Theme { get; private set; }
        public int Lifespan { get; private set; }
        public int EntropyTick { get; private set; }
        public int Weight { get; private set; }
        public bool ChaosSource { get; set; }
        public string Version { get; private set; }
        public DateTime CreatedAt { get; private set; }
        public DateTime UpdatedAt { get; private set; }
        public Dictionary<string, object> Metadata { get; private set; }

        // For transaction/rollback
        private Motif _snapshot;

        public Motif(string theme, int lifespan, int entropyTick = 0, int weight = 1, bool chaosSource = false, string version = "1.0.0", Dictionary<string, object> metadata = null)
        {
            Theme = theme;
            Lifespan = lifespan;
            EntropyTick = entropyTick;
            Weight = weight;
            ChaosSource = chaosSource;
            Version = version;
            CreatedAt = DateTime.UtcNow;
            UpdatedAt = DateTime.UtcNow;
            Metadata = metadata ?? new Dictionary<string, object>();
        }

        public ValidationResult Validate()
        {
            var result = new ValidationResult { IsValid = true };
            if (string.IsNullOrEmpty(Theme))
            {
                result.IsValid = false;
                result.Errors.Add("Theme is required.");
            }
            if (Lifespan < 1 || Lifespan > 10)
            {
                result.IsValid = false;
                result.Errors.Add("Lifespan must be between 1 and 10.");
            }
            if (EntropyTick < 0)
            {
                result.IsValid = false;
                result.Errors.Add("EntropyTick cannot be negative.");
            }
            if (Weight < 0)
            {
                result.IsValid = false;
                result.Errors.Add("Weight cannot be negative.");
            }
            // Add more business rule checks as needed
            return result;
        }

        public void IncrementEntropy()
        {
            EntropyTick++;
            UpdatedAt = DateTime.UtcNow;
        }

        public bool NeedsRotation() => EntropyTick >= Lifespan;

        public void SetChaosSource(bool value)
        {
            ChaosSource = value;
            UpdatedAt = DateTime.UtcNow;
        }

        public void SetWeight(int weight)
        {
            Weight = weight;
            UpdatedAt = DateTime.UtcNow;
        }

        public bool SetTheme(string theme)
        {
            try
            {
                if (string.IsNullOrEmpty(theme)) return false;
                Theme = theme;
                return true;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Motif.SetTheme failed", "Motif.SetTheme");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return false;
            }
        }

        public bool SetLifespan(int lifespan)
        {
            try
            {
                if (lifespan <= 0) return false;
                Lifespan = lifespan;
                return true;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Motif.SetLifespan failed", "Motif.SetLifespan");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return false;
            }
        }

        public bool SetVersion(string version)
        {
            try
            {
                if (string.IsNullOrEmpty(version)) return false;
                Version = version;
                return true;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Motif.SetVersion failed", "Motif.SetVersion");
                VisualDM.Core.MonitoringManager.Instance?.IncrementErrorCount();
                return false;
            }
        }

        public void AddOrUpdateMetadata(string key, object value)
        {
            Metadata[key] = value;
            UpdatedAt = DateTime.UtcNow;
        }

        // Transaction support
        public void BeginTransaction()
        {
            _snapshot = this.MemberwiseClone() as Motif;
        }

        public void CommitTransaction()
        {
            _snapshot = null;
        }

        public void RollbackTransaction()
        {
            if (_snapshot != null)
            {
                Theme = _snapshot.Theme;
                Lifespan = _snapshot.Lifespan;
                EntropyTick = _snapshot.EntropyTick;
                Weight = _snapshot.Weight;
                ChaosSource = _snapshot.ChaosSource;
                Version = _snapshot.Version;
                CreatedAt = _snapshot.CreatedAt;
                UpdatedAt = _snapshot.UpdatedAt;
                Metadata = new Dictionary<string, object>(_snapshot.Metadata);
                _snapshot = null;
            }
        }
    }
}
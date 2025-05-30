using System.Collections.Generic;
using System.Threading.Tasks;
using System;
using UnityEngine;
using VDM.Runtime.Magic.Models;
using VDM.Runtime.Services.Http;


namespace VDM.Runtime.Magic.Services
{
    /// <summary>
    /// HTTP service for magic system operations
    /// </summary>
    public class MagicService : BaseHttpService
    {
        private const string MAGIC_ENDPOINT = "/api/magic";
        private const string SPELLS_ENDPOINT = "/api/spells";
        private const string CASTING_ENDPOINT = "/api/casting";

        public MagicService() : base()
        {
        }

        #region Spell Management

        /// <summary>
        /// Get all available spells
        /// </summary>
        public async Task<List<Spell>> GetSpellsAsync()
        {
            try
            {
                var response = await GetAsync<List<Spell>>($"{SPELLS_ENDPOINT}");
                return response ?? new List<Spell>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get spells: {ex.Message}");
                return new List<Spell>();
            }
        }

        /// <summary>
        /// Get a specific spell by ID
        /// </summary>
        public async Task<Spell> GetSpellAsync(string spellId)
        {
            try
            {
                return await GetAsync<Spell>($"{SPELLS_ENDPOINT}/{spellId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get spell {spellId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get spells by school
        /// </summary>
        public async Task<List<Spell>> GetSpellsBySchoolAsync(MagicSchool school)
        {
            try
            {
                var response = await GetAsync<List<Spell>>($"{SPELLS_ENDPOINT}/school/{school}");
                return response ?? new List<Spell>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get spells for school {school}: {ex.Message}");
                return new List<Spell>();
            }
        }

        /// <summary>
        /// Get spells by domain
        /// </summary>
        public async Task<List<Spell>> GetSpellsByDomainAsync(MagicDomain domain)
        {
            try
            {
                var response = await GetAsync<List<Spell>>($"{SPELLS_ENDPOINT}/domain/{domain}");
                return response ?? new List<Spell>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get spells for domain {domain}: {ex.Message}");
                return new List<Spell>();
            }
        }

        /// <summary>
        /// Create a new spell
        /// </summary>
        public async Task<Spell> CreateSpellAsync(Spell spell)
        {
            try
            {
                return await PostAsync<Spell>($"{SPELLS_ENDPOINT}", spell);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to create spell: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update an existing spell
        /// </summary>
        public async Task<Spell> UpdateSpellAsync(string spellId, Spell spell)
        {
            try
            {
                return await PutAsync<Spell>($"{SPELLS_ENDPOINT}/{spellId}", spell);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update spell {spellId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Delete a spell
        /// </summary>
        public async Task<bool> DeleteSpellAsync(string spellId)
        {
            try
            {
                await DeleteAsync($"{SPELLS_ENDPOINT}/{spellId}");
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to delete spell {spellId}: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Spellcaster Management

        /// <summary>
        /// Get spellcaster information
        /// </summary>
        public async Task<Spellcaster> GetSpellcasterAsync(string casterId)
        {
            try
            {
                return await GetAsync<Spellcaster>($"{MAGIC_ENDPOINT}/casters/{casterId}");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get spellcaster {casterId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Update spellcaster information
        /// </summary>
        public async Task<Spellcaster> UpdateSpellcasterAsync(string casterId, Spellcaster caster)
        {
            try
            {
                return await PutAsync<Spellcaster>($"{MAGIC_ENDPOINT}/casters/{casterId}", caster);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to update spellcaster {casterId}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Get known spells for a caster
        /// </summary>
        public async Task<List<string>> GetKnownSpellsAsync(string casterId)
        {
            try
            {
                var response = await GetAsync<List<string>>($"{MAGIC_ENDPOINT}/casters/{casterId}/known-spells");
                return response ?? new List<string>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get known spells for {casterId}: {ex.Message}");
                return new List<string>();
            }
        }

        /// <summary>
        /// Learn a new spell
        /// </summary>
        public async Task<bool> LearnSpellAsync(string casterId, string spellId)
        {
            try
            {
                var request = new { spellId = spellId };
                await PostAsync($"{MAGIC_ENDPOINT}/casters/{casterId}/learn-spell", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to learn spell {spellId} for {casterId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Prepare spells for casting
        /// </summary>
        public async Task<bool> PrepareSpellsAsync(string casterId, List<string> spellIds)
        {
            try
            {
                var request = new { spellIds = spellIds };
                await PostAsync($"{MAGIC_ENDPOINT}/casters/{casterId}/prepare-spells", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to prepare spells for {casterId}: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Spell Casting

        /// <summary>
        /// Cast a spell
        /// </summary>
        public async Task<SpellCastingResult> CastSpellAsync(string casterId, string spellId, string targetId = null, int upcastLevel = 0)
        {
            try
            {
                var request = new CastSpellRequest
                {
                    CasterId = casterId,
                    SpellId = spellId,
                    TargetId = targetId,
                    UpcastLevel = upcastLevel
                };

                return await PostAsync<SpellCastingResult>($"{CASTING_ENDPOINT}/cast", request);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to cast spell {spellId}: {ex.Message}");
                return new SpellCastingResult(CastingResult.Failure, null, null)
                {
                    Message = ex.Message
                };
            }
        }

        /// <summary>
        /// Get available spells for casting
        /// </summary>
        public async Task<List<Spell>> GetAvailableSpellsAsync(string casterId)
        {
            try
            {
                var response = await GetAsync<List<Spell>>($"{CASTING_ENDPOINT}/available/{casterId}");
                return response ?? new List<Spell>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get available spells for {casterId}: {ex.Message}");
                return new List<Spell>();
            }
        }

        /// <summary>
        /// Interrupt spell casting
        /// </summary>
        public async Task<bool> InterruptCastingAsync(string casterId)
        {
            try
            {
                await PostAsync($"{CASTING_ENDPOINT}/interrupt/{casterId}", null);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to interrupt casting for {casterId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Dispel magic effects
        /// </summary>
        public async Task<bool> DispelMagicAsync(string targetId, string effectId = null)
        {
            try
            {
                var endpoint = string.IsNullOrEmpty(effectId) 
                    ? $"{MAGIC_ENDPOINT}/dispel/{targetId}"
                    : $"{MAGIC_ENDPOINT}/dispel/{targetId}/{effectId}";
                
                await PostAsync(endpoint, null);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to dispel magic on {targetId}: {ex.Message}");
                return false;
            }
        }

        #endregion

        #region Magic System State

        /// <summary>
        /// Get current magic system state
        /// </summary>
        public async Task<MagicSystemState> GetMagicSystemStateAsync()
        {
            try
            {
                return await GetAsync<MagicSystemState>($"{MAGIC_ENDPOINT}/state");
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get magic system state: {ex.Message}");
                return new MagicSystemState();
            }
        }

        /// <summary>
        /// Get active spell effects
        /// </summary>
        public async Task<List<ActiveSpellEffect>> GetActiveEffectsAsync(string targetId = null)
        {
            try
            {
                var endpoint = string.IsNullOrEmpty(targetId) 
                    ? $"{MAGIC_ENDPOINT}/effects"
                    : $"{MAGIC_ENDPOINT}/effects/{targetId}";
                
                var response = await GetAsync<List<ActiveSpellEffect>>(endpoint);
                return response ?? new List<ActiveSpellEffect>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get active effects: {ex.Message}");
                return new List<ActiveSpellEffect>();
            }
        }

        /// <summary>
        /// Get magic events
        /// </summary>
        public async Task<List<MagicEvent>> GetMagicEventsAsync(int limit = 50)
        {
            try
            {
                var response = await GetAsync<List<MagicEvent>>($"{MAGIC_ENDPOINT}/events?limit={limit}");
                return response ?? new List<MagicEvent>();
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to get magic events: {ex.Message}");
                return new List<MagicEvent>();
            }
        }

        #endregion

        #region Resource Management

        /// <summary>
        /// Restore mana for a caster
        /// </summary>
        public async Task<bool> RestoreManaAsync(string casterId, int amount)
        {
            try
            {
                var request = new { amount = amount };
                await PostAsync($"{MAGIC_ENDPOINT}/casters/{casterId}/restore-mana", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to restore mana for {casterId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Restore concentration for a caster
        /// </summary>
        public async Task<bool> RestoreConcentrationAsync(string casterId, int amount)
        {
            try
            {
                var request = new { amount = amount };
                await PostAsync($"{MAGIC_ENDPOINT}/casters/{casterId}/restore-concentration", request);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to restore concentration for {casterId}: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Take a long rest to restore all resources
        /// </summary>
        public async Task<bool> LongRestAsync(string casterId)
        {
            try
            {
                await PostAsync($"{MAGIC_ENDPOINT}/casters/{casterId}/long-rest", null);
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to long rest for {casterId}: {ex.Message}");
                return false;
            }
        }

        #endregion
    }

    /// <summary>
    /// Request model for casting spells
    /// </summary>
    [Serializable]
    public class CastSpellRequest
    {
        public string CasterId;
        public string SpellId;
        public string TargetId;
        public int UpcastLevel;
        public Vector3? TargetPosition;
        public Dictionary<string, object> Parameters = new Dictionary<string, object>();
    }

    /// <summary>
    /// Magic system state for tracking current magic session
    /// </summary>
    [Serializable]
    public class MagicState
    {
        public string SessionId;
        public List<Spellcaster> Participants = new List<Spellcaster>();
        public List<ActiveSpellEffect> ActiveEffects = new List<ActiveSpellEffect>();
        public bool MagicSuppressed;
        public float MagicIntensity = 1.0f;
        public DateTime LastUpdated;
    }
} 
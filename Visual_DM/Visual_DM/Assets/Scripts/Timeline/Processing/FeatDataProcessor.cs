using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Visual_DM.Timeline.Models;
using UnityEngine;
using UnityEngine.Networking;

namespace Visual_DM.Timeline.Processing
{
    public class FeatDataProcessor
    {
        public FeatDataSet DataSet { get; private set; } = new FeatDataSet();
        public bool IsLoaded { get; private set; } = false;
        public string LastError { get; private set; }

        // API endpoint for feat data (replace with actual endpoint)
        private const string FeatApiUrl = "https://api.example.com/feats";

        public async Task<bool> LoadFeatsFromApiAsync()
        {
            try
            {
                using (UnityWebRequest www = UnityWebRequest.Get(FeatApiUrl))
                {
                    var op = www.SendWebRequest();
                    while (!op.isDone)
                        await Task.Yield();

#if UNITY_2020_1_OR_NEWER
                    if (www.result != UnityWebRequest.Result.Success)
#else
                    if (www.isNetworkError || www.isHttpError)
#endif
                    {
                        LastError = www.error;
                        Debug.LogError($"Failed to fetch feats: {www.error}");
                        return false;
                    }

                    string json = www.downloadHandler.text;
                    DataSet = JsonUtility.FromJson<FeatDataSet>(json);
                    DataSet.BuildIndex();
                    IsLoaded = true;
                    return true;
                }
            }
            catch (Exception ex)
            {
                LastError = ex.Message;
                Debug.LogError($"Exception loading feats: {ex}");
                return false;
            }
        }

        // Process prerequisite chains and detect circular dependencies
        public bool ValidatePrerequisites(out List<string> circularChains)
        {
            circularChains = new List<string>();
            var visited = new HashSet<string>();
            var stack = new HashSet<string>();

            foreach (var feat in DataSet.Feats)
            {
                if (HasCircularDependency(feat, visited, stack, out var chain))
                {
                    circularChains.Add(chain);
                }
            }
            return circularChains.Count == 0;
        }

        private bool HasCircularDependency(Feat feat, HashSet<string> visited, HashSet<string> stack, out string chain)
        {
            chain = string.Empty;
            if (stack.Contains(feat.Id))
            {
                chain = string.Join(" -> ", stack) + $" -> {feat.Id}";
                return true;
            }
            if (visited.Contains(feat.Id)) return false;
            visited.Add(feat.Id);
            stack.Add(feat.Id);
            foreach (var prereqId in feat.Prerequisites)
            {
                var prereq = DataSet.GetFeatById(prereqId);
                if (prereq != null && HasCircularDependency(prereq, visited, stack, out chain))
                    return true;
            }
            stack.Remove(feat.Id);
            return false;
        }

        // Filtering and search methods
        public IEnumerable<Feat> FilterByCategory(FeatCategory category)
        {
            return DataSet.GetFeatsByCategory(category);
        }

        public IEnumerable<Feat> FilterByLevel(int level)
        {
            return DataSet.GetFeatsByLevel(level);
        }

        public IEnumerable<Feat> SearchByName(string searchTerm)
        {
            return DataSet.Feats.Where(f => f.Name.IndexOf(searchTerm, StringComparison.OrdinalIgnoreCase) >= 0);
        }

        public IEnumerable<Feat> GetAvailableFeatsAtLevel(int level)
        {
            return DataSet.Feats.Where(f => f.LevelRequirement <= level && f.Prerequisites.All(pid => DataSet.GetFeatById(pid) != null));
        }
    }
} 
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

namespace VisualDM.World
{
    public class CityMapController : MonoBehaviour
    {
        public GameObject buildingPrefab;
        public GameObject npcPrefab;
        public Transform cityMapParent;
        public WeatherEffectController cityWeatherEffectController;

        private List<GameObject> spawnedBuildings = new List<GameObject>();
        private List<GameObject> spawnedNPCs = new List<GameObject>();

        // Stub for city POI data structure
        public class CityPOIData
        {
            public int buildingCount = 10;
            public int npcCount = 30;
            // Add more fields as needed
        }

        [Serializable]
        public class CityPOIWrapper
        {
            public CityPOIData cityPOIData;
        }

        public void InstantiateCityMap(CityPOIData poiData, string weatherType = "Clear")
        {
            ClearCityMap();
            // Instantiate buildings
            foreach (var b in poiData.buildings)
            {
                GameObject prefab = GetBuildingPrefab(b.type);
                Vector3 pos = new Vector3(b.x * 2f, b.y * 2f, 0);
                var building = Instantiate(prefab, pos, Quaternion.identity, cityMapParent);
                spawnedBuildings.Add(building);
            }
            // Instantiate NPCs
            foreach (var n in poiData.npcs)
            {
                GameObject prefab = GetNPCPrefab(n.role);
                Vector3 pos = new Vector3(n.x * 2f, n.y * 2f, 0);
                var npc = Instantiate(prefab, pos, Quaternion.identity, cityMapParent);
                spawnedNPCs.Add(npc);
            }
            // Set city weather effect
            if (cityWeatherEffectController != null)
                cityWeatherEffectController.SetWeather(weatherType);
        }

        public void ClearCityMap()
        {
            foreach (var obj in spawnedBuildings) Destroy(obj);
            foreach (var obj in spawnedNPCs) Destroy(obj);
            spawnedBuildings.Clear();
            spawnedNPCs.Clear();
        }

        // Stub for loading city POI data (replace with backend call as needed)
        public IEnumerator LoadCityPOIData(string poiId, System.Action<CityPOIData> callback)
        {
            string url = $"http://localhost:8000/poi/{poiId}";
            using (UnityWebRequest req = UnityWebRequest.Get(url))
            {
                yield return req.SendWebRequest();
                if (req.result == UnityWebRequest.Result.Success)
                {
                    // Unity's JsonUtility requires a root object
                    CityPOIWrapper wrapper = JsonUtility.FromJson<CityPOIWrapper>(req.downloadHandler.text);
                    callback(wrapper.cityPOIData);
                }
                else
                {
                    // Fallback: empty city
                    callback(new CityPOIData { buildings = new List<BuildingData>(), npcs = new List<NPCData>() });
                }
            }
        }

        public void SetCityWeather(string weatherType)
        {
            if (cityWeatherEffectController != null)
                cityWeatherEffectController.SetWeather(weatherType);
        }
    }
} 
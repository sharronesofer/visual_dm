using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.World;

namespace VisualDM.World
{
    public class RegionMapController : MonoBehaviour
    {
        public GameObject hexPrefab;
        public GameObject cityIconPrefab;
        public GameObject metropolisIconPrefab;
        public Transform mapParent;
        public RegionWeatherSystem weatherSystem;
        public CityMapController cityMapController;
        public GameObject regionMapUI;
        public GameObject cityMapUI;
        public Camera mainCamera;
        public Transform regionCameraTarget;
        public Transform cityCameraTarget;
        public float zoomDuration = 1.0f;
        public float cityOrthoSize = 10f;
        public float regionOrthoSize = 30f;
        public WeatherEffectController weatherEffectController;

        private Dictionary<string, GameObject> hexObjects = new Dictionary<string, GameObject>();
        private Dictionary<string, string> claimedByCity = new Dictionary<string, string>();
        private Dictionary<string, List<string>> metropolisHexes = new Dictionary<string, List<string>>();
        private int regionWidth = 15; // Example size, tune as needed
        private int regionHeight = 15;

        // Example data structure for region tiles (replace with actual data source)
        public class RegionTile
        {
            public int x, y;
            public string claimed_by_city;
            public bool is_metropolis;
        }
        public List<RegionTile> regionTiles = new List<RegionTile>();

        void Start()
        {
            RenderRegionMap();
        }

        public void RenderRegionMap()
        {
            foreach (var tile in regionTiles)
            {
                Vector3 pos = HexToWorld(tile.x, tile.y);
                GameObject hex = Instantiate(hexPrefab, pos, Quaternion.identity, mapParent);
                hex.name = $"Hex_{tile.x}_{tile.y}";
                hexObjects[$"{tile.x}_{tile.y}"] = hex;
                // Overlay city/metropolis icons
                if (!string.IsNullOrEmpty(tile.claimed_by_city))
                {
                    if (tile.is_metropolis)
                    {
                        Instantiate(metropolisIconPrefab, pos, Quaternion.identity, hex.transform);
                    }
                    else
                    {
                        Instantiate(cityIconPrefab, pos, Quaternion.identity, hex.transform);
                    }
                }
                // Fetch and display weather
                StartCoroutine(weatherSystem.GetWeather(tile.x, tile.y, (weather) => {
                    // Example: Change hex color based on weather
                    var renderer = hex.GetComponent<SpriteRenderer>();
                    if (renderer != null)
                    {
                        if (weather.weather.Contains("Rain")) renderer.color = Color.blue;
                        else if (weather.weather.Contains("Snow")) renderer.color = Color.white;
                        else renderer.color = Color.green;
                    }
                    // Set weather effect (only for main region or as needed)
                    if (tile.x == 0 && tile.y == 0 && weatherEffectController != null)
                    {
                        weatherEffectController.SetWeather(weather.weather);
                    }
                }));
            }
        }

        Vector3 HexToWorld(int x, int y)
        {
            float xOffset = 0.866f; // sqrt(3)/2 for flat-topped hexes
            float yOffset = 0.75f;
            return new Vector3(x * xOffset, y * yOffset, 0);
        }

        // Example click handler for zoom-in
        public void OnHexClicked(int x, int y)
        {
            var tile = regionTiles.Find(t => t.x == x && t.y == y);
            if (tile != null && !string.IsNullOrEmpty(tile.claimed_by_city))
            {
                StartCoroutine(ZoomInToCity(tile));
            }
        }

        IEnumerator ZoomInToCity(RegionTile tile)
        {
            // Animate camera/UI to city map (zoom in)
            yield return StartCoroutine(AnimateCameraZoom(regionCameraTarget, cityCameraTarget, regionOrthoSize, cityOrthoSize, zoomDuration));
            regionMapUI.SetActive(false);
            cityMapUI.SetActive(true);
            // Fetch weather for this city region
            string weatherType = "Clear";
            bool weatherFetched = false;
            yield return StartCoroutine(weatherSystem.GetWeather(tile.x, tile.y, (weather) => {
                weatherType = weather.weather;
                weatherFetched = true;
            }));
            while (!weatherFetched) yield return null;
            // Load and instantiate city map with weather
            string poiId = tile.claimed_by_city; // Use claimed_by_city as POI ID (adjust as needed)
            yield return StartCoroutine(cityMapController.LoadCityPOIData(poiId, (poiData) => {
                cityMapController.InstantiateCityMap(poiData, weatherType);
            }));
        }

        public void ZoomOutToRegion()
        {
            StartCoroutine(ZoomOutCoroutine());
        }
        IEnumerator ZoomOutCoroutine()
        {
            // Animate camera/UI back to region map (zoom out)
            yield return StartCoroutine(AnimateCameraZoom(cityCameraTarget, regionCameraTarget, cityOrthoSize, regionOrthoSize, zoomDuration));
            cityMapController.ClearCityMap();
            cityMapUI.SetActive(false);
            regionMapUI.SetActive(true);
        }

        IEnumerator AnimateCameraZoom(Transform fromTarget, Transform toTarget, float fromSize, float toSize, float duration)
        {
            float t = 0f;
            Vector3 startPos = fromTarget.position;
            Vector3 endPos = toTarget.position;
            float startSize = fromSize;
            float endSize = toSize;
            while (t < 1f)
            {
                t += Time.deltaTime / duration;
                mainCamera.transform.position = Vector3.Lerp(startPos, endPos, t);
                mainCamera.orthographicSize = Mathf.Lerp(startSize, endSize, t);
                yield return null;
            }
            mainCamera.transform.position = endPos;
            mainCamera.orthographicSize = endSize;
        }
    }
} 
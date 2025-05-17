using UnityEngine;

public class GameLoader : MonoBehaviour
{
    public int seed = 0;

    void Start()
    {
        WorldGenerator.GenerateWorld(seed);
        NPCSpawner.SpawnAll();
        UIManager.InitializeHUD();
        Destroy(gameObject);
    }
} 
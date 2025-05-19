using UnityEngine;

[System.Serializable]
public class TerrainSpriteEntry
{
    public string terrainType;
    public string spritePath;
}

[CreateAssetMenu(fileName = "TerrainTypeMapping", menuName = "ScriptableObjects/TerrainTypeMapping", order = 1)]
public class TerrainTypeMapping : ScriptableObject
{
    public TerrainSpriteEntry[] mappings;

    public string GetSpritePath(string terrainType)
    {
        foreach (var entry in mappings)
        {
            if (entry.terrainType == terrainType)
                return entry.spritePath;
        }
        return null;
    }
} 
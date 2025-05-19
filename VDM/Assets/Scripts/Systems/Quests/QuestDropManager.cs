using System.Collections.Generic;
using UnityEngine;

public class QuestDropManager : MonoBehaviour
{
    public static QuestDropManager Instance { get; private set; }

    private Dictionary<string, QuestItemDropData> dropDataById = new Dictionary<string, QuestItemDropData>();

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    public void RegisterDropData(QuestItemDropData data)
    {
        if (data != null && !string.IsNullOrEmpty(data.ItemId))
        {
            dropDataById[data.ItemId] = data;
        }
    }

    public QuestItemDropData GetDropData(string itemId)
    {
        dropDataById.TryGetValue(itemId, out var data);
        return data;
    }

    public void UpdateDropData(string itemId, QuestItemDropData newData)
    {
        if (!string.IsNullOrEmpty(itemId) && newData != null)
        {
            dropDataById[itemId] = newData;
        }
    }

    public IEnumerable<QuestItemDropData> GetAllDropData()
    {
        return dropDataById.Values;
    }
} 
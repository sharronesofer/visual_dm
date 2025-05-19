using System;
using System.IO;
using System.Threading;
using UnityEngine;

// Reference: See /docs/bible_qa.md for design rationale and requirements.
// This file is part of the Action Response Time System.
// Config file: StreamingAssets/ActionTimingConfig.json

public enum ActionType
{
    BasicAttack,
    SpecialAbility,
    ContextualAction,
    ChainAction
}

public class TimingConfiguration
{
    private static readonly object _lock = new object();
    private static TimingConfiguration _instance;
    public static TimingConfiguration Instance
    {
        get
        {
            if (_instance == null)
            {
                lock (_lock)
                {
                    if (_instance == null)
                        _instance = new TimingConfiguration();
                }
            }
            return _instance;
        }
    }

    private const int DefaultBasicAttackMs = 50;
    private const int DefaultSpecialAbilityMs = 100;
    private const int DefaultContextualActionMs = 150;
    private const int DefaultChainActionMs = 80;
    private const int MinMs = 10;
    private const int MaxMs = 1000;

    public int BasicAttackMs { get; private set; } = DefaultBasicAttackMs;
    public int SpecialAbilityMs { get; private set; } = DefaultSpecialAbilityMs;
    public int ContextualActionMs { get; private set; } = DefaultContextualActionMs;
    public int ChainActionMs { get; private set; } = DefaultChainActionMs;

    private FileSystemWatcher _watcher;
    private string _configPath;

    private TimingConfiguration()
    {
        _configPath = Path.Combine(Application.streamingAssetsPath, "ActionTimingConfig.json");
        LoadConfig();
#if UNITY_EDITOR
        SetupWatcher();
#endif
    }

    private void SetupWatcher()
    {
        if (!File.Exists(_configPath)) return;
        _watcher = new FileSystemWatcher(Path.GetDirectoryName(_configPath), Path.GetFileName(_configPath));
        _watcher.Changed += (s, e) => LoadConfig();
        _watcher.EnableRaisingEvents = true;
    }

    public void Reload() => LoadConfig();

    private void LoadConfig()
    {
        lock (_lock)
        {
            try
            {
                if (File.Exists(_configPath))
                {
                    string json = File.ReadAllText(_configPath);
                    var data = JsonUtility.FromJson<TimingConfigData>(json);
                    BasicAttackMs = Validate(data.basicAttackMs, DefaultBasicAttackMs);
                    SpecialAbilityMs = Validate(data.specialAbilityMs, DefaultSpecialAbilityMs);
                    ContextualActionMs = Validate(data.contextualActionMs, DefaultContextualActionMs);
                    ChainActionMs = Validate(data.chainActionMs, DefaultChainActionMs);
                }
                else
                {
                    SetDefaults();
                    Debug.LogWarning($"Timing config not found, using defaults.");
                }
            }
            catch (Exception ex)
            {
                SetDefaults();
                Debug.LogWarning($"Failed to load timing config, using defaults. Error: {ex.Message}");
            }
        }
    }

    private int Validate(int value, int fallback)
    {
        if (value < MinMs || value > MaxMs)
        {
            Debug.LogWarning($"Timing value {value}ms out of bounds, using fallback {fallback}ms.");
            return fallback;
        }
        return value;
    }

    private void SetDefaults()
    {
        BasicAttackMs = DefaultBasicAttackMs;
        SpecialAbilityMs = DefaultSpecialAbilityMs;
        ContextualActionMs = DefaultContextualActionMs;
        ChainActionMs = DefaultChainActionMs;
    }

    public int GetTimingMs(ActionType type)
    {
        switch (type)
        {
            case ActionType.BasicAttack: return BasicAttackMs;
            case ActionType.SpecialAbility: return SpecialAbilityMs;
            case ActionType.ContextualAction: return ContextualActionMs;
            case ActionType.ChainAction: return ChainActionMs;
            default: return DefaultBasicAttackMs;
        }
    }

    [Serializable]
    private class TimingConfigData
    {
        public int basicAttackMs = DefaultBasicAttackMs;
        public int specialAbilityMs = DefaultSpecialAbilityMs;
        public int contextualActionMs = DefaultContextualActionMs;
        public int chainActionMs = DefaultChainActionMs;
    }
} 
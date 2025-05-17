#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(QuestItemDropConfig))]
public class QuestItemDropConfigEditor : Editor
{
    public override void OnInspectorGUI()
    {
        serializedObject.Update();
        var config = (QuestItemDropConfig)target;

        EditorGUILayout.LabelField("Quest Item Drop Configuration", EditorStyles.boldLabel);
        EditorGUILayout.PropertyField(serializedObject.FindProperty("ItemId"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("BaseDropRate"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("MinDropRate"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("MaxDropRate"));

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Rarity Modifiers", EditorStyles.boldLabel);
        var rarityMods = serializedObject.FindProperty("RarityModifiers");
        EditorGUILayout.PropertyField(rarityMods, true);
        if (GUILayout.Button("Add Rarity Modifier"))
        {
            rarityMods.arraySize++;
        }

        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Enemy Type Modifiers", EditorStyles.boldLabel);
        var enemyMods = serializedObject.FindProperty("EnemyTypeModifiers");
        EditorGUILayout.PropertyField(enemyMods, true);
        if (GUILayout.Button("Add Enemy Type Modifier"))
        {
            enemyMods.arraySize++;
        }

        EditorGUILayout.Space();
        EditorGUILayout.PropertyField(serializedObject.FindProperty("PityActivationThreshold"));
        EditorGUILayout.PropertyField(serializedObject.FindProperty("PityScalingFactor"));

        EditorGUILayout.Space();
        if (GUILayout.Button("Set All Rarity Modifiers to 1"))
        {
            for (int i = 0; i < config.RarityModifiers.Count; i++)
                config.RarityModifiers[i].Modifier = 1f;
        }
        if (GUILayout.Button("Set All Enemy Type Modifiers to 1"))
        {
            for (int i = 0; i < config.EnemyTypeModifiers.Count; i++)
                config.EnemyTypeModifiers[i].Modifier = 1f;
        }

        serializedObject.ApplyModifiedProperties();
    }
}
#endif 
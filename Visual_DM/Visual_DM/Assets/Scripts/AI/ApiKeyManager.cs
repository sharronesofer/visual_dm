using System;
using System.IO;
using UnityEngine;

namespace AI
{
    public class ApiKeyManager
    {
        private const string ApiKeyEnvVar = "GPT_API_KEY";
        private const string ConfigFileName = "gpt_api_key.cfg";

        public string GetApiKey()
        {
            // Try environment variable first
            string apiKey = Environment.GetEnvironmentVariable(ApiKeyEnvVar);
            if (!string.IsNullOrEmpty(apiKey))
                return apiKey;

            // Fallback: load from encrypted config file
            string path = Path.Combine(Application.persistentDataPath, ConfigFileName);
            if (File.Exists(path))
            {
                string encrypted = File.ReadAllText(path);
                // TODO: Decrypt
                return encrypted; // Replace with decrypted value
            }
            return null;
        }

        public void SetApiKey(string apiKey)
        {
            // Save encrypted to config file
            string path = Path.Combine(Application.persistentDataPath, ConfigFileName);
            // TODO: Encrypt
            File.WriteAllText(path, apiKey); // Replace with encrypted value
        }
    }
} 
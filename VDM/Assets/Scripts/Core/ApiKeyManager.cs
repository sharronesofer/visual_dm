using System;
using System.IO;
using UnityEngine;
using System.Security.Cryptography;
using System.Text;

namespace VisualDM.Core
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
                try
                {
                    string encrypted = File.ReadAllText(path);
                    return Decrypt(encrypted);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Failed to read or decrypt API key: {ex.Message}");
                    return null;
                }
            }
            return null;
        }

        public void SetApiKey(string apiKey)
        {
            if (string.IsNullOrWhiteSpace(apiKey))
            {
                Debug.LogError("API key cannot be null or empty.");
                return;
            }
            string path = Path.Combine(Application.persistentDataPath, ConfigFileName);
            try
            {
                string encrypted = Encrypt(apiKey);
                File.WriteAllText(path, encrypted);
            }
            catch (Exception ex)
            {
                Debug.LogError($"Failed to encrypt or write API key: {ex.Message}");
            }
        }

        // Simple AES encryption/decryption for demonstration (not for production secrets)
        private static readonly byte[] Key = Encoding.UTF8.GetBytes("VisualDM_AES_Key1"); // 16 bytes for AES-128
        private static readonly byte[] IV = Encoding.UTF8.GetBytes("VisualDM_AES_IV_1"); // 16 bytes

        private string Encrypt(string plainText)
        {
            using (var aes = Aes.Create())
            {
                aes.Key = Key;
                aes.IV = IV;
                var encryptor = aes.CreateEncryptor(aes.Key, aes.IV);
                using (var ms = new MemoryStream())
                using (var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
                using (var sw = new StreamWriter(cs))
                {
                    sw.Write(plainText);
                }
                return Convert.ToBase64String(ms.ToArray());
            }
        }

        private string Decrypt(string cipherText)
        {
            using (var aes = Aes.Create())
            {
                aes.Key = Key;
                aes.IV = IV;
                var decryptor = aes.CreateDecryptor(aes.Key, aes.IV);
                using (var ms = new MemoryStream(Convert.FromBase64String(cipherText)))
                using (var cs = new CryptoStream(ms, decryptor, CryptoStreamMode.Read))
                using (var sr = new StreamReader(cs))
                {
                    return sr.ReadToEnd();
                }
            }
        }
    }
}
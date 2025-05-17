using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace VisualDM.Core
{
    /// <summary>
    /// Handles CAPTCHA functionality for authentication forms
    /// </summary>
    public class CaptchaService : MonoBehaviour
    {
        [Serializable]
        public class CaptchaResponse
        {
            public string challenge_id;
            public CaptchaData data;
        }

        [Serializable]
        public class CaptchaData
        {
            public string image;
            public ImageMetadata metadata;
            public string question;
            [JsonProperty("type")]
            public string captchaType;
            public string[] items;
            public Dictionary<string, int> shapes;
            public string target_shape;
        }

        [Serializable]
        public class ImageMetadata
        {
            public string type;
            public string format;
            public int width;
            public int height;
            public string difficulty;
        }

        [Serializable]
        public class ValidationRequest
        {
            public string challenge_id;
            public string response;
            public string client_id;
        }

        [Serializable]
        public class ValidationResponse
        {
            public bool valid;
            public string message;
            public string error;
            public int? attempts_remaining;
            public int? retry_after;
        }

        // Singleton instance
        private static CaptchaService _instance;
        public static CaptchaService Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("CaptchaService");
                    _instance = go.AddComponent<CaptchaService>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        // Configuration
        [Header("CAPTCHA Settings")]
        [SerializeField] private string apiBaseUrl = "https://yourgameserver.com/api/v1/captcha/native";
        [SerializeField] private string captchaType = "image";
        [SerializeField] private string difficulty = "medium";
        [SerializeField] private float captchaRefreshInterval = 5f * 60f; // 5 minutes

        // Current CAPTCHA state
        private string currentChallengeId;
        private Texture2D currentCaptchaImage;
        private string currentLogicQuestion;
        private DateTime lastCaptchaTime;
        private string deviceId;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }

            _instance = this;
            DontDestroyOnLoad(gameObject);

            // Generate a unique device ID if not already saved
            deviceId = PlayerPrefs.GetString("DeviceId", "");
            if (string.IsNullOrEmpty(deviceId))
            {
                deviceId = SystemInfo.deviceUniqueIdentifier;
                if (string.IsNullOrEmpty(deviceId))
                {
                    deviceId = Guid.NewGuid().ToString();
                }
                PlayerPrefs.SetString("DeviceId", deviceId);
                PlayerPrefs.Save();
            }
        }

        /// <summary>
        /// Gets a new CAPTCHA challenge from the server
        /// </summary>
        /// <returns>Coroutine for asynchronous execution</returns>
        public IEnumerator GetCaptcha(Action<bool, string> onComplete)
        {
            string url = $"{apiBaseUrl}?type={captchaType}&difficulty={difficulty}&client_id={deviceId}";
            
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                // Set request timeout
                request.timeout = 10; // 10 seconds
                
                yield return request.SendWebRequest();

                if (request.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogError($"CAPTCHA Request Error: {request.error}");
                    onComplete?.Invoke(false, "Failed to load CAPTCHA. Please try again.");
                    yield break;
                }

                try
                {
                    string responseJson = request.downloadHandler.text;
                    CaptchaResponse response = JsonConvert.DeserializeObject<CaptchaResponse>(responseJson);
                    
                    if (response == null || string.IsNullOrEmpty(response.challenge_id))
                    {
                        Debug.LogError("Invalid CAPTCHA response from server");
                        onComplete?.Invoke(false, "Invalid response from server");
                        yield break;
                    }

                    // Store the challenge ID for validation later
                    currentChallengeId = response.challenge_id;
                    lastCaptchaTime = DateTime.Now;
                    
                    // Process different CAPTCHA types
                    if (captchaType == "image" && !string.IsNullOrEmpty(response.data.image))
                    {
                        // Convert base64 to texture
                        byte[] imageBytes = Convert.FromBase64String(response.data.image);
                        currentCaptchaImage = new Texture2D(2, 2);
                        currentCaptchaImage.LoadImage(imageBytes);
                        currentLogicQuestion = null;
                    }
                    else if (captchaType == "logic" && !string.IsNullOrEmpty(response.data.question))
                    {
                        // Store the logic question
                        currentLogicQuestion = response.data.question;
                        currentCaptchaImage = null;
                    }
                    else
                    {
                        Debug.LogError("Unsupported CAPTCHA type or missing data");
                        onComplete?.Invoke(false, "Unsupported CAPTCHA type");
                        yield break;
                    }
                    
                    onComplete?.Invoke(true, null);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"CAPTCHA Parsing Error: {ex.Message}");
                    onComplete?.Invoke(false, "Failed to process CAPTCHA");
                }
            }
        }

        /// <summary>
        /// Validates a user's CAPTCHA response
        /// </summary>
        /// <param name="userResponse">The user's answer to the CAPTCHA</param>
        /// <param name="onComplete">Callback with validation result</param>
        /// <returns>Coroutine for asynchronous execution</returns>
        public IEnumerator ValidateCaptcha(string userResponse, Action<bool, string> onComplete)
        {
            if (string.IsNullOrEmpty(currentChallengeId))
            {
                onComplete?.Invoke(false, "No active CAPTCHA. Please refresh.");
                yield break;
            }

            if (string.IsNullOrEmpty(userResponse))
            {
                onComplete?.Invoke(false, "Please enter your response");
                yield break;
            }

            string url = $"{apiBaseUrl}/validate";
            
            // Create validation request
            ValidationRequest validationRequest = new ValidationRequest
            {
                challenge_id = currentChallengeId,
                response = userResponse,
                client_id = deviceId
            };
            
            string requestJson = JsonConvert.SerializeObject(validationRequest);
            
            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(requestJson);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                request.timeout = 10; // 10 seconds
                
                yield return request.SendWebRequest();

                if (request.result != UnityWebRequest.Result.Success)
                {
                    if (request.responseCode == 429) // Rate limited
                    {
                        try
                        {
                            string responseJson = request.downloadHandler.text;
                            ValidationResponse response = JsonConvert.DeserializeObject<ValidationResponse>(responseJson);
                            int retryAfter = response.retry_after ?? 300;
                            onComplete?.Invoke(false, $"Too many attempts. Please try again in {retryAfter / 60} minutes.");
                        }
                        catch (Exception)
                        {
                            onComplete?.Invoke(false, "Too many attempts. Please try again later.");
                        }
                    }
                    else
                    {
                        Debug.LogError($"CAPTCHA Validation Error: {request.error}");
                        onComplete?.Invoke(false, "Failed to validate CAPTCHA. Please try again.");
                    }
                    yield break;
                }

                try
                {
                    string responseJson = request.downloadHandler.text;
                    ValidationResponse response = JsonConvert.DeserializeObject<ValidationResponse>(responseJson);
                    
                    if (response.valid)
                    {
                        onComplete?.Invoke(true, null);
                    }
                    else
                    {
                        string message = response.message ?? "Incorrect response";
                        if (response.attempts_remaining.HasValue)
                        {
                            message += $" ({response.attempts_remaining} attempts remaining)";
                        }
                        onComplete?.Invoke(false, message);
                        
                        // If no attempts remain or captcha expired, get a new one automatically
                        if (response.error == "max_attempts" || response.error == "expired")
                        {
                            StartCoroutine(GetCaptcha((success, errorMsg) => { }));
                        }
                    }
                }
                catch (Exception ex)
                {
                    Debug.LogError($"CAPTCHA Validation Parsing Error: {ex.Message}");
                    onComplete?.Invoke(false, "Error processing validation response");
                }
            }
        }

        /// <summary>
        /// Gets the current CAPTCHA image texture
        /// </summary>
        /// <returns>CAPTCHA image as a Texture2D</returns>
        public Texture2D GetCaptchaImage()
        {
            return currentCaptchaImage;
        }

        /// <summary>
        /// Gets the current logic question for text-based CAPTCHA
        /// </summary>
        /// <returns>Logic question string</returns>
        public string GetLogicQuestion()
        {
            return currentLogicQuestion;
        }

        /// <summary>
        /// Gets the current challenge ID for validation
        /// </summary>
        /// <returns>Challenge ID string</returns>
        public string GetChallengeId()
        {
            return currentChallengeId;
        }

        /// <summary>
        /// Checks if the current CAPTCHA is expired
        /// </summary>
        /// <returns>True if CAPTCHA needs refreshing</returns>
        public bool IsCaptchaExpired()
        {
            // Check if we have a CAPTCHA
            if (string.IsNullOrEmpty(currentChallengeId))
            {
                return true;
            }
            
            // Check if it's been too long since we got the CAPTCHA
            TimeSpan elapsed = DateTime.Now - lastCaptchaTime;
            return elapsed.TotalSeconds >= captchaRefreshInterval;
        }

        /// <summary>
        /// Sets the CAPTCHA type (image, logic)
        /// </summary>
        /// <param name="type">CAPTCHA type</param>
        public void SetCaptchaType(string type)
        {
            if (type != "image" && type != "logic")
            {
                Debug.LogWarning($"Unsupported CAPTCHA type: {type}, defaulting to image");
                captchaType = "image";
                return;
            }
            
            captchaType = type;
        }

        /// <summary>
        /// Sets the difficulty level (easy, medium, hard)
        /// </summary>
        /// <param name="level">Difficulty level</param>
        public void SetDifficulty(string level)
        {
            if (level != "easy" && level != "medium" && level != "hard")
            {
                Debug.LogWarning($"Unsupported difficulty level: {level}, defaulting to medium");
                difficulty = "medium";
                return;
            }
            
            difficulty = level;
        }
    }
} 
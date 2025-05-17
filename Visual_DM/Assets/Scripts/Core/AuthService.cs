using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace VisualDM.Core
{
    /// <summary>
    /// Handles authentication operations with the backend server
    /// </summary>
    public class AuthService : MonoBehaviour
    {
        [Serializable]
        public class LoginRequest
        {
            public string username_or_email;
            public string password;
            public string device_id;
            public string platform;
            public string version;
            public string captcha_challenge_id;
            public string captcha_response;
        }

        [Serializable]
        public class RegisterRequest
        {
            public string username;
            public string email;
            public string password;
            public string first_name;
            public string last_name;
            public string device_id;
            public string platform;
            public string captcha_challenge_id;
            public string captcha_response;
        }

        [Serializable]
        public class AuthResponse
        {
            public UserData user;
            public string token;
            public string error;
        }

        [Serializable]
        public class UserData
        {
            public int id;
            public string username;
            public string email;
            public string first_name;
            public string last_name;
            public string created_at;
            public string updated_at;
            public string last_login;
        }

        // Singleton instance
        private static AuthService _instance;
        public static AuthService Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("AuthService");
                    _instance = go.AddComponent<AuthService>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        // Events
        public event Action<bool, string> OnLoginComplete;
        public event Action<bool, string> OnRegistrationComplete;
        public event Action<bool> OnLogoutComplete;

        // Configuration
        [Header("Authentication Settings")]
        [SerializeField] private string apiBaseUrl = "https://yourgameserver.com/api/v1/auth/native";
        [SerializeField] private string loginEndpoint = "/login";
        [SerializeField] private string registerEndpoint = "/register";
        [SerializeField] private string logoutEndpoint = "/logout";
        [SerializeField] private string validateTokenEndpoint = "/validate-token";

        // User state
        private UserData currentUser;
        private string authToken;
        private bool isLoggedIn;
        private string deviceId;
        private string platformInfo;
        private string clientVersion;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }

            _instance = this;
            DontDestroyOnLoad(gameObject);

            // Get device info
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

            // Get platform info
            platformInfo = $"Unity {Application.platform}";
            clientVersion = Application.version;

            // Try to restore session from PlayerPrefs
            RestoreSession();
        }

        private void RestoreSession()
        {
            authToken = PlayerPrefs.GetString("AuthToken", "");
            
            if (!string.IsNullOrEmpty(authToken))
            {
                // Validate the token
                StartCoroutine(ValidateToken());
            }
        }

        /// <summary>
        /// Attempts to login with the provided credentials, including CAPTCHA validation
        /// </summary>
        /// <param name="usernameOrEmail">Username or email</param>
        /// <param name="password">Password</param>
        /// <param name="captchaResponse">User's response to the CAPTCHA challenge</param>
        /// <returns>Coroutine for asynchronous execution</returns>
        public IEnumerator Login(string usernameOrEmail, string password, string captchaResponse)
        {
            // Check if we have an active CAPTCHA
            if (string.IsNullOrEmpty(CaptchaService.Instance.GetChallengeId()))
            {
                OnLoginComplete?.Invoke(false, "CAPTCHA validation required. Please refresh the CAPTCHA.");
                yield break;
            }
            
            // Create login request
            LoginRequest request = new LoginRequest
            {
                username_or_email = usernameOrEmail,
                password = password,
                device_id = deviceId,
                platform = platformInfo,
                version = clientVersion,
                captcha_challenge_id = CaptchaService.Instance.GetChallengeId(),
                captcha_response = captchaResponse
            };
            
            string requestJson = JsonConvert.SerializeObject(request);
            string url = apiBaseUrl + loginEndpoint;
            
            using (UnityWebRequest webRequest = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(requestJson);
                webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
                webRequest.downloadHandler = new DownloadHandlerBuffer();
                webRequest.SetRequestHeader("Content-Type", "application/json");
                webRequest.timeout = 10; // 10 seconds
                
                yield return webRequest.SendWebRequest();

                if (webRequest.result != UnityWebRequest.Result.Success)
                {
                    if (webRequest.responseCode == 401)
                    {
                        OnLoginComplete?.Invoke(false, "Invalid username or password");
                    }
                    else if (webRequest.responseCode == 429)
                    {
                        OnLoginComplete?.Invoke(false, "Too many login attempts. Please try again later.");
                    }
                    else
                    {
                        Debug.LogError($"Login Error: {webRequest.error}");
                        OnLoginComplete?.Invoke(false, "Login failed. Please try again.");
                    }
                    yield break;
                }

                try
                {
                    string responseJson = webRequest.downloadHandler.text;
                    AuthResponse response = JsonConvert.DeserializeObject<AuthResponse>(responseJson);
                    
                    if (response == null || response.user == null || string.IsNullOrEmpty(response.token))
                    {
                        Debug.LogError("Invalid auth response from server");
                        OnLoginComplete?.Invoke(false, "Invalid response from server");
                        yield break;
                    }
                    
                    // Store auth data
                    currentUser = response.user;
                    authToken = response.token;
                    isLoggedIn = true;
                    
                    // Save to PlayerPrefs
                    PlayerPrefs.SetString("AuthToken", authToken);
                    PlayerPrefs.Save();
                    
                    OnLoginComplete?.Invoke(true, null);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Login Parsing Error: {ex.Message}");
                    OnLoginComplete?.Invoke(false, "Failed to process login response");
                }
            }
        }

        /// <summary>
        /// Registers a new user with the provided information, including CAPTCHA validation
        /// </summary>
        /// <param name="username">Desired username</param>
        /// <param name="email">Email address</param>
        /// <param name="password">Password</param>
        /// <param name="firstName">First name (optional)</param>
        /// <param name="lastName">Last name (optional)</param>
        /// <param name="captchaResponse">User's response to the CAPTCHA challenge</param>
        /// <returns>Coroutine for asynchronous execution</returns>
        public IEnumerator Register(string username, string email, string password, 
                                 string firstName, string lastName, string captchaResponse)
        {
            // Check if we have an active CAPTCHA
            if (string.IsNullOrEmpty(CaptchaService.Instance.GetChallengeId()))
            {
                OnRegistrationComplete?.Invoke(false, "CAPTCHA validation required. Please refresh the CAPTCHA.");
                yield break;
            }
            
            // Create registration request
            RegisterRequest request = new RegisterRequest
            {
                username = username,
                email = email,
                password = password,
                first_name = firstName,
                last_name = lastName,
                device_id = deviceId,
                platform = platformInfo,
                captcha_challenge_id = CaptchaService.Instance.GetChallengeId(),
                captcha_response = captchaResponse
            };
            
            string requestJson = JsonConvert.SerializeObject(request);
            string url = apiBaseUrl + registerEndpoint;
            
            using (UnityWebRequest webRequest = new UnityWebRequest(url, "POST"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(requestJson);
                webRequest.uploadHandler = new UploadHandlerRaw(bodyRaw);
                webRequest.downloadHandler = new DownloadHandlerBuffer();
                webRequest.SetRequestHeader("Content-Type", "application/json");
                webRequest.timeout = 10; // 10 seconds
                
                yield return webRequest.SendWebRequest();

                if (webRequest.result != UnityWebRequest.Result.Success)
                {
                    if (webRequest.responseCode == 409)
                    {
                        OnRegistrationComplete?.Invoke(false, "Username or email already exists");
                    }
                    else if (webRequest.responseCode == 400)
                    {
                        // Try to parse error message
                        try
                        {
                            string responseJson = webRequest.downloadHandler.text;
                            AuthResponse response = JsonConvert.DeserializeObject<AuthResponse>(responseJson);
                            string errorMsg = response?.error ?? "Invalid registration data";
                            OnRegistrationComplete?.Invoke(false, errorMsg);
                        }
                        catch
                        {
                            OnRegistrationComplete?.Invoke(false, "Invalid registration data");
                        }
                    }
                    else if (webRequest.responseCode == 429)
                    {
                        OnRegistrationComplete?.Invoke(false, "Too many registration attempts. Please try again later.");
                    }
                    else
                    {
                        Debug.LogError($"Registration Error: {webRequest.error}");
                        OnRegistrationComplete?.Invoke(false, "Registration failed. Please try again.");
                    }
                    yield break;
                }

                try
                {
                    string responseJson = webRequest.downloadHandler.text;
                    AuthResponse response = JsonConvert.DeserializeObject<AuthResponse>(responseJson);
                    
                    if (response == null || response.user == null || string.IsNullOrEmpty(response.token))
                    {
                        Debug.LogError("Invalid registration response from server");
                        OnRegistrationComplete?.Invoke(false, "Invalid response from server");
                        yield break;
                    }
                    
                    // Store auth data
                    currentUser = response.user;
                    authToken = response.token;
                    isLoggedIn = true;
                    
                    // Save to PlayerPrefs
                    PlayerPrefs.SetString("AuthToken", authToken);
                    PlayerPrefs.Save();
                    
                    OnRegistrationComplete?.Invoke(true, null);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Registration Parsing Error: {ex.Message}");
                    OnRegistrationComplete?.Invoke(false, "Failed to process registration response");
                }
            }
        }

        /// <summary>
        /// Logs out the current user
        /// </summary>
        /// <returns>Coroutine for asynchronous execution</returns>
        public IEnumerator Logout()
        {
            if (!isLoggedIn || string.IsNullOrEmpty(authToken))
            {
                // Already logged out
                isLoggedIn = false;
                currentUser = null;
                authToken = null;
                
                // Clear PlayerPrefs
                PlayerPrefs.DeleteKey("AuthToken");
                PlayerPrefs.Save();
                
                OnLogoutComplete?.Invoke(true);
                yield break;
            }
            
            string url = apiBaseUrl + logoutEndpoint;
            
            using (UnityWebRequest webRequest = new UnityWebRequest(url, "POST"))
            {
                webRequest.downloadHandler = new DownloadHandlerBuffer();
                webRequest.SetRequestHeader("Authorization", "Bearer " + authToken);
                webRequest.timeout = 10; // 10 seconds
                
                yield return webRequest.SendWebRequest();

                // Clear user data regardless of success
                isLoggedIn = false;
                currentUser = null;
                authToken = null;
                
                // Clear PlayerPrefs
                PlayerPrefs.DeleteKey("AuthToken");
                PlayerPrefs.Save();
                
                // Notify completion
                OnLogoutComplete?.Invoke(webRequest.result == UnityWebRequest.Result.Success);
                
                if (webRequest.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogWarning($"Logout Error: {webRequest.error}");
                }
            }
        }

        /// <summary>
        /// Validates the current auth token
        /// </summary>
        /// <returns>Coroutine for asynchronous execution</returns>
        private IEnumerator ValidateToken()
        {
            if (string.IsNullOrEmpty(authToken))
            {
                isLoggedIn = false;
                yield break;
            }
            
            string url = apiBaseUrl + validateTokenEndpoint;
            
            using (UnityWebRequest webRequest = new UnityWebRequest(url, "POST"))
            {
                webRequest.downloadHandler = new DownloadHandlerBuffer();
                webRequest.SetRequestHeader("Authorization", "Bearer " + authToken);
                webRequest.timeout = 10; // 10 seconds
                
                yield return webRequest.SendWebRequest();

                if (webRequest.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogWarning($"Token validation error: {webRequest.error}");
                    isLoggedIn = false;
                    currentUser = null;
                    authToken = null;
                    
                    // Clear PlayerPrefs
                    PlayerPrefs.DeleteKey("AuthToken");
                    PlayerPrefs.Save();
                    yield break;
                }

                try
                {
                    string responseJson = webRequest.downloadHandler.text;
                    dynamic response = JsonConvert.DeserializeObject<dynamic>(responseJson);
                    
                    if (response == null || !response.valid)
                    {
                        isLoggedIn = false;
                        currentUser = null;
                        authToken = null;
                        
                        // Clear PlayerPrefs
                        PlayerPrefs.DeleteKey("AuthToken");
                        PlayerPrefs.Save();
                        yield break;
                    }
                    
                    // Token is valid, update user data
                    string userJson = JsonConvert.SerializeObject(response.user);
                    currentUser = JsonConvert.DeserializeObject<UserData>(userJson);
                    isLoggedIn = true;
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Token Validation Parsing Error: {ex.Message}");
                    isLoggedIn = false;
                    currentUser = null;
                    authToken = null;
                    
                    // Clear PlayerPrefs
                    PlayerPrefs.DeleteKey("AuthToken");
                    PlayerPrefs.Save();
                }
            }
        }

        /// <summary>
        /// Gets the current user data
        /// </summary>
        /// <returns>User data or null if not logged in</returns>
        public UserData GetCurrentUser()
        {
            return currentUser;
        }

        /// <summary>
        /// Gets the current auth token
        /// </summary>
        /// <returns>Auth token or null if not logged in</returns>
        public string GetAuthToken()
        {
            return authToken;
        }

        /// <summary>
        /// Checks if the user is currently logged in
        /// </summary>
        /// <returns>True if logged in</returns>
        public bool IsLoggedIn()
        {
            return isLoggedIn;
        }
    }
} 
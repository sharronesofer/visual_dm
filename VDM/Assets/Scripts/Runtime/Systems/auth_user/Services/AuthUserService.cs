using System;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Systems.AuthUser.Models;

namespace VDM.Systems.AuthUser.Services
{
    /// <summary>
    /// Frontend authentication and user service that interfaces with backend auth_user system
    /// Handles user authentication, session management, and user preferences
    /// </summary>
    public class AuthUserService : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private bool enableDebugLogging = true;
        [SerializeField] private bool persistSession = true;
        [SerializeField] private float sessionCheckInterval = 300f; // 5 minutes
        
        // Events
        public static event Action<User> OnUserLoggedIn;
        public static event Action OnUserLoggedOut;
        public static event Action<AuthenticationState> OnAuthenticationStateChanged;
        public static event Action<UserPreferences> OnUserPreferencesUpdated;
        
        // State
        private User currentUser;
        private AuthToken currentToken;
        private Session currentSession;
        private AuthenticationState authState = AuthenticationState.Unauthenticated;
        private bool isInitialized = false;
        
        public User CurrentUser => currentUser;
        public bool IsAuthenticated => authState == AuthenticationState.Authenticated && currentUser != null;
        public AuthenticationState AuthState => authState;
        
        private void Awake()
        {
            InitializeService();
        }
        
        private void Start()
        {
            if (persistSession)
            {
                LoadPersistedSession();
            }
            
            InvokeRepeating(nameof(CheckSessionValidity), sessionCheckInterval, sessionCheckInterval);
        }
        
        private void InitializeService()
        {
            if (isInitialized) return;
            
            if (enableDebugLogging)
                Debug.Log("AuthUserService: Initializing authentication system...");
            
            SetAuthenticationState(AuthenticationState.Unauthenticated);
            isInitialized = true;
        }
        
        public async Task<LoginResponse> LoginAsync(string username, string password, bool rememberMe = false)
        {
            try
            {
                SetAuthenticationState(AuthenticationState.Authenticating);
                
                if (enableDebugLogging)
                    Debug.Log($"AuthUserService: Attempting login for user: {username}");
                
                var loginRequest = new LoginRequest
                {
                    username = username,
                    password = password,
                    rememberMe = rememberMe
                };
                
                // TODO: Send login request to backend
                // var response = await BackendService.LoginAsync(loginRequest);
                
                // Placeholder success response
                var response = new LoginResponse
                {
                    success = true,
                    message = "Login successful",
                    user = new User
                    {
                        id = Guid.NewGuid().ToString(),
                        username = username,
                        email = $"{username}@example.com",
                        role = UserRole.Player,
                        isActive = true,
                        createdAt = DateTime.Now,
                        lastLoginAt = DateTime.Now
                    },
                    token = new AuthToken
                    {
                        accessToken = "placeholder_token",
                        refreshToken = "placeholder_refresh",
                        expiresAt = DateTime.Now.AddHours(24),
                        tokenType = "Bearer"
                    }
                };
                
                if (response.success)
                {
                    currentUser = response.user;
                    currentToken = response.token;
                    
                    if (persistSession && rememberMe)
                    {
                        SaveSessionToPlayerPrefs();
                    }
                    
                    SetAuthenticationState(AuthenticationState.Authenticated);
                    OnUserLoggedIn?.Invoke(currentUser);
                    
                    if (enableDebugLogging)
                        Debug.Log($"AuthUserService: Login successful for user: {username}");
                }
                else
                {
                    SetAuthenticationState(AuthenticationState.Error);
                    
                    if (enableDebugLogging)
                        Debug.LogWarning($"AuthUserService: Login failed: {response.message}");
                }
                
                return response;
            }
            catch (Exception ex)
            {
                SetAuthenticationState(AuthenticationState.Error);
                Debug.LogError($"AuthUserService: Login error: {ex.Message}");
                
                return new LoginResponse
                {
                    success = false,
                    message = ex.Message
                };
            }
        }
        
        public async Task LogoutAsync()
        {
            try
            {
                if (enableDebugLogging)
                    Debug.Log("AuthUserService: Logging out user");
                
                // TODO: Send logout request to backend
                // await BackendService.LogoutAsync(currentToken);
                
                ClearSession();
                SetAuthenticationState(AuthenticationState.Unauthenticated);
                OnUserLoggedOut?.Invoke();
                
                if (enableDebugLogging)
                    Debug.Log("AuthUserService: Logout successful");
            }
            catch (Exception ex)
            {
                Debug.LogError($"AuthUserService: Logout error: {ex.Message}");
            }
        }
        
        public async Task<bool> RefreshTokenAsync()
        {
            try
            {
                if (currentToken == null || string.IsNullOrEmpty(currentToken.refreshToken))
                {
                    return false;
                }
                
                // TODO: Send refresh token request to backend
                // var newToken = await BackendService.RefreshTokenAsync(currentToken.refreshToken);
                
                if (enableDebugLogging)
                    Debug.Log("AuthUserService: Token refreshed successfully");
                
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"AuthUserService: Token refresh error: {ex.Message}");
                SetAuthenticationState(AuthenticationState.TokenExpired);
                return false;
            }
        }
        
        public async Task<bool> UpdateUserPreferencesAsync(UserPreferences preferences)
        {
            try
            {
                if (!IsAuthenticated)
                {
                    Debug.LogWarning("AuthUserService: Cannot update preferences - user not authenticated");
                    return false;
                }
                
                // TODO: Send preferences update to backend
                // var result = await BackendService.UpdateUserPreferencesAsync(currentUser.id, preferences);
                
                currentUser.preferences = preferences;
                OnUserPreferencesUpdated?.Invoke(preferences);
                
                if (enableDebugLogging)
                    Debug.Log("AuthUserService: User preferences updated");
                
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"AuthUserService: Preferences update error: {ex.Message}");
                return false;
            }
        }
        
        private void CheckSessionValidity()
        {
            if (currentToken != null && DateTime.Now >= currentToken.expiresAt)
            {
                if (enableDebugLogging)
                    Debug.Log("AuthUserService: Token expired, attempting refresh");
                
                _ = RefreshTokenAsync();
            }
        }
        
        private void SetAuthenticationState(AuthenticationState newState)
        {
            if (authState != newState)
            {
                authState = newState;
                OnAuthenticationStateChanged?.Invoke(authState);
            }
        }
        
        private void SaveSessionToPlayerPrefs()
        {
            if (currentUser != null && currentToken != null)
            {
                PlayerPrefs.SetString("VDM_UserId", currentUser.id);
                PlayerPrefs.SetString("VDM_AccessToken", currentToken.accessToken);
                PlayerPrefs.SetString("VDM_RefreshToken", currentToken.refreshToken);
                PlayerPrefs.Save();
            }
        }
        
        private void LoadPersistedSession()
        {
            if (PlayerPrefs.HasKey("VDM_UserId"))
            {
                string userId = PlayerPrefs.GetString("VDM_UserId");
                string accessToken = PlayerPrefs.GetString("VDM_AccessToken");
                string refreshToken = PlayerPrefs.GetString("VDM_RefreshToken");
                
                if (!string.IsNullOrEmpty(userId) && !string.IsNullOrEmpty(accessToken))
                {
                    // TODO: Validate session with backend
                    if (enableDebugLogging)
                        Debug.Log("AuthUserService: Found persisted session, validating...");
                }
            }
        }
        
        private void ClearSession()
        {
            currentUser = null;
            currentToken = null;
            currentSession = null;
            
            PlayerPrefs.DeleteKey("VDM_UserId");
            PlayerPrefs.DeleteKey("VDM_AccessToken");
            PlayerPrefs.DeleteKey("VDM_RefreshToken");
            PlayerPrefs.Save();
        }
    }
} 
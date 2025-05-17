using UnityEngine;

namespace VisualDM.API
{
    /// <summary>
    /// Configuration for API endpoints and settings
    /// </summary>
    [CreateAssetMenu(fileName = "ApiConfig", menuName = "VisualDM/API Config")]
    public class ApiConfig : ScriptableObject
    {
        [Header("Server Settings")]
        [Tooltip("Base URL for the API")]
        [SerializeField] private string baseUrl = "http://localhost:5000/api";
        
        [Tooltip("Timeout in seconds for API requests")]
        [SerializeField] private int timeoutSeconds = 30;
        
        [Tooltip("Number of retry attempts for failed requests")]
        [SerializeField] private int maxRetryAttempts = 3;
        
        [Header("Authentication")]
        [Tooltip("Whether to use authentication")]
        [SerializeField] private bool useAuthentication = true;
        
        [Tooltip("Authentication endpoint path")]
        [SerializeField] private string authEndpoint = "/auth/login";

        // Endpoint paths
        [Header("Endpoint Paths")]
        [SerializeField] private string dialogueEndpoint = "/dialogue/generate";
        [SerializeField] private string entityEndpoint = "/entity";
        
        // Properties
        public string BaseUrl => baseUrl;
        public int TimeoutSeconds => timeoutSeconds;
        public int MaxRetryAttempts => maxRetryAttempts;
        public bool UseAuthentication => useAuthentication;
        public string AuthEndpoint => baseUrl + authEndpoint;
        public string DialogueEndpoint => baseUrl + dialogueEndpoint;
        public string EntityEndpoint => baseUrl + entityEndpoint;

        // Full URLs for common endpoints
        public string GetFullUrl(string endpointPath)
        {
            return $"{baseUrl}{endpointPath}";
        }
    }
} 
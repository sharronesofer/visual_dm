using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Systems.AuthUser.Models
{
    /// <summary>
    /// Core authentication and user system models for Unity frontend
    /// Mirrors backend auth_user system structure
    /// </summary>
    
    [Serializable]
    public class User
    {
        public string id;
        public string username;
        public string email;
        public DateTime createdAt;
        public DateTime lastLoginAt;
        public UserRole role;
        public UserPreferences preferences;
        public bool isActive;
    }
    
    [Serializable]
    public class UserPreferences
    {
        public Dictionary<string, object> settings;
        public string theme;
        public string language;
        public bool enableNotifications;
        public float audioVolume;
        public float musicVolume;
    }
    
    [Serializable]
    public class AuthToken
    {
        public string accessToken;
        public string refreshToken;
        public DateTime expiresAt;
        public string tokenType;
    }
    
    [Serializable]
    public class LoginRequest
    {
        public string username;
        public string password;
        public bool rememberMe;
    }
    
    [Serializable]
    public class LoginResponse
    {
        public bool success;
        public string message;
        public User user;
        public AuthToken token;
    }
    
    [Serializable]
    public class Session
    {
        public string sessionId;
        public string userId;
        public DateTime startTime;
        public DateTime lastActivity;
        public bool isActive;
        public Dictionary<string, object> sessionData;
    }
    
    public enum UserRole
    {
        Guest,
        Player,
        GameMaster,
        Administrator
    }
    
    public enum AuthenticationState
    {
        Unauthenticated,
        Authenticating,
        Authenticated,
        TokenExpired,
        Error
    }
} 
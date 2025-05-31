using System;
using System.Collections.Generic;
using VDM.DTOs.Core.Shared;

namespace VDM.DTOs.Core.Auth
{
    /// <summary>
    /// User role enumeration
    /// </summary>
    public enum UserRoleDTO
    {
        Player,
        GameMaster,
        Admin,
        Moderator
    }

    /// <summary>
    /// User status enumeration
    /// </summary>
    public enum UserStatusDTO
    {
        Active,
        Inactive,
        Suspended,
        Banned,
        PendingVerification
    }

    /// <summary>
    /// User model for authentication and user management
    /// </summary>
    [Serializable]
    public class UserDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Username { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string DisplayName { get; set; }
        public UserRoleDTO Role { get; set; } = UserRoleDTO.Player;
        public UserStatusDTO Status { get; set; } = UserStatusDTO.Active;
        public bool EmailVerified { get; set; } = false;
        public DateTime? LastLogin { get; set; }
        public string ProfilePictureUrl { get; set; }
        public Dictionary<string, object> Preferences { get; set; } = new Dictionary<string, object>();
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Session model for tracking user sessions
    /// </summary>
    [Serializable]
    public class SessionDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;
        public string UserId { get; set; } = string.Empty;
        public string Token { get; set; } = string.Empty;
        public string RefreshToken { get; set; }
        public DateTime ExpiresAt { get; set; }
        public DateTime LastActivity { get; set; } = DateTime.UtcNow;
        public string IpAddress { get; set; }
        public string UserAgent { get; set; }
        public bool IsActive { get; set; } = true;
        public Dictionary<string, object> DeviceInfo { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Permission model for role-based access control
    /// </summary>
    [Serializable]
    public class PermissionDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public string Resource { get; set; } = string.Empty;
        public string Action { get; set; } = string.Empty; // create, read, update, delete, etc.
        public Dictionary<string, object> Conditions { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Role model for grouping permissions
    /// </summary>
    [Serializable]
    public class RoleDTO : MetadataDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; }
        public List<PermissionDTO> Permissions { get; set; } = new List<PermissionDTO>();
        public bool IsSystemRole { get; set; } = false;
    }

    // ================ Request DTOs ================

    /// <summary>
    /// User registration request
    /// </summary>
    [Serializable]
    public class RegisterRequestDTO
    {
        public string Username { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
        public string DisplayName { get; set; }
        public Dictionary<string, object> Preferences { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// User login request
    /// </summary>
    [Serializable]
    public class LoginRequestDTO
    {
        public string Username { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
        public bool RememberMe { get; set; } = false;
    }

    /// <summary>
    /// Password change request
    /// </summary>
    [Serializable]
    public class ChangePasswordRequestDTO
    {
        public string CurrentPassword { get; set; } = string.Empty;
        public string NewPassword { get; set; } = string.Empty;
    }

    /// <summary>
    /// Password reset request
    /// </summary>
    [Serializable]
    public class ResetPasswordRequestDTO
    {
        public string Email { get; set; } = string.Empty;
    }

    /// <summary>
    /// Token refresh request
    /// </summary>
    [Serializable]
    public class RefreshTokenRequestDTO
    {
        public string RefreshToken { get; set; } = string.Empty;
    }

    // ================ Response DTOs ================

    /// <summary>
    /// Authentication response
    /// </summary>
    [Serializable]
    public class AuthResponseDTO : SuccessResponseDTO
    {
        public UserDTO User { get; set; } = new UserDTO();
        public string AccessToken { get; set; } = string.Empty;
        public string RefreshToken { get; set; } = string.Empty;
        public DateTime ExpiresAt { get; set; }
    }

    /// <summary>
    /// User profile response
    /// </summary>
    [Serializable]
    public class UserProfileResponseDTO : SuccessResponseDTO
    {
        public UserDTO User { get; set; } = new UserDTO();
    }

    /// <summary>
    /// Session validation response
    /// </summary>
    [Serializable]
    public class SessionValidationResponseDTO : SuccessResponseDTO
    {
        public bool IsValid { get; set; } = false;
        public SessionDTO Session { get; set; }
        public UserDTO User { get; set; }
    }
} 
using Newtonsoft.Json;
using System.Collections.Generic;
using System;
using UnityEngine;


namespace VDM.Runtime.AuthUser.Models
{
    #region Core Enums
    
    /// <summary>
    /// User account status
    /// </summary>
    [Serializable]
    public enum UserStatus
    {
        Active,
        Inactive,
        Suspended,
        Banned,
        PendingVerification,
        Deleted
    }
    
    /// <summary>
    /// User role types
    /// </summary>
    [Serializable]
    public enum UserRole
    {
        Player,
        Moderator,
        Admin,
        Developer,
        Beta,
        VIP
    }
    
    /// <summary>
    /// Authentication provider types
    /// </summary>
    [Serializable]
    public enum AuthProvider
    {
        Internal,
        Google,
        Facebook,
        Twitter,
        Discord,
        Steam,
        Apple
    }
    
    /// <summary>
    /// Privacy settings
    /// </summary>
    [Serializable]
    public enum PrivacyLevel
    {
        Public,
        Friends,
        Private
    }
    
    /// <summary>
    /// Theme preferences
    /// </summary>
    [Serializable]
    public enum ThemeType
    {
        Light,
        Dark,
        Auto,
        Custom
    }
    
    /// <summary>
    /// Language preferences
    /// </summary>
    [Serializable]
    public enum Language
    {
        English,
        Spanish,
        French,
        German,
        Italian,
        Portuguese,
        Russian,
        Japanese,
        Chinese,
        Korean
    }
    
    #endregion
    
    #region Authentication Models
    
    /// <summary>
    /// Login request model
    /// </summary>
    [Serializable]
    public class LoginRequest
    {
        [JsonProperty("email")]
        public string Email { get; set; }
        
        [JsonProperty("password")]
        public string Password { get; set; }
        
        [JsonProperty("remember_me")]
        public bool RememberMe { get; set; }
        
        [JsonProperty("device_id")]
        public string DeviceId { get; set; }
        
        [JsonProperty("provider")]
        public AuthProvider Provider { get; set; } = AuthProvider.Internal;
        
        [JsonProperty("provider_token")]
        public string ProviderToken { get; set; }
    }
    
    /// <summary>
    /// Registration request model
    /// </summary>
    [Serializable]
    public class RegisterRequest
    {
        [JsonProperty("username")]
        public string Username { get; set; }
        
        [JsonProperty("email")]
        public string Email { get; set; }
        
        [JsonProperty("password")]
        public string Password { get; set; }
        
        [JsonProperty("confirm_password")]
        public string ConfirmPassword { get; set; }
        
        [JsonProperty("display_name")]
        public string DisplayName { get; set; }
        
        [JsonProperty("date_of_birth")]
        public DateTime DateOfBirth { get; set; }
        
        [JsonProperty("accept_terms")]
        public bool AcceptTerms { get; set; }
        
        [JsonProperty("accept_privacy")]
        public bool AcceptPrivacy { get; set; }
        
        [JsonProperty("marketing_consent")]
        public bool MarketingConsent { get; set; }
        
        [JsonProperty("device_id")]
        public string DeviceId { get; set; }
        
        [JsonProperty("referral_code")]
        public string ReferralCode { get; set; }
    }
    
    /// <summary>
    /// Password reset request model
    /// </summary>
    [Serializable]
    public class PasswordResetRequest
    {
        [JsonProperty("email")]
        public string Email { get; set; }
        
        [JsonProperty("reset_token")]
        public string ResetToken { get; set; }
        
        [JsonProperty("new_password")]
        public string NewPassword { get; set; }
        
        [JsonProperty("confirm_password")]
        public string ConfirmPassword { get; set; }
    }
    
    /// <summary>
    /// Authentication response model
    /// </summary>
    [Serializable]
    public class AuthResponse
    {
        [JsonProperty("access_token")]
        public string AccessToken { get; set; }
        
        [JsonProperty("refresh_token")]
        public string RefreshToken { get; set; }
        
        [JsonProperty("token_type")]
        public string TokenType { get; set; } = "Bearer";
        
        [JsonProperty("expires_in")]
        public int ExpiresIn { get; set; }
        
        [JsonProperty("user")]
        public UserModel User { get; set; }
        
        [JsonProperty("permissions")]
        public List<string> Permissions { get; set; } = new List<string>();
        
        [JsonProperty("is_first_login")]
        public bool IsFirstLogin { get; set; }
        
        [JsonProperty("requires_verification")]
        public bool RequiresVerification { get; set; }
        
        [JsonProperty("mfa_required")]
        public bool MfaRequired { get; set; }
        
        [JsonProperty("mfa_methods")]
        public List<string> MfaMethods { get; set; } = new List<string>();
    }
    
    /// <summary>
    /// Multi-factor authentication model
    /// </summary>
    [Serializable]
    public class MfaRequest
    {
        [JsonProperty("user_id")]
        public string UserId { get; set; }
        
        [JsonProperty("method")]
        public string Method { get; set; }
        
        [JsonProperty("code")]
        public string Code { get; set; }
        
        [JsonProperty("backup_code")]
        public string BackupCode { get; set; }
        
        [JsonProperty("device_id")]
        public string DeviceId { get; set; }
        
        [JsonProperty("remember_device")]
        public bool RememberDevice { get; set; }
    }
    
    #endregion
    
    #region User Models
    
    /// <summary>
    /// Complete user model
    /// </summary>
    [Serializable]
    public class UserModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("username")]
        public string Username { get; set; }
        
        [JsonProperty("email")]
        public string Email { get; set; }
        
        [JsonProperty("display_name")]
        public string DisplayName { get; set; }
        
        [JsonProperty("avatar_url")]
        public string AvatarUrl { get; set; }
        
        [JsonProperty("status")]
        public UserStatus Status { get; set; }
        
        [JsonProperty("role")]
        public UserRole Role { get; set; }
        
        [JsonProperty("level")]
        public int Level { get; set; }
        
        [JsonProperty("experience")]
        public long Experience { get; set; }
        
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; }
        
        [JsonProperty("last_login")]
        public DateTime LastLogin { get; set; }
        
        [JsonProperty("last_seen")]
        public DateTime LastSeen { get; set; }
        
        [JsonProperty("is_online")]
        public bool IsOnline { get; set; }
        
        [JsonProperty("is_verified")]
        public bool IsVerified { get; set; }
        
        [JsonProperty("premium_expires")]
        public DateTime? PremiumExpires { get; set; }
        
        [JsonProperty("profile")]
        public UserProfileModel Profile { get; set; }
        
        [JsonProperty("preferences")]
        public UserPreferencesModel Preferences { get; set; }
        
        [JsonProperty("statistics")]
        public UserStatisticsModel Statistics { get; set; }
        
        [JsonProperty("achievements")]
        public List<string> Achievements { get; set; } = new List<string>();
        
        [JsonProperty("friends")]
        public List<string> Friends { get; set; } = new List<string>();
        
        [JsonProperty("blocked_users")]
        public List<string> BlockedUsers { get; set; } = new List<string>();
        
        [JsonProperty("badges")]
        public List<BadgeModel> Badges { get; set; } = new List<BadgeModel>();
    }
    
    /// <summary>
    /// User profile information
    /// </summary>
    [Serializable]
    public class UserProfileModel
    {
        [JsonProperty("bio")]
        public string Bio { get; set; }
        
        [JsonProperty("location")]
        public string Location { get; set; }
        
        [JsonProperty("website")]
        public string Website { get; set; }
        
        [JsonProperty("date_of_birth")]
        public DateTime? DateOfBirth { get; set; }
        
        [JsonProperty("gender")]
        public string Gender { get; set; }
        
        [JsonProperty("timezone")]
        public string Timezone { get; set; }
        
        [JsonProperty("favorite_games")]
        public List<string> FavoriteGames { get; set; } = new List<string>();
        
        [JsonProperty("interests")]
        public List<string> Interests { get; set; } = new List<string>();
        
        [JsonProperty("social_links")]
        public Dictionary<string, string> SocialLinks { get; set; } = new Dictionary<string, string>();
        
        [JsonProperty("privacy_settings")]
        public PrivacySettingsModel PrivacySettings { get; set; }
        
        [JsonProperty("custom_fields")]
        public Dictionary<string, object> CustomFields { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// User preferences and settings
    /// </summary>
    [Serializable]
    public class UserPreferencesModel
    {
        [JsonProperty("language")]
        public Language Language { get; set; } = Language.English;
        
        [JsonProperty("theme")]
        public ThemeType Theme { get; set; } = ThemeType.Dark;
        
        [JsonProperty("notifications")]
        public NotificationPreferencesModel Notifications { get; set; }
        
        [JsonProperty("gameplay")]
        public GameplayPreferencesModel Gameplay { get; set; }
        
        [JsonProperty("audio")]
        public AudioPreferencesModel Audio { get; set; }
        
        [JsonProperty("video")]
        public VideoPreferencesModel Video { get; set; }
        
        [JsonProperty("accessibility")]
        public AccessibilityPreferencesModel Accessibility { get; set; }
        
        [JsonProperty("privacy")]
        public PrivacySettingsModel Privacy { get; set; }
        
        [JsonProperty("communication")]
        public CommunicationPreferencesModel Communication { get; set; }
    }
    
    /// <summary>
    /// User statistics and metrics
    /// </summary>
    [Serializable]
    public class UserStatisticsModel
    {
        [JsonProperty("total_playtime")]
        public long TotalPlaytime { get; set; }
        
        [JsonProperty("games_played")]
        public int GamesPlayed { get; set; }
        
        [JsonProperty("achievements_unlocked")]
        public int AchievementsUnlocked { get; set; }
        
        [JsonProperty("quests_completed")]
        public int QuestsCompleted { get; set; }
        
        [JsonProperty("characters_created")]
        public int CharactersCreated { get; set; }
        
        [JsonProperty("friends_count")]
        public int FriendsCount { get; set; }
        
        [JsonProperty("messages_sent")]
        public int MessagesSent { get; set; }
        
        [JsonProperty("login_streak")]
        public int LoginStreak { get; set; }
        
        [JsonProperty("last_streak_date")]
        public DateTime LastStreakDate { get; set; }
        
        [JsonProperty("custom_stats")]
        public Dictionary<string, object> CustomStats { get; set; } = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// User badge information
    /// </summary>
    [Serializable]
    public class BadgeModel
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("name")]
        public string Name { get; set; }
        
        [JsonProperty("description")]
        public string Description { get; set; }
        
        [JsonProperty("icon_url")]
        public string IconUrl { get; set; }
        
        [JsonProperty("rarity")]
        public string Rarity { get; set; }
        
        [JsonProperty("earned_at")]
        public DateTime EarnedAt { get; set; }
        
        [JsonProperty("is_visible")]
        public bool IsVisible { get; set; } = true;
    }
    
    #endregion
    
    #region Preference Models
    
    /// <summary>
    /// Notification preferences
    /// </summary>
    [Serializable]
    public class NotificationPreferencesModel
    {
        [JsonProperty("email_notifications")]
        public bool EmailNotifications { get; set; } = true;
        
        [JsonProperty("push_notifications")]
        public bool PushNotifications { get; set; } = true;
        
        [JsonProperty("in_game_notifications")]
        public bool InGameNotifications { get; set; } = true;
        
        [JsonProperty("friend_requests")]
        public bool FriendRequests { get; set; } = true;
        
        [JsonProperty("messages")]
        public bool Messages { get; set; } = true;
        
        [JsonProperty("quest_updates")]
        public bool QuestUpdates { get; set; } = true;
        
        [JsonProperty("achievement_unlocks")]
        public bool AchievementUnlocks { get; set; } = true;
        
        [JsonProperty("maintenance_alerts")]
        public bool MaintenanceAlerts { get; set; } = true;
        
        [JsonProperty("marketing")]
        public bool Marketing { get; set; } = false;
        
        [JsonProperty("sound_enabled")]
        public bool SoundEnabled { get; set; } = true;
        
        [JsonProperty("quiet_hours_start")]
        public string QuietHoursStart { get; set; } = "22:00";
        
        [JsonProperty("quiet_hours_end")]
        public string QuietHoursEnd { get; set; } = "08:00";
    }
    
    /// <summary>
    /// Gameplay preferences
    /// </summary>
    [Serializable]
    public class GameplayPreferencesModel
    {
        [JsonProperty("difficulty")]
        public string Difficulty { get; set; } = "Normal";
        
        [JsonProperty("auto_save")]
        public bool AutoSave { get; set; } = true;
        
        [JsonProperty("auto_save_interval")]
        public int AutoSaveInterval { get; set; } = 300; // seconds
        
        [JsonProperty("show_tutorials")]
        public bool ShowTutorials { get; set; } = true;
        
        [JsonProperty("show_hints")]
        public bool ShowHints { get; set; } = true;
        
        [JsonProperty("pause_on_focus_loss")]
        public bool PauseOnFocusLoss { get; set; } = true;
        
        [JsonProperty("auto_loot")]
        public bool AutoLoot { get; set; } = false;
        
        [JsonProperty("skip_cinematics")]
        public bool SkipCinematics { get; set; } = false;
        
        [JsonProperty("movement_speed")]
        public float MovementSpeed { get; set; } = 1f;
        
        [JsonProperty("camera_sensitivity")]
        public float CameraSensitivity { get; set; } = 1f;
        
        [JsonProperty("invert_camera_y")]
        public bool InvertCameraY { get; set; } = false;
    }
    
    /// <summary>
    /// Audio preferences
    /// </summary>
    [Serializable]
    public class AudioPreferencesModel
    {
        [JsonProperty("master_volume")]
        public float MasterVolume { get; set; } = 1f;
        
        [JsonProperty("music_volume")]
        public float MusicVolume { get; set; } = 0.8f;
        
        [JsonProperty("sfx_volume")]
        public float SfxVolume { get; set; } = 1f;
        
        [JsonProperty("voice_volume")]
        public float VoiceVolume { get; set; } = 1f;
        
        [JsonProperty("ui_volume")]
        public float UiVolume { get; set; } = 0.7f;
        
        [JsonProperty("mute_when_minimized")]
        public bool MuteWhenMinimized { get; set; } = true;
        
        [JsonProperty("enable_voice_chat")]
        public bool EnableVoiceChat { get; set; } = true;
        
        [JsonProperty("voice_chat_volume")]
        public float VoiceChatVolume { get; set; } = 1f;
        
        [JsonProperty("microphone_sensitivity")]
        public float MicrophoneSensitivity { get; set; } = 0.5f;
        
        [JsonProperty("push_to_talk")]
        public bool PushToTalk { get; set; } = false;
        
        [JsonProperty("audio_quality")]
        public string AudioQuality { get; set; } = "High";
    }
    
    /// <summary>
    /// Video and graphics preferences
    /// </summary>
    [Serializable]
    public class VideoPreferencesModel
    {
        [JsonProperty("resolution")]
        public string Resolution { get; set; } = "1920x1080";
        
        [JsonProperty("fullscreen")]
        public bool Fullscreen { get; set; } = true;
        
        [JsonProperty("vsync")]
        public bool VSync { get; set; } = true;
        
        [JsonProperty("frame_rate_limit")]
        public int FrameRateLimit { get; set; } = 60;
        
        [JsonProperty("graphics_quality")]
        public string GraphicsQuality { get; set; } = "High";
        
        [JsonProperty("texture_quality")]
        public string TextureQuality { get; set; } = "High";
        
        [JsonProperty("shadow_quality")]
        public string ShadowQuality { get; set; } = "Medium";
        
        [JsonProperty("anti_aliasing")]
        public string AntiAliasing { get; set; } = "FXAA";
        
        [JsonProperty("motion_blur")]
        public bool MotionBlur { get; set; } = true;
        
        [JsonProperty("bloom")]
        public bool Bloom { get; set; } = true;
        
        [JsonProperty("brightness")]
        public float Brightness { get; set; } = 0.5f;
        
        [JsonProperty("contrast")]
        public float Contrast { get; set; } = 0.5f;
    }
    
    /// <summary>
    /// Accessibility preferences
    /// </summary>
    [Serializable]
    public class AccessibilityPreferencesModel
    {
        [JsonProperty("colorblind_support")]
        public bool ColorblindSupport { get; set; } = false;
        
        [JsonProperty("colorblind_type")]
        public string ColorblindType { get; set; } = "None";
        
        [JsonProperty("high_contrast")]
        public bool HighContrast { get; set; } = false;
        
        [JsonProperty("large_text")]
        public bool LargeText { get; set; } = false;
        
        [JsonProperty("screen_reader")]
        public bool ScreenReader { get; set; } = false;
        
        [JsonProperty("subtitles")]
        public bool Subtitles { get; set; } = false;
        
        [JsonProperty("subtitle_size")]
        public float SubtitleSize { get; set; } = 1f;
        
        [JsonProperty("reduced_motion")]
        public bool ReducedMotion { get; set; } = false;
        
        [JsonProperty("simplified_ui")]
        public bool SimplifiedUI { get; set; } = false;
        
        [JsonProperty("voice_commands")]
        public bool VoiceCommands { get; set; } = false;
        
        [JsonProperty("sticky_keys")]
        public bool StickyKeys { get; set; } = false;
    }
    
    /// <summary>
    /// Privacy settings
    /// </summary>
    [Serializable]
    public class PrivacySettingsModel
    {
        [JsonProperty("profile_visibility")]
        public PrivacyLevel ProfileVisibility { get; set; } = PrivacyLevel.Public;
        
        [JsonProperty("activity_visibility")]
        public PrivacyLevel ActivityVisibility { get; set; } = PrivacyLevel.Friends;
        
        [JsonProperty("friend_list_visibility")]
        public PrivacyLevel FriendListVisibility { get; set; } = PrivacyLevel.Friends;
        
        [JsonProperty("achievement_visibility")]
        public PrivacyLevel AchievementVisibility { get; set; } = PrivacyLevel.Public;
        
        [JsonProperty("allow_friend_requests")]
        public bool AllowFriendRequests { get; set; } = true;
        
        [JsonProperty("allow_messages")]
        public bool AllowMessages { get; set; } = true;
        
        [JsonProperty("allow_invites")]
        public bool AllowInvites { get; set; } = true;
        
        [JsonProperty("show_online_status")]
        public bool ShowOnlineStatus { get; set; } = true;
        
        [JsonProperty("data_sharing")]
        public bool DataSharing { get; set; } = false;
        
        [JsonProperty("analytics")]
        public bool Analytics { get; set; } = true;
        
        [JsonProperty("personalized_ads")]
        public bool PersonalizedAds { get; set; } = false;
    }
    
    /// <summary>
    /// Communication preferences
    /// </summary>
    [Serializable]
    public class CommunicationPreferencesModel
    {
        [JsonProperty("auto_accept_friend_requests")]
        public bool AutoAcceptFriendRequests { get; set; } = false;
        
        [JsonProperty("allow_voice_chat")]
        public bool AllowVoiceChat { get; set; } = true;
        
        [JsonProperty("allow_text_chat")]
        public bool AllowTextChat { get; set; } = true;
        
        [JsonProperty("profanity_filter")]
        public bool ProfanityFilter { get; set; } = true;
        
        [JsonProperty("mature_content")]
        public bool MatureContent { get; set; } = false;
        
        [JsonProperty("block_strangers")]
        public bool BlockStrangers { get; set; } = false;
        
        [JsonProperty("auto_join_party")]
        public bool AutoJoinParty { get; set; } = false;
        
        [JsonProperty("preferred_language")]
        public Language PreferredLanguage { get; set; } = Language.English;
    }
    
    #endregion
    
    #region Update Models
    
    /// <summary>
    /// User profile update request
    /// </summary>
    [Serializable]
    public class UserProfileUpdateRequest
    {
        [JsonProperty("display_name")]
        public string DisplayName { get; set; }
        
        [JsonProperty("bio")]
        public string Bio { get; set; }
        
        [JsonProperty("location")]
        public string Location { get; set; }
        
        [JsonProperty("website")]
        public string Website { get; set; }
        
        [JsonProperty("avatar_url")]
        public string AvatarUrl { get; set; }
        
        [JsonProperty("social_links")]
        public Dictionary<string, string> SocialLinks { get; set; }
        
        [JsonProperty("interests")]
        public List<string> Interests { get; set; }
    }
    
    /// <summary>
    /// User preferences update request
    /// </summary>
    [Serializable]
    public class UserPreferencesUpdateRequest
    {
        [JsonProperty("preferences")]
        public UserPreferencesModel Preferences { get; set; }
    }
    
    /// <summary>
    /// Password change request
    /// </summary>
    [Serializable]
    public class PasswordChangeRequest
    {
        [JsonProperty("current_password")]
        public string CurrentPassword { get; set; }
        
        [JsonProperty("new_password")]
        public string NewPassword { get; set; }
        
        [JsonProperty("confirm_password")]
        public string ConfirmPassword { get; set; }
    }
    
    /// <summary>
    /// Email change request
    /// </summary>
    [Serializable]
    public class EmailChangeRequest
    {
        [JsonProperty("new_email")]
        public string NewEmail { get; set; }
        
        [JsonProperty("password")]
        public string Password { get; set; }
        
        [JsonProperty("verification_code")]
        public string VerificationCode { get; set; }
    }
    
    #endregion
    
    #region Response Models
    
    /// <summary>
    /// Generic API response
    /// </summary>
    [Serializable]
    public class ApiResponse<T>
    {
        [JsonProperty("success")]
        public bool Success { get; set; }
        
        [JsonProperty("data")]
        public T Data { get; set; }
        
        [JsonProperty("message")]
        public string Message { get; set; }
        
        [JsonProperty("errors")]
        public List<string> Errors { get; set; } = new List<string>();
        
        [JsonProperty("timestamp")]
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }
    
    /// <summary>
    /// User list response
    /// </summary>
    [Serializable]
    public class UserListResponse
    {
        [JsonProperty("users")]
        public List<UserModel> Users { get; set; } = new List<UserModel>();
        
        [JsonProperty("total")]
        public int Total { get; set; }
        
        [JsonProperty("page")]
        public int Page { get; set; }
        
        [JsonProperty("page_size")]
        public int PageSize { get; set; }
        
        [JsonProperty("has_more")]
        public bool HasMore { get; set; }
    }
    
    /// <summary>
    /// Session information
    /// </summary>
    [Serializable]
    public class SessionInfo
    {
        [JsonProperty("id")]
        public string Id { get; set; }
        
        [JsonProperty("user_id")]
        public string UserId { get; set; }
        
        [JsonProperty("device_id")]
        public string DeviceId { get; set; }
        
        [JsonProperty("ip_address")]
        public string IpAddress { get; set; }
        
        [JsonProperty("user_agent")]
        public string UserAgent { get; set; }
        
        [JsonProperty("created_at")]
        public DateTime CreatedAt { get; set; }
        
        [JsonProperty("last_activity")]
        public DateTime LastActivity { get; set; }
        
        [JsonProperty("expires_at")]
        public DateTime ExpiresAt { get; set; }
        
        [JsonProperty("is_active")]
        public bool IsActive { get; set; }
        
        [JsonProperty("location")]
        public string Location { get; set; }
    }
    
    #endregion
} 
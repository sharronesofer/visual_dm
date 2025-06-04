using System.Threading.Tasks;
using VDM.DTOs.Character;

namespace VDM.Core.Services
{
    /// <summary>
    /// Service interface for skill check operations.
    /// Communicates with the backend noncombat skills system.
    /// </summary>
    public interface ISkillCheckService
    {
        /// <summary>
        /// Execute a standard skill check.
        /// </summary>
        /// <param name="skillCheckData">Skill check parameters</param>
        /// <returns>Skill check result</returns>
        Task<SkillCheckResultDTO> MakeSkillCheckAsync(object skillCheckData);

        /// <summary>
        /// Get passive skill score for a character.
        /// </summary>
        /// <param name="passiveData">Passive skill parameters</param>
        /// <returns>Passive skill score</returns>
        Task<int> GetPassiveSkillScoreAsync(object passiveData);

        /// <summary>
        /// Execute an opposed skill check between two characters.
        /// </summary>
        /// <param name="opposedData">Opposed check parameters</param>
        /// <returns>Opposed check result</returns>
        Task<OpposedSkillCheckResultDTO> MakeOpposedSkillCheckAsync(object opposedData);

        /// <summary>
        /// Execute a group skill check.
        /// </summary>
        /// <param name="groupData">Group check parameters</param>
        /// <returns>Group check result</returns>
        Task<GroupSkillCheckResultDTO> MakeGroupSkillCheckAsync(object groupData);

        /// <summary>
        /// Execute a perception check.
        /// </summary>
        /// <param name="perceptionData">Perception check parameters</param>
        /// <returns>Perception check result</returns>
        Task<PerceptionResultDTO> MakePerceptionCheckAsync(object perceptionData);

        /// <summary>
        /// Execute a stealth check.
        /// </summary>
        /// <param name="stealthData">Stealth check parameters</param>
        /// <returns>Stealth check result</returns>
        Task<StealthResultDTO> MakeStealthCheckAsync(object stealthData);

        /// <summary>
        /// Execute a social interaction check.
        /// </summary>
        /// <param name="socialData">Social interaction parameters</param>
        /// <returns>Social interaction result</returns>
        Task<SocialResultDTO> MakeSocialCheckAsync(object socialData);

        /// <summary>
        /// Execute an investigation check.
        /// </summary>
        /// <param name="investigationData">Investigation parameters</param>
        /// <returns>Investigation result</returns>
        Task<InvestigationResultDTO> MakeInvestigationCheckAsync(object investigationData);

        /// <summary>
        /// Get available skill options for a given context.
        /// </summary>
        /// <param name="contextData">Context parameters</param>
        /// <returns>Available skill options</returns>
        Task<SkillCheckRequestDTO> GetSkillOptionsAsync(object contextData);

        /// <summary>
        /// Log a skill check result for analytics.
        /// </summary>
        /// <param name="logData">Log parameters</param>
        /// <returns>Log entry ID</returns>
        Task<string> LogSkillCheckAsync(object logData);

        /// <summary>
        /// Get skill check analytics for a character.
        /// </summary>
        /// <param name="analyticsData">Analytics parameters</param>
        /// <returns>Analytics data</returns>
        Task<object> GetSkillAnalyticsAsync(object analyticsData);
    }
} 
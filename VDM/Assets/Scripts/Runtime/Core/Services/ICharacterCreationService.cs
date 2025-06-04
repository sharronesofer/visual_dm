using System.Collections.Generic;
using System.Threading.Tasks;
using VDM.DTOs.Character;

namespace VDM.Core.Services
{
    /// <summary>
    /// Interface for character creation service operations
    /// </summary>
    public interface ICharacterCreationService
    {
        // Race and Background Data
        Task<AvailableRacesResponseDTO> GetAvailableRacesAsync();
        Task<AvailableBackgroundsResponseDTO> GetAvailableBackgroundsAsync();
        Task<RaceDTO> GetRaceDetailsAsync(string raceId);
        Task<BackgroundDTO> GetBackgroundDetailsAsync(string backgroundId);

        // Character Creation
        Task<CharacterCreationResponseDTO> CreateCharacterAsync(CharacterCreationRequestDTO request);
        Task<CharacterValidationResponseDTO> ValidateCharacterAsync(CharacterCreationRequestDTO request);
        Task<CharacterStatsDTO> CalculateCharacterStatsAsync(string raceId, string backgroundId, AttributesDTO attributes);

        // Character Management
        Task<List<CharacterDTO>> GetPlayerCharactersAsync(string playerId);
        Task<CharacterDTO> GetCharacterAsync(string characterId);
        Task<bool> DeleteCharacterAsync(string characterId);
        Task<CharacterDTO> UpdateCharacterAsync(CharacterDTO character);

        // Configuration
        Task<PointBuyConfigDTO> GetPointBuyConfigAsync();
        Task<StandardArrayConfigDTO> GetStandardArrayConfigAsync();

        // Portrait and Assets
        Task<List<string>> GetAvailablePortraitsAsync(string raceId = null);
        Task<string> UploadPortraitAsync(byte[] imageData, string fileName);
    }
} 
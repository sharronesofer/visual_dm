namespace VisualDM.Systems.Integration
{
    public interface ICharacterSystem
    {
        void OnQuestEvent(QuestEventData eventData);
        CharacterState GetCharacterStateForQuest(string questId);
        void SyncCharacterState(CharacterState state);
        // Add more methods as needed for integration
    }

    public class CharacterState
    {
        public string StateId;
        public string Description;
        // Add more fields as needed
    }
} 
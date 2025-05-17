namespace Systems.Integration
{
    public interface IWorldSystem
    {
        void OnQuestEvent(QuestEventData eventData);
        WorldState GetWorldStateForQuest(string questId);
        void SyncWorldState(WorldState state);
        // Add more methods as needed for integration
    }

    public class WorldState
    {
        public string StateId;
        public string Description;
        // Add more fields as needed
    }
} 
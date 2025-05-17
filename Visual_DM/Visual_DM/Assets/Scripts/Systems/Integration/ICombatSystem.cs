namespace Systems.Integration
{
    public interface ICombatSystem
    {
        void OnQuestEvent(QuestEventData eventData);
        CombatState GetCombatStateForQuest(string questId);
        void SyncCombatState(CombatState state);
        // Add more methods as needed for integration
    }

    // Example data structures for integration
    public class QuestEventData
    {
        public string QuestId;
        public string EventType;
        public object Payload;
    }

    public class CombatState
    {
        public string StateId;
        public string Description;
        // Add more fields as needed
    }
} 
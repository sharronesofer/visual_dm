namespace VisualDM.Systems.Integration
{
    public interface IInventorySystem
    {
        void OnQuestEvent(QuestEventData eventData);
        InventoryState GetInventoryStateForQuest(string questId);
        void SyncInventoryState(InventoryState state);
        // Add more methods as needed for integration
    }

    public class InventoryState
    {
        public string StateId;
        public string Description;
        // Add more fields as needed
    }
} 
namespace VisualDM.Systems.Integration
{
    public interface IMarketSystem
    {
        void OnQuestEvent(QuestEventData eventData);
        MarketState GetMarketStateForQuest(string questId);
        void SyncMarketState(MarketState state);
        // Add more methods as needed for integration
    }

    public class MarketState
    {
        public string StateId;
        public string Description;
        // Add more fields as needed
    }
} 
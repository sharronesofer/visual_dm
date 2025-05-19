// Canonical analytics event types:
// GameStart, GameEnd, MemoryEvent, RumorEvent, MotifEvent, PopulationEvent, POIStateEvent, FactionEvent, QuestEvent, CombatEvent, TimeEvent, StorageEvent, RelationshipEvent, WorldStateEvent, CustomEvent
public class AnalyticsEvent
{
    public int TypeId;
    public string TypeName;
    public string Payload;
    public DateTime Timestamp;
    public string SessionId;
    // Extend with additional fields as needed
} 
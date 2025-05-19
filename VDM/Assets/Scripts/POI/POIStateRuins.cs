namespace VDM.POI
{
    /// <summary>
    /// Represents the Ruins state of a POI.
    /// </summary>
    public class POIStateRuins : POIState
    {
        public POIStateRuins(IPOIStateContext context) : base(context) { }

        public override string StateName => "Ruins";

        public override void EnterState()
        {
            // Logic for entering Ruins state (e.g., visuals, disable all services)
        }

        public override void ExitState()
        {
            // Logic for exiting Ruins state
        }

        public override void CheckTransition()
        {
            // If special event triggers, transition to Dungeon
            // (Population-based transition to Dungeon is not automatic)
            // This logic will be expanded in later subtasks
        }
    }
} 
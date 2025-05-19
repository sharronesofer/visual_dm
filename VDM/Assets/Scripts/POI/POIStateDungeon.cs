namespace VDM.POI
{
    /// <summary>
    /// Represents the Dungeon state of a POI.
    /// </summary>
    public class POIStateDungeon : POIState
    {
        public POIStateDungeon(IPOIStateContext context) : base(context) { }

        public override string StateName => "Dungeon";

        public override void EnterState()
        {
            // Logic for entering Dungeon state (e.g., visuals, spawn enemies)
        }

        public override void ExitState()
        {
            // Logic for exiting Dungeon state
        }

        public override void CheckTransition()
        {
            // Dungeon is typically a terminal state; transitions out may be manual only
        }
    }
} 
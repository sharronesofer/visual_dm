namespace VDM.POI
{
    /// <summary>
    /// Represents the Declining state of a POI.
    /// </summary>
    public class POIStateDeclining : POIState
    {
        public POIStateDeclining(IPOIStateContext context) : base(context) { }

        public override string StateName => "Declining";

        public override void EnterState()
        {
            // Logic for entering Declining state (e.g., change visuals)
        }

        public override void ExitState()
        {
            // Logic for exiting Declining state
        }

        public override void CheckTransition()
        {
            var manager = context as POIStateManager;
            var rules = manager?.GetTransitionRuleSet();
            if (rules == null) return;
            // Declining -> Abandoned
            var toAbandoned = rules.GetRule(POIStateType.Declining, POIStateType.Abandoned);
            if (toAbandoned.HasValue && context.CurrentPopulation < toAbandoned.Value.populationThreshold * context.MaxPopulation)
            {
                manager.ChangeState(new POIStateAbandoned(context));
                return;
            }
            // Declining -> Normal (if not one-way)
            var toNormal = rules.GetRule(POIStateType.Declining, POIStateType.Normal);
            if (toNormal.HasValue && !toNormal.Value.oneWayOnly && context.CurrentPopulation > toNormal.Value.populationThreshold * context.MaxPopulation)
            {
                manager.ChangeState(new POIStateNormal(context));
            }
        }
    }
} 
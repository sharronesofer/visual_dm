namespace VDM.POI
{
    /// <summary>
    /// Represents the Abandoned state of a POI.
    /// </summary>
    public class POIStateAbandoned : POIState
    {
        public POIStateAbandoned(IPOIStateContext context) : base(context) { }

        public override string StateName => "Abandoned";

        public override void EnterState()
        {
            // Logic for entering Abandoned state (e.g., visuals, disable services)
        }

        public override void ExitState()
        {
            // Logic for exiting Abandoned state
        }

        public override void CheckTransition()
        {
            var manager = context as POIStateManager;
            var rules = manager?.GetTransitionRuleSet();
            if (rules == null) return;
            // Abandoned -> Ruins
            var toRuins = rules.GetRule(POIStateType.Abandoned, POIStateType.Ruins);
            if (toRuins.HasValue && context.CurrentPopulation < toRuins.Value.populationThreshold * context.MaxPopulation)
            {
                manager.ChangeState(new POIStateRuins(context));
                return;
            }
            // Abandoned -> Declining (if not one-way)
            var toDeclining = rules.GetRule(POIStateType.Abandoned, POIStateType.Declining);
            if (toDeclining.HasValue && !toDeclining.Value.oneWayOnly && context.CurrentPopulation > toDeclining.Value.populationThreshold * context.MaxPopulation)
            {
                manager.ChangeState(new POIStateDeclining(context));
            }
        }
    }
} 
namespace VDM.POI
{
    /// <summary>
    /// Represents the Normal state of a POI.
    /// </summary>
    public class POIStateNormal : POIState
    {
        public POIStateNormal(IPOIStateContext context) : base(context) { }

        public override string StateName => "Normal";

        public override void EnterState()
        {
            // Logic for entering Normal state (e.g., reset visuals)
        }

        public override void ExitState()
        {
            // Logic for exiting Normal state
        }

        public override void CheckTransition()
        {
            var manager = context as POIStateManager;
            var rules = manager?.GetTransitionRuleSet();
            if (rules == null) return;
            // Check for Normal -> Declining
            var rule = rules.GetRule(POIStateType.Normal, POIStateType.Declining);
            if (rule.HasValue && context.CurrentPopulation < rule.Value.populationThreshold * context.MaxPopulation)
            {
                manager.ChangeState(new POIStateDeclining(context));
            }
        }
    }
} 
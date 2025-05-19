namespace VDM.POI
{
    /// <summary>
    /// Interface for POI state context access, used for decoupling and testability.
    /// </summary>
    public interface IPOIStateContext
    {
        int CurrentPopulation { get; }
        int MaxPopulation { get; }
        float PopulationChangeRate { get; }
        // Add other relevant properties/methods as needed for state logic
        void ChangeState(POIState newState);
        POIState CurrentState { get; }
    }
} 
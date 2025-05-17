using Systems.Integration;

public static class IntegrationBootstrap
{
    public static void Initialize()
    {
        // ... existing registrations ...
        ChaosEngineRegistration.Register();
        // ... existing code ...
    }
}
using System;
using Systems.Integration;

namespace Systems.Integration
{
    public class ChaosEngine : IChaosEngine
    {
        private ChaosState _state = new ChaosState { ChaosLevel = 0.0f, Description = "Stable" };

        public void OnMotifEvent(MotifEventData eventData)
        {
            // Simple logic: increase chaos on certain motif events
            if (eventData.EventType == "MotifRotated" || eventData.EventType == "MotifRolled")
            {
                _state.ChaosLevel += eventData.IsChaosSource ? 0.2f : 0.05f;
                if (_state.ChaosLevel > 1.0f) _state.ChaosLevel = 1.0f;
                _state.Description = _state.ChaosLevel > 0.5f ? "Chaotic" : "Stable";
                IntegrationLogger.Log($"[ChaosEngine] Motif event received: {eventData.MotifTheme}, chaos now {_state.ChaosLevel}", LogLevel.Info, "ChaosEngine", "MotifSystem", eventData.EventType, "Info");
            }
        }

        public ChaosState GetChaosState()
        {
            return _state;
        }

        public void SyncChaosState(ChaosState state)
        {
            _state = state;
            IntegrationLogger.Log($"[ChaosEngine] Chaos state synced: {_state.ChaosLevel}", LogLevel.Info, "ChaosEngine", "System", "Sync", "Info");
        }
    }

    // Registration helper
    public static class ChaosEngineRegistration
    {
        public static void Register()
        {
            ServiceLocator.Instance.Register<IChaosEngine>(new ChaosEngine());
        }
    }
}
using UnityEngine;

namespace VisualDM.Theft
{
    public class TheftSystemBootstrapper : MonoBehaviour
    {
        private void Awake()
        {
            if (FindObjectOfType<ItemValueManager>() == null)
                new GameObject("ItemValueManager").AddComponent<ItemValueManager>();
            if (FindObjectOfType<StolenStateManager>() == null)
                new GameObject("StolenStateManager").AddComponent<StolenStateManager>();
            if (FindObjectOfType<TheftBountyCalculator>() == null)
                new GameObject("TheftBountyCalculator").AddComponent<TheftBountyCalculator>();
            if (FindObjectOfType<POIExitDetector>() == null)
                new GameObject("POIExitDetector").AddComponent<POIExitDetector>();
        }
    }
} 
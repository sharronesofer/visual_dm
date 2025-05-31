using UnityEngine;

namespace VDM.Core
{
    /// <summary>
    /// Simple test script to verify Unity compilation
    /// </summary>
    public class CompilationTest : MonoBehaviour
    {
        [Header("Test Configuration")]
        [SerializeField] private bool enableLogging = true;

        private void Start()
        {
            if (enableLogging)
            {
                Debug.Log("CompilationTest: Unity compilation successful!");
            }
        }

        /// <summary>
        /// Test method for verification
        /// </summary>
        public void TestMethod()
        {
            Debug.Log("CompilationTest: Test method executed successfully");
        }
    }
} 
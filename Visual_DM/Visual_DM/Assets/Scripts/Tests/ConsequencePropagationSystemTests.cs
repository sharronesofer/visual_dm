using System.Collections.Generic;
using NUnit.Framework;
using VisualDM.Quest;

namespace VisualDM.Tests
{
    public class MockConsequenceListener : IConsequenceListener
    {
        public List<IConsequence> Received = new();
        public void OnConsequence(IConsequence consequence)
        {
            Received.Add(consequence);
        }
    }

    public class ConsequencePropagationSystemTests
    {
        [SetUp]
        public void Setup()
        {
            // Clear listeners before each test
            var system = ConsequencePropagationSystem.Instance;
            foreach (ConsequenceCategory cat in System.Enum.GetValues(typeof(ConsequenceCategory)))
            {
                // Unregister all listeners (reflection or internal access may be needed in real code)
            }
        }

        [Test]
        public void Test_Listener_Receives_Consequence()
        {
            var system = ConsequencePropagationSystem.Instance;
            var listener = new MockConsequenceListener();
            system.RegisterListener(ConsequenceCategory.NPC, listener);
            var consequence = new Consequence
            {
                Category = ConsequenceCategory.NPC,
                Severity = ConsequenceSeverity.Major,
                Description = "NPC angered",
                Payload = null
            };
            system.PropagateConsequence(consequence);
            Assert.Contains(consequence, listener.Received);
        }

        [Test]
        public void Test_Conflict_Resolution_Highest_Severity()
        {
            var c1 = new Consequence { Severity = ConsequenceSeverity.Minor };
            var c2 = new Consequence { Severity = ConsequenceSeverity.Critical };
            var c3 = new Consequence { Severity = ConsequenceSeverity.Moderate };
            var resolved = ConsequencePropagationSystem.Instance.ResolveConflicts(new List<IConsequence> { c1, c2, c3 });
            Assert.AreEqual(ConsequenceSeverity.Critical, resolved.Severity);
        }

        [Test]
        public void Test_Chained_Consequences_Propagate()
        {
            var system = ConsequencePropagationSystem.Instance;
            var listener = new MockConsequenceListener();
            system.RegisterListener(ConsequenceCategory.Faction, listener);
            var chained = new Consequence
            {
                Category = ConsequenceCategory.Faction,
                Severity = ConsequenceSeverity.Minor,
                Description = "Faction alerted"
            };
            var root = new Consequence
            {
                Category = ConsequenceCategory.Faction,
                Severity = ConsequenceSeverity.Major,
                Description = "Faction angered",
                ChainedConsequences = new List<IConsequence> { chained }
            };
            system.PropagateConsequence(root);
            Assert.Contains(root, listener.Received);
            Assert.Contains(chained, listener.Received);
        }

        [Test]
        public void Test_Unregister_Listener()
        {
            var system = ConsequencePropagationSystem.Instance;
            var listener = new MockConsequenceListener();
            system.RegisterListener(ConsequenceCategory.World, listener);
            system.UnregisterListener(ConsequenceCategory.World, listener);
            var consequence = new Consequence { Category = ConsequenceCategory.World, Severity = ConsequenceSeverity.Minor };
            system.PropagateConsequence(consequence);
            Assert.IsEmpty(listener.Received);
        }
    }
} 
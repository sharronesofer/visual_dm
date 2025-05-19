using System;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using VisualDM.Quest;

namespace VisualDM.Tests
{
    public class ConditionalConsequenceSystemTests
    {
        [SetUp]
        public void Setup()
        {
            // Clear listeners and delayed consequences before each test
            var system = ConditionalConsequenceSystem.Instance;
            // Not directly accessible, but in real code, would reset state here
        }

        [Test]
        public void Test_And_ConditionTree_Evaluates_Correctly()
        {
            var leaf1 = new ConditionTree { Type = ConditionType.Leaf, LeafEvaluator = () => true };
            var leaf2 = new ConditionTree { Type = ConditionType.Leaf, LeafEvaluator = () => false };
            var andTree = new ConditionTree { Type = ConditionType.And, Children = new List<ConditionTree> { leaf1, leaf2 } };
            Assert.IsFalse(andTree.Evaluate());
            leaf2.LeafEvaluator = () => true;
            Assert.IsTrue(andTree.Evaluate());
        }

        [Test]
        public void Test_Or_ConditionTree_Evaluates_Correctly()
        {
            var leaf1 = new ConditionTree { Type = ConditionType.Leaf, LeafEvaluator = () => false };
            var leaf2 = new ConditionTree { Type = ConditionType.Leaf, LeafEvaluator = () => true };
            var orTree = new ConditionTree { Type = ConditionType.Or, Children = new List<ConditionTree> { leaf1, leaf2 } };
            Assert.IsTrue(orTree.Evaluate());
            leaf2.LeafEvaluator = () => false;
            Assert.IsFalse(orTree.Evaluate());
        }

        [Test]
        public void Test_Delayed_Consequence_Triggers()
        {
            var system = ConditionalConsequenceSystem.Instance;
            var consequence = new Consequence { Category = ConsequenceCategory.World, Severity = ConsequenceSeverity.Minor };
            var dc = new DelayedConsequence { Consequence = consequence, DelaySeconds = 0.01f };
            system.RegisterDelayedConsequence(dc);
            // Simulate passage of time
            dc.TriggerTime = DateTime.UtcNow.AddMilliseconds(-20);
            system.Update();
            Assert.IsTrue(dc.Triggered);
        }

        [Test]
        public void Test_TriggerListener_OnGameEvent()
        {
            var system = ConditionalConsequenceSystem.Instance;
            bool triggered = false;
            var listener = new TriggerListener
            {
                EventName = "TestEvent",
                Condition = new ConditionTree { Type = ConditionType.Leaf, LeafEvaluator = () => true },
                Consequence = new Consequence { Category = ConsequenceCategory.NPC, Severity = ConsequenceSeverity.Major },
                OnTriggered = () => triggered = true
            };
            system.RegisterTriggerListener(listener);
            system.OnGameEvent("TestEvent");
            Assert.IsTrue(triggered);
        }

        [Test]
        public void Test_Interrupt_Delayed_Consequence()
        {
            var system = ConditionalConsequenceSystem.Instance;
            bool interrupted = false;
            var dc = new DelayedConsequence { Consequence = new Consequence(), DelaySeconds = 10f, OnInterrupt = () => interrupted = true };
            system.RegisterDelayedConsequence(dc);
            system.InterruptDelayedConsequence(dc);
            Assert.IsTrue(interrupted);
        }
    }
} 
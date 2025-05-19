using NUnit.Framework;
using VDM.Systems.Combat;
using System.Collections.Generic;

namespace VDM.Tests.Systems.Combat
{
    [TestFixture]
    public class ActionPipelineTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var pipeline = new ActionPipeline();
            Assert.IsNotNull(pipeline);
        }

        [Test]
        public void AddAction_AddsActionToPipeline()
        {
            var pipeline = new ActionPipeline();
            var action = new CombatAction(CombatActionType.Attack, null, null);
            pipeline.AddAction(action);
            Assert.AreEqual(1, pipeline.ActionCount);
        }

        [Test]
        public void ProcessActions_ExecutesAllActions()
        {
            var pipeline = new ActionPipeline();
            var action1 = new CombatAction(CombatActionType.Attack, null, null);
            var action2 = new CombatAction(CombatActionType.Defend, null, null);
            pipeline.AddAction(action1);
            pipeline.AddAction(action2);
            pipeline.ProcessActions();
            Assert.AreEqual(0, pipeline.ActionCount); // Should be empty after processing
        }

        [Test]
        public void Clear_RemovesAllActions()
        {
            var pipeline = new ActionPipeline();
            pipeline.AddAction(new CombatAction(CombatActionType.Attack, null, null));
            pipeline.Clear();
            Assert.AreEqual(0, pipeline.ActionCount);
        }

        [Test]
        public void AddAction_NullAction_Throws()
        {
            var pipeline = new ActionPipeline();
            Assert.Throws<System.ArgumentNullException>(() => pipeline.AddAction(null));
        }
    }
} 
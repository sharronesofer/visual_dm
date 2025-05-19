using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using VisualDM.CombatSystem;

namespace VisualDM.Tests
{
    public class TurnBasedCombatControllerTests
    {
        private GameObject testObj;
        private TurnBasedCombatController controller;
        private GameObject entityA, entityB, entityC;

        [SetUp]
        public void SetUp()
        {
            testObj = new GameObject("TestCombatController");
            controller = testObj.AddComponent<TurnBasedCombatController>();
            entityA = new GameObject("EntityA");
            entityB = new GameObject("EntityB");
            entityC = new GameObject("EntityC");
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(testObj);
            Object.DestroyImmediate(entityA);
            Object.DestroyImmediate(entityB);
            Object.DestroyImmediate(entityC);
        }

        [Test]
        public void TestTurnOrderInitialization()
        {
            var combatants = new List<GameObject> { entityA, entityB, entityC };
            controller.StartCombat(combatants);
            var turnOrder = controller.TurnManager.GetTurnOrderSnapshot();
            Assert.AreEqual(3, turnOrder.Count);
            Assert.Contains(entityA, turnOrder);
            Assert.Contains(entityB, turnOrder);
            Assert.Contains(entityC, turnOrder);
        }

        [Test]
        public void TestAddAndRemoveCombatant()
        {
            var combatants = new List<GameObject> { entityA, entityB };
            controller.StartCombat(combatants);
            controller.AddCombatant(entityC);
            Assert.Contains(entityC, controller.TurnManager.GetTurnOrderSnapshot());
            controller.RemoveCombatant(entityB);
            Assert.IsFalse(controller.TurnManager.GetTurnOrderSnapshot().Contains(entityB));
        }

        [Test]
        public void TestProcessActionEndsTurn()
        {
            var combatants = new List<GameObject> { entityA };
            controller.StartCombat(combatants);
            bool turnEnded = false;
            controller.TurnManager.OnTurnEnded += (entity) => { turnEnded = true; };
            var request = new ActionRequest(ActionType.Attack, 1, Time.time);
            var state = new CharacterState();
            controller.ProcessAction(request, state);
            Assert.IsTrue(turnEnded);
        }

        [Test]
        public void TestGameStateValidation()
        {
            var combatants = new List<GameObject> { entityA };
            controller.StartCombat(combatants);
            var valid = controller.StateValidator.ValidateState(combatants, controller.EntityTracker);
            Assert.IsTrue(valid);
            // Simulate dead entity
            var state = controller.EntityTracker.GetState(entityA);
            state.IsAlive = false;
            valid = controller.StateValidator.ValidateState(combatants, controller.EntityTracker);
            Assert.IsFalse(valid);
        }
    }
} 
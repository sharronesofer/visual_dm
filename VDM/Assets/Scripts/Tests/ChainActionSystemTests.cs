using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using VisualDM.Systems.ChainActionSystem;

namespace VisualDM.Tests
{
    public class ChainActionSystemTests
    {
        private GameObject _testOwner;
        private ChainActionSystem _system;

        [SetUp]
        public void Setup()
        {
            _testOwner = new GameObject("TestOwner");
            var go = new GameObject("ChainActionSystem");
            _system = go.AddComponent<ChainActionSystem>();
        }

        [TearDown]
        public void Teardown()
        {
            Object.DestroyImmediate(_testOwner);
            Object.DestroyImmediate(_system.gameObject);
        }

        [UnityTest]
        public IEnumerator ChainExecutesInOrder()
        {
            var chain = new ChainDefinition
            {
                ChainName = "TestChain",
                Links = new System.Collections.Generic.List<ChainLink>
                {
                    new ChainLink { Action = new TimedChainAction("A", 0.1f) },
                    new ChainLink { Action = new TimedChainAction("B", 0.1f) },
                }
            };
            bool chainEnded = false;
            VisualDM.Systems.EventSystem.EventBus.Instance.Subscribe<ChainEndedEvent>(e =>
            {
                if (e.Definition.ChainName == "TestChain") chainEnded = true;
            });
            _system.StartChain(chain, _testOwner);
            yield return new WaitForSeconds(0.25f);
            Assert.IsTrue(chainEnded, "Chain should complete in order");
        }

        [UnityTest]
        public IEnumerator ChainCanBeInterrupted()
        {
            var chain = new ChainDefinition
            {
                ChainName = "InterruptChain",
                Links = new System.Collections.Generic.List<ChainLink>
                {
                    new ChainLink { Action = new TimedChainAction("A", 0.5f) },
                    new ChainLink { Action = new TimedChainAction("B", 0.5f) },
                }
            };
            bool interrupted = false;
            VisualDM.Systems.EventSystem.EventBus.Instance.Subscribe<ChainInterruptedEvent>(e =>
            {
                if (e.Definition.ChainName == "InterruptChain") interrupted = true;
            });
            _system.StartChain(chain, _testOwner);
            yield return new WaitForSeconds(0.1f);
            _system.InterruptChain(_testOwner, new BasicChainInterrupt(1, (ctx, act) => true));
            yield return new WaitForSeconds(0.1f);
            Assert.IsTrue(interrupted, "Chain should be interrupted");
        }

        [UnityTest]
        public IEnumerator ChainResumesAfterInterruption()
        {
            var chain = new ChainDefinition
            {
                ChainName = "ResumeChain",
                Links = new System.Collections.Generic.List<ChainLink>
                {
                    new ChainLink { Action = new TimedChainAction("A", 0.1f) },
                    new ChainLink { Action = new TimedChainAction("B", 0.1f) },
                }
            };
            bool resumed = false;
            VisualDM.Systems.EventSystem.EventBus.Instance.Subscribe<ChainResumedEvent>(e =>
            {
                if (e.Definition.ChainName == "ResumeChain") resumed = true;
            });
            _system.StartChain(chain, _testOwner);
            yield return new WaitForSeconds(0.05f);
            _system.InterruptChain(_testOwner, new BasicChainInterrupt(1, (ctx, act) => true));
            yield return new WaitForSeconds(0.05f);
            _system.ResumeChain(_testOwner);
            yield return new WaitForSeconds(0.25f);
            Assert.IsTrue(resumed, "Chain should resume after interruption");
        }

        [UnityTest]
        public IEnumerator ChainAction_EnqueuesAndExecutesThroughPipeline()
        {
            // Setup ActionQueue and ActionPipeline
            var actionQueueObj = new GameObject("ActionQueue");
            var actionQueue = actionQueueObj.AddComponent<VisualDM.Core.ActionQueue>();
            var pipeline = new ActionPipeline(new DefaultPreProcess(), new ChainActionExecutionStrategy(), new DefaultPostProcess());

            // Create a chain definition
            var chain = new ChainDefinition
            {
                ChainName = "PipelineChain",
                Links = new System.Collections.Generic.List<ChainLink>
                {
                    new ChainLink { Action = new TimedChainAction("A", 0.05f) },
                    new ChainLink { Action = new TimedChainAction("B", 0.05f) },
                }
            };
            var owner = new GameObject("PipelineOwner");
            var context = new ChainContext { Owner = owner };
            var chainCtx = new ChainActionSystem.ChainActionContext { Definition = chain, Context = context };

            // Enqueue as ChainAction
            var entry = new VisualDM.Core.ActionEntry(
                VisualDM.Core.ActionType.ChainAction,
                VisualDM.Core.ActionSource.Player,
                VisualDM.Core.PriorityTier.Normal,
                1000f,
                chainCtx
            );
            actionQueue.EnqueueAction(entry);

            // Simulate pipeline processing
            var dequeued = actionQueue.DequeueAction();
            Assert.IsNotNull(dequeued, "ChainAction should be dequeued");
            var request = new VisualDM.CombatSystem.ActionRequest(
                VisualDM.CombatSystem.ActionType.ChainAction,
                "Player",
                75,
                Time.time,
                chainCtx
            );
            bool chainStarted = false;
            VisualDM.Systems.EventSystem.EventBus.Instance.Subscribe<ChainStartedEvent>(e =>
            {
                if (e.Definition.ChainName == "PipelineChain") chainStarted = true;
            });
            pipeline.Run(request, null);
            yield return new WaitForSeconds(0.1f);
            Assert.IsTrue(chainStarted, "ChainAction should trigger ChainStartedEvent through pipeline");
        }
    }
} 
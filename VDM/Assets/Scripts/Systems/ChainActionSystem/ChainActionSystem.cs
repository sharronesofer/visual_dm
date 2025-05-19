using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.EventSystem;
using VisualDM.Systems;

namespace VisualDM.Systems.ChainActionSystem
{
    // Represents a single action in a chain
    public interface IChainAction
    {
        string Name { get; }
        bool Validate(ChainContext context);
        void Execute(ChainContext context, Action onComplete);
        bool CanInterrupt(ChainContext context, IChainInterrupt interrupt);
        void OnInterrupted(ChainContext context, IChainInterrupt interrupt);
    }

    // Represents an interruption event
    public interface IChainInterrupt
    {
        int Priority { get; }
        bool ShouldInterrupt(ChainContext context, IChainAction currentAction);
    }

    // Contextual data for chain execution
    public class ChainContext
    {
        public GameObject Owner;
        public Dictionary<string, object> Data = new();
        public int CurrentStep = 0;
        public bool IsInterrupted = false;
        public float ChainStartTime;
        public float LastActionTime;
        // Add more as needed
    }

    // Defines a chain of actions
    [Serializable]
    public class ChainDefinition
    {
        public string ChainName;
        public List<ChainLink> Links = new();
        public bool AllowBranching = false;
        public float TimeoutSeconds = 0f;
        // Add more as needed
    }

    [Serializable]
    public class ChainLink
    {
        public IChainAction Action;
        public float DelayAfter = 0f; // Time before next action
        public List<ChainBranch> Branches = new(); // For conditional logic
    }

    [Serializable]
    public class ChainBranch
    {
        public Func<ChainContext, bool> Condition;
        public int TargetLinkIndex;
    }

    // Main system for managing chain actions
    public class ChainActionSystem : MonoBehaviour
    {
        public static ChainActionSystem Instance { get; private set; }

        private readonly List<ActiveChain> _activeChains = new();

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        public void StartChain(ChainDefinition definition, GameObject owner)
        {
            var context = new ChainContext
            {
                Owner = owner,
                ChainStartTime = Time.time,
                LastActionTime = Time.time
            };
            EnqueueChainAction(definition, context);
        }

        private void EnqueueChainAction(ChainDefinition definition, ChainContext context)
        {
            // Bridge: Enqueue a ChainAction in the main ActionQueue
            var actionQueueObj = GameObject.Find("ActionQueue");
            if (actionQueueObj == null)
            {
                Debug.LogError("ActionQueue GameObject not found. ChainAction cannot be enqueued.");
                return;
            }
            var actionQueue = actionQueueObj.GetComponent<VisualDM.Core.ActionQueue>();
            if (actionQueue == null)
            {
                Debug.LogError("ActionQueue component not found. ChainAction cannot be enqueued.");
                return;
            }
            var entry = new VisualDM.Core.ActionEntry(
                VisualDM.Core.ActionType.ChainAction,
                VisualDM.Core.ActionSource.Player, // Or AI as appropriate
                VisualDM.Core.PriorityTier.Normal,
                1000f, // Expiry (ms), can be tuned
                new ChainActionContext { Definition = definition, Context = context }
            );
            actionQueue.EnqueueAction(entry);
        }

        // Helper context for passing chain data through ActionQueue
        public class ChainActionContext
        {
            public ChainDefinition Definition;
            public ChainContext Context;
        }

        private void ExecuteNextAction(ActiveChain chain)
        {
            if (chain.Context.IsInterrupted || chain.Context.CurrentStep >= chain.Definition.Links.Count)
            {
                // Systems: Chain ended (success or interrupted)
                int importance = chain.Context.IsInterrupted ? 8 : 6;
                string info = chain.Context.IsInterrupted ? "ChainInterrupted" : "ChainEnd";
                SystemsManager.Instance?.TriggerSystems(ActionType.UI, importance, chain.Context.Owner.transform.position, new SystemsContext { ExtraInfo = info });
                EventBus.Instance.Publish(new ChainEndedEvent(chain.Definition, chain.Context.Owner, chain.Context.IsInterrupted));
                _activeChains.Remove(chain);
                return;
            }
            var link = chain.Definition.Links[chain.Context.CurrentStep];
            if (!link.Action.Validate(chain.Context))
            {
                // Systems: Chain failed
                SystemsManager.Instance?.TriggerSystems(ActionType.UI, 7, chain.Context.Owner.transform.position, new SystemsContext { ExtraInfo = "ChainFailed" });
                EventBus.Instance.Publish(new ChainFailedEvent(chain.Definition, chain.Context.Owner, chain.Context.CurrentStep));
                _activeChains.Remove(chain);
                return;
            }
            // Systems: Action executed in chain
            SystemsManager.Instance?.TriggerSystems(ActionType.AttackLight, 4, chain.Context.Owner.transform.position, new SystemsContext { ExtraInfo = $"ChainAction_{chain.Context.CurrentStep}" });
            link.Action.Execute(chain.Context, () =>
            {
                chain.Context.LastActionTime = Time.time;
                // Handle branching
                if (link.Branches != null && link.Branches.Count > 0)
                {
                    foreach (var branch in link.Branches)
                    {
                        if (branch.Condition(chain.Context))
                        {
                            chain.Context.CurrentStep = branch.TargetLinkIndex;
                            ExecuteNextAction(chain);
                            return;
                        }
                    }
                }
                chain.Context.CurrentStep++;
                ExecuteNextAction(chain);
            });
        }

        public void InterruptChain(GameObject owner, IChainInterrupt interrupt)
        {
            var chain = _activeChains.Find(c => c.Context.Owner == owner);
            if (chain == null) return;
            var link = chain.Definition.Links[chain.Context.CurrentStep];
            if (link.Action.CanInterrupt(chain.Context, interrupt))
            {
                link.Action.OnInterrupted(chain.Context, interrupt);
                chain.Context.IsInterrupted = true;
                // Systems: Chain interrupted
                SystemsManager.Instance?.TriggerSystems(ActionType.UI, 8, owner.transform.position, new SystemsContext { ExtraInfo = "ChainInterrupted" });
                EventBus.Instance.Publish(new ChainInterruptedEvent(chain.Definition, owner, interrupt));
            }
        }

        // For checkpointing, resuming, etc.
        public void ResumeChain(GameObject owner)
        {
            var chain = _activeChains.Find(c => c.Context.Owner == owner && c.Context.IsInterrupted);
            if (chain == null) return;
            chain.Context.IsInterrupted = false;
            ExecuteNextAction(chain);
            EventBus.Instance.Publish(new ChainResumedEvent(chain.Definition, owner));
        }

        // Internal representation of an active chain
        private class ActiveChain
        {
            public ChainDefinition Definition;
            public ChainContext Context;
            public ActiveChain(ChainDefinition def, ChainContext ctx)
            {
                Definition = def;
                Context = ctx;
            }
        }
    }

    // Event types for observer pattern
    public record ChainStartedEvent(ChainDefinition Definition, GameObject Owner);
    public record ChainEndedEvent(ChainDefinition Definition, GameObject Owner, bool Interrupted);
    public record ChainFailedEvent(ChainDefinition Definition, GameObject Owner, int FailedStep);
    public record ChainInterruptedEvent(ChainDefinition Definition, GameObject Owner, IChainInterrupt Interrupt);
    public record ChainResumedEvent(ChainDefinition Definition, GameObject Owner);
} 
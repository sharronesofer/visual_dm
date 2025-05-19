using System;
using UnityEngine;

namespace VisualDM.Systems.ChainActionSystem
{
    // A simple timed action that completes after a delay
    public class TimedChainAction : IChainAction
    {
        public string Name { get; }
        private float _duration;
        public TimedChainAction(string name, float duration)
        {
            Name = name;
            _duration = duration;
        }
        public bool Validate(ChainContext context) => true;
        public void Execute(ChainContext context, Action onComplete)
        {
            context.Owner.GetComponent<MonoBehaviour>().StartCoroutine(WaitAndComplete(onComplete));
        }
        private System.Collections.IEnumerator WaitAndComplete(Action onComplete)
        {
            yield return new WaitForSeconds(_duration);
            onComplete?.Invoke();
        }
        public bool CanInterrupt(ChainContext context, IChainInterrupt interrupt) => true;
        public void OnInterrupted(ChainContext context, IChainInterrupt interrupt) { /* Optionally handle cleanup */ }
    }

    // A conditional action that only executes if a condition is met
    public class ConditionalChainAction : IChainAction
    {
        public string Name { get; }
        private Func<ChainContext, bool> _condition;
        public ConditionalChainAction(string name, Func<ChainContext, bool> condition)
        {
            Name = name;
            _condition = condition;
        }
        public bool Validate(ChainContext context) => _condition(context);
        public void Execute(ChainContext context, Action onComplete)
        {
            onComplete?.Invoke();
        }
        public bool CanInterrupt(ChainContext context, IChainInterrupt interrupt) => false;
        public void OnInterrupted(ChainContext context, IChainInterrupt interrupt) { }
    }

    // A simple interrupt with priority
    public class BasicChainInterrupt : IChainInterrupt
    {
        public int Priority { get; }
        private Func<ChainContext, IChainAction, bool> _shouldInterrupt;
        public BasicChainInterrupt(int priority, Func<ChainContext, IChainAction, bool> shouldInterrupt)
        {
            Priority = priority;
            _shouldInterrupt = shouldInterrupt;
        }
        public bool ShouldInterrupt(ChainContext context, IChainAction currentAction)
            => _shouldInterrupt(context, currentAction);
    }
} 